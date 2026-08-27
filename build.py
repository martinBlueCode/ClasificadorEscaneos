import re
import subprocess
import sys
import os

# Ruta del archivo de versión
RUTA_VERSION = os.path.join(os.path.dirname(__file__), "version.py")

def incrementar_version(version_str: str) -> str:
    """
    Incrementa la versión en formato X.Y
    Ejemplos:
    0.1 -> 0.2
    0.9 -> 1.0
    1.0 -> 1.1
    """
    partes = version_str.strip().split('.')
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

def actualizar_archivo_version(nueva_version: str):
    contenido = f'VERSION = "{nueva_version}"\nNOMBRE_APP = f"Renombrar Escaneos MB. {{VERSION}}"\n'
    with open(RUTA_VERSION, "w", encoding="utf-8") as f:
        f.write(contenido)

def obtener_version_actual() -> str:
    if not os.path.exists(RUTA_VERSION):
        return "0.0"
    with open(RUTA_VERSION, "r", encoding="utf-8") as f:
        contenido = f.read()
    match = re.search(r'VERSION\s*=\s*["\']([^"\']+)["\']', contenido)
    return match.group(1) if match else "0.0"

def compilar():
    v_actual = obtener_version_actual()
    v_nueva = incrementar_version(v_actual)
    actualizar_archivo_version(v_nueva)
    
    nombre_ejecutable = f"Renombrar Escaneos MB. {v_nueva}"
    print(f"\n=======================================================")
    print(f"🚀 Incrementando version a: MB. {v_nueva}")
    print(f"📦 Compilando ejecutable: {nombre_ejecutable}.exe")
    print(f"=======================================================\n")
    
    import os
    
    # Detectar si usa OneDrive para el escritorio
    escritorio_onedrive = os.path.join(os.environ['USERPROFILE'], 'OneDrive', 'Escritorio')
    if os.path.exists(escritorio_onedrive):
        escritorio = escritorio_onedrive
    else:
        escritorio = os.path.join(os.environ['USERPROFILE'], 'Desktop')
    
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--noconsole",
        "--onefile",
        "--clean",
        "--name", nombre_ejecutable,
        "--distpath", escritorio,
        "--hidden-import", "customtkinter",
        "--hidden-import", "tkinterdnd2",
        "--hidden-import", "pymupdf",
        "--hidden-import", "fitz",
        "--hidden-import", "PIL",
        "--collect-all", "customtkinter",
        "--collect-all", "tkinterdnd2",
        "main.py"
    ]
    
    res = subprocess.run(cmd)
    if res.returncode == 0:
        print(f"\n=======================================================")
        print(f"✅ ¡Compilacion exitosa!")
        print(f"📁 Ubicacion: {escritorio}\\{nombre_ejecutable}.exe")
        print(f"=======================================================\n")
    else:
        print(f"\n❌ Error al compilar (codigo {res.returncode})\n")

if __name__ == "__main__":
    compilar()
