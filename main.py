import sys
import requests
import customtkinter as ctk
from tkinter import messagebox
from views.main_window import MainWindow
from controllers.app_controller import AppController

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
            # Timeout corto de 3s. Así, si no estás en la red del trabajo, brinca rápido al DDNS.
            respuesta = requests.post(url, data=params, timeout=3)
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
        except Exception as e:
            # print("Error:", e) # Puedes descomentar esto para depurar en consola
            continue # Falla de conexión, intentar con la siguiente URL
            
    return False # Ambas fallaron o no devolvieron resultados

def main():
    # Comprobar llave de acceso antes de hacer nada
    if not check_license():
        import tkinter as tk
        root = tk.Tk()
        root.withdraw() # Ocultar ventana base vacía
        messagebox.showerror("Acceso Denegado", "Acceso denegado, comunicate con el area de Logística y Planeación.")
        sys.exit()

    # Configuración de apariencia
    ctk.set_appearance_mode("Light")  # Modo tradicional (claro)
    ctk.set_default_color_theme("blue")  # Tema base de colores

    # Instanciar la vista principal
    app = MainWindow()
    
    # Instanciar el controlador y conectarlo a la vista
    controller = AppController(app)

    # Iniciar el loop principal de la aplicación
    app.mainloop()

if __name__ == "__main__":
    main()
