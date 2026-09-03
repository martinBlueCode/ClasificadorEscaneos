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
        Admite formatos:
        - Materia IO (4 partes): INVEACDMX/IO/777/2026
        - Otras materias con OV (5 partes): INVEACDMX/OV/DU/777/2026
        """
        partes = [p.strip() for p in expediente.split('/') if p.strip()]
        if len(partes) == 4:
            prefix, materia, number, year = partes
            ov = ""
        elif len(partes) == 5:
            prefix, ov, materia, number, year = partes
        else:
            return False, "El formato del expediente no es válido."
            
        if not prefix or prefix not in ["INVEACDMX", "INVEADF"]:
            return False, "Falta seleccionar un prefijo válido para el expediente (INVEACDMX / INVEADF)."
        if len(partes) == 5 and ov != "OV":
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

    def obtener_componentes_expediente(self, expediente: str) -> Tuple[str, str, str, str, str, str]:
        """
        Extrae los componentes del expediente y genera el nombre de la carpeta:
        (prefijo, ov, materia, numero, anio, nombre_carpeta)
        - Para IO: (prefijo, "", "IO", numero, anio, "PREFIJO-IO-NUM-ANIO")
        - Para otros: (prefijo, "OV", materia, numero, anio, "PREFIJO-OV-MATERIA-NUM-ANIO")
        """
        partes = [p.strip() for p in expediente.split('/') if p.strip()]
        if len(partes) == 4:
            prefijo, materia, numero, anio = partes
            ov = ""
            nombre_carpeta = f"{prefijo}-{materia}-{numero}-{anio}"
            return prefijo, ov, materia, numero, anio, nombre_carpeta
        elif len(partes) == 5:
            prefijo, ov, materia, numero, anio = partes
            if materia == "IO":
                ov = ""
                nombre_carpeta = f"{prefijo}-IO-{numero}-{anio}"
            else:
                nombre_carpeta = f"{prefijo}-{ov}-{materia}-{numero}-{anio}"
            return prefijo, ov, materia, numero, anio, nombre_carpeta
        else:
            raise ValueError("Formato de expediente inválido.")

    def calcular_rango_expediente(self, numero: str) -> str:
        """
        Calcula el rango numérico de 100 en 100 para el número de expediente:
        1..100 -> 001-100
        101..200 -> 101-200
        507 -> 501-600
        777 -> 701-800
        901..1000 -> 901-1000
        1001..1100 -> 1001-1100
        """
        num = int(numero)
        inicio = ((num - 1) // 100) * 100 + 1
        fin = ((num - 1) // 100 + 1) * 100
        return f"{inicio:03d}-{fin}"

    def verificar_y_crear_carpetas(self, expediente: str) -> Tuple[str, List[str]]:
        """
        Verifica paso a paso la existencia de las carpetas:
        1. Año (ej. 2026)
        2. Materia (ej. INSPECCIONES OCULARES, MEDIOS PUBLICITARIOS, DU, etc.)
        3. Rango (ej. INVEACDMX-IO-701-800 para IO, INVEACDMX-OV-DU-701-800 para DU)
        4. Carpeta del Expediente (ej. INVEACDMX-IO-777-2026 para IO, INVEACDMX-OV-DU-777-2026 para DU)
        Crea las que falten y devuelve la ruta destino junto con la lista de carpetas creadas.
        """
        prefijo, ov, materia, numero, anio, nombre_carpeta = self.obtener_componentes_expediente(expediente)
        rango_num = self.calcular_rango_expediente(numero)

        # Mapeo de nombres de carpeta de materia y carpeta de rango
        if materia == "IO":
            carpeta_materia = "INSPECCIONES OCULARES"
            carpeta_rango = f"{prefijo}-IO-{rango_num}"
        elif materia == "MP":
            carpeta_materia = "MEDIOS PUBLICITARIOS"
            carpeta_rango = f"{prefijo}-{ov}-{materia}-{rango_num}"
        else:
            carpeta_materia = materia
            carpeta_rango = f"{prefijo}-{ov}-{materia}-{rango_num}"
        
        ruta_anio = os.path.join(self.ruta_base, anio)
        ruta_materia = os.path.join(ruta_anio, carpeta_materia)
        ruta_rango = os.path.join(ruta_materia, carpeta_rango)
        ruta_expediente = os.path.join(ruta_rango, nombre_carpeta)
        
        carpetas_creadas = []
        if not os.path.exists(ruta_anio):
            carpetas_creadas.append("LA CARPETA DEL AÑO")
        if not os.path.exists(ruta_materia):
            carpetas_creadas.append("LA CARPETA DE LA MATERIA")
        if not os.path.exists(ruta_rango):
            carpetas_creadas.append("LA CARPETA DE RANGO")
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
            elif num_carpetas == 4:
                lineas_reporte.append(f"4 CARPETAS CREADAS ({carpetas_creadas[0]}, {carpetas_creadas[1]}, {carpetas_creadas[2]} Y {carpetas_creadas[3]})")
            else:
                lineas_reporte.append(f"{num_carpetas} CARPETAS CREADAS ({', '.join(carpetas_creadas[:-1])} Y {carpetas_creadas[-1]})")

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

    def enviar_a_papelera(self, ruta_archivo: str) -> Tuple[bool, str]:
        """
        Envía un archivo a la papelera de reciclaje de Windows de forma segura.
        Retorna (Éxito, Mensaje)
        """
        if not os.path.exists(ruta_archivo):
            return False, "El archivo ya no existe en el sistema."

        try:
            # Si send2trash está instalado, usarlo como opción alternativa
            try:
                import send2trash
                send2trash.send2trash(os.path.abspath(ruta_archivo))
                return True, "Archivo enviado a la papelera."
            except ImportError:
                pass

            # API Nativa de Windows mediante SHFileOperationW
            if os.name == 'nt':
                import ctypes
                from ctypes import wintypes

                class SHFILEOPSTRUCTW(ctypes.Structure):
                    _fields_ = [
                        ("hwnd", wintypes.HWND),
                        ("wFunc", wintypes.UINT),
                        ("pFrom", wintypes.LPCWSTR),
                        ("pTo", wintypes.LPCWSTR),
                        ("fFlags", wintypes.WORD),
                        ("fAnyOperationsAborted", wintypes.BOOL),
                        ("hNameMappings", wintypes.LPVOID),
                        ("lpszProgressTitle", wintypes.LPCWSTR),
                    ]

                FO_DELETE = 0x0003
                FOF_ALLOWUNDO = 0x0040       # Habilita envío a la papelera de reciclaje
                FOF_NOCONFIRMATION = 0x0010  # Sin diálogo del sistema (confirmado previamente)
                FOF_SILENT = 0x0004          # Sin ventana de progreso del sistema

                # La ruta de origen debe tener doble terminador nulo
                abs_path = os.path.abspath(ruta_archivo)
                p_from = abs_path + '\0\0'

                fileop = SHFILEOPSTRUCTW()
                fileop.hwnd = None
                fileop.wFunc = FO_DELETE
                fileop.pFrom = p_from
                fileop.pTo = None
                fileop.fFlags = FOF_ALLOWUNDO | FOF_NOCONFIRMATION | FOF_SILENT
                fileop.fAnyOperationsAborted = False
                fileop.hNameMappings = None
                fileop.lpszProgressTitle = None

                res = ctypes.windll.shell32.SHFileOperationW(ctypes.byref(fileop))
                if res != 0 or fileop.fAnyOperationsAborted:
                    return False, f"No se pudo enviar el archivo a la papelera (Código de error: {res})."
                return True, "Archivo enviado a la papelera con éxito."
            else:
                os.remove(ruta_archivo)
                return True, "Archivo eliminado con éxito."
        except Exception as e:
            return False, f"Error al eliminar archivo: {str(e)}"


