import tkinter as tk
import customtkinter as ctk
import math
import os
import threading
import time
from version import NOMBRE_APP, VERSION

class CircularProgressBar(tk.Canvas):
    def __init__(self, parent, size=150, thickness=10, bg_color="#FFFFFF", ring_bg="#E2E8F0", 
                 accent_color="#2563EB", text_color="#1E293B", font_family="Segoe UI", **kwargs):
        super().__init__(parent, width=size, height=size, bg=bg_color, highlightthickness=0, **kwargs)
        self.size = size
        self.thickness = thickness
        self.ring_bg = ring_bg
        self.accent_color = accent_color
        self.text_color = text_color
        self.font_family = font_family
        
        self.target_percent = 0.0
        self.current_percent = 0.0
        self.rotation_angle = 0.0
        self.is_animating = False
        
        self.center = size / 2
        self.radius = (size - thickness) / 2 - 4
        
        self._draw_static()

    def _draw_static(self):
        self.delete("all")
        x0 = self.center - self.radius
        y0 = self.center - self.radius
        x1 = self.center + self.radius
        y1 = self.center + self.radius
        
        # Anillo de fondo gris suave
        self.create_oval(x0, y0, x1, y1, outline=self.ring_bg, width=self.thickness)
        
        # Texto de porcentaje inicial
        self.text_id = self.create_text(
            self.center, self.center,
            text=f"{int(self.current_percent)}%",
            font=(self.font_family, 18, "bold"),
            fill=self.text_color
        )

    def set_progress(self, percent: float):
        self.target_percent = max(0.0, min(100.0, float(percent)))
        if not self.is_animating:
            self.is_animating = True
            self._animate_step()

    def _animate_step(self):
        # Suavizado / interpolación hacia el target_percent
        diff = self.target_percent - self.current_percent
        if abs(diff) > 0.3:
            self.current_percent += diff * 0.25
        else:
            self.current_percent = self.target_percent

        # Giro continuo
        self.rotation_angle = (self.rotation_angle + 6) % 360
        
        self.delete("progress_arc")
        
        x0 = self.center - self.radius
        y0 = self.center - self.radius
        x1 = self.center + self.radius
        y1 = self.center + self.radius
        
        # Longitud del arco basada en el porcentaje actual
        extent = max(10, (self.current_percent / 100.0) * 359.9)
        start_angle = (90 - self.rotation_angle) % 360
        
        # Dibujar el arco activo
        self.create_arc(
            x0, y0, x1, y1,
            start=start_angle,
            extent=-extent,
            outline=self.accent_color,
            width=self.thickness,
            style=tk.ARC,
            tags="progress_arc"
        )
        
        # Actualizar texto del porcentaje
        self.itemconfigure(self.text_id, text=f"{int(self.current_percent)}%")
        self.tag_raise(self.text_id)

        # Continuar la animación si está activa
        if self.is_animating:
            self.after(25, self._animate_step)


class SplashScreen(ctk.CTk):
    def __init__(self, on_success_callback, check_license_func):
        super().__init__()
        
        self.on_success_callback = on_success_callback
        self.check_license_func = check_license_func
        self.license_valid = False
        
        # Configuración de apariencia
        ctk.set_appearance_mode("Light")
        ctk.set_default_color_theme("blue")
        
        # Configuración de ventana sin bordes
        self.overrideredirect(True)
        self.configure(fg_color="#FFFFFF")
        
        # Icono si existe
        posibles_iconos = ["icono.ico", "app.ico", "icon.ico", "logo.ico"]
        for ico in posibles_iconos:
            if os.path.exists(ico):
                try:
                    self.iconbitmap(ico)
                except Exception:
                    pass
                break
        
        # Dimensiones y centrado
        ancho = 420
        alto = 380
        pantalla_ancho = self.winfo_screenwidth()
        pantalla_alto = self.winfo_screenheight()
        pos_x = int((pantalla_ancho - ancho) / 2)
        pos_y = int((pantalla_alto - alto) / 2)
        self.geometry(f"{ancho}x{alto}+{pos_x}+{pos_y}")
        self.attributes("-topmost", True)
        
        # Contenedor principal con tarjeta estilizada
        self.card = ctk.CTkFrame(
            self,
            fg_color="#FFFFFF",
            corner_radius=16,
            border_width=2,
            border_color="#E2E8F0"
        )
        self.card.pack(fill="both", expand=True, padx=2, pady=2)
        
        # Título y Versión
        self.lbl_title = ctk.CTkLabel(
            self.card,
            text="Clasificador de Escaneos MB",
            font=ctk.CTkFont(family="Segoe UI", size=20, weight="bold"),
            text_color="#0F172A"
        )
        self.lbl_title.pack(pady=(28, 4))
        
        self.lbl_subtitle = ctk.CTkLabel(
            self.card,
            text=f"Versión {VERSION} • Iniciando componentes",
            font=ctk.CTkFont(family="Segoe UI", size=12),
            text_color="#64748B"
        )
        self.lbl_subtitle.pack(pady=(0, 18))
        
        # Indicador Circular con Porcentaje
        self.progress_bar = CircularProgressBar(
            self.card,
            size=140,
            thickness=9,
            bg_color="#FFFFFF",
            ring_bg="#F1F5F9",
            accent_color="#2563EB",
            text_color="#1E293B",
            font_family="Segoe UI"
        )
        self.progress_bar.pack(pady=6)
        
        # Mensaje de estado dinámico
        self.lbl_status = ctk.CTkLabel(
            self.card,
            text="Iniciando sistema...",
            font=ctk.CTkFont(family="Segoe UI", size=13, weight="normal"),
            text_color="#475569"
        )
        self.lbl_status.pack(pady=(16, 6))
        
        # Etiqueta de aviso / pie de página
        self.lbl_footer = ctk.CTkLabel(
            self.card,
            text="Logística y Planeación • Por favor espere un momento",
            font=ctk.CTkFont(family="Segoe UI", size=10),
            text_color="#94A3B8"
        )
        self.lbl_footer.pack(side="bottom", pady=(0, 16))
        
        # Iniciar proceso de carga en segundo plano tras mostrar la ventana
        self.after(100, self._start_loading_task)

    def update_status(self, percent: float, text: str):
        """Actualiza el progreso y el texto de estado de forma segura para hilos"""
        self.after(0, lambda: self._apply_update(percent, text))

    def _apply_update(self, percent: float, text: str):
        self.progress_bar.set_progress(percent)
        self.lbl_status.configure(text=text)

    def _start_loading_task(self):
        threading.Thread(target=self._worker, daemon=True).start()

    def _worker(self):
        try:
            # 1. Inicio de entorno (1.0s)
            self.update_status(20, "Iniciando entorno...")
            time.sleep(1.0)
            
            # 2. Verificación de licencia (~1.0s)
            self.update_status(40, "Verificando acceso y licencia...")
            self.license_valid = self.check_license_func()
            
            if not self.license_valid:
                self.update_status(50, "Acceso no autorizado.")
                time.sleep(0.8)
                self.after(0, self._handle_license_denied)
                return
            
            time.sleep(0.8)
            
            # 3. Carga real de módulos y librerías pesadas (~1.0s)
            self.update_status(65, "Cargando módulos y componentes...")
            try:
                import fitz
                from PIL import Image
                import views.main_window
                import controllers.app_controller
                import models.file_manager
            except Exception as e:
                print(f"Advertencia precarga de módulos: {e}")
            time.sleep(0.9)
            
            # 4. Preparación de interfaz (1.0s)
            self.update_status(85, "Preparando interfaz gráfica...")
            time.sleep(1.0)
            
            # 5. Finalización exitosa (1.0s)
            self.update_status(100, "¡Iniciando aplicación!")
            time.sleep(1.0)
            
            self.after(0, self._finish_and_launch)
            
        except Exception as e:
            # En caso de error inesperado en la carga
            print(f"Error durante la inicialización: {e}")
            self.after(0, self._finish_and_launch)

    def _handle_license_denied(self):
        from tkinter import messagebox
        import sys
        self.withdraw()
        messagebox.showerror(
            "Acceso Denegado",
            "Acceso denegado, comunícate con el área de Logística y Planeación."
        )
        self.destroy()
        sys.exit()

    def _finish_and_launch(self):
        self.progress_bar.is_animating = False
        self.destroy()
        # Llamar al callback que arranca la ventana principal
        self.on_success_callback()
