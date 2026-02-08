import os

# --- DEFINICIÓN DE RUTAS PROFESIONALES (Windows) ---
PROJECT_ROOT = r'D:\banco-mex-emulacion'
SCRIPTS_DIR = os.path.join(PROJECT_ROOT, 'scripts')
BACKUP_DIR = r'D:\Backups_SPEI'

def setup_environment():
    # 1. Crear directorios si no existen
    for folder in [SCRIPTS_DIR, BACKUP_DIR]:
        if not os.path.exists(folder):
            os.makedirs(folder)
            print(f"Creada carpeta: {folder}")

    # 2. Contenido del script de respaldo definitivo
    backup_script_content = f"""# =================================================================
# SCRIPT DE RESPALDO DE INFRAESTRUCTURA - BANCO DE MÉXICO (EMULACIÓN)
# Autor: Luciano Jimenez - Solutions Project Leader
# =================================================================
import os
import tarfile
from datetime import datetime

SOURCE = r'{PROJECT_ROOT}'
DESTINATION = r'{BACKUP_DIR}'
EXCLUDE = {{'venv', '__pycache__', '.pulumi', 'scripts', '.git'}}

def run():
    ts = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"SPEI_Full_Backup_LucianoJimenez_{{ts}}.tar.gz"
    target = os.path.join(DESTINATION, filename)
    
    print(f"Iniciando respaldo en: {{target}}")
    
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
"""

    # 3. Escribir el script en la ruta indicada
    script_path = os.path.join(SCRIPTS_DIR, 'backup_spei.py')
    with open(script_path, 'w', encoding='utf-8') as f:
        f.write(backup_script_content)
    
    print(f"\n✅ ENTORNO LISTO, Luciano.")
    print(f"El script de respaldo se ha creado en: {script_path}")

if __name__ == '__main__':
    setup_environment()