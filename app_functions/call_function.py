from google.genai import types
from agent_functions.run_query import schema_run_query, run_query
from agent_functions.run_pipeline import schema_run_pipeline, run_pipeline
from agent_functions.read_contratacion import schema_read_contratacion, read_contratacion
from agent_functions.search_related_leyes import schema_search_related_leyes, search_related_leyes
from collections.abc import Callable


def call_function( database, function_call: types.FunctionCall, verbose: bool = False ) -> types.Content:
    if verbose:
        print(f"Calling function: {function_call.name}({function_call.args})")
    else:
        print(f" - Calling function: {function_call.name}")

    function_map: dict[str, Callable[..., str]] = {
                    "run_query": run_query,
                    "run_pipeline": run_pipeline,
                    "read_contratacion": read_contratacion,
                    "search_related_leyes": search_related_leyes,
                    }
    
    if function_call.name in function_map:
        args = dict(function_call.args) if function_call.args else {}

        if function_call.name == "read_contratacion":
            function_result = function_map[function_call.name](**args)
        else:
            args["database"] = database
            function_result = function_map[function_call.name](**args)

        return types.Content(
            role="tool",
            parts=[
                types.Part.from_function_response(
                    name=function_call.name,
                    response={"result": function_result},
                )
            ],
        )

    return types.Content(
        role="tool",
        parts=[
            types.Part.from_function_response(
                name=function_call.name,
                response={"error": f"Unknown function: {function_call.name}"},
            )
        ],
    )


    

available_functions = types.Tool(
    function_declarations=[schema_run_query,
                           schema_run_pipeline,
                           schema_read_contratacion,
                           schema_search_related_leyes,
                           ],
)
