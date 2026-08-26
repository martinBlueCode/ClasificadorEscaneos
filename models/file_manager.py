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
        ov = partes[1].strip()
        materia = partes[2].strip()
        number = partes[3].strip()
        year = partes[4].strip()
        
        if not prefix or prefix not in ["INVEACDMX", "INVEADF"]:
            return False, "Falta seleccionar un prefijo válido para el expediente (INVEACDMX / INVEADF)."
        if ov != "OV":
            return False, "El formato del expediente debe incluir /OV/."
        if not materia:
            return False, "Falta seleccionar la materia del expediente."
        if not number:
            return False, "Falta ingresar el número de expediente."
        if not year:
            return False, "Falta seleccionar el año del expediente."
            
        if not number.isdigit():
            return False, "El número de expediente debe contener únicamente dígitos."
        if number.startswith('0'):
            return False, "El número de expediente no puede iniciar con 0."
        if not (year.isdigit() and len(year) == 4):
            return False, "El año del expediente debe ser un año válido de 4 dígitos."
            
        return True, ""

    def validar_expediente(self, expediente: str) -> bool:
        """
        Valida que el expediente tenga la forma correcta.
        """
        valido, _ = self.validar_expediente_detalle(expediente)
        return valido

    def obtener_componentes_expediente(self, expediente: str) -> Tuple[str, str, str, str, str, str]:
        """
        Extrae los componentes del expediente y genera el nombre de la carpeta:
        (prefix, ov, materia, numero, anio, nombre_carpeta)
        """
        partes = expediente.split('/')
        if len(partes) != 5:
            raise ValueError("Formato de expediente inválido.")
        
        prefix = partes[0].strip()
        ov = partes[1].strip()
        materia = partes[2].strip()
        numero = partes[3].strip()
        anio = partes[4].strip()
        nombre_carpeta = f"{prefix}-{ov}-{materia}-{numero}-{anio}"
        return prefix, ov, materia, numero, anio, nombre_carpeta

    def generar_ruta_expediente(self, expediente: str) -> str:
        r"""
        Genera la ruta basada en el expediente:
        INVEACDMX/OV/DU/507/2026 -> [RUTA_BASE]\DU\2026\INVEACDMX-OV-DU-507-2026
        """
        _, _, materia, _, anio, nombre_carpeta = self.obtener_componentes_expediente(expediente)
        ruta = os.path.join(self.ruta_base, materia, anio, nombre_carpeta)
        return ruta

    def verificar_y_crear_carpetas(self, expediente: str) -> Tuple[str, List[str]]:
        """
        Verifica paso a paso la existencia de las carpetas:
        1. Materia
        2. Año
        3. Carpeta del Expediente
        Crea las que falten y devuelve la ruta destino junto con la lista de carpetas creadas.
        """
        _, _, materia, _, anio, nombre_carpeta = self.obtener_componentes_expediente(expediente)
        
        ruta_materia = os.path.join(self.ruta_base, materia)
        ruta_anio = os.path.join(ruta_materia, anio)
        ruta_expediente = os.path.join(ruta_anio, nombre_carpeta)
        
        carpetas_creadas = []
        if not os.path.exists(ruta_materia):
            carpetas_creadas.append("LA CARPETA DE LA MATERIA")
        if not os.path.exists(ruta_anio):
            carpetas_creadas.append("LA CARPETA DEL AÑO")
        if not os.path.exists(ruta_expediente):
            carpetas_creadas.append("LA CARPETA DEL EXPEDIENTE")
            
        os.makedirs(ruta_expediente, exist_ok=True)
        return ruta_expediente, carpetas_creadas

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

    def enviar_archivos_lote(self, expediente: str, lista_rutas: List[str]) -> Tuple[bool, str, dict]:
        """
        Mueve una lista de archivos a la carpeta del expediente en ruta_base.
        Retorna (Éxito, Mensaje_Reporte, Stats)
        """
        valido, mensaje_error = self.validar_expediente_detalle(expediente)
        if not valido:
            return False, mensaje_error, {"archivos_colocados": 0, "carpetas_creadas": [], "errores": [mensaje_error]}

        if not lista_rutas:
            return False, "No se seleccionaron archivos para enviar.", {"archivos_colocados": 0, "carpetas_creadas": [], "errores": []}

        try:
            ruta_destino, carpetas_creadas = self.verificar_y_crear_carpetas(expediente)
            
            archivos_colocados = 0
            errores = []

            for ruta_archivo in lista_rutas:
                if not os.path.exists(ruta_archivo):
                    errores.append(f"El archivo no existe: {os.path.basename(ruta_archivo)}")
                    continue

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
                archivos_colocados += 1

            # Generar reporte
            lineas_reporte = []
            if archivos_colocados == 1:
                lineas_reporte.append("1 ARCHIVO COLOCADO EN LA CARPETA DESTINO")
            else:
                lineas_reporte.append(f"{archivos_colocados} ARCHIVOS COLOCADOS EN LA CARPETA DESTINO")

            num_carpetas = len(carpetas_creadas)
            if num_carpetas == 0:
                lineas_reporte.append("0 CARPETAS CREADAS (LA CARPETA DEL EXPEDIENTE YA EXISTÍA)")
            elif num_carpetas == 1:
                lineas_reporte.append(f"1 CARPETA NUEVA CREADA ({carpetas_creadas[0]})")
            elif num_carpetas == 2:
                lineas_reporte.append(f"2 CARPETAS CREADAS ({carpetas_creadas[0]} Y {carpetas_creadas[1]})")
            elif num_carpetas == 3:
                lineas_reporte.append(f"3 CARPETAS CREADAS ({carpetas_creadas[0]}, {carpetas_creadas[1]} Y {carpetas_creadas[2]})")

            reporte_texto = "\n".join(lineas_reporte)
            
            stats = {
                "archivos_colocados": archivos_colocados,
                "carpetas_creadas": carpetas_creadas,
                "errores": errores,
                "ruta_destino": ruta_destino
            }

            if archivos_colocados > 0:
                return True, reporte_texto, stats
            else:
                return False, f"No se pudo colocar ningún archivo.\n" + "\n".join(errores), stats

        except Exception as e:
            return False, f"Error al procesar archivos: {str(e)}", {"archivos_colocados": 0, "carpetas_creadas": [], "errores": [str(e)]}

    def enviar_archivo(self, expediente: str, ruta_archivo: str) -> Tuple[bool, str]:
        """
        Compatibilidad para envío de un solo archivo.
        """
        exito, reporte, _ = self.enviar_archivos_lote(expediente, [ruta_archivo])
        return exito, reporte
