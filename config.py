import os

# Configuración global
RUTA_BASE = r"C:\Expedientes_Prueba"
RUTA_ORIGEN_DEFECTO = r"C:\Users\LmartinezN\Desktop\DOCUMENTOS SSC"

# Paleta de 19 colores (Rojo a Gris) basada en tu espectro
PALETA_COLORES = [
    "#E8413A", "#CF1E64", "#922497", "#5B3191", "#32469A", 
    "#1A76C8", "#009FE3", "#00AEB6", "#00896F", "#499E46", 
    "#81B643", "#BCCF2A", "#FDC717", "#F99C1D", "#F26922", 
    "#E34827", "#7C564B", "#898A8C", "#5A6771"
]

def obtener_color_hover(hex_color):
    """Oscurece un color hex para el efecto hover"""
    hex_color = hex_color.lstrip('#')
    r, g, b = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    r = max(0, int(r * 0.7))
    g = max(0, int(g * 0.7))
    b = max(0, int(b * 0.7))
    return f"#{r:02x}{g:02x}{b:02x}"

# Definición de botones (sin color, se asigan dinámicamente)
DEFINICION_BOTONES = [
    ("VVE", "Visitas de verificacion"),
    ("VV_COMP", "Visitas de verificacion complementaria"),
    ("IMC", "Medidas Cautelares"),
    ("CLA", "Clausura"),
    ("IO", "Inspecciones Oculares"),
    ("RTS", "Retiro de sellos"),
    ("RPS", "Reposicion de sellos"),
    ("NCS", "Notificacion con sancion"),
    ("NSS", "Notificacion sin sancion"),
    ("NAC", "Notificacion de acuerdo"),
    ("RT-MP", "Retiro de medio publicitario"),
    ("RT-A", "Retiro de anuncio"),
    ("DEV-MP", "Devolucion de medio publicitario"),
    ("DEV-A", "Devolucion de anuncio"),
    ("DEV-\nMOBUR", "Devolucion de mobiliario urbano")
]

CLASIFICACIONES = []
for i, (nombre, desc) in enumerate(DEFINICION_BOTONES):
    color_base = PALETA_COLORES[i % len(PALETA_COLORES)]
    CLASIFICACIONES.append({
        "nombre": nombre,
        "descripcion": desc,
        "color": color_base,
        "hover": obtener_color_hover(color_base)
    })
