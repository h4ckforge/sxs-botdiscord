from utils import db

# ============================================================
# Tabla de niveles
# ============================================================
NIVELES = [
    (0, 0, 299),
    (1, 300, 699),
    (2, 700, 1199),
    (3, 1200, 1799),
    (4, 1800, float('inf'))
]

def calcular_nivel(xp_total: int) -> int:
    """Retorna el nivel correspondiente al XP total."""
    for nivel, minimo, maximo in NIVELES:
        if minimo <= xp_total <= maximo:
            return nivel
    return 0

def xp_para_siguiente_nivel(xp_total: int) -> dict:
    """Retorna info de progreso al siguiente nivel."""
    nivel_actual = calcular_nivel(xp_total)
    for nivel, minimo, maximo in NIVELES:
        if nivel == nivel_actual + 1:
            return {
                "nivel_actual": nivel_actual,
                "nivel_siguiente": nivel,
                "xp_necesario": minimo,
                "xp_faltante": max(0, minimo - xp_total)
            }
    return {
        "nivel_actual": nivel_actual,
        "nivel_siguiente": None,
        "xp_necesario": None,
        "xp_faltante": 0
    }

def calcular_xp_evento(actividad: dict, es_creador: bool = False) -> int:
    """Calcula XP que recibe un participante por un evento."""
    xp = actividad.get("xp_base", 10)
    if es_creador:
        xp += actividad.get("xp_bonus_creador", 2)
    return xp

def actualizar_xp_temporada(miembro_id: int, temporada_id: int, xp_ganado: int, es_creador: bool = False):
    """Actualiza xp_eventos y nivel en xp_temporada para un miembro."""
    registro = db.get("xp_temporada", {
        "miembro_id": miembro_id,
        "temporada_id": temporada_id
    })

    if not registro:
        print(f"[XP] No se encontró registro xp_temporada para miembro {miembro_id}")
        return None

    r = registro[0]
    nuevo_xp_eventos = r["xp_eventos"] + xp_ganado
    nuevo_xp_total = nuevo_xp_eventos  # por ahora solo eventos
    nuevo_nivel = calcular_nivel(nuevo_xp_total)
    nuevos_eventos = r["eventos_participados"] + 1
    nuevos_creados = r["eventos_creados"] + (1 if es_creador else 0)

    db.update("xp_temporada", {
        "xp_eventos": nuevo_xp_eventos,
        "xp_total": nuevo_xp_total,
        "nivel": nuevo_nivel,
        "eventos_participados": nuevos_eventos,
        "eventos_creados": nuevos_creados
    }, {
        "miembro_id": miembro_id,
        "temporada_id": temporada_id
    })

    return {
        "xp_ganado": xp_ganado,
        "xp_total": nuevo_xp_total,
        "nivel": nuevo_nivel
    }

def actualizar_xp_shepherd(miembro_id: int, xp_ganado: int, es_raid: bool = False):
    """Actualiza xp_shepherd de un miembro. Nunca resetea."""
    registro = db.get("xp_shepherd", {"miembro_id": miembro_id})

    if registro:
        r = registro[0]
        db.update("xp_shepherd", {
            "xp_shepherd": r["xp_shepherd"] + xp_ganado,
            "raids_participadas": r["raids_participadas"] + (1 if es_raid else 0)
        }, {"miembro_id": miembro_id})
    else:
        db.insert("xp_shepherd", {
            "miembro_id": miembro_id,
            "xp_shepherd": xp_ganado,
            "raids_participadas": 1 if es_raid else 0,
            "raids_creadas": 0
        })
