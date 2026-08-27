import re
import subprocess
import sys
import os

# Ruta del archivo de versión
RUTA_VERSION = os.path.join(os.path.dirname(__file__), "version.py")

def incrementar_version(version_str: str) -> str:
    """
    Incrementa la versión en base decimal de 3 dígitos (X.Y.Z donde cada uno llega a 9).
    Ejemplos:
    0.0.1 -> 0.0.2
    0.0.9 -> 0.1.0
    0.1.9 -> 0.2.0
    0.9.9 -> 1.0.0
    """
    partes = version_str.strip().split('.')
    if len(partes) != 3:
        major, minor, patch = 0, 0, 1
    else:
        try:
            major, minor, patch = int(partes[0]), int(partes[1]), int(partes[2])
        except ValueError:
            major, minor, patch = 0, 0, 1

    # Calcular correlativo numérico y sumar 1
    numero_actual = major * 100 + minor * 10 + patch
    nuevo_numero = numero_actual + 1

    nuevo_major = nuevo_numero // 100
    nuevo_minor = (nuevo_numero % 100) // 10
    nuevo_patch = nuevo_numero % 10

    return f"{nuevo_major}.{nuevo_minor}.{nuevo_patch}"

def actualizar_archivo_version(nueva_version: str):
    contenido = f'VERSION = "{nueva_version}"\nNOMBRE_APP = f"Renombrar Escaneos V.{{VERSION}}"\n'
    with open(RUTA_VERSION, "w", encoding="utf-8") as f:
        f.write(contenido)

def obtener_version_actual() -> str:
    if not os.path.exists(RUTA_VERSION):
        return "0.0.0"
    with open(RUTA_VERSION, "r", encoding="utf-8") as f:
        contenido = f.read()
    match = re.search(r'VERSION\s*=\s*["\']([^"\']+)["\']', contenido)
    return match.group(1) if match else "0.0.0"

def compilar():
    v_actual = obtener_version_actual()
    v_nueva = incrementar_version(v_actual)
    actualizar_archivo_version(v_nueva)
    
    nombre_ejecutable = f"Renombrar Escaneos V.{v_nueva}"
    print(f"\n=======================================================")
    print(f"🚀 Incrementando version a: V.{v_nueva}")
    print(f"📦 Compilando ejecutable: {nombre_ejecutable}.exe")
    print(f"=======================================================\n")
    
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--noconsole",
        "--onefile",
        "--clean",
        "--name", nombre_ejecutable,
        "--hidden-import", "customtkinter",
        "--hidden-import", "tkinterdnd2",
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
        print(f"📁 Ubicacion: dist/{nombre_ejecutable}.exe")
        print(f"=======================================================\n")
    else:
        print(f"\n❌ Error al compilar (codigo {res.returncode})\n")

if __name__ == "__main__":
    compilar()
