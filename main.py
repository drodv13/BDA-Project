import sys

from google.genai import types
import argparse
import pandas as pd
import json

from constants import *

from app_functions.connect_genai import connect_genai
from app_functions.connect_db import connect_db
from app_functions.print_tokens import print_tokens
from app_functions.generate_model_config import generate_model_config
from app_functions.call_function import call_function, available_functions

def main():
    client = connect_genai()

    parser = argparse.ArgumentParser(
                    prog='Mongo Agent',
                    description='CLI MongoDB Agent that helps the user generate queries and interiorize them',
                    epilog='Big Data Analytics Signature, Universidad del Pacífico')

    # positional arguments (required by default)
    parser.add_argument("prompt", type=str, help="User query in natural language.")

    # positional arguments (required by default)
    #parser.add_argument("database", type=str, help="Desired database to be worked")
    database = connect_db("proyectoBDA")

    # boolean flags (true/false switches)
    parser.add_argument( "-v", "--verbose", action="store_true", help="Increase output detail" )

    args = parser.parse_args()
    prompt = args.prompt
    verbose = args.verbose
    print(prompt)

    messages = [ types.Content(role="user", parts=[types.Part.from_text(text=args.prompt)]) ]

    model_configuration = types.GenerateContentConfig(system_instruction=SYSTEM_PROMPT,     # prompt used to set the tone of the agent
                                                      temperature=0,                        # deterministic level
                                                      tools=[available_functions],          # consider the available functions
                                                      )


    for i in range(20):
        print("\n\n\nloop:", i)
        #config = generate_model_config()
        response = client.models.generate_content(model=MODEL, contents=messages, config=model_configuration) #gemini-2.5-flash-lite
        
        if response.candidates:
            for candidate in response.candidates:
                messages.append(candidate.content)
        else:
            print("No candidates where found.")


        # --- RUN FUNCTION SELECTED BY THE AGENT--

        if response.function_calls: # check if the agent called any function
            for function_call in response.function_calls:
                print(f"\nFunction to call: {function_call.name}({function_call.args})")

                function_call_result = call_function(database, function_call, verbose)

                if function_call_result.parts == []:
                    raise Exception("function_call_result parts is empty")
                
                if function_call_result.parts[0].function_response is None:
                    raise Exception("function_call_result response is None")
                
                if function_call_result.parts[0].function_response.response is None:
                    raise Exception("function_call_result response response is None")
                
                messages.append(types.Content(role="user", parts= function_call_result.parts))

                if args.verbose:
                    result = function_call_result.parts[0].function_response.response["result"]
                    print("-> Verbose:\n\n")
                    if isinstance(result, str):
                        print(result)
                    elif isinstance(result, dict):
                        print(json.dumps(result, indent=2, ensure_ascii=False, default=str))
                    else:
                        print(pd.DataFrame(result))
                    
                    print_tokens(response)
        else:
            print("No function call found in the response.")
            print(response.text) 
            return None

    print("No solution was found within the loop.")
    sys.exit(1)


if __name__ == "__main__":
    main()
