from google import genai

def print_tokens(response):
    metadata = response.usage_metadata
    if not metadata: raise Exception("No metadata was found.")

    prompt_tokens   = metadata.prompt_token_count
    response_tokens = metadata.candidates_token_count

    if not prompt_tokens or not response_tokens: raise Exception("Token-usage data is not complete.")

    print(f"Prompt tokens: {prompt_tokens}\nResponse tokens: {response_tokens}")
