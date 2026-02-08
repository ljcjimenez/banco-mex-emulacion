# =================================================================
# PROTOCOLO DE RESPALDO DE EVIDENCIA - BANCO-MEX
# Autor: Luciano Jimenez Castro
# Gobernanza: Art. 31 (Preservación de Evidencia)
# =================================================================

import shutil
import os
import zipfile
from datetime import datetime

# Directorios y Metadatos
autor = "Luciano Jimenez Castro"
origen = os.path.dirname(os.path.abspath(__file__))
destino_raiz = r'D:\Backups_SPEI'
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
ruta_respaldo = os.path.join(destino_raiz, f"Respaldo_SPEI_{timestamp}")

archivos_criticos = ['__main__.py', '.env', 'certificado_cumplimiento.txt', 'backup.py']

def ejecutar_respaldo():
    print("="*60)
    print(f"PROTOCOLO DE RESPALDO | AUTOR: {autor}")
    print(f"FECHA: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*60)

    try:
        if not os.path.exists(ruta_respaldo):
            os.makedirs(ruta_respaldo)

        for archivo in archivos_criticos:
            ruta_origen = os.path.join(origen, archivo)
            if os.path.exists(ruta_origen):
                shutil.copy2(ruta_origen, ruta_respaldo)
                print(f"[OK] Respaldado: {archivo}")

        nombre_zip = f"{ruta_respaldo}.zip"
        with zipfile.ZipFile(nombre_zip, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for raiz, dirs, ficheros in os.walk(ruta_respaldo):
                for f in ficheros:
                    zipf.write(os.path.join(raiz, f), f)
        
        print("-" * 60)
        print(f"[!] RESPALDO FIRMADO POR {autor.upper()}")
        print(f"[*] Ubicación: {nombre_zip}")
        print("-" * 60)

    except Exception as e:
        print(f"[ERROR]: {e}")

if __name__ == "__main__":
    ejecutar_respaldo()