import pandas as pd
from google.genai import types

schema_search_related_leyes = types.FunctionDeclaration(
    name="search_related_leyes",
    description=(
        "Runs an aggregation pipeline against the 'leyes' collection to find legal norms that "
        "substantively affect or regulate a contratación previously loaded via read_contratacion. "
        "DO NOT rely on sector_clasificado matching alone — sector is a coarse, often unreliable "
        "auto-classification and many records have sector_clasificado='Sin clasificar'. A sector match "
        "alone is weak evidence of relevance and should never be the only filter used. "
        "\n\n"
        "Prioritize CONTENT-BASED matching, but keep regex terms SHORT and SINGLE-CONCEPT — "
        "1 to 3 words maximum, never a full phrase or sentence copied from descripcion_proceso. "
        "Laws use formal, generic legal/regulatory language; contract descriptions use specific, "
        "operational language. These rarely share exact phrasing, so searching for an exact long "
        "phrase (e.g. 'CAMPAÑA REACTIVACIÓN NORTE 2DA ETAPA') will almost always return zero results "
        "even when a relevant law exists. "
        "\n\n"
        "Instead, identify the underlying REGULATED ACTIVITY, INDUSTRY, or LEGAL CONCEPT behind the "
        "contract, and search for THAT — not the contract's own marketing/project name. "
        "Examples: a contract titled 'CAMPAÑA REACTIVACIÓN NORTE 2DA ETAPA — Facebook/Instagram Ads' "
        "is really about 'publicidad' or 'medios digitales' or 'comunicación social', not about the "
        "campaign's specific name. A contract for 'Mantenimiento de vehículos policiales' is really "
        "about 'transporte' or 'seguridad' as a regulatory domain. Strip out project codenames, dates, "
        "stage/etapa numbers, and branded platform names — search for the general subject matter instead. "
        "\n\n"
        "Run MULTIPLE separate broad searches (single short keywords, not combined into one long regex) "
        "rather than one narrow query. If a search returns zero results, broaden further (shorter word, "
        "more general concept) rather than adding more specificity. Combine a few short keyword regex "
        "matches with $or, and use sector as a secondary/supporting filter only, not the primary one. "
        "\n\n"
        "Also consider: numero/norma type filters if the contratación references a specific law by "
        "number; date range filters on publicacion if only laws in effect during vigencia.fecha_inicio "
        "to fecha_fin are relevant. "
        "\n\n"
        "Always exclude texto_completo and texto_por_pagina from the returned fields unless the user "
        "explicitly asks to read the full law text — these are large and should not be projected back."
    ),
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "pipeline": types.Schema(
                type=types.Type.ARRAY,
                description=(
                    "MongoDB aggregation pipeline as an array of stages, run against the 'leyes' collection. "
                    "Each stage is an object with a single operator key (e.g. $match, $sort, $limit, $project). "
                    "Prefer $match stages with $or combining several SHORT (1-3 word) regex terms representing "
                    "general concepts, not long literal phrases. Stages are executed in order."
                ),
                items=types.Schema(
                    type=types.Type.OBJECT,
                    description=(
                        "A single aggregation stage. Example of a GOOD content-based match (short, general terms): "
                        "{'$match': {'$or': [{'descripcion': {'$regex': 'publicidad', '$options': 'i'}}, "
                        "{'descripcion': {'$regex': 'medios digitales', '$options': 'i'}}, "
                        "{'texto_completo': {'$regex': 'comunicación social', '$options': 'i'}}]}}. "
                        "AVOID long literal phrases like {'$regex': 'CAMPAÑA REACTIVACIÓN NORTE 2DA ETAPA'} — "
                        "these almost never match anything."
                    )
                )
            ),
        },
        required=["pipeline"]
    )
)

def search_related_leyes(database, pipeline: list):
    """
    Runs an agent-constructed aggregation pipeline against the 'leyes' collection
    to find legal norms potentially relevant to a contratación the agent has
    already seen in context (via cargar_contratacion).
    """
    collection = database["leyes"]
    pipeline += [{"$unset": ["_id", "texto_completo", "texto_por_pagina"]}]
    results = list(collection.aggregate(pipeline))
    if not results:
        return "No se encontraron leyes relevantes para esta contratación."
    return results
