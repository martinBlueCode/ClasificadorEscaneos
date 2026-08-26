import os
import tkinter.messagebox as messagebox
from tkinter import filedialog
from models.file_manager import FileManager
import json
from config import RUTA_ORIGEN_DEFECTO, DICCIONARIO_SUBMENUS_MAESTRO, CONFIGURACION_SUBMENUS

SETTINGS_FILE = "settings.json"

def load_settings():
    if os.path.exists(SETTINGS_FILE):
        try:
            with open(SETTINGS_FILE, "r") as f:
                return json.load(f)
        except:
            return {}
    return {}

def save_settings(data):
    try:
        with open(SETTINGS_FILE, "w") as f:
            json.dump(data, f)
    except:
        pass

class AppController:
    def __init__(self, view):
        self.view = view
        self.model = FileManager()
        self.settings = load_settings()
        
        origen_cache = self.settings.get("ruta_origen", "")
        if origen_cache and os.path.exists(origen_cache):
            self.ruta_carpeta_origen = origen_cache
        else:
            self.ruta_carpeta_origen = ""
            
        destino_cache = self.settings.get("ruta_destino", "")
        if destino_cache and os.path.exists(destino_cache):
            self.ruta_carpeta_destino = destino_cache
            self.model.ruta_base = destino_cache
        else:
            self.ruta_carpeta_destino = self.model.ruta_base

        self.archivos_en_carpeta = []
        self.archivo_activo = None
        self.archivos_seleccionados = []

        # Conectar botones de la carpeta vinculada
        self.view.btn_refrescar.configure(command=self.refrescar_carpeta)
        self.view.btn_origen.configure(command=self.cambiar_carpeta)
        self.view.btn_destino.configure(command=self.cambiar_destino)
        self.view.btn_enviar.configure(command=self.enviar_archivo_destino)
        
        self.ctrl_pressed = False
        self.view.bind("<KeyPress-Control_L>", self.on_ctrl_press)
        self.view.bind("<KeyRelease-Control_L>", self.on_ctrl_release)
        self.view.bind("<KeyPress-Control_R>", self.on_ctrl_press)
        self.view.bind("<KeyRelease-Control_R>", self.on_ctrl_release)
        
        self.view.lbl_ruta_destino.configure(text=f"{self.ruta_carpeta_destino}" if self.ruta_carpeta_destino else "No seleccionado")
        
        # Conectar evento de Drag and Drop (opcional si arrastran archivos encima)
        self.view.dnd_bind('<<Drop>>', self.cargar_escaneos_dnd)
        
        # Conectar los botones de clasificación dinámicamente con el diccionario maestro
        for btn in self.view.botones_clasificacion:
            name = btn.cget("text")
            if name in CONFIGURACION_SUBMENUS:
                lista_claves = CONFIGURACION_SUBMENUS[name]
                options = {clave: DICCIONARIO_SUBMENUS_MAESTRO.get(clave, clave) for clave in lista_claves}
                from views.main_window import ClickMenu
                clasif_info = next((c for c in getattr(self.view, 'clasificaciones', []) if c["nombre"] == name), {})
                resalte = clasif_info.get("resalte_submenu")
                ClickMenu(
                    btn, 
                    options, 
                    lambda sub, pref=name, opt=options: self.clasificar_con_subopcion(pref, sub, opt),
                    active_bg=resalte,
                    active_fg=clasif_info.get("text_color") if resalte else None
                )
            else:
                btn.configure(command=lambda c=name: self.clasificar_escaneos(c))

        # Cargar archivos de la carpeta por defecto al iniciar
        self.refrescar_carpeta()

    def cambiar_carpeta(self):
        nueva_carpeta = filedialog.askdirectory(
            title="Seleccionar Carpeta de Escaneos",
            initialdir=self.ruta_carpeta_origen if os.path.exists(self.ruta_carpeta_origen) else None
        )
        if nueva_carpeta:
            self.ruta_carpeta_origen = nueva_carpeta
            self.settings["ruta_origen"] = nueva_carpeta
            save_settings(self.settings)
            
            self.archivo_activo = None
            self.refrescar_carpeta()

    def cambiar_destino(self):
        nueva_carpeta = filedialog.askdirectory(
            title="Seleccionar Carpeta de Destino",
            initialdir=self.ruta_carpeta_destino if os.path.exists(self.ruta_carpeta_destino) else None
        )
        if nueva_carpeta:
            self.ruta_carpeta_destino = nueva_carpeta
            self.model.ruta_base = nueva_carpeta
            self.settings["ruta_destino"] = nueva_carpeta
            save_settings(self.settings)
            self.view.lbl_ruta_destino.configure(text=f"{self.ruta_carpeta_destino}")

    def refrescar_carpeta(self):
        if self.ruta_carpeta_origen and os.path.exists(self.ruta_carpeta_origen):
            self.view.lbl_ruta_carpeta.configure(text=f"{self.ruta_carpeta_origen}")
        else:
            self.view.lbl_ruta_carpeta.configure(text="No seleccionado")
            
        self.archivos_en_carpeta = []

        if os.path.exists(self.ruta_carpeta_origen):
            try:
                todos_los_archivos = os.listdir(self.ruta_carpeta_origen)
                archivos_pdf = [
                    os.path.join(self.ruta_carpeta_origen, f)
                    for f in todos_los_archivos
                    if f.lower().endswith(".pdf") and os.path.isfile(os.path.join(self.ruta_carpeta_origen, f))
                ]
                # Ordenar alfabéticamente
                archivos_pdf.sort()
                self.archivos_en_carpeta = archivos_pdf
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo leer la carpeta:\n{str(e)}")

        # Si el archivo activo ya no existe o no hay ninguno, seleccionar el primero disponible
        if self.archivos_en_carpeta:
            if not self.archivo_activo or self.archivo_activo not in self.archivos_en_carpeta:
                self.seleccionar_archivo(self.archivos_en_carpeta[0])
            else:
                self.seleccionar_archivo(self.archivo_activo)
        else:
            self.limpiar_estado()
            self.view.mostrar_lista_archivos([], self.seleccionar_archivo, None)

    def on_ctrl_press(self, event):
        self.ctrl_pressed = True

    def on_ctrl_release(self, event):
        self.ctrl_pressed = False

    def seleccionar_archivo(self, ruta_archivo: str):
        if self.ctrl_pressed:
            if ruta_archivo in self.archivos_seleccionados:
                self.archivos_seleccionados.remove(ruta_archivo)
                if self.archivo_activo == ruta_archivo:
                    self.archivo_activo = self.archivos_seleccionados[-1] if self.archivos_seleccionados else None
            else:
                self.archivos_seleccionados.append(ruta_archivo)
                self.archivo_activo = ruta_archivo
        else:
            self.archivo_activo = ruta_archivo
            self.archivos_seleccionados = [ruta_archivo]
            
        if self.archivos_seleccionados:
            if len(self.archivos_seleccionados) == 1:
                nombre_base = os.path.basename(self.archivos_seleccionados[0])
                texto = f"{nombre_base}"
            else:
                texto = f"{len(self.archivos_seleccionados)} seleccionados"
            
            self.view.lbl_archivo_activo.configure(text=texto, text_color="#0284c7")
            if self.archivo_activo:
                self.view.mostrar_preview(self.archivo_activo)
        else:
            self.limpiar_estado()
            return
            
        self.view.mostrar_lista_archivos(self.archivos_en_carpeta, self.seleccionar_archivo, self.archivos_seleccionados)

    def cargar_escaneos_dnd(self, event):
        archivos = self.view.tk.splitlist(event.data)
        archivos_validos = [f for f in archivos if f.lower().endswith('.pdf') and os.path.exists(f)]
        
        if archivos_validos:
            self.seleccionar_archivo(archivos_validos[0])
        else:
            messagebox.showwarning("Advertencia", "Los archivos arrastrados no son documentos PDF válidos (.pdf).")

    def clasificar_con_subopcion(self, prefijo_boton: str, sub_opcion: str, siglas_map: dict = None):
        if siglas_map is None:
            siglas_map = {
                "Oficio Comision": "OC",
                "Citatorio": "CT",
                "Orden": "OR",
                "Carta de derechos": "CD",
                "Acta": "AC",
                "Acuerdo": "ACU",
                "Informe de Inejecucion": "II"
            }
        siglas = siglas_map.get(sub_opcion, sub_opcion)
        self.clasificar_escaneos(f"{prefijo_boton}_{siglas}")

    def clasificar_escaneos(self, clasificacion: str):
        # Solo renombra en sitio
        if not self.archivos_seleccionados:
            messagebox.showwarning("Atención", "Por favor selecciona un archivo de la lista para renombrar.")
            return
            
        if len(self.archivos_seleccionados) > 1:
            messagebox.showwarning("Atención", "Selecciona solo 1 archivo para renombrar.")
            return

        fecha = self.view.get_fecha_ejecucion()
        nombre_final = f"{fecha}_{clasificacion}"
        
        exito, mensaje, nueva_ruta = self.model.renombrar_archivo_en_sitio(nombre_final, self.archivo_activo)
        
        if exito:
            # Actualizar la lista en memoria
            if self.archivo_activo in self.archivos_en_carpeta:
                idx = self.archivos_en_carpeta.index(self.archivo_activo)
                self.archivos_en_carpeta[idx] = nueva_ruta
            
            # Mantener seleccionado
            self.seleccionar_archivo(nueva_ruta)
        else:
            messagebox.showerror("Error", mensaje)

    def enviar_archivo_destino(self):
        if not self.archivos_seleccionados:
            messagebox.showwarning("Atención", "Por favor selecciona al menos un archivo para enviar.")
            return
            
        import re
        patron = r"^\d{4}-\d{2}-\d{2}_.+\.pdf$"
        
        for ruta in self.archivos_seleccionados:
            nombre = os.path.basename(ruta)
            if not re.match(patron, nombre, re.IGNORECASE):
                if len(self.archivos_seleccionados) == 1:
                    messagebox.showwarning("Atención", "Este archivo no ha sido renombrado.")
                else:
                    messagebox.showwarning("Atención", "La selección contiene archivos sin renombrar.")
                return
            
        expediente = self.view.entry_expediente.get().strip()
        
        exito, reporte, stats = self.model.enviar_archivos_lote(expediente, self.archivos_seleccionados)
        if exito:
            if stats.get("errores"):
                errores_txt = "\n".join(stats["errores"])
                messagebox.showwarning("Enviados con advertencias", f"{reporte}\n\nAdvertencias:\n{errores_txt}")
            else:
                messagebox.showinfo("Reporte de Envío", reporte)
        else:
            messagebox.showerror("Error", reporte)
            
        self.refrescar_carpeta()

    def limpiar_estado(self):
        self.archivo_activo = None
        self.archivos_seleccionados = []
        self.view.lbl_archivo_activo.configure(text="Ninguno", text_color="gray")
        self.view.limpiar_preview()
        self.view.mostrar_lista_archivos(self.archivos_en_carpeta, self.seleccionar_archivo, None)
