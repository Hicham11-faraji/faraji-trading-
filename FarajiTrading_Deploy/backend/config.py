
import os

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "faraji-secret-2024")
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL",
        "sqlite:///faraji.db"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "faraji-jwt-2024")
    JWT_ACCESS_TOKEN_EXPIRES = 86400

CASABLANCA_STOCKS = {
    "ATW":  {"name": "Attijariwafa Bank",         "sector": "Banques"},
    "BCP":  {"name": "Banque Centrale Populaire", "sector": "Banques"},
    "BOA":  {"name": "Bank of Africa",            "sector": "Banques"},
    "CIH":  {"name": "CIH Bank",                 "sector": "Banques"},
    "CDM":  {"name": "Credit du Maroc",           "sector": "Banques"},
    "IAM":  {"name": "Maroc Telecom",             "sector": "Telecom"},
    "TQM":  {"name": "Taqa Morocco",              "sector": "Energie"},
    "GAZ":  {"name": "Afriquia Gaz",              "sector": "Energie"},
    "LHM":  {"name": "LafargeHolcim Maroc",       "sector": "BTP"},
    "CMA":  {"name": "Ciments du Maroc",          "sector": "BTP"},
    "MNG":  {"name": "Managem",                   "sector": "Mines"},
    "SMI":  {"name": "SMI",                       "sector": "Mines"},
    "CSR":  {"name": "Cosumar",                   "sector": "Agroalimentaire"},
    "LES":  {"name": "Lesieur Cristal",           "sector": "Agroalimentaire"},
    "DWY":  {"name": "Dari Couspate",             "sector": "Agroalimentaire"},
    "SBM":  {"name": "Brasseries du Maroc",       "sector": "Agroalimentaire"},
    "HPS":  {"name": "HPS",                       "sector": "Technologie"},
    "M2M":  {"name": "M2M Group",                 "sector": "Technologie"},
    "DIS":  {"name": "Disway",                    "sector": "Technologie"},
    "WAA":  {"name": "Wafa Assurance",            "sector": "Assurances"},
    "SAH":  {"name": "Saham Assurance",           "sector": "Assurances"},
    "ADH":  {"name": "Douja Prom Addoha",         "sector": "Immobilier"},
    "ADI":  {"name": "Alliances",                 "sector": "Immobilier"},
    "LBV":  {"name": "Label Vie",                 "sector": "Distribution"},
    "AUT":  {"name": "Auto Hall",                 "sector": "Distribution"},
    "MDP":  {"name": "Marsa Maroc",               "sector": "Transport"},
    "CTM":  {"name": "CTM",                       "sector": "Transport"},
    "SLF":  {"name": "Salafin",                   "sector": "Financement"},
    "MAB":  {"name": "Maghrebail",                "sector": "Financement"},
    "SNP":  {"name": "SNEP",                      "sector": "Chimie"},
    "ALM":  {"name": "Aluminium du Maroc",        "sector": "Industrie"},
    "NEX":  {"name": "Nexans Maroc",              "sector": "Industrie"},
    "DHO":  {"name": "Delta Holding",             "sector": "Holding"},
    "RIS":  {"name": "Risma",                     "sector": "Tourisme"},
    "PRO":  {"name": "Promopharm",                "sector": "Pharmacie"},
    "MASI": {"name": "MASI Indice",               "sector": "Indice"},
}
