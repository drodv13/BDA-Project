from app_functions.connect_db import connect_db
from agent_functions.run_query import run_query
import pandas as pd


db = connect_db("sample_mflix")
movies = "movies"
filter = {"title": "The Great Train Robbery"}
limit = 5


resultado = run_query(db, movies, filter, limit)
print(pd.DataFrame(resultado))
