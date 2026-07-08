import requests
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from dotenv import load_dotenv, find_dotenv
from components.supabase import supabase

load_dotenv(find_dotenv())

API_KEY = os.getenv("SPORTS_DB")

url = 