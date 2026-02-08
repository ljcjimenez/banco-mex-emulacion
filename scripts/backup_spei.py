# =================================================================
# SCRIPT DE RESPALDO DE INFRAESTRUCTURA - BANCO DE MÉXICO (EMULACIÓN)
# Autor: Luciano Jimenez - Solutions Project Leader
# =================================================================
import os
import tarfile
from datetime import datetime

SOURCE = r'D:\banco-mex-emulacion'
DESTINATION = r'D:\Backups_SPEI'
EXCLUDE = {'venv', '__pycache__', '.pulumi', 'scripts', '.git'}

def run():
    ts = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"SPEI_Full_Backup_LucianoJimenez_{ts}.tar.gz"
    target = os.path.join(DESTINATION, filename)
    
    print(f"Iniciando respaldo en: {target}")
    
    with tarfile.open(target, "w:gz") as tar:
        for root, dirs, files in os.walk(SOURCE):
            dirs[:] = [d for d in dirs if d not in EXCLUDE]
            for file in files:
                full_path = os.path.join(root, file)
                # Conserva estructura relativa para portabilidad
                arcname = os.path.relpath(full_path, SOURCE)
                tar.add(full_path, arcname=arcname)
    
    print(f"✅ Respaldo exitoso. Estructura conservada para cumplimiento Banxico.")

if __name__ == '__main__':
    run()
