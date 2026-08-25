import customtkinter as ctk
from views.main_window import MainWindow
from controllers.app_controller import AppController

def main():
    # Configuración de apariencia
    ctk.set_appearance_mode("System")  # Modo oscuro/claro según el sistema
    ctk.set_default_color_theme("blue")  # Tema base de colores

    # Instanciar la vista principal
    app = MainWindow()
    
    # Instanciar el controlador y conectarlo a la vista
    controller = AppController(app)

    # Iniciar el loop principal de la aplicación
    app.mainloop()

if __name__ == "__main__":
    main()
