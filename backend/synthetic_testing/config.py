import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CACHE_DIR = os.path.join(BASE_DIR, "cache")
ANSWERS_CACHE_DIR = os.path.join(CACHE_DIR, "answers")
PERSONAS_CACHE_DIR = os.path.join(CACHE_DIR, "personas")
REPORTS_DIR = os.path.join(BASE_DIR, "reports")
MODES_DIR = os.path.join(BASE_DIR, "modes")
PERSONAS_DIR = os.path.join(BASE_DIR, "personas")
PAIRS_DIR = os.path.join(BASE_DIR, "pairs")

os.makedirs(ANSWERS_CACHE_DIR, exist_ok=True)
os.makedirs(PERSONAS_CACHE_DIR, exist_ok=True)
os.makedirs(REPORTS_DIR, exist_ok=True)
