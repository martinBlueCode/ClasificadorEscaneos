import os
import colorsys

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

def obtener_color_texto_oscuro(hex_color):
    """Genera una versión sustancialmente más oscura del mismo color para el texto"""
    hex_color = hex_color.lstrip('#')
    r, g, b = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    factor = 0.28
    return f"#{int(r * factor):02x}{int(g * factor):02x}{int(b * factor):02x}"

# Definición de botones (sin color, se asigan dinámicamente)
DEFINICION_BOTONES = [
    ("VVE", "Visitas de verificacion"),
    ("IMC", "Medidas Cautelares"),
    ("VVC", "Visitas de verificacion complementaria"),
    ("CLA", "Clausura"),
    ("IO", "Inspecciones Oculares"),
    ("RTS", "Retiro de sellos"),
    #NOTIFICACIONES CON CALENDARIO RESOLUCION Y ACUERDO
    ("AD", "Acuerdos"),
    ("RE", "Resoluciones"),
    
]

# Colores personalizados definidos por el usuario
COLORES_PERSONALIZADOS = {
    "VVE": {
        "color": "#F52727",
        "text_color": "#440303",
        "hover": obtener_color_hover("#F52727"),
        "resalte_submenu": "#FCBBBB"
    },
    "IMC": {
        "color": "#C527F5",
        "text_color": "#350344",
        "hover": obtener_color_hover("#C527F5"),
        "resalte_submenu": "#EDBBFC"
    },
    "VVC": {
        "color": "#F5275E",
        "text_color": "#440315",
        "hover": obtener_color_hover("#F5275E"),
        "resalte_submenu": "#FCBBCC"
    },
    "CLA": {
        "color": "#8B27F5",
        "text_color": "#390570",
        "hover": obtener_color_hover("#8B27F5"),
        "resalte_submenu": "#DABBFC"
    },
    "IO": {
        "color": "#F58E27",
        "text_color": "#442403",
        "hover": obtener_color_hover("#F58E27"),
        "resalte_submenu": "#FCDBBB"
    }
}

CLASIFICACIONES = []
for i, (nombre, desc) in enumerate(DEFINICION_BOTONES):
    if nombre in COLORES_PERSONALIZADOS:
        datos = COLORES_PERSONALIZADOS[nombre]
        CLASIFICACIONES.append({
            "nombre": nombre,
            "descripcion": desc,
            "color": datos["color"],
            "hover": datos.get("hover", obtener_color_hover(datos["color"])),
            "text_color": datos["text_color"],
            "resalte_submenu": datos.get("resalte_submenu")
        })
    else:
        color_base = PALETA_COLORES[i % len(PALETA_COLORES)]
        CLASIFICACIONES.append({
            "nombre": nombre,
            "descripcion": desc,
            "color": color_base,
            "hover": obtener_color_hover(color_base),
            "text_color": obtener_color_texto_oscuro(color_base),
            "resalte_submenu": None
        })

# Diccionario maestro con todas las opciones posibles para los submenús y sus siglas
DICCIONARIO_SUBMENUS_MAESTRO = {
    # Oficios de comision
    "Oficio Comision": "OC",
    "Oficio Comision (Combo)": "NAC-RTS-RPS-OC",    
    
    "Oficio Comision RPS/IMC": "RPS-IMC-OC",
    "Oficio Comision RPS/CLA": "RPS-CLA-OC",

    "Oficio Comision RTS/IMC": "IMC-OC",
    "Oficio Comision RTS/CLA": "CLA-OC",    
    "Oficio Comision RTS_IMC": "RTS_IMC-OC",

    "Oficio Comision NAC/AD": "NAC-OC",
    "Oficio Comision NCS/RE": "NCS-OC",
    "Oficio Comision NSS/RE": "NSS-OC",
    
    # Otros documentos
    "Orden": "OR",
    "Carta de derechos": "CD",
    "Acta": "AC",    
    "Informe de Inejecucion": "II",
    "Retiro de Sellos": "RTS-AC",
    "Reposicion de Sellos": "RPS-AC",
    "Inspeccion Ocular": "IO-AC",
    "Razon": "RA",
    "Acuerdo": "AD",
    "Citatorio": "CT",
    "Resolucion": "RE",
    "Acuerdo NAC/AD": "NAC",

    # Notificaciones
    "Cedula de Acuerdo": "NAC-CE", 
    "Notificacion con Sancion": "NCS-CE",
    "Notificacion sin Sancion": "NSS-CE",  
    "Citatorio de Acuerdo": "NAC-CT", 
    "Citatorio de NCS": "NCS-CT",
    "Citatorio de NSS": "NSS-CT",
    "Razon de Acuerdo": "NAC-RA", 
    "Razon de NCS": "NCS-RA",
    "Razon de NSS": "NSS-RA", 

    "Ct Instructivo de Acuerdo": "NAC-CI", 
    "Ct Instructivo de NCS": "NCS-CI",
    "Ct Instructivo de NSS": "NSS-CI",     

    # Clausura
    "Retiro de Sellos IMC": "RTS_IMC-AC",

    # Inspecciones
    "Oficio Comision S/Exp": "OC",
    "Acta S/Exp": "AC",
    "Acta IO/IMC": "IMC-AC",
    "Acta IO/CLA": "CLA-AC",
    "Acta RPS/IMC": "RPS-IMC-AC",
    "Acta RPS/CLA": "RPS-CLA-AC",
    "Acta Acuerdo/IMC": "RPS-IMC-AD",
    "Acta Acuerdo/CLA": "RPS-CLA-AD",
    "Acuerdo IMC": "IMC-AD",
    "Acuerdo CLA": "CLA-AD",

    # Retiros
    "Acta RTS/IMC": "IMC-AC",
    "Acta RTS/CLA": "CLA-AC",
    "Acuerdo/IMC": "IMC-AD",
    "Acuerdo/CLA": "CLA-AD",
    "Acuerdo/RTS/IMC": "IMC-AD",
    "Acuerdo/RTS/CLA": "CLA-AD",
    "Cedula NAC/CE": "NAC-CE",
    
    "Razon NAC/RA": "NAC-RA",
    "Citatorio NAC/CT": "NAC-CT",
    "Citatorio instructivo NAC/CI": "NAC-CI",    
    "Instructivo NAC/IN": "NAC-IN",

    # Resoluciones
    "Resolucion NCS/RE": "NCS",
    "Razon NCS/RA": "NCS-RA",
    "Citatorio NCS/CT": "NCS-CT",
    "Citatorio instructivo NCS/CI": "NCS-CI",    
    "Instructivo NCS/IN": "NCS-IN",

    "Resolucion NSS/RE": "NSS",
    "Razon NSS/RA": "NSS-RA",
    "Citatorio NSS/CT": "NSS-CT",
    "Citatorio instructivo NSS/CI": "NSS-CI",    
    "Instructivo NSS/IN": "NSS-IN"
    
}

# Configuración de qué opciones del diccionario maestro tiene cada botón
CONFIGURACION_SUBMENUS = {
    "VVE": [
        "Oficio Comision", 
        "Citatorio", 
        "Orden", 
        "Carta de derechos", 
        "Acta", 
        "Informe de Inejecucion"
    ],
    "IMC": [
        "Oficio Comision", 
        "Orden", 
        "Acta", 
        "Acuerdo", 
        "Retiro de Sellos"
    ],
    "VVC": [
        "Oficio Comision", 
        "Orden", 
        "Acta", 
        "Carta de derechos", 
        "Citatorio", 
        "Oficio Comision (Combo)",
        "Cedula de Acuerdo",
        "Citatorio de Acuerdo",
        "Retiro de Sellos", 
        "Reposicion de Sellos", 
        "Informe de Inejecucion"
    ],
    "CLA": [
        "Oficio Comision", 
        "Oficio Comision RTS_IMC",
        "Orden", 
        "Acta", 
        "Resolucion", 
        "Retiro de Sellos IMC"
    ],
    "IO": [
        "Oficio Comision S/Exp", 
        "Acta S/Exp",         
        "Oficio Comision RPS/IMC",
        "Acta IO/IMC",
        "Acta RPS/IMC",
        "Acuerdo IMC",
        "Oficio Comision RPS/CLA",
        "Acta IO/CLA",        
        "Acta RPS/CLA",
        "Acuerdo CLA" 
    ],
    "RTS": [        
        "Oficio Comision RTS/IMC",
        "Acta RTS/IMC",
        "Acuerdo/RTS/IMC", 
        "Cedula NAC/CE",
        "Oficio Comision RTS/CLA",        
        "Acta RTS/CLA",
        "Acuerdo/RTS/CLA",        
        "Cedula NAC/CE",    
        "Razon NAC/RA",    
        "Citatorio NAC/CT",    
        "Citatorio instructivo NAC/CI",
        "Instructivo NAC/IN" 
    ],
    "AD": [
        "Oficio Comision NAC/AD",
        "Acuerdo NAC/AD",
        "Razon NAC/RA",
        "Citatorio NAC/CT",
        "Citatorio instructivo NAC/CI",
        "Cedula NAC/CE",
        "Instructivo NAC/IN"
    ],
    "RE": [
        "Oficio Comision NCS/RE",
        "Resolucion NCS/RE",
        "Razon NCS/RA",
        "Citatorio NCS/CT",
        "Citatorio instructivo NCS/CI",
        "Cedula NCS/CE",
        "Instructivo NCS/IN",
        #Notificaciones sin sancion
        "Oficio Comision NSS/RE",
        "Resolucion NSS/RE",
        "Razon NSS/RA",
        "Citatorio NSS/CT",
        "Citatorio instructivo NSS/CI",
        "Cedula NSS/CE",
        "Instructivo NSS/IN"
    ],
}


