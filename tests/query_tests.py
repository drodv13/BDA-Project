from app_functions.connect_db import connect_db
from agent_functions.run_pipeline import run_pipeline
import pandas as pd


db = connect_db("proyectoBDA")
coleccion = db["leyes"]


print(coleccion.distinct("norma"))

"""
What are the top 5 contracts with the highest monto_contratado_total in the technology sector? Just consider the moneda: Dólar Norteamericano. Show me the descripcion_proceso, moneda and monto_contratado_total
"""


"""
pipeline = [{'$match': {'clasificacion.sector': 'Tecnología'}}, 
            {'$sort': {'monto_contratado_total': -1}}, 
            {'$limit': 5}
            ]


resultado = run_pipeline(db, contrataciones, pipeline)

if isinstance(resultado, list):
    print(pd.DataFrame(resultado))
else:
    print(resultado)
"""