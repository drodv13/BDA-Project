from google.genai import types

schema_run_pipeline = types.FunctionDeclaration(
    name="run_pipeline",
    description=(
        "Runs a MongoDB aggregation pipeline on a specified collection and returns the results. "
        "Use this for complex operations that go beyond simple filtering, such as grouping, joining collections with $lookup, "
        "computing aggregates (sum, avg, count), reshaping documents with $project, or multi-stage transformations. "
        "Prefer this over run_query when the task requires joining collections or computing derived values."
    ),
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "collection_name": types.Schema(
                type=types.Type.STRING,
                description="Name of the MongoDB collection to run the pipeline on ('leyes' or 'contrataciones')."
            ),
            "pipeline": types.Schema(
                type=types.Type.ARRAY,
                description=(
                    "MongoDB aggregation pipeline as an array of stages. "
                    "Each stage is an object with a single operator key (e.g. $match, $group, $lookup, $sort, $limit, $project, $unwind). "
                    "Stages are executed in order."
                ),
                items=types.Schema(
                    type=types.Type.OBJECT,
                    description="A single aggregation stage (e.g. {'$match': {'stock': {'$gt': 0}}})."
                )
            ),
        },
        required=["collection_name", "pipeline"]
    )
)

def run_pipeline(database, collection_name: str, pipeline,):
    collection = database[collection_name]
    pipeline += [{"$unset": "_id"}]
    results = list(collection.aggregate(pipeline))

    if not results: return "No results found. Try adjusting your filters or search terms."

    return results
