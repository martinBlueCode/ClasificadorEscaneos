import json
import os

def _obtener_version():
    directorio = os.path.dirname(os.path.abspath(__file__))
    ruta_json = os.path.join(directorio, "settings.json")
    if os.path.exists(ruta_json):
        try:
            with open(ruta_json, "r", encoding="utf-8") as f:
                data = json.load(f)
                return data.get("version", "0.3")
        except Exception:
            pass
    return "0.3"

VERSION = _obtener_version()
NOMBRE_APP = f"Escaneos MB. {VERSION}"

