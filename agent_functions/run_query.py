from google.genai import types

schema_run_query = types.FunctionDeclaration(
    name="run_query",
    description=(
        "Runs a MongoDB find() query on a specified collection and returns the matching documents. "
        "Use this for simple filtering and lookups. "
        "The query parameter follows standard MongoDB query syntax (e.g. field filters, comparison operators). "
        "Results are limited to avoid large payloads — use the limit parameter to control how many documents to retrieve."
    ),
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "collection_name": types.Schema(
                type=types.Type.STRING,
                description="Name of the MongoDB collection to query ('leyes' or 'contrataciones')."
            ),
            "query": types.Schema(
                type=types.Type.OBJECT,
                description=(
                    "MongoDB query filter in standard MQL syntax. "
                    "Use {} to return all documents. "
                    "Supports operators like $gt, $lt, $in, $regex, etc."
                )
            ),
            "limit": types.Schema(
                type=types.Type.INTEGER,
                description="Maximum number of documents to return. Defaults to 5."
            ),
        },
        required=["collection_name", "query"]
    )
)

def run_query(database, collection_name: str, query, limit: int = 5):
    collection = database[collection_name]
    results = list(collection.find(query, {"_id": 0}).limit(limit))

    if not results: return f"No results found for **'{query}'**. Try a different search term."

    return results
