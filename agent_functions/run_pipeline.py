import numpy as np
import pandas as pd


def to_native(v):
    """
    Convierte recursivamente cualquier tipo numpy/pandas (int64, float64, bool_,
    Timestamp, etc.) a su equivalente nativo de Python, incluyendo dentro de
    dicts y listas anidadas. Úsalo como última capa de defensa antes de
    devolver cualquier documento que vaya a Mongo o a json.dumps/serialización.
    """
    if v is None:
        return None
    if isinstance(v, dict):
        return {k: to_native(val) for k, val in v.items()}
    if isinstance(v, (list, tuple)):
        return [to_native(item) for item in v]
    if isinstance(v, np.integer):
        return int(v)
    if isinstance(v, np.floating):
        return float(v) if not np.isnan(v) else None
    if isinstance(v, np.bool_):
        return bool(v)
    if isinstance(v, pd.Timestamp):
        return v.to_pydatetime()
    if isinstance(v, float) and pd.isna(v):
        return None
    return v


def clean_val(v):
    """Convierte NaN/NaT de pandas a None (se mantiene por compatibilidad)"""
    if pd.isna(v):
        return None
    return v


def to_dt(v):
    """Convierte Timestamp de pandas a datetime nativo (o None si es NaT)"""
    if pd.isna(v):
        return None
    return v.to_pydatetime()


def construir_documento(grupo):
    """
    Arma un documento de contrato a partir de todas las filas con el mismo
    codigo_contrato. Los campos que son constantes dentro del grupo se guardan
    una sola vez a nivel del documento; los que varían por fila (num_item,
    monto_contratado_item, ajustes, ruc_destinatario_pago) van dentro de 'items'.
    """
    primera = grupo.iloc[0]

    doc = {
        "codigo_contrato": primera["codigo_contrato"],
        "num_contrato": primera["num_contrato"],
        "descripcion_proceso": primera["descripcion_proceso"],
        "entidad": {
            "codigo_entidad": primera["codigoentidad"],
            "codigo_convocatoria": primera["codigoconvocatoria"],
        },
        "ruc_contratista": primera["ruc_contratista"],
        "moneda": primera["moneda"],
        "monto_contratado_total": primera["monto_contratado_total"],
        "items": [construir_item(fila) for _, fila in grupo.sort_values("num_item").iterrows()],
        "resolucion": {
            "tiene_resolucion": (primera["tieneresolucion"] == "SI"),
            "url_contrato": primera["urlcontrato"],
        },
        "publicacion": {
            "es_publicado": primera["espublicado"],
            "fecha_publicacion": to_dt(primera["fecha_publicacion_contrato"]),
        },
        "vigencia": {
            "fecha_suscripcion": to_dt(primera["fecha_suscripcion_contrato"]),
            "fecha_inicio": to_dt(primera["fecha_vigencia_inicial"]),
            "fecha_fin": to_dt(primera["fecha_vigencia_final"]),
            "fecha_fin_actualizada": to_dt(primera["fecha_vigencia_fin_actualizada"]),
        },
        "clasificacion": {
            "sector": primera["sector_clasificado"],
            "metodo": primera["metodo_clasificacion"],
        },
    }

    return to_native(doc)


def construir_item(fila):
    """Arma el subdocumento de item (línea de detalle / registro de movimiento)"""
    item = {
        "num_item": fila["num_item"],
        "monto_contratado_item": fila["monto_contratado_item"],
        "ruc_destinatario_pago": fila["ruc_destinatario_pago"],
        "ajustes": {
            "monto_adicional": clean_val(fila["monto_adicional"]),
            "monto_reduccion": clean_val(fila["monto_reduccion"]),
            "monto_prorroga": clean_val(fila["monto_prorroga"]),
            "monto_complementario": clean_val(fila["monto_complementario"]),
        },
    }
    return to_native(item)