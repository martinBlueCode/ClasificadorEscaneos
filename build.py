import json
import subprocess
import sys
import os

if hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass

RUTA_BASE = os.path.dirname(os.path.abspath(__file__))
RUTA_SETTINGS = os.path.join(RUTA_BASE, "settings.json")

def incrementar_version(version_str: str) -> str:
    """
    Incrementa la versión en formato X.Y
    Ejemplos:
    0.1 -> 0.2
    0.9 -> 1.0
    1.0 -> 1.1
    """
    partes = str(version_str).strip().split('.')
    if len(partes) != 2:
        major, minor = 0, 0
    else:
        try:
            major, minor = int(partes[0]), int(partes[1])
        except ValueError:
            major, minor = 0, 0

    minor += 1
    if minor >= 10:
        major += 1
        minor = 0

    return f"{major}.{minor}"

def obtener_configuracion() -> dict:
    if os.path.exists(RUTA_SETTINGS):
        try:
            with open(RUTA_SETTINGS, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {"version": "0.3"}

def guardar_version_en_settings(nueva_version: str):
    config = obtener_configuracion()
    config["version"] = nueva_version
    with open(RUTA_SETTINGS, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=4, ensure_ascii=False)

def limpiar_archivos_spec():
    """Elimina cualquier archivo .spec que haya quedado en la raíz"""
    for archivo in os.listdir(RUTA_BASE):
        if archivo.endswith(".spec"):
            try:
                os.remove(os.path.join(RUTA_BASE, archivo))
                print(f"🧹 Eliminado archivo .spec: {archivo}")
            except Exception:
                pass

def compilar():
    config = obtener_configuracion()
    v_actual = config.get("version", "0.3")
    v_nueva = incrementar_version(v_actual)
    guardar_version_en_settings(v_nueva)
    
    nombre_ejecutable = f"Renombrar Escaneos MB. {v_nueva}"
    
    print(f"\n=======================================================")
    print(f"🚀 Version actualizada en settings.json: {v_nueva}")
    print(f"📦 Compilando ejecutable: {nombre_ejecutable}.exe")
    print(f"=======================================================\n")
    
    # Detectar si usa OneDrive para el escritorio
    escritorio_onedrive = os.path.join(os.environ['USERPROFILE'], 'OneDrive', 'Escritorio')
    if os.path.exists(escritorio_onedrive):
        escritorio = escritorio_onedrive
    else:
        escritorio = os.path.join(os.environ['USERPROFILE'], 'Desktop')
    
    # Carpeta build donde se guardarán los archivos temporales de compilación
    carpeta_build = os.path.join(RUTA_BASE, "build")
    os.makedirs(carpeta_build, exist_ok=True)
    
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--noconsole",
        "--onefile",
        "--clean",
        "--name", nombre_ejecutable,
        "--specpath", carpeta_build,      # Guarda el .spec dentro de build/
        "--workpath", carpeta_build,      # Guarda temporales dentro de build/
        "--distpath", escritorio,
        "--hidden-import", "customtkinter",
        "--hidden-import", "tkinterdnd2",
        "--hidden-import", "pymupdf",
        "--hidden-import", "fitz",
        "--hidden-import", "PIL",
        "--hidden-import", "requests",
        "--collect-all", "customtkinter",
        "--collect-all", "tkinterdnd2",
    ]
    
    # Si existe un archivo de icono (.ico) en la carpeta, aplicarlo automáticamente
    posibles_iconos = ["icono.ico", "app.ico", "icon.ico", "logo.ico"]
    for ico in posibles_iconos:
        ico_path = os.path.join(RUTA_BASE, ico)
        if os.path.exists(ico_path):
            print(f"🎨 Usando icono: {ico}")
            cmd.extend(["--icon", ico_path])
            cmd.extend(["--add-data", f"{ico_path};."])
            break
            
    # Añadir settings.json empaquetado
    if os.path.exists(RUTA_SETTINGS):
        cmd.extend(["--add-data", f"{RUTA_SETTINGS};."])

    # Añadir carpeta resources si existe
    ruta_resources = os.path.join(RUTA_BASE, "resources")
    if os.path.exists(ruta_resources):
        cmd.extend(["--add-data", f"{ruta_resources};resources"])
        
    cmd.append("main.py")
    
    res = subprocess.run(cmd, cwd=RUTA_BASE)
    
    # Limpieza final: asegurar que no quede ningún .spec en la raíz
    limpiar_archivos_spec()
    
    if res.returncode == 0:
        print(f"\n=======================================================")
        print(f"✅ ¡Compilacion exitosa!")
        print(f"📁 Ubicacion: {escritorio}\\{nombre_ejecutable}.exe")
        print(f"✨ Raiz del proyecto 100% limpia de archivos .spec")
        print(f"=======================================================\n")
    else:
        print(f"\n❌ Error al compilar (codigo {res.returncode})\n")

if __name__ == "__main__":
    compilar()
