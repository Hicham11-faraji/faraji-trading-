
from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from models.stock import db
from models.user import User

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/register", methods=["POST"])
def register():
    data = request.get_json()
    username = data.get("username", "").strip()
    email = data.get("email", "").strip()
    password = data.get("password", "")
    if not username or not email or not password:
        return jsonify({"error": "Tous les champs sont requis"}), 400
    if len(password) < 6:
        return jsonify({"error": "Mot de passe trop court"}), 400
    if User.query.filter_by(username=username).first():
        return jsonify({"error": "Nom d utilisateur existe déjà"}), 400
    if User.query.filter_by(email=email).first():
        return jsonify({"error": "Email déjà utilisé"}), 400
    user = User(username=username, email=email)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()
    token = create_access_token(identity=user.id)
    return jsonify({"message": "Inscription réussie", "token": token,
        "user": {"id": user.id, "username": user.username, "email": user.email, "balance": user.balance}}), 201

@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    user = User.query.filter_by(username=data.get("username", "")).first()
    if not user or not user.check_password(data.get("password", "")):
        return jsonify({"error": "Identifiants incorrects"}), 401
    token = create_access_token(identity=user.id)
    return jsonify({"message": "Connexion réussie", "token": token,
        "user": {"id": user.id, "username": user.username, "email": user.email, "balance": user.balance}})

@auth_bp.route("/profile", methods=["GET"])
@jwt_required()
def profile():
    user = User.query.get(get_jwt_identity())
    if not user:
        return jsonify({"error": "Utilisateur non trouvé"}), 404
    return jsonify({"id": user.id, "username": user.username, "email": user.email, "balance": user.balance})
