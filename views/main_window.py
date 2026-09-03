import customtkinter as ctk
import tkinter as tk
from PIL import Image, ImageTk
import os
import sys
import fitz  # PyMuPDF
import datetime
import calendar
from config import CLASIFICACIONES
from version import NOMBRE_APP
from tkinterdnd2 import TkinterDnD, DND_FILES

_CACHE_CTK_DELETE_ICON = None

def obtener_icono_delete_ctk(size=(24, 24)):
    global _CACHE_CTK_DELETE_ICON
    if _CACHE_CTK_DELETE_ICON is not None:
        return _CACHE_CTK_DELETE_ICON
        
    posibles_rutas = [
        os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "resources", "delete-svg.svg"),
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "resources", "delete-svg.svg"),
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "resources", "delete-svg.svg"),
        os.path.join(os.getcwd(), "resources", "delete-svg.svg"),
        r"c:\Users\LmartinezN\Documents\CAMBIOS_SISTEMA\ClasificadorEscaneos\resources\delete-svg.svg",
        r"c:\Users\LmartinezN\Documents\BlueCore-Pandora\resources\delete-svg.svg",
    ]
    if hasattr(sys, '_MEIPASS'):
        posibles_rutas.insert(0, os.path.join(sys._MEIPASS, "resources", "delete-svg.svg"))
        posibles_rutas.insert(0, os.path.join(sys._MEIPASS, "delete-svg.svg"))

    for ruta in posibles_rutas:
        if ruta and os.path.exists(ruta):
            try:
                doc = fitz.open(ruta)
                pix = doc[0].get_pixmap(dpi=300, alpha=True)
                img = Image.frombytes("RGBA", [pix.width, pix.height], pix.samples)
                doc.close()
                _CACHE_CTK_DELETE_ICON = ctk.CTkImage(light_image=img, dark_image=img, size=size)
                return _CACHE_CTK_DELETE_ICON
            except Exception:
                pass
    return None

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
        
        is_light = ctk.get_appearance_mode() == "Light"
        bg_col = "#374151" if is_light else "#2b2b2b"
        fg_col = "white"
        label = tk.Label(tw, text=self.text, justify='left',
                         background=bg_col, fg=fg_col, relief='solid', borderwidth=1,
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


class CTkConfirmDeleteDialog(ctk.CTkToplevel):
    def __init__(self, master, filename: str, on_confirm_callback):
        super().__init__(master)
        self.title("Confirmar eliminación")
        self.on_confirm_callback = on_confirm_callback
        
        self.resizable(False, False)
        self.transient(master)
        
        # Frame contenedor
        main_frame = ctk.CTkFrame(self, fg_color="transparent")
        main_frame.pack(fill="both", expand=True, padx=25, pady=25)
        
        # Texto superior
        lbl_msg = ctk.CTkLabel(
            main_frame,
            text="Se eliminará el archivo:",
            font=("Arial", 15),
            text_color=("gray25", "gray80")
        )
        lbl_msg.pack(pady=(0, 10))
        
        # Nombre de archivo en grande
        lbl_filename = ctk.CTkLabel(
            main_frame,
            text=filename,
            font=("Arial", 17, "bold"),
            text_color=("#dc2626", "#f87171"),
            wraplength=420,
            justify="center"
        )
        lbl_filename.pack(pady=(0, 25))
        
        # Frame para botones Aceptar / Cancelar
        btn_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        btn_frame.pack(fill="x", pady=(5, 0))
        
        # Botón Aceptar (rojo)
        self.btn_aceptar = ctk.CTkButton(
            btn_frame,
            text="Aceptar",
            fg_color="#dc2626",
            hover_color="#b91c1c",
            text_color="white",
            font=("Arial", 14, "bold"),
            height=38,
            width=130,
            command=self._on_aceptar
        )
        self.btn_aceptar.pack(side="left", expand=True, padx=(0, 10))
        
        # Botón Cancelar (azul)
        self.btn_cancelar = ctk.CTkButton(
            btn_frame,
            text="Cancelar",
            fg_color="#2563eb",
            hover_color="#1d4ed8",
            text_color="white",
            font=("Arial", 14, "bold"),
            height=38,
            width=130,
            command=self._on_cancelar
        )
        self.btn_cancelar.pack(side="right", expand=True, padx=(10, 0))
        
        # Atajos de teclado
        self.bind("<Escape>", lambda e: self._on_cancelar())
        self.bind("<Return>", lambda e: self._on_aceptar())
        
        # Calcular posición centrada sobre la ventana principal
        self.update_idletasks()
        w = max(460, self.winfo_reqwidth())
        h = max(190, self.winfo_reqheight())
        try:
            x = master.winfo_rootx() + (master.winfo_width() // 2) - (w // 2)
            y = master.winfo_rooty() + (master.winfo_height() // 2) - (h // 2)
            self.geometry(f"{w}x{h}+{max(0, x)}+{max(0, y)}")
        except Exception:
            self.geometry(f"{w}x{h}")
            
        self.grab_set()
        self.btn_cancelar.focus()

    def _on_aceptar(self):
        try:
            self.grab_release()
        except Exception:
            pass
        self.destroy()
        if self.on_confirm_callback:
            self.on_confirm_callback()

    def _on_cancelar(self):
        try:
            self.grab_release()
        except Exception:
            pass
        self.destroy()


class CTkCalendarPopup(ctk.CTkToplevel):
    def __init__(self, master, current_date, callback, anchor_widget=None, x=None, y=None, theme="blue", allow_clear=False):
        super().__init__(master)
        self.title("Seleccionar Fecha")
        
        is_orange = (theme == "orange")
        is_light = ctk.get_appearance_mode() == "Light"
        self.allow_clear = allow_clear or is_orange
        self.anchor_widget = anchor_widget
        
        self.h_win = 365 if self.allow_clear else 320
        if anchor_widget and anchor_widget.winfo_exists():
            x = anchor_widget.winfo_rootx()
            y = anchor_widget.winfo_rooty() + anchor_widget.winfo_height() + 5
            self.geometry(f"300x{self.h_win}+{x}+{y}")
        elif x is not None and y is not None:
            self.geometry(f"300x{self.h_win}+{x}+{y}")
        else:
            self.geometry(f"300x{self.h_win}")
            
        self.resizable(False, False)
        self.transient(master)  # Vínculo a ventana principal
        self.grab_set()         # Bloquear interacción con ventana principal
        
        self.callback = callback
        self.selected_date = current_date
        self.year = current_date.year if current_date else datetime.date.today().year
        self.month = current_date.month if current_date else datetime.date.today().month
        self.theme = theme
        
        self.primary_color = "#ea580c" if is_orange else "#1f538d"
        self.primary_hover = "#c2410c" if is_orange else "#14375e"
        
        if is_orange:
            bg_top = "#fff7ed" if is_light else "#2a1205"
            self.configure(fg_color=bg_top)
            
        # Header: Navegación de mes
        self.header_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.header_frame.pack(fill="x", padx=10, pady=10)
        
        self.btn_prev = ctk.CTkButton(
            self.header_frame, 
            text="<", 
            width=30, 
            fg_color=self.primary_color,
            hover_color=self.primary_hover,
            command=self.prev_month
        )
        self.btn_prev.pack(side="left")
        
        month_txt_color = "#9a3412" if (is_orange and is_light) else ("#fdba74" if is_orange else None)
        self.lbl_month = ctk.CTkLabel(
            self.header_frame, 
            text="", 
            font=("Arial", 14, "bold"),
            text_color=month_txt_color if month_txt_color else ("black" if is_light else "white")
        )
        self.lbl_month.pack(side="left", expand=True)
        
        self.btn_next = ctk.CTkButton(
            self.header_frame, 
            text=">", 
            width=30, 
            fg_color=self.primary_color,
            hover_color=self.primary_hover,
            command=self.next_month
        )
        self.btn_next.pack(side="right")
        
        # Grid de días con fondo naranja si es temática naranja
        days_bg = "#ffedd5" if (is_orange and is_light) else ("#3b1708" if is_orange else None)
        if days_bg:
            self.days_frame = ctk.CTkFrame(self, fg_color=days_bg, corner_radius=8)
        else:
            self.days_frame = ctk.CTkFrame(self)
        self.days_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        
        # Nombres de días de la semana
        weekdays = ["Lu", "Ma", "Mi", "Ju", "Vi", "Sá", "Do"]
        for col, day_name in enumerate(weekdays):
            header_day_col = "#c2410c" if (is_orange and is_light) else ("#f97316" if is_orange else "gray")
            lbl = ctk.CTkLabel(self.days_frame, text=day_name, font=("Arial", 11, "bold"), text_color=header_day_col)
            lbl.grid(row=0, column=col, pady=5, sticky="nsew")
            
        for i in range(7):
            self.days_frame.grid_columnconfigure(i, weight=1)
            
        self.day_buttons = []
        self.draw_calendar()

        # Botón Borrar para eliminar la fecha y dejarla en blanco
        if self.allow_clear:
            self.bottom_frame = ctk.CTkFrame(self, fg_color="transparent")
            self.bottom_frame.pack(fill="x", padx=10, pady=(0, 10))
            
            self.btn_borrar = ctk.CTkButton(
                self.bottom_frame,
                text="🗑 Borrar",
                font=("Arial", 13, "bold"),
                fg_color=("#fee2e2", "#450a0a") if is_orange else ("gray80", "gray30"),
                text_color="#dc2626" if is_orange else ("black", "white"),
                hover_color=("#fecaca", "#7f1d1d") if is_orange else ("gray70", "gray40"),
                height=32,
                command=self.clear_date
            )
            self.btn_borrar.pack(fill="x")

        # Anclaje dinámico: si la ventana principal se mueve, mover el calendario en conjunto
        self._bind_id = self.master.bind("<Configure>", self._on_master_configure, add="+")

    def _on_master_configure(self, event=None):
        if not self.winfo_exists():
            return
        if self.anchor_widget and self.anchor_widget.winfo_exists():
            try:
                x = self.anchor_widget.winfo_rootx()
                y = self.anchor_widget.winfo_rooty() + self.anchor_widget.winfo_height() + 5
                self.geometry(f"+{x}+{y}")
            except Exception:
                pass

    def draw_calendar(self):
        # Limpiar botones anteriores
        for btn in self.day_buttons:
            btn.destroy()
        self.day_buttons.clear()
        
        is_orange = (self.theme == "orange")
        is_light = ctk.get_appearance_mode() == "Light"
        
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
                is_selected = (self.selected_date is not None and
                               self.year == self.selected_date.year and 
                               self.month == self.selected_date.month and 
                               day == self.selected_date.day)
                
                if is_selected:
                    fg_col = self.primary_color
                    text_col = "white"
                    hover_col = self.primary_hover
                else:
                    fg_col = "transparent"
                    text_col = "#7c2d12" if (is_orange and is_light) else ("#fed7aa" if is_orange else ("white" if not is_light else "black"))
                    hover_col = "#fed7aa" if (is_orange and is_light) else ("#7c2d12" if is_orange else "#2b2b2b")
                
                btn = ctk.CTkButton(
                    self.days_frame,
                    text=str(day),
                    width=30,
                    height=30,
                    fg_color=fg_col,
                    text_color=text_col,
                    hover_color=hover_col,
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

    def clear_date(self):
        self.callback(None)
        self.destroy()

    def destroy(self):
        if hasattr(self, '_bind_id') and self._bind_id and self.master:
            try:
                self.master.unbind("<Configure>", self._bind_id)
            except Exception:
                pass
            self._bind_id = None
        super().destroy()


class ClickMenu:
    def __init__(self, widget, options_dict, command_callback, active_bg=None, active_fg=None):
        self.widget = widget
        self.options_dict = options_dict
        self.command_callback = command_callback
        self.active_bg = active_bg
        self.active_fg = active_fg
        self.menu = None
        
        self.widget.configure(command=self.show_menu)
        
    def show_menu(self):
        if self.menu:
            try:
                self.menu.destroy()
            except Exception:
                pass
                
        is_light = ctk.get_appearance_mode() == "Light"
        bg_col = "#ffffff" if is_light else "#2b2b2b"
        fg_col = "#111827" if is_light else "white"
        active_bg = self.active_bg if self.active_bg else "#1f538d"
        active_fg = self.active_fg if self.active_fg else ("white" if not self.active_bg else "#111827")

        self.menu = tk.Menu(
            self.widget,
            tearoff=0,
            background=bg_col,
            foreground=fg_col,
            activebackground=active_bg,
            activeforeground=active_fg,
            font=("Arial", 11)
        )
        
        def make_command(lbl):
            return lambda: self.command_callback(lbl)

        btn_text = self.widget.cget("text")
        for idx, label in enumerate(self.options_dict.keys()):
            item_kwargs = {
                "label": label,
                "command": make_command(label)
            }
            # Opciones de VVC (primeras 5 y últimas 6)
            if btn_text == "VVC":
                if idx < 5:
                    vvc_bg = "#FAC7EA"
                    vvc_hover_bg = "#f7b0e0"
                else:
                    vvc_bg = "#EAFAC7"
                    vvc_hover_bg = "#dbf5ad"
                item_kwargs["background"] = vvc_bg
                item_kwargs["foreground"] = "black"
                item_kwargs["activebackground"] = vvc_hover_bg
                item_kwargs["activeforeground"] = "black"

            # Opciones de IO (primeras 2, 3 a 5, 6 a 9)
            elif btn_text == "IO":
                if idx < 2:
                    io_bg = "#FDE3AF"
                    io_hover_bg = "#fcd992"
                elif idx < 5:
                    io_bg = "#EAFAC7"
                    io_hover_bg = "#dbf5ad"
                else:
                    io_bg = "#E9BFFD"
                    io_hover_bg = "#dfa6f7"
                item_kwargs["background"] = io_bg
                item_kwargs["foreground"] = "black"
                item_kwargs["activebackground"] = io_hover_bg
                item_kwargs["activeforeground"] = "black"

            # Opciones de RTS (primeras 4, opciones 5 en adelante)
            elif btn_text == "RTS":
                if idx < 4:
                    rts_bg = "#BACDF2"
                    rts_hover_bg = "#a2bbf0"
                else:
                    rts_bg = "#F2BACD"
                    rts_hover_bg = "#f0a2ba"
                item_kwargs["background"] = rts_bg
                item_kwargs["foreground"] = "black"
                item_kwargs["activebackground"] = rts_hover_bg
                item_kwargs["activeforeground"] = "black"

            # Opciones de RE (primeras 6, opciones 7 a 12)
            elif btn_text == "RE":
                if idx < 6:
                    re_bg = "#AFFDF6"
                    re_hover_bg = "#94fcee"
                else:
                    re_bg = "#F7AFFD"
                    re_hover_bg = "#f394fc"
                item_kwargs["background"] = re_bg
                item_kwargs["foreground"] = "black"
                item_kwargs["activebackground"] = re_hover_bg
                item_kwargs["activeforeground"] = "black"

            self.menu.add_command(**item_kwargs)
            
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
            width=115, # Aumentado 15%
            font=("Arial", 14),
            dropdown_font=("Arial", 14)
        )
        self.pref_combo.grid(row=0, column=0, padx=(0, 2), sticky="w")
        self.pref_combo.set("INVEACDMX")  # Valor por defecto
        
        # 2. Separador Fijo: /OV/
        self.lbl_ov = ctk.CTkLabel(
            self,
            text="/",
            font=("Arial", 14, "bold")
        )
        self.lbl_ov.grid(row=0, column=1, padx=2, sticky="w")
        
        # 3. Selector de Materia
        self.materia_combo = ctk.CTkOptionMenu(
            self,
            values=["DU", "MP", "IO", "A", "AFO", "DUYUS", "MOBUR"],
            width=88, # Aumentado 15%
            font=("Arial", 14),
            dropdown_font=("Arial", 14)
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
            width=63, # Aumentado 15%
            font=("Arial", 14)
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
            width=88, # Aumentado 15%
            font=("Arial", 14),
            dropdown_font=("Arial", 14)
        )
        self.year_combo.grid(row=0, column=6, padx=(2, 0), sticky="w")
        self.year_combo.set("")  # En blanco por defecto

    def _on_num_write(self, *args):
        val = self.num_var.get()
        # Conservar solo dígitos
        clean_val = "".join([c for c in val if c.isdigit()])
        # No permitir el 0 como primer dígito
        clean_val = clean_val.lstrip('0')
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
        
        # Para IO no lleva OV, para las demás materias incluye OV
        if materia == "IO":
            return f"{prefix}/IO/{number}/{year}"
        else:
            return f"{prefix}/OV/{materia}/{number}/{year}"

    def limpiar(self):
        # El prefijo (INVEACDMX / INVEADF) se conserva seleccionado
        self.materia_combo.set("")
        self.num_var.set("")
        self.year_combo.set("")


class MainWindow(Tk):
    def __init__(self):
        super().__init__()
        
        # Habilitar Drag and Drop para toda la ventana
        self.drop_target_register(DND_FILES)

        self.title(NOMBRE_APP)

        # Configurar icono de la ventana si está disponible
        for posible_icono in ["icono.ico", "app.ico", "icon.ico"]:
            ruta_posible = os.path.join(os.path.dirname(os.path.dirname(__file__)), posible_icono)
            if os.path.exists(ruta_posible):
                try:
                    self.iconbitmap(ruta_posible)
                    break
                except Exception:
                    pass
            elif os.path.exists(posible_icono):
                try:
                    self.iconbitmap(posible_icono)
                    break
                except Exception:
                    pass

        # Configurar tamaño inicial al 80% exacto de la pantalla (ancho y alto), centrado
        screen_w = self.winfo_screenwidth()
        screen_h = self.winfo_screenheight()
        self.init_w = int(screen_w * 0.8)
        self.init_h = int(screen_h * 0.8)
        pos_x = int((screen_w - self.init_w) / 2)
        pos_y = int((screen_h - self.init_h) / 2)
        self.geometry(f"{self.init_w}x{self.init_h}+{pos_x}+{pos_y}")
        self.minsize(int(screen_w * 0.5), int(screen_h * 0.5))

        # Configurar grid con 'uniform' para forzar porcentajes estrictos independientemente del contenido
        # 3 columnas: Izquierda 25%, Centro 50%, Derecha 25%
        self.grid_columnconfigure(0, weight=25, uniform="grupos_paneles")
        self.grid_columnconfigure(1, weight=45, uniform="grupos_paneles")
        self.grid_columnconfigure(2, weight=30, uniform="grupos_paneles")
        self.grid_rowconfigure(0, weight=1)

        self._crear_panel_izquierdo()
        self._crear_panel_preview()
        self._crear_panel_archivos()
        self.clasificaciones = CLASIFICACIONES

    def _crear_panel_izquierdo(self):
        self.panel_izquierdo = ctk.CTkFrame(self)
        self.panel_izquierdo.grid(row=0, column=0, padx=(20, 10), pady=20, sticky="nsew")
        self.panel_izquierdo.grid_columnconfigure(0, weight=1)

        # Expediente
        ctk.CTkLabel(self.panel_izquierdo, text="Expediente:", font=("Arial", 14, "bold")).grid(row=0, column=0, padx=10, pady=(20, 5), sticky="w")
        self.entry_expediente = ExpedienteInputFrame(self.panel_izquierdo)
        self.entry_expediente.grid(row=1, column=0, padx=10, pady=(0, 15), sticky="w")

        # Fechas lado a lado (Ejecución y Resolución / Acuerdo)
        self.frame_fechas = ctk.CTkFrame(self.panel_izquierdo, fg_color="transparent")
        self.frame_fechas.grid(row=2, column=0, padx=10, pady=(5, 15), sticky="w")
        
        # 1. Ejecución (Izquierda)
        self.frame_fecha_ejec = ctk.CTkFrame(self.frame_fechas, fg_color="transparent")
        self.frame_fecha_ejec.pack(side="left", padx=(0, 20))
        
        ctk.CTkLabel(
            self.frame_fecha_ejec, 
            text="Ejecución:", 
            font=("Arial", 14, "bold")
        ).pack(anchor="w", pady=(0, 5))
        
        self.fecha_ejecucion = datetime.date.today()
        self.btn_fecha = ctk.CTkButton(
            self.frame_fecha_ejec,
            text=self.fecha_ejecucion.strftime("%Y-%m-%d"),
            width=140,
            font=("Arial", 14),
            command=self.abrir_calendario
        )
        self.btn_fecha.pack(anchor="w")

        # 2. Resolución / Acuerdo (Derecha, Naranja)
        self.frame_fecha_res = ctk.CTkFrame(self.frame_fechas, fg_color="transparent")
        self.frame_fecha_res.pack(side="left")
        
        ctk.CTkLabel(
            self.frame_fecha_res, 
            text="Resolución / Acuerdo:", 
            font=("Arial", 14, "bold")
        ).pack(anchor="w", pady=(0, 5))
        
        self.fecha_resolucion = None
        self.btn_fecha_resolucion = ctk.CTkButton(
            self.frame_fecha_res,
            text="YYYY-mm-dd",
            width=140,
            font=("Arial", 14),
            fg_color="#ea580c",
            hover_color="#c2410c",
            command=self.abrir_calendario_resolucion
        )
        self.btn_fecha_resolucion.pack(anchor="w")

        # Archivo activo seleccionado
        self.frame_seleccionado = ctk.CTkFrame(self.panel_izquierdo, fg_color="transparent")
        self.frame_seleccionado.grid(row=3, column=0, padx=10, pady=(0, 10), sticky="w")
        
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
            font=("Arial", 17, "bold")
        )
        self.lbl_archivo_activo.pack(side="left")

        # Clasificaciones (ScrollableFrame para alojar los botones)
        ctk.CTkLabel(self.panel_izquierdo, text="Renombrar:", font=("Arial", 14, "bold")).grid(row=4, column=0, padx=10, pady=(10, 5), sticky="w")
        
        self.scroll_frame = ctk.CTkScrollableFrame(self.panel_izquierdo)
        self.scroll_frame.grid(row=5, column=0, padx=10, pady=5, sticky="nsew")
        self.panel_izquierdo.grid_rowconfigure(5, weight=1)

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
                text_color=clasif.get("text_color", "white"),
                height=75
            )
            btn.grid(row=r, column=c, padx=4, pady=4, sticky="ew")
            self.botones_clasificacion.append(btn)

    def abrir_calendario(self):
        CTkCalendarPopup(self, self.fecha_ejecucion, self.actualizar_fecha, anchor_widget=self.btn_fecha, theme="blue")

    def actualizar_fecha(self, nueva_fecha):
        if nueva_fecha:
            self.fecha_ejecucion = nueva_fecha
            self.btn_fecha.configure(text=self.fecha_ejecucion.strftime("%Y-%m-%d"))

    def get_fecha_ejecucion(self) -> str:
        return self.fecha_ejecucion.strftime("%Y-%m-%d")

    def abrir_calendario_resolucion(self):
        init_date = self.fecha_resolucion if self.fecha_resolucion else datetime.date.today()
        CTkCalendarPopup(self, init_date, self.actualizar_fecha_resolucion, anchor_widget=self.btn_fecha_resolucion, theme="orange")

    def actualizar_fecha_resolucion(self, nueva_fecha):
        self.fecha_resolucion = nueva_fecha
        self.btn_fecha_resolucion.configure(text=self.fecha_resolucion.strftime("%Y-%m-%d") if self.fecha_resolucion else "YYYY-mm-dd")

    def limpiar_fecha_resolucion(self):
        self.fecha_resolucion = None
        self.btn_fecha_resolucion.configure(text="YYYY-mm-dd")

    def get_fecha_resolucion(self) -> str:
        if self.fecha_resolucion:
            return self.fecha_resolucion.strftime("%Y-%m-%d")
        return ""

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

        self.lbl_preview = ctk.CTkLabel(self.frame_preview_container, text="Sin documento", fg_color=("gray85", "gray20"), text_color=("gray40", "gray70"), corner_radius=10)
        self.lbl_preview.grid(row=0, column=0, sticky="nsew")
        
        # Atributos para redimensionamiento y zoom
        self.original_img = None
        self.resize_timer = None
        self.zoom_level = 1.0
        self.pan_x = 0
        self.pan_y = 0
        self.drag_start_x = 0
        self.drag_start_y = 0
        self.frame_preview_container.bind("<Configure>", self.on_resize)
        
        # Eventos de ratón para interactividad
        self.lbl_preview.bind("<Button-1>", self.on_preview_click)
        self.lbl_preview.bind("<B1-Motion>", self.on_preview_drag)
        self.lbl_preview.bind("<Button-3>", self.on_preview_right_click)

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
        self.panel_archivos.grid_rowconfigure(1, weight=1)
        self.panel_archivos.grid_columnconfigure(0, weight=1)
        
        # Contenedor superior centrado que agrupa botones, rutas y botón enviar
        frame_top = ctk.CTkFrame(self.panel_archivos, fg_color="transparent")
        frame_top.grid(row=0, column=0, pady=(15, 10))
        frame_top.grid_columnconfigure(0, weight=1)

        # 1. Botones de control
        frame_botones_top = ctk.CTkFrame(frame_top, fg_color="transparent")
        frame_botones_top.grid(row=0, column=0, pady=(0, 10))

        self.btn_origen = ctk.CTkButton(frame_botones_top, text="📂 Origen", width=90, height=33, font=("Arial", 14), fg_color=("#3a7ebf", "#1f538d"), hover_color=("#326da8", "#14375e"), text_color="white")
        self.btn_origen.pack(side="left", padx=4)

        self.btn_destino = ctk.CTkButton(frame_botones_top, text="📂 Destino", width=90, height=33, font=("Arial", 14), fg_color=("#3a7ebf", "#1f538d"), hover_color=("#326da8", "#14375e"), text_color="white")
        self.btn_destino.pack(side="left", padx=4)

        self.btn_refrescar = ctk.CTkButton(frame_botones_top, text="🔄 Recargar", width=90, height=33, font=("Arial", 14), fg_color=("#3a7ebf", "#1f538d"), hover_color=("#326da8", "#14375e"), text_color="white")
        self.btn_refrescar.pack(side="left", padx=4)

        # 2. Etiqueta con ruta de la carpeta origen
        self.frame_ruta_origen = ctk.CTkFrame(frame_top, fg_color="transparent")
        self.frame_ruta_origen.grid(row=1, column=0, pady=(0, 2))
        
        self.lbl_origen_titulo = ctk.CTkLabel(
            self.frame_ruta_origen, 
            text="Origen:", 
            font=("Arial", 15, "bold")
        )
        self.lbl_origen_titulo.pack(side="left", padx=(0, 5))
        
        self.lbl_ruta_carpeta = ctk.CTkLabel(
            self.frame_ruta_origen, 
            text="No seleccionado", 
            font=("Arial", 16), 
            text_color=("#0284c7", "#38bdf8")
        )
        self.lbl_ruta_carpeta.pack(side="left")

        # 3. Etiqueta con ruta de destino
        self.frame_ruta_destino = ctk.CTkFrame(frame_top, fg_color="transparent")
        self.frame_ruta_destino.grid(row=2, column=0, pady=(0, 10))
        
        self.lbl_destino_titulo = ctk.CTkLabel(
            self.frame_ruta_destino, 
            text="Destino:", 
            font=("Arial", 15, "bold")
        )
        self.lbl_destino_titulo.pack(side="left", padx=(0, 5))
        
        self.lbl_ruta_destino = ctk.CTkLabel(
            self.frame_ruta_destino, 
            text="Por defecto", 
            font=("Arial", 16), 
            text_color=("#0284c7", "#38bdf8")
        )
        self.lbl_ruta_destino.pack(side="left")

        # 4. Botón Enviar a Carpeta (se adapta al ancho del conjunto superior)
        self.btn_enviar = ctk.CTkButton(
            frame_top,
            text="📤 Enviar a Carpeta",
            font=("Arial", 18, "bold"),
            fg_color="#10b981", # Verde
            hover_color="#059669",
            height=42
        )
        self.btn_enviar.grid(row=3, column=0, pady=(0, 5), sticky="ew")

        # Lista de archivos con Scroll
        self.scroll_archivos = ctk.CTkScrollableFrame(self.panel_archivos)
        self.scroll_archivos.grid(row=1, column=0, padx=10, pady=5, sticky="nsew")
        self.scroll_archivos.grid_columnconfigure(0, weight=1)

        # Contador inferior
        self.lbl_total_archivos = ctk.CTkLabel(self.panel_archivos, text="0 archivos encontrados", text_color="gray", font=("Arial", 13))
        self.lbl_total_archivos.grid(row=2, column=0, padx=10, pady=(5, 10))


    def actualizar_seleccion(self, archivos_seleccionados):
        if not hasattr(self, 'widgets_lista'): return
        is_light = ctk.get_appearance_mode() == "Light"
        import re
        patron = r"^\d{4}-\d{2}-\d{2}[-].+\.pdf$"
        
        for item in self.widgets_lista:
            if not isinstance(item, tuple): continue
            if len(item) == 5:
                frame_item, lbl_icon, lbl_text, btn_delete, ruta_completa = item
            elif len(item) == 4:
                frame_item, lbl_icon, lbl_text, ruta_completa = item
                btn_delete = None
            else:
                continue

            nombre_archivo = os.path.basename(ruta_completa)
            es_activo = (ruta_completa in archivos_seleccionados)
            es_renombrado = bool(re.match(patron, nombre_archivo, re.IGNORECASE))
            
            if es_activo:
                fg_col = "#1f538d"
                txt_col = "white"
                hover_col = "#14375e"
            elif es_renombrado:
                fg_col = "#fed7aa" if is_light else "#9a3412"
                txt_col = "#0f172a" if is_light else "white"
                hover_col = "#fdba74" if is_light else "#7c2d12"
            else:
                fg_col = "#e2e8f0" if is_light else "gray22"
                txt_col = "#0f172a" if is_light else "white"
                hover_col = "#cbd5e1" if is_light else "gray32"
                
            frame_item.configure(fg_color=fg_col)
            frame_item.base_fg = fg_col
            frame_item.hover_bg = hover_col
            
            lbl_icon.configure(text_color=txt_col)
            lbl_text.configure(text_color=txt_col, font=("Arial", 14, "bold" if es_activo else "normal"))

    def mostrar_lista_archivos(self, lista_archivos, callback_click, archivos_seleccionados=None, callback_rename=None, callback_delete=None):
        if archivos_seleccionados is None:
            archivos_seleccionados = []
            
        if not hasattr(self, 'widgets_lista'):
            self.widgets_lista = []
            
        # Limpiar lista anterior
        for item in self.widgets_lista:
            try:
                if isinstance(item, tuple):
                    item[0].destroy()
                else:
                    item.destroy()
            except:
                pass
        self.widgets_lista.clear()

        self.lbl_total_archivos.configure(text=f"{len(lista_archivos)} archivo(s) PDF encontrado(s)")

        if not lista_archivos:
            lbl_vacio = ctk.CTkLabel(self.scroll_archivos, text="No hay archivos PDF en la carpeta", text_color="gray")
            lbl_vacio.pack(pady=30)
            return

        is_light = ctk.get_appearance_mode() == "Light"
        import re
        patron = r"^\d{4}-\d{2}-\d{2}[-].+\.pdf$"

        for index, ruta_completa in enumerate(lista_archivos):
            nombre_archivo = os.path.basename(ruta_completa)
            es_activo = (ruta_completa in archivos_seleccionados)
            es_renombrado = bool(re.match(patron, nombre_archivo, re.IGNORECASE))

            if es_activo:
                fg_col = "#1f538d"
                hover_col = "#14375e"
                txt_col = "white"
            elif es_renombrado:
                fg_col = "#fed7aa" if is_light else "#9a3412"
                hover_col = "#fdba74" if is_light else "#7c2d12"
                txt_col = "#0f172a" if is_light else "white"
            else:
                fg_col = "#e2e8f0" if is_light else "gray22"
                hover_col = "#cbd5e1" if is_light else "gray32"
                txt_col = "#0f172a" if is_light else "white"

            # Reemplazar el botón simple por un contenedor para controlar fuentes independientes
            frame_item = ctk.CTkFrame(self.scroll_archivos, fg_color=fg_col, corner_radius=6, height=38)
            frame_item.pack(fill="x", padx=3, pady=3)
            frame_item.pack_propagate(False)
            
            frame_item.base_fg = fg_col
            frame_item.hover_bg = hover_col

            # Icono grande
            lbl_icon = ctk.CTkLabel(frame_item, text=f"{index + 1}. 📄", font=("Arial", 22), text_color=txt_col)
            lbl_icon.pack(side="left", padx=(10, 5))

            # Botón de eliminar con icono SVG en la lateral extrema derecha
            if callback_delete:
                def on_delete_action(r=ruta_completa, n=nombre_archivo):
                    CTkConfirmDeleteDialog(self, n, lambda: callback_delete(r))

                ctk_icon = obtener_icono_delete_ctk(size=(24, 24))
                if ctk_icon:
                    btn_delete = ctk.CTkButton(
                        frame_item,
                        image=ctk_icon,
                        text="",
                        width=30,
                        height=30,
                        corner_radius=6,
                        fg_color="transparent",
                        hover_color="#fee2e2" if is_light else "#450a0a",
                        cursor="hand2"
                    )
                else:
                    btn_delete = ctk.CTkButton(
                        frame_item,
                        text="🗑",
                        font=("Arial", 16),
                        width=30,
                        height=30,
                        corner_radius=6,
                        fg_color="transparent",
                        text_color="#A32A10",
                        hover_color="#fee2e2" if is_light else "#450a0a",
                        cursor="hand2"
                    )

                btn_delete.pack(side="right", padx=(4, 8))
                btn_delete.configure(command=on_delete_action)
                ToolTip(btn_delete, "Eliminar archivo")
            else:
                btn_delete = None

            # Texto normal
            lbl_text = ctk.CTkLabel(frame_item, text=nombre_archivo, font=("Arial", 14, "bold" if es_activo else "normal"), text_color=txt_col, anchor="w")
            lbl_text.pack(side="left", fill="x", expand=True)
            self.widgets_lista.append((frame_item, lbl_icon, lbl_text, btn_delete, ruta_completa))

            # Efectos hover dinámicos unificados para todo el grupo (frame, icono y texto)
            def on_enter(e, f=frame_item):
                f.configure(fg_color=getattr(f, 'hover_bg', f.cget('fg_color')))
            
            def on_leave(e, f=frame_item):
                try:
                    x, y = f.winfo_pointerxy()
                    wx = f.winfo_rootx()
                    wy = f.winfo_rooty()
                    ww = f.winfo_width()
                    wh = f.winfo_height()
                    # Solo remover hover si el cursor realmente salió del área del frame
                    if not (wx <= x < wx + ww and wy <= y < wy + wh):
                        f.configure(fg_color=getattr(f, 'base_fg', f.cget('fg_color')))
                except Exception:
                    f.configure(fg_color=getattr(f, 'base_fg', f.cget('fg_color')))
                
            def on_click(e, r=ruta_completa):
                is_shift = bool(e.state & 0x0001)
                is_ctrl = bool(e.state & 0x0004)
                self.scroll_archivos.after(10, lambda: callback_click(r, is_ctrl=is_ctrl, is_shift=is_shift))
                
            def on_double_click(e, frame=frame_item, lbl=lbl_text, original_path=ruta_completa, name=nombre_archivo):
                if not callback_rename: return
                lbl.pack_forget()
                entry = ctk.CTkEntry(frame, font=("Arial", 14), text_color=lbl.cget("text_color"), fg_color="transparent")
                entry.pack(side="left", fill="x", expand=True)
                
                nombre_base = name[:-4] if name.lower().endswith(".pdf") else name
                entry.insert(0, nombre_base)
                entry.focus()
                
                def cancel_edit(ev=None):
                    try:
                        entry.pack_forget()
                        lbl.pack(side="left", fill="x", expand=True)
                        entry.destroy()
                    except:
                        pass
                
                def on_edit_finish(ev=None):
                    nuevo_texto = entry.get().strip()
                    if nuevo_texto and nuevo_texto != nombre_base:
                        callback_rename(original_path, nuevo_texto)
                    else:
                        cancel_edit()
                        
                entry.bind("<Return>", on_edit_finish)
                entry.bind("<Escape>", cancel_edit)
                entry.bind("<FocusOut>", cancel_edit)

            # Asignar hover y clic a todos los elementos del grupo para evitar parpadeos
            for widget in (frame_item, lbl_icon, lbl_text):
                widget.bind("<Enter>", on_enter)
                widget.bind("<Leave>", on_leave)
                widget.bind("<Button-1>", on_click)
            
            # Doble clic sobre el texto para renombrar
            lbl_text.bind("<Double-Button-1>", on_double_click)

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
            
            # Resetear zoom al cambiar de página
            self.zoom_level = 1.0
            self.pan_x = 0
            self.pan_y = 0
            
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
            
        # Calcular aspect ratio base para ajustar a la ventana
        img_w, img_h = self.original_img.size
        ratio_w = cw / img_w
        ratio_h = ch / img_h
        base_ratio = min(ratio_w, ratio_h)
        
        zoom = getattr(self, "zoom_level", 1.0)
        
        if zoom == 1.0:
            # Tamaño normal (Fit)
            new_w = int(img_w * base_ratio)
            new_h = int(img_h * base_ratio)
            
            if new_w > 0 and new_h > 0:
                ctk_img = ctk.CTkImage(light_image=self.original_img, dark_image=self.original_img, size=(new_w, new_h))
                self.lbl_preview.configure(image=ctk_img, text="")
        else:
            # Tamaño agrandado (Zoom)
            pan_x = getattr(self, "pan_x", 0)
            pan_y = getattr(self, "pan_y", 0)
            
            scale_factor = base_ratio * zoom
            
            # Coordenadas de la porción visible respecto a la imagen original de alta resolución
            left = pan_x / scale_factor
            top = pan_y / scale_factor
            right = (pan_x + cw) / scale_factor
            bottom = (pan_y + ch) / scale_factor
            
            # Asegurar límites dentro de la imagen original
            left = max(0, min(left, img_w))
            top = max(0, min(top, img_h))
            right = max(0, min(right, img_w))
            bottom = max(0, min(bottom, img_h))
            
            # Recortar solo lo que se va a mostrar
            cropped_img = self.original_img.crop((left, top, right, bottom))
            
            # El tamaño en pantalla de este recorte
            disp_w = int((right - left) * scale_factor)
            disp_h = int((bottom - top) * scale_factor)
            
            if disp_w > 0 and disp_h > 0:
                ctk_img = ctk.CTkImage(light_image=cropped_img, dark_image=cropped_img, size=(disp_w, disp_h))
                self.lbl_preview.configure(image=ctk_img, text="")

    def on_preview_click(self, event):
        if not self.original_img: return
        self.drag_start_x = event.x
        self.drag_start_y = event.y
        
        zoom_levels = [1.0, 1.5, 1.75, 2.0]
        current_zoom = getattr(self, "zoom_level", 1.0)
        
        try:
            current_idx = zoom_levels.index(current_zoom)
        except ValueError:
            current_idx = 0
            
        if current_idx < len(zoom_levels) - 1:
            old_zoom = current_zoom
            new_zoom = zoom_levels[current_idx + 1]
            self.zoom_level = new_zoom
            
            cw = self.frame_preview_container.winfo_width()
            ch = self.frame_preview_container.winfo_height()
            img_w, img_h = self.original_img.size
            base_ratio = min(cw / img_w, ch / img_h)
            full_scaled_w = int(img_w * base_ratio * self.zoom_level)
            full_scaled_h = int(img_h * base_ratio * self.zoom_level)
            
            if old_zoom == 1.0:
                # Calcular el offset que CTkLabel aplica para centrar la imagen ajustada
                offset_x = (cw - int(img_w * base_ratio)) / 2
                offset_y = (ch - int(img_h * base_ratio)) / 2
                
                # Posición del clic relativa a la imagen (en escala 1.0)
                img_x = event.x - offset_x
                img_y = event.y - offset_y
                
                # Nueva posición de ese punto en la imagen agrandada
                ratio = new_zoom / old_zoom
                new_img_x = img_x * ratio
                new_img_y = img_y * ratio
                
                # Ajustar pan para que el punto siga bajo el cursor
                self.pan_x = int(new_img_x - event.x)
                self.pan_y = int(new_img_y - event.y)
            else:
                # Mantener el punto actual bajo el cursor
                ratio = new_zoom / old_zoom
                self.pan_x = int((self.pan_x + event.x) * ratio - event.x)
                self.pan_y = int((self.pan_y + event.y) * ratio - event.y)
                
            # Clamp
            max_pan_x = max(0, full_scaled_w - cw)
            max_pan_y = max(0, full_scaled_h - ch)
            self.pan_x = max(0, min(self.pan_x, max_pan_x))
            self.pan_y = max(0, min(self.pan_y, max_pan_y))
                
            self.actualizar_imagen_preview()

    def on_preview_drag(self, event):
        if not self.original_img or getattr(self, "zoom_level", 1.0) == 1.0: return
        
        dx = event.x - self.drag_start_x
        dy = event.y - self.drag_start_y
        self.drag_start_x = event.x
        self.drag_start_y = event.event_y if hasattr(event, "event_y") else event.y
        
        self.pan_x -= dx
        self.pan_y -= dy
        
        # Clamp
        cw = self.frame_preview_container.winfo_width()
        ch = self.frame_preview_container.winfo_height()
        img_w, img_h = self.original_img.size
        base_ratio = min(cw / img_w, ch / img_h)
        full_scaled_w = int(img_w * base_ratio * self.zoom_level)
        full_scaled_h = int(img_h * base_ratio * self.zoom_level)
        
        max_pan_x = max(0, full_scaled_w - cw)
        max_pan_y = max(0, full_scaled_h - ch)
        
        self.pan_x = max(0, min(self.pan_x, max_pan_x))
        self.pan_y = max(0, min(self.pan_y, max_pan_y))
        
        self.actualizar_imagen_preview()

    def on_preview_right_click(self, event):
        zoom_levels = [1.0, 1.5, 1.75, 2.0]
        current_zoom = getattr(self, "zoom_level", 1.0)
        
        try:
            current_idx = zoom_levels.index(current_zoom)
        except ValueError:
            current_idx = 0
            
        if current_idx > 0:
            old_zoom = current_zoom
            new_zoom = zoom_levels[current_idx - 1]
            self.zoom_level = new_zoom
            
            if new_zoom == 1.0:
                self.pan_x = 0
                self.pan_y = 0
            else:
                cw = self.frame_preview_container.winfo_width()
                ch = self.frame_preview_container.winfo_height()
                img_w, img_h = self.original_img.size
                base_ratio = min(cw / img_w, ch / img_h)
                full_scaled_w = int(img_w * base_ratio * self.zoom_level)
                full_scaled_h = int(img_h * base_ratio * self.zoom_level)
                
                ratio = new_zoom / old_zoom
                self.pan_x = int((self.pan_x + event.x) * ratio - event.x)
                self.pan_y = int((self.pan_y + event.y) * ratio - event.y)
                
                max_pan_x = max(0, full_scaled_w - cw)
                max_pan_y = max(0, full_scaled_h - ch)
                self.pan_x = max(0, min(self.pan_x, max_pan_x))
                self.pan_y = max(0, min(self.pan_y, max_pan_y))
                
            self.actualizar_imagen_preview()

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
        self.zoom_level = 1.0
        self.pan_x = 0
        self.pan_y = 0
        self.lbl_preview.configure(image=None, text="Sin imagen")
        self.lbl_pagina.configure(text="Página 0 / 0")
        self.btn_prev.configure(state="disabled")
        self.btn_next.configure(state="disabled")
