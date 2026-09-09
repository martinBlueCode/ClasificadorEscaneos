import sys
import ctypes
import requests
import customtkinter as ctk

# Intentar cerrar pyi_splash si PyInstaller splash estuviese activo
try:
    import pyi_splash
    if hasattr(pyi_splash, 'is_alive') and pyi_splash.is_alive():
        pyi_splash.update_text("Iniciando...")
        pyi_splash.close()
    elif hasattr(pyi_splash, 'close'):
        pyi_splash.close()
except Exception:
    pass

# Control de instancia única (Mutex de Windows)
# Evita abrir múltiples instancias si el usuario presiona doble clic repetidas veces
_app_mutex = None

def asegurar_instancia_unica():
    # Solo aplicar en el ejecutable compilado para permitir reinicios en desarrollo con nodemon
    if not getattr(sys, 'frozen', False):
        return None

    global _app_mutex
    MUTEX_NAME = "Global\\ClasificadorEscaneosMB_SingleInstanceMutex"
    kernel32 = ctypes.windll.kernel32
    _app_mutex = kernel32.CreateMutexW(None, False, MUTEX_NAME)
    last_error = kernel32.GetLastError()
    # 183 = ERROR_ALREADY_EXISTS
    if last_error == 183:
        # Ya existe una instancia abierta o iniciándose
        sys.exit(0)
    return _app_mutex

def check_license():
    token = "0349b119ce074b6df00b14cba7cd27b9"
    params = {
        "token": token,
        "action": "raw_query",
        "query": "SELECT skan FROM zwrich WHERE id = 1"
    }
    
    # 1. IP Local en el trabajo
    # 2. DDNS Externo si la local falla
    urls = [
        "http://172.16.0.3/sistemacva/adminlyp/api_db.php",
        "http://lto7.ddns.net/sistemacva/adminlyp/api_db.php"
    ]
    
    for url in urls:
        try:
            # Timeout corto de 1.8s para no retrasar el inicio
            respuesta = requests.post(url, data=params, timeout=1.8)
            if respuesta.status_code == 200:
                json_res = respuesta.json()
                # La API en raw_query devuelve {"message": "...", "columns": [...], "data": [...]}
                if "error" in json_res:
                    return False
                
                datos = json_res.get("data", [])
                
                if isinstance(datos, list) and len(datos) > 0 and len(datos[0]) > 0:
                    valor_skan = str(datos[0][0])
                    if valor_skan == "1":
                        return True
                    else:
                        return False # Acceso explícitamente denegado (valor no es 1)
        except Exception:
            continue # Falla de conexión, intentar con la siguiente URL
            
    return False # Ambas fallaron o no devolvieron resultados

def main():
    asegurar_instancia_unica()
    
    from views.main_window import MainWindow
    from controllers.app_controller import AppController
    from views.splash_screen import SplashScreen

    # Configuración de apariencia
    ctk.set_appearance_mode("Light")  # Modo tradicional (claro)
    ctk.set_default_color_theme("blue")  # Tema base de colores

    # 1. Instanciar la vista principal y mantenerla oculta mientras corre el Splash
    app = MainWindow()
    app.withdraw()
    
    # 2. Instanciar el controlador y conectarlo a la vista
    controller = AppController(app)

    def al_completar_splash():
        # Mostrar ventana principal centrada y traer al frente
        if app.winfo_exists():
            app.deiconify()
            app.lift()
            app.focus_force()

    # 3. Mostrar la pantalla de carga como Toplevel sobre la aplicación
    splash = SplashScreen(
        master=app,
        on_success_callback=al_completar_splash,
        check_license_func=check_license
    )

    # Iniciar el loop principal de la aplicación
    app.mainloop()

if __name__ == "__main__":
    main()
