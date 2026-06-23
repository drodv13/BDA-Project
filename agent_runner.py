from google.genai import types
from constants import *
from app_functions.connect_genai import connect_genai
from app_functions.connect_db import connect_db
from app_functions.call_function import (
    call_function,
    available_functions
)


def ask_agent(prompt, document_content=""):

    client = connect_genai()
    database = connect_db("proyectoBDA")

    # Si el usuario subió un documento, respondemos directamente con Gemini
    # usando el texto extraído del archivo. No usamos herramientas MongoDB.
    if document_content:

        document_prompt = f"""
Eres un asistente especializado en analizar documentos de contrataciones públicas.

El usuario ha subido un documento. Responde únicamente usando el contenido del documento subido.
No llames herramientas externas.
No intentes leer archivos por nombre.
No uses read_contratacion.
No uses run_query.
No uses run_pipeline.
No uses search_related_leyes.

DOCUMENTO SUBIDO:
{document_content[:30000]}

PREGUNTA DEL USUARIO:
{prompt}
"""

        response = client.models.generate_content(
            model=MODEL,
            contents=[
                types.Content(
                    role="user",
                    parts=[
                        types.Part.from_text(text=document_prompt)
                    ]
                )
            ],
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_PROMPT,
                temperature=0,
            ),
        )

        return {
            "answer": response.text,
            "tools": []
        }

    # Si no hay documento subido, usamos el agente normal con herramientas MongoDB.
    messages = [
        types.Content(
            role="user",
            parts=[
                types.Part.from_text(text=prompt)
            ]
        )
    ]

    model_configuration = types.GenerateContentConfig(
        system_instruction=SYSTEM_PROMPT,
        temperature=0,
        tools=[available_functions],
    )

    tool_history = []

    for _ in range(20):

        response = client.models.generate_content(
            model=MODEL,
            contents=messages,
            config=model_configuration,
        )

        if response.candidates:
            for candidate in response.candidates:
                messages.append(candidate.content)

        if response.function_calls:

            for function_call in response.function_calls:

                tool_history.append(
                    {
                        "tool": function_call.name,
                        "args": dict(function_call.args)
                        if function_call.args
                        else {}
                    }
                )

                function_call_result = call_function(
                    database,
                    function_call,
                    False
                )

                messages.append(
                    types.Content(
                        role="user",
                        parts=function_call_result.parts
                    )
                )

        else:

            return {
                "answer": response.text,
                "tools": tool_history
            }

    return {
        "answer": "No se encontró una respuesta.",
        "tools": tool_history
    }
