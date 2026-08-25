import customtkinter as ctk
import tkinter as tk
from PIL import Image
import os
import fitz  # PyMuPDF
import datetime
import calendar
from config import CLASIFICACIONES
from tkinterdnd2 import TkinterDnD, DND_FILES

class Tk(ctk.CTk, TkinterDnD.DnDWrapper):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.TkdndVersion = TkinterDnD._require(self)

class ToolTip:
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tooltip_window = None
        self.check_id = None
        self.widget.bind("<Enter>", self.show_tooltip)

    def show_tooltip(self, event=None):
        if self.tooltip_window:
            return
            
        x = self.widget.winfo_rootx() + 25
        y = self.widget.winfo_rooty() + 25
        self.tooltip_window = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(True)
        tw.wm_geometry(f"+{x}+{y}")
        
        label = tk.Label(tw, text=self.text, justify='left',
                         background="#2b2b2b", fg="white", relief='solid', borderwidth=1,
                         font=("Arial", 12, "normal"), padx=8, pady=4)
        label.pack(ipadx=1)
        
        self.check_mouse()

    def check_mouse(self):
        if not self.tooltip_window:
            return
            
        try:
            x, y = self.widget.winfo_pointerxy()
            wx = self.widget.winfo_rootx()
            wy = self.widget.winfo_rooty()
            ww = self.widget.winfo_width()
            wh = self.widget.winfo_height()
            
            # Si el mouse sale del perímetro, lo ocultamos de inmediato
            if not (wx <= x <= wx + ww and wy <= y <= wy + wh):
                self.hide_tooltip()
                return
                
            self.check_id = self.widget.after(50, self.check_mouse)
        except Exception:
            self.hide_tooltip()

    def hide_tooltip(self, event=None):
        if self.check_id:
            try:
                self.widget.after_cancel(self.check_id)
            except Exception:
                pass
            self.check_id = None
            
        if self.tooltip_window:
            self.tooltip_window.destroy()
            self.tooltip_window = None


class CTkCalendarPopup(ctk.CTkToplevel):
    def __init__(self, master, current_date, callback, x=None, y=None):
        super().__init__(master)
        self.title("Seleccionar Fecha")
        if x is not None and y is not None:
            self.geometry(f"300x320+{x}+{y}")
        else:
            self.geometry("300x320")
        self.resizable(False, False)
        self.transient(master)  # Vínculo a ventana principal
        self.grab_set()         # Bloquear interacción con ventana principal
        
        self.callback = callback
        self.selected_date = current_date
        self.year = current_date.year
        self.month = current_date.month
        
        # Header: Navegación de mes
        self.header_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.header_frame.pack(fill="x", padx=10, pady=10)
        
        self.btn_prev = ctk.CTkButton(self.header_frame, text="<", width=30, command=self.prev_month)
        self.btn_prev.pack(side="left")
        
        self.lbl_month = ctk.CTkLabel(self.header_frame, text="", font=("Arial", 14, "bold"))
        self.lbl_month.pack(side="left", expand=True)
        
        self.btn_next = ctk.CTkButton(self.header_frame, text=">", width=30, command=self.next_month)
        self.btn_next.pack(side="right")
        
        # Grid de días
        self.days_frame = ctk.CTkFrame(self)
        self.days_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        
        # Nombres de días de la semana
        weekdays = ["Lu", "Ma", "Mi", "Ju", "Vi", "Sá", "Do"]
        for col, day_name in enumerate(weekdays):
            lbl = ctk.CTkLabel(self.days_frame, text=day_name, font=("Arial", 11, "bold"), text_color="gray")
            lbl.grid(row=0, column=col, pady=5, sticky="nsew")
            
        for i in range(7):
            self.days_frame.grid_columnconfigure(i, weight=1)
            
        self.day_buttons = []
        self.draw_calendar()

    def draw_calendar(self):
        # Limpiar botones anteriores
        for btn in self.day_buttons:
            btn.destroy()
        self.day_buttons.clear()
        
        # Nombre del mes
        meses = [
            "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
            "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"
        ]
        self.lbl_month.configure(text=f"{meses[self.month - 1]} {self.year}")
        
        # Obtener matriz del mes
        month_cal = calendar.monthcalendar(self.year, self.month)
        
        for row_idx, week in enumerate(month_cal, start=1):
            for col_idx, day in enumerate(week):
                if day == 0:
                    continue
                # Resaltar el día seleccionado
                is_selected = (self.year == self.selected_date.year and 
                               self.month == self.selected_date.month and 
                               day == self.selected_date.day)
                
                fg_col = "#1f538d" if is_selected else "transparent"
                text_col = "white" if is_selected else ("white" if ctk.get_appearance_mode() == "Dark" else "black")
                
                btn = ctk.CTkButton(
                    self.days_frame,
                    text=str(day),
                    width=30,
                    height=30,
                    fg_color=fg_col,
                    text_color=text_col,
                    hover_color="#2b2b2b" if not is_selected else "#1f538d",
                    command=lambda d=day: self.select_day(d)
                )
                btn.grid(row=row_idx, column=col_idx, padx=2, pady=2)
                self.day_buttons.append(btn)

    def prev_month(self):
        if self.month == 1:
            self.month = 12
            self.year -= 1
        else:
            self.month -= 1
        self.draw_calendar()

    def next_month(self):
        if self.month == 12:
            self.month = 1
            self.year += 1
        else:
            self.month += 1
        self.draw_calendar()

    def select_day(self, day):
        chosen_date = datetime.date(self.year, self.month, day)
        self.callback(chosen_date)
        self.destroy()


class ClickMenu:
    def __init__(self, widget, options_dict, command_callback):
        self.widget = widget
        self.options_dict = options_dict
        self.command_callback = command_callback
        self.menu = None
        
        self.widget.configure(command=self.show_menu)
        
    def show_menu(self):
        if self.menu:
            try:
                self.menu.destroy()
            except Exception:
                pass
                
        self.menu = tk.Menu(
            self.widget,
            tearoff=0,
            background="#2b2b2b",
            foreground="white",
            activebackground="#1f538d",
            activeforeground="white",
            font=("Arial", 11)
        )
        
        def make_command(lbl):
            return lambda: self.command_callback(lbl)

        for label in self.options_dict.keys():
            self.menu.add_command(
                label=label,
                command=make_command(label)
            )
            
        x = self.widget.winfo_rootx()
        y = self.widget.winfo_rooty() + self.widget.winfo_height()
        
        self.menu.post(x, y)


class ExpedienteInputFrame(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        
        # 1. Selector de Prefijo (INVEACDMX, INVEADF)
        self.pref_combo = ctk.CTkOptionMenu(
            self,
            values=["INVEACDMX", "INVEADF"],
            width=110,
            font=("Arial", 13),
            dropdown_font=("Arial", 13)
        )
        self.pref_combo.grid(row=0, column=0, padx=(0, 2), sticky="w")
        self.pref_combo.set("INVEACDMX")  # Valor por defecto
        
        # 2. Separador Fijo: /OV/
        self.lbl_ov = ctk.CTkLabel(
            self,
            text="/OV/",
            font=("Arial", 14, "bold")
        )
        self.lbl_ov.grid(row=0, column=1, padx=2, sticky="w")
        
        # 3. Selector de Materia (DU, MP, IO, A, AFO, DUYUS, MOBUR)
        self.materia_combo = ctk.CTkOptionMenu(
            self,
            values=["DU", "MP", "IO", "A", "AFO", "DUYUS", "MOBUR"],
            width=90,
            font=("Arial", 13),
            dropdown_font=("Arial", 13)
        )
        self.materia_combo.grid(row=0, column=2, padx=2, sticky="w")
        self.materia_combo.set("DU")  # Valor por defecto
        
        # 4. Separador: /
        self.lbl_sep1 = ctk.CTkLabel(
            self,
            text="/",
            font=("Arial", 14, "bold")
        )
        self.lbl_sep1.grid(row=0, column=3, padx=2, sticky="w")
        
        # 5. Campo Numérico: 1 a 4 dígitos, solo números
        self.num_var = ctk.StringVar()
        self.num_var.trace_add("write", self._on_num_write)
        
        self.num_entry = ctk.CTkEntry(
            self,
            textvariable=self.num_var,
            width=60,
            font=("Arial", 13)
        )
        self.num_entry.grid(row=0, column=4, padx=2, sticky="w")
        
        # 6. Separador: /
        self.lbl_sep2 = ctk.CTkLabel(
            self,
            text="/",
            font=("Arial", 14, "bold")
        )
        self.lbl_sep2.grid(row=0, column=5, padx=2, sticky="w")
        
        # 7. Selector de Año: año actual y 10 años atrás
        import datetime
        current_year = datetime.datetime.now().year
        years = [str(y) for y in range(current_year, current_year - 11, -1)]
        
        self.year_combo = ctk.CTkOptionMenu(
            self,
            values=years,
            width=80,
            font=("Arial", 13),
            dropdown_font=("Arial", 13)
        )
        self.year_combo.grid(row=0, column=6, padx=(2, 0), sticky="w")
        self.year_combo.set("")  # En blanco por defecto

    def _on_num_write(self, *args):
        val = self.num_var.get()
        # Conservar solo dígitos
        clean_val = "".join([c for c in val if c.isdigit()])
        # Limitar a máximo 4 caracteres
        if len(clean_val) > 4:
            clean_val = clean_val[:4]
        if val != clean_val:
            self.num_var.set(clean_val)

    def get(self):
        prefix = self.pref_combo.get()
        materia = self.materia_combo.get()
        
        number = self.num_var.get().strip()
        # Eliminar ceros a la izquierda si es un número válido
        if number.isdigit():
            number = str(int(number))
            
        year = self.year_combo.get()
        
        # Devolver en el formato esperado
        return f"{prefix}/OV/{materia}/{number}/{year}"


class MainWindow(Tk):
    def __init__(self):
        super().__init__()
        
        # Habilitar Drag and Drop para toda la ventana
        self.drop_target_register(DND_FILES)

        self.title("Clasificador de Escaneos")
        self.geometry("1280x720")
        self.minsize(1050, 600)

        # Configurar grid (3 columnas: Izquierda - Formulario/Clasificación, Centro - Previsualización, Derecha - Lista de Archivos)
        self.grid_columnconfigure(0, weight=3, uniform="columnas")
        self.grid_columnconfigure(1, weight=4, uniform="columnas")
        self.grid_columnconfigure(2, weight=3, uniform="columnas")
        self.grid_rowconfigure(0, weight=1)

        self._crear_panel_izquierdo()
        self._crear_panel_preview()
        self._crear_panel_archivos()

    def _crear_panel_izquierdo(self):
        self.panel_izquierdo = ctk.CTkFrame(self)
        self.panel_izquierdo.grid(row=0, column=0, padx=(20, 10), pady=20, sticky="nsew")
        self.panel_izquierdo.grid_columnconfigure(0, weight=1)

        # Expediente
        ctk.CTkLabel(self.panel_izquierdo, text="Número de Expediente:", font=("Arial", 14, "bold")).grid(row=0, column=0, padx=10, pady=(20, 5), sticky="w")
        self.entry_expediente = ExpedienteInputFrame(self.panel_izquierdo)
        self.entry_expediente.grid(row=1, column=0, padx=10, pady=(0, 15), sticky="w")

        # Fecha de ejecución
        ctk.CTkLabel(self.panel_izquierdo, text="Fecha de ejecución:", font=("Arial", 14, "bold")).grid(row=2, column=0, padx=10, pady=(5, 5), sticky="w")
        self.fecha_ejecucion = datetime.date.today()
        self.btn_fecha = ctk.CTkButton(
            self.panel_izquierdo,
            text=self.fecha_ejecucion.strftime("%Y-%m-%d"),
            width=150,
            font=("Arial", 14),
            command=self.abrir_calendario
        )
        self.btn_fecha.grid(row=3, column=0, padx=10, pady=(0, 15), sticky="w")

        # Archivo activo seleccionado
        self.frame_seleccionado = ctk.CTkFrame(self.panel_izquierdo, fg_color="transparent")
        self.frame_seleccionado.grid(row=4, column=0, padx=10, pady=(0, 10), sticky="w")
        
        self.lbl_seleccionado_titulo = ctk.CTkLabel(
            self.frame_seleccionado, 
            text="Seleccionado:", 
            text_color="black",
            font=("Arial", 14, "bold")
        )
        self.lbl_seleccionado_titulo.pack(side="left", padx=(0, 5))
        
        self.lbl_archivo_activo = ctk.CTkLabel(
            self.frame_seleccionado, 
            text="Ninguno", 
            text_color="gray",
            font=("Arial", 18, "bold")
        )
        self.lbl_archivo_activo.pack(side="left")

        # Clasificaciones (ScrollableFrame para alojar los botones)
        ctk.CTkLabel(self.panel_izquierdo, text="Renombrar:", font=("Arial", 14, "bold")).grid(row=5, column=0, padx=10, pady=(10, 5), sticky="w")
        
        self.scroll_frame = ctk.CTkScrollableFrame(self.panel_izquierdo)
        self.scroll_frame.grid(row=6, column=0, padx=10, pady=5, sticky="nsew")
        self.panel_izquierdo.grid_rowconfigure(6, weight=1)

        # Configurar 4 columnas para la retícula
        self.scroll_frame.grid_columnconfigure((0, 1, 2, 3), weight=1)

        self.botones_clasificacion = []
        for i, clasif in enumerate(CLASIFICACIONES):
            r = i // 4
            c = i % 4
            btn = ctk.CTkButton(
                self.scroll_frame, 
                text=clasif["nombre"],
                font=("Arial", 13, "bold"),
                fg_color=clasif["color"], 
                hover_color=clasif["hover"],
                height=75
            )
            btn.grid(row=r, column=c, padx=4, pady=4, sticky="ew")
            self.botones_clasificacion.append(btn)

    def abrir_calendario(self):
        x = self.btn_fecha.winfo_rootx()
        y = self.btn_fecha.winfo_rooty() + self.btn_fecha.winfo_height() + 5
        CTkCalendarPopup(self, self.fecha_ejecucion, self.actualizar_fecha, x=x, y=y)

    def actualizar_fecha(self, nueva_fecha):
        self.fecha_ejecucion = nueva_fecha
        self.btn_fecha.configure(text=self.fecha_ejecucion.strftime("%Y-%m-%d"))

    def get_fecha_ejecucion(self) -> str:
        return self.fecha_ejecucion.strftime("%Y-%m-%d")

    def _crear_panel_preview(self):
        self.panel_preview = ctk.CTkFrame(self)
        self.panel_preview.grid(row=0, column=1, padx=10, pady=20, sticky="nsew")
        self.panel_preview.grid_rowconfigure(0, weight=1)
        self.panel_preview.grid_columnconfigure(0, weight=1)

        # Contenedor para el canvas del PDF
        self.frame_preview_container = ctk.CTkFrame(self.panel_preview, fg_color="transparent")
        self.frame_preview_container.grid(row=0, column=0, padx=10, pady=(10, 0), sticky="nsew")
        self.frame_preview_container.grid_propagate(False)
        self.frame_preview_container.grid_rowconfigure(0, weight=1)
        self.frame_preview_container.grid_columnconfigure(0, weight=1)

        self.lbl_preview = ctk.CTkLabel(self.frame_preview_container, text="Sin documento", fg_color="gray20", corner_radius=10)
        self.lbl_preview.grid(row=0, column=0, sticky="nsew")
        
        # Atributos para redimensionamiento
        self.original_img = None
        self.resize_timer = None
        self.frame_preview_container.bind("<Configure>", self.on_resize)

        # Controles de navegación PDF
        self.frame_nav = ctk.CTkFrame(self.panel_preview, fg_color="transparent")
        self.frame_nav.grid(row=2, column=0, pady=(0, 15))

        self.btn_prev = ctk.CTkButton(self.frame_nav, text="<", width=40, command=self.pagina_anterior, state="disabled")
        self.btn_prev.pack(side="left", padx=10)

        self.lbl_pagina = ctk.CTkLabel(self.frame_nav, text="Página 0 / 0", width=100)
        self.lbl_pagina.pack(side="left", padx=10)

        self.btn_next = ctk.CTkButton(self.frame_nav, text=">", width=40, command=self.pagina_siguiente, state="disabled")
        self.btn_next.pack(side="left", padx=10)

        # Estado del PDF
        self.current_pdf_path = None
        self.current_page = 0
        self.total_pages = 0

    def _crear_panel_archivos(self):
        self.panel_archivos = ctk.CTkFrame(self)
        self.panel_archivos.grid(row=0, column=2, padx=(10, 20), pady=20, sticky="nsew")
        self.panel_archivos.grid_rowconfigure(4, weight=1)
        self.panel_archivos.grid_columnconfigure(0, weight=1)

        # Encabezado con título y botones de control
        frame_top_archivos = ctk.CTkFrame(self.panel_archivos, fg_color="transparent")
        frame_top_archivos.grid(row=0, column=0, padx=10, pady=(15, 5), sticky="ew")
        frame_top_archivos.grid_columnconfigure(0, weight=1)

        self.lbl_titulo_archivos = ctk.CTkLabel(frame_top_archivos, text="DOCUMENTOS SSC", font=("Arial", 15, "bold"))
        self.lbl_titulo_archivos.grid(row=0, column=0, sticky="w")
        
        frame_botones_top = ctk.CTkFrame(frame_top_archivos, fg_color="transparent")
        frame_botones_top.grid(row=0, column=1, sticky="e")

        self.btn_origen = ctk.CTkButton(frame_botones_top, text="📂 Origen", width=80, height=30, font=("Arial", 13), fg_color="gray30", hover_color="gray40")
        self.btn_origen.pack(side="left", padx=2)

        self.btn_destino = ctk.CTkButton(frame_botones_top, text="📂 Destino", width=80, height=30, font=("Arial", 13), fg_color="gray30", hover_color="gray40")
        self.btn_destino.pack(side="left", padx=2)

        self.btn_refrescar = ctk.CTkButton(frame_botones_top, text="🔄 Recargar", width=80, height=30, font=("Arial", 13), fg_color="gray30", hover_color="gray40")
        self.btn_refrescar.pack(side="left", padx=2)

        # Etiqueta con ruta de la carpeta origen
        self.frame_ruta_origen = ctk.CTkFrame(self.panel_archivos, fg_color="transparent")
        self.frame_ruta_origen.grid(row=1, column=0, padx=10, pady=(15, 2), sticky="ew")
        
        self.lbl_origen_titulo = ctk.CTkLabel(
            self.frame_ruta_origen, 
            text="Origen:", 
            font=("Arial", 13, "bold"), 
            text_color="black"
        )
        self.lbl_origen_titulo.pack(side="left", padx=(0, 5))
        
        self.lbl_ruta_carpeta = ctk.CTkLabel(
            self.frame_ruta_origen, 
            text="No seleccionado", 
            font=("Arial", 14), 
            text_color="gray"
        )
        self.lbl_ruta_carpeta.pack(side="left")

        # Etiqueta con ruta de destino
        self.frame_ruta_destino = ctk.CTkFrame(self.panel_archivos, fg_color="transparent")
        self.frame_ruta_destino.grid(row=2, column=0, padx=10, pady=(0, 5), sticky="ew")
        
        self.lbl_destino_titulo = ctk.CTkLabel(
            self.frame_ruta_destino, 
            text="Destino:", 
            font=("Arial", 13, "bold"), 
            text_color="black"
        )
        self.lbl_destino_titulo.pack(side="left", padx=(0, 5))
        
        self.lbl_ruta_destino = ctk.CTkLabel(
            self.frame_ruta_destino, 
            text="Por defecto", 
            font=("Arial", 14), 
            text_color="gray"
        )
        self.lbl_ruta_destino.pack(side="left")

        # Botón Enviar a Carpeta
        self.btn_enviar = ctk.CTkButton(
            self.panel_archivos,
            text="📤 Enviar a carpeta",
            font=("Arial", 15, "bold"),
            fg_color="#10b981", # Verde
            hover_color="#059669",
            height=35
        )
        self.btn_enviar.grid(row=3, column=0, padx=10, pady=(0, 10), sticky="ew")

        # Lista de archivos con Scroll
        self.scroll_archivos = ctk.CTkScrollableFrame(self.panel_archivos)
        self.scroll_archivos.grid(row=4, column=0, padx=10, pady=5, sticky="nsew")
        self.scroll_archivos.grid_columnconfigure(0, weight=1)

        # Contador inferior
        self.lbl_total_archivos = ctk.CTkLabel(self.panel_archivos, text="0 archivos encontrados", text_color="gray", font=("Arial", 13))
        self.lbl_total_archivos.grid(row=5, column=0, padx=10, pady=(5, 10))

    def mostrar_lista_archivos(self, lista_archivos, callback_click, archivos_seleccionados=None):
        if archivos_seleccionados is None:
            archivos_seleccionados = []
            
        if not hasattr(self, 'widgets_lista'):
            self.widgets_lista = []
            
        # Limpiar lista anterior
        for widget in self.widgets_lista:
            try:
                widget.destroy()
            except:
                pass
        self.widgets_lista.clear()

        self.lbl_total_archivos.configure(text=f"{len(lista_archivos)} archivo(s) PDF encontrado(s)")

        if not lista_archivos:
            lbl_vacio = ctk.CTkLabel(self.scroll_archivos, text="No hay archivos PDF en la carpeta", text_color="gray")
            lbl_vacio.pack(pady=30)
            return

        for index, ruta_completa in enumerate(lista_archivos):
            nombre_archivo = os.path.basename(ruta_completa)
            es_activo = (ruta_completa in archivos_seleccionados)

            fg_col = "#1f538d" if es_activo else "gray22"
            hover_col = "#14375e" if es_activo else "gray32"
            txt_col = "white"

            # Reemplazar el botón simple por un contenedor para controlar fuentes independientes
            frame_item = ctk.CTkFrame(self.scroll_archivos, fg_color=fg_col, corner_radius=6, height=38)
            frame_item.pack(fill="x", padx=3, pady=3)
            frame_item.pack_propagate(False)
            self.widgets_lista.append(frame_item)

            # Icono grande
            lbl_icon = ctk.CTkLabel(frame_item, text=f"{index + 1}. 📄", font=("Arial", 22), text_color=txt_col)
            lbl_icon.pack(side="left", padx=(10, 5))

            # Texto normal
            lbl_text = ctk.CTkLabel(frame_item, text=nombre_archivo, font=("Arial", 14, "bold" if es_activo else "normal"), text_color=txt_col, anchor="w")
            lbl_text.pack(side="left", fill="x", expand=True)

            # Efectos hover
            def on_enter(e, f=frame_item, hc=hover_col):
                f.configure(fg_color=hc)
            
            def on_leave(e, f=frame_item, fc=fg_col):
                f.configure(fg_color=fc)
                
            def on_click(e, r=ruta_completa):
                # Usar after() para evitar que Tkinter crashee silenciosamente al destruir 
                # los widgets desde el mismo evento del ratón que los disparó.
                self.scroll_archivos.after(10, lambda: callback_click(r))

            frame_item.bind("<Enter>", on_enter)
            frame_item.bind("<Leave>", on_leave)
            
            frame_item.bind("<Button-1>", on_click)
            lbl_icon.bind("<Button-1>", on_click)
            lbl_text.bind("<Button-1>", on_click)

    def actualizar_contador(self, cantidad):
        self.lbl_contador.configure(text=f"{cantidad} archivos seleccionados")

    def mostrar_preview(self, ruta_documento):
        try:
            self.current_pdf_path = ruta_documento
            doc = fitz.open(ruta_documento)
            self.total_pages = doc.page_count
            doc.close()
            
            self.current_page = 0
            self.renderizar_pagina()
        except Exception as e:
            self.lbl_preview.configure(image=None, text="Error al cargar documento PDF")
            self.lbl_pagina.configure(text="Página 0 / 0")
            self.btn_prev.configure(state="disabled")
            self.btn_next.configure(state="disabled")

    def renderizar_pagina(self):
        if not self.current_pdf_path or self.total_pages == 0:
            return
            
        try:
            doc = fitz.open(self.current_pdf_path)
            pagina = doc.load_page(self.current_page)
            
            # Convertir a pixmap (imagen) con escala para mejor resolución
            pix = pagina.get_pixmap(matrix=fitz.Matrix(2, 2))
            
            # Convertir pixmap a imagen Pillow y guardarla en original_img
            mode = "RGBA" if pix.alpha else "RGB"
            self.original_img = Image.frombytes(mode, [pix.width, pix.height], pix.samples)
            
            doc.close()
            
            self.lbl_pagina.configure(text=f"Página {self.current_page + 1} / {self.total_pages}")
            
            # Actualizar botones
            self.btn_prev.configure(state="normal" if self.current_page > 0 else "disabled")
            self.btn_next.configure(state="normal" if self.current_page < self.total_pages - 1 else "disabled")
            
            # Renderizar al tamaño actual del contenedor
            self.actualizar_imagen_preview()
            
        except Exception as e:
            self.lbl_preview.configure(image=None, text="Error al renderizar página")

    def on_resize(self, event):
        if self.resize_timer:
            self.after_cancel(self.resize_timer)
        self.resize_timer = self.after(150, self.actualizar_imagen_preview)

    def actualizar_imagen_preview(self):
        if not self.original_img:
            return
            
        # Obtener tamaño actual del contenedor
        cw = self.frame_preview_container.winfo_width()
        ch = self.frame_preview_container.winfo_height()
        
        if cw < 50 or ch < 50:
            return
            
        # Calcular aspect ratio para no deformar
        img_w, img_h = self.original_img.size
        ratio_w = cw / img_w
        ratio_h = ch / img_h
        ratio = min(ratio_w, ratio_h)
        
        new_w = int(img_w * ratio)
        new_h = int(img_h * ratio)
        
        if new_w > 0 and new_h > 0:
            ctk_img = ctk.CTkImage(light_image=self.original_img, dark_image=self.original_img, size=(new_w, new_h))
            self.lbl_preview.configure(image=ctk_img, text="")

    def pagina_anterior(self):
        if self.current_page > 0:
            self.current_page -= 1
            self.renderizar_pagina()

    def pagina_siguiente(self):
        if self.current_page < self.total_pages - 1:
            self.current_page += 1
            self.renderizar_pagina()

    def limpiar_preview(self):
        self.current_pdf_path = None
        self.current_page = 0
        self.total_pages = 0
        self.original_img = None
        self.lbl_preview.configure(image=None, text="Sin imagen")
        self.lbl_pagina.configure(text="Página 0 / 0")
        self.btn_prev.configure(state="disabled")
        self.btn_next.configure(state="disabled")
