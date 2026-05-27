"""Точка входа Streamlit: streamlit run app.py"""

from src.db.database import init_database
from ui.main import run

init_database()
run()
