import pandas as pd
from google.genai import types
from .contratacion2json import construir_documento

schema_read_contratacion = types.FunctionDeclaration(
    name="read_contratacion",
    description=(
        "Reads a file (CSV or Excel) containing a single contratación (public contract) record "
        "and converts it into a structured JSON document matching the contrataciones collection schema. "
        "Use this FIRST when the user provides a file path to a contratación, before attempting to search "
        "for related leyes. The returned JSON gives context (sector, descripcion_proceso, monto, etc.) "
        "needed to reason about which legal norms might be relevant."
    ),
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "ruta_archivo": types.Schema(
                type=types.Type.STRING,
                description=(
                    "Absolute or relative path to the CSV or Excel (.xlsx, .xls) file containing "
                    "a single contratación record."
                )
            ),
        },
        required=["ruta_archivo"]
    )
)

def read_contratacion(ruta_archivo: str):
    """
    Lee un archivo (CSV o Excel) con una única fila de contratación
    y devuelve el documento JSON armado mediante construir_documento().
    """
    if ruta_archivo.endswith((".xlsx", ".xls")):
        df = pd.read_excel(ruta_archivo, engine="openpyxl")
    else:
        df = pd.read_csv(ruta_archivo)

    if df.empty:
        return "El archivo no contiene registros."

    df["moneda"] = df["moneda"].replace({"Nuevos Soles": "Soles"})

    # construir_documento espera un grupo (DataFrame), no una fila —
    # como solo hay una fila/item, el "grupo" es el propio df
    return construir_documento(df)