import os
import shutil
from typing import List, Tuple
from config import RUTA_BASE

class FileManager:
    def __init__(self):
        pass

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

        ruta = os.path.join(RUTA_BASE, anio, siglas, numero)
        return ruta

    def clasificar_archivos(self, expediente: str, clasificacion: str, archivos: List[str]) -> Tuple[bool, str]:
        """
        Mueve y renombra los archivos a la carpeta del expediente.
        Retorna (éxito, mensaje)
        """
        valido, mensaje_error = self.validar_expediente_detalle(expediente)
        if not valido:
            return False, mensaje_error
            
        if not archivos:
            return False, "No hay archivos seleccionados para clasificar."

        try:
            ruta_destino = self.generar_ruta_expediente(expediente)
            
            # Crear directorios si no existen
            if not os.path.exists(ruta_destino):
                os.makedirs(ruta_destino)

            # Reemplazar espacios por guiones bajos para el nombre del archivo
            nombre_base = clasificacion.replace(" ", "_")

            archivos_movidos = 0
            for i, archivo_origen in enumerate(archivos, start=1):
                if not os.path.exists(archivo_origen):
                    continue
                
                _, extension = os.path.splitext(archivo_origen)
                
                if i == 1:
                    # El primer archivo se guarda con el nombre base directo sin número
                    nuevo_nombre = f"{nombre_base}{extension}"
                    ruta_final = os.path.join(ruta_destino, nuevo_nombre)
                    if os.path.exists(ruta_final):
                        # Si ya existe, buscar con sufijo _1, _2, etc.
                        contador = 1
                        while os.path.exists(ruta_final):
                            nuevo_nombre = f"{nombre_base}_{contador}{extension}"
                            ruta_final = os.path.join(ruta_destino, nuevo_nombre)
                            contador += 1
                else:
                    # Archivos adicionales se guardan con sufijo _1, _2, etc.
                    contador = i - 1
                    nuevo_nombre = f"{nombre_base}_{contador}{extension}"
                    ruta_final = os.path.join(ruta_destino, nuevo_nombre)
                    while os.path.exists(ruta_final):
                        contador += 1
                        nuevo_nombre = f"{nombre_base}_{contador}{extension}"
                        ruta_final = os.path.join(ruta_destino, nuevo_nombre)

                shutil.move(archivo_origen, ruta_final)
                archivos_movidos += 1
            
            return True, f"Se movieron exitosamente {archivos_movidos} archivo(s) a:\n{ruta_destino}"
            
        except Exception as e:
            return False, f"Error al procesar archivos: {str(e)}"
