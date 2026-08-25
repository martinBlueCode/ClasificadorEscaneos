import os
import tkinter.messagebox as messagebox
from tkinter import filedialog
from models.file_manager import FileManager
from config import RUTA_ORIGEN_DEFECTO

class AppController:
    def __init__(self, view):
        self.view = view
        self.model = FileManager()
        self.ruta_carpeta_origen = RUTA_ORIGEN_DEFECTO
        self.archivos_en_carpeta = []
        self.archivo_activo = None
        self.archivos_seleccionados = []

        # Conectar botones de la carpeta vinculada
        self.view.btn_refrescar.configure(command=self.refrescar_carpeta)
        self.view.btn_cambiar_carpeta.configure(command=self.cambiar_carpeta)
        
        # Conectar evento de Drag and Drop (opcional si arrastran archivos encima)
        self.view.dnd_bind('<<Drop>>', self.cargar_escaneos_dnd)
        
        # Conectar los botones de clasificación dinámicamente
        for btn in self.view.botones_clasificacion:
            name = btn.cget("text")
            if name == "VVE":
                # Al hacer clic directo en VVE
                btn.configure(command=lambda: self.clasificar_escaneos("VVE"))
                # Agregar menú de hover
                from views.main_window import HoverMenu
                options = {
                    "Oficio Comision": "OC",
                    "Citatorio": "CT",
                    "Orden": "OR",
                    "Carta de derechos": "CD",
                    "Acta": "AC",
                    "Informe de Inejecucion": "II"
                }
                HoverMenu(btn, options, self.clasificar_con_subopcion)
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
            self.archivo_activo = None
            self.refrescar_carpeta()

    def refrescar_carpeta(self):
        self.view.lbl_ruta_carpeta.configure(text=self.ruta_carpeta_origen)
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

    def seleccionar_archivo(self, ruta_archivo: str):
        self.archivo_activo = ruta_archivo
        self.archivos_seleccionados = [ruta_archivo]
        
        nombre_base = os.path.basename(ruta_archivo)
        self.view.lbl_archivo_activo.configure(
            text=f"Seleccionado: {nombre_base}", 
            text_color="#38bdf8"
        )
        self.view.mostrar_lista_archivos(self.archivos_en_carpeta, self.seleccionar_archivo, self.archivo_activo)
        self.view.mostrar_preview(ruta_archivo)

    def cargar_escaneos_dnd(self, event):
        archivos = self.view.tk.splitlist(event.data)
        archivos_validos = [f for f in archivos if f.lower().endswith('.pdf') and os.path.exists(f)]
        
        if archivos_validos:
            self.seleccionar_archivo(archivos_validos[0])
        else:
            messagebox.showwarning("Advertencia", "Los archivos arrastrados no son documentos PDF válidos (.pdf).")

    def clasificar_con_subopcion(self, sub_opcion: str):
        siglas_map = {
            "Oficio Comision": "OC",
            "Oficio Comisión": "OC",
            "Citatorio": "CT",
            "Orden": "OR",
            "Carta de derechos": "CD",
            "Acta": "AC",
            "Informe de inejecucion": "II",
            "Informe de Inejecución": "II",
            "Informe de Inejecucion": "II"
        }
        siglas = siglas_map.get(sub_opcion, sub_opcion)
        self.clasificar_escaneos(f"VVE_{siglas}")

    def clasificar_escaneos(self, clasificacion: str):
        expediente = self.view.entry_expediente.get().strip()
        
        # Validar si hay un archivo seleccionado
        if not self.archivos_seleccionados:
            messagebox.showwarning("Atención", "Por favor selecciona un archivo de la lista para clasificar.")
            return

        # Obtener la fecha de ejecución elegida por el usuario
        fecha = self.view.get_fecha_ejecucion()
        nombre_final = f"{fecha}_{clasificacion}"
        
        exito, mensaje = self.model.clasificar_archivos(expediente, nombre_final, self.archivos_seleccionados)
        
        if exito:
            messagebox.showinfo("Éxito", mensaje)
            # Refrescar la carpeta para que el archivo movido desaparezca y pase al siguiente
            self.archivo_activo = None
            self.refrescar_carpeta()
        else:
            messagebox.showerror("Error", mensaje)

    def limpiar_estado(self):
        self.archivo_activo = None
        self.archivos_seleccionados = []
        self.view.lbl_archivo_activo.configure(text="Ningún archivo seleccionado", text_color="gray")
        self.view.limpiar_preview()
        self.view.mostrar_lista_archivos(self.archivos_en_carpeta, self.seleccionar_archivo, None)
