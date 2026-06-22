from google.genai import types
from constants import *
from app_functions.connect_genai import connect_genai
from app_functions.connect_db import connect_db
from app_functions.call_function import (
    call_function,
    available_functions
)


def ask_agent(prompt):

    client = connect_genai()
    database = connect_db("proyectoBDA")

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