import os
import shutil
from typing import List, Tuple
from config import RUTA_BASE

class FileManager:
    def __init__(self):
        self.ruta_base = RUTA_BASE

    def validar_expediente_detalle(self, expediente: str) -> Tuple[bool, str]:
        """
        Valida el expediente parte por parte y devuelve si es válido junto con
        un mensaje específico en caso de que falte o sea incorrecto algún dato.
        """
        partes = expediente.split('/')
        if len(partes) != 5:
            return False, "El formato del expediente no es válido."
            
        prefix = partes[0].strip()
        materia = partes[2].strip()
        number = partes[3].strip()
        year = partes[4].strip()
        
        if not prefix:
            return False, "Falta seleccionar el prefijo del expediente (INVEACDMX / INVEADF)."
        if not materia:
            return False, "Falta seleccionar la materia del expediente."
        if not number:
            return False, "Falta ingresar el número de expediente."
        if not year:
            return False, "Falta seleccionar el año del expediente."
            
        if not number.isdigit():
            return False, "El número de expediente debe contener únicamente dígitos."
            
        return True, ""

    def validar_expediente(self, expediente: str) -> bool:
        """
        Valida que el expediente tenga la forma correcta.
        """
        valido, _ = self.validar_expediente_detalle(expediente)
        return valido

    def generar_ruta_expediente(self, expediente: str) -> str:
        """
        Genera la ruta basada en el expediente.
        INVEACDMX/OV/DU/1525/2026 -> [RUTA_BASE]\2026\DU\1525
        """
        partes = expediente.split('/')
        if len(partes) != 5:
            raise ValueError("Formato de expediente inválido.")
        
        siglas = partes[2]
        numero = partes[3]
        anio = partes[4]

        ruta = os.path.join(self.ruta_base, anio, siglas, numero)
        return ruta

    def renombrar_archivo_en_sitio(self, clasificacion: str, ruta_archivo: str) -> Tuple[bool, str, str]:
        """
        Renombra el archivo en su misma carpeta (origen) con la clasificación y fecha indicada.
        Retorna (Éxito, Mensaje, Nueva Ruta)
        """
        if not os.path.exists(ruta_archivo):
            return False, "El archivo origen no existe.", ""
            
        directorio = os.path.dirname(ruta_archivo)
        _, extension = os.path.splitext(ruta_archivo)
        nombre_base = clasificacion.replace(" ", "_")
        nuevo_nombre = f"{nombre_base}{extension}"
        ruta_final = os.path.join(directorio, nuevo_nombre)
        
        if ruta_archivo == ruta_final:
            return True, "El archivo ya tiene este nombre.", ruta_final
            
        if os.path.exists(ruta_final):
            return False, "Ya existe un archivo con ese nombre, envíalo a su carpeta", ""
                
        try:
            os.rename(ruta_archivo, ruta_final)
            return True, f"Renombrado a: {nuevo_nombre}", ruta_final
        except Exception as e:
            return False, f"Error al renombrar: {str(e)}", ""

    def enviar_archivo(self, expediente: str, ruta_archivo: str) -> Tuple[bool, str]:
        """
        Mueve el archivo seleccionado a la carpeta del expediente en ruta_base.
        Retorna (Éxito, mensaje)
        """
        valido, mensaje_error = self.validar_expediente_detalle(expediente)
        if not valido:
            return False, mensaje_error
            
        if not os.path.exists(ruta_archivo):
            return False, "El archivo no existe o no hay un archivo seleccionado válido."

        try:
            ruta_destino = self.generar_ruta_expediente(expediente)
            
            # Crear directorios si no existen
            if not os.path.exists(ruta_destino):
                os.makedirs(ruta_destino)

            nombre_archivo = os.path.basename(ruta_archivo)
            ruta_final = os.path.join(ruta_destino, nombre_archivo)
            
            if os.path.exists(ruta_final):
                # Evitar colisión
                nombre_base, extension = os.path.splitext(nombre_archivo)
                contador = 1
                while os.path.exists(ruta_final):
                    nuevo_nombre = f"{nombre_base}_{contador}{extension}"
                    ruta_final = os.path.join(ruta_destino, nuevo_nombre)
                    contador += 1

            shutil.move(ruta_archivo, ruta_final)
            return True, f"Archivo enviado exitosamente a:\n{ruta_destino}"
            
        except Exception as e:
            return False, f"Error al procesar archivo: {str(e)}"
