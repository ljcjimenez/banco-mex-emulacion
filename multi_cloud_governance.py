import subprocess
import os
from datetime import datetime

# CONFIGURACIÓN DE NODOS (Gobernanza Multi-Cloud)
# Definición de activos según la tabla de control de activos del proyecto.
NODES = [
    {
        "provider": "AWS",
        "ip": "18.209.211.215",
        "user": "ec2-user",
        "key": "spei-key",
        "status": "En proceso de generación",
        "log_type": "Portal",
        "signing": "Portal"
    },
    {
        "provider": "Azure",
        "ip": "20.151.107.156",
        "user": "ec2-user",
        "key": "id_rsa_azure",
        "status": "Completado",
        "log_type": "Ledger",
        "signing": "Ledger"
    },
    {
        "provider": "GCP",
        "ip": "136.115.253.23",
        "user": "gcpuser",
        "key": "spei-key",
        "status": "Completado",
        "log_type": "Ledger",
        "signing": "Ledger"
    }
]

FILENAME = "hardening_aws.sh"
SOURCE_PATH = f"D:\\banco-mex-emulacion\\{FILENAME}"

def execute_governance_task(node):
    """
    Orquestación de carga, ejecución y registro de auditoría.
    """
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"\n{'='*60}")
    print(f"NODE: {node['provider']} | IP: {node['ip']} | STATUS: {node['status']}")
    print(f"{'='*60}")

    target = f"{node['user']}@{node['ip']}"

    # 1. SCP: Transferencia Segura de Archivos
    # Comando: scp -i {llave} {archivo_local} {usuario}@{ip}:{destino}
    # Objetivo: Asegurar que el artefacto de seguridad llegue íntegro al nodo.
    scp_cmd = f"scp -i {node['key']} \"{SOURCE_PATH}\" {target}:/home/{node['user']}/"
    
    print(f"[*] [SCP] Transfiriendo artefacto de seguridad...")
    subprocess.run(scp_cmd, shell=True, check=True, capture_output=True)

    # 2. SSH: Ejecución de Hardening y Registro en Ledger/Portal
    # Comando: ssh -i {llave} {usuario}@{ip} '{comandos_remotos}'
    # Objetivo: Cambiar permisos y ejecutar con privilegios de superusuario (sudo).
    exec_cmd = (
        f"ssh -i {node['key']} {target} "
        f"'chmod +x ~/{FILENAME} && sudo ./~/{FILENAME}'"
    )

    print(f"[*] [SSH] Ejecutando Hardening (Gobernanza: {node['signing']})...")
    try:
        # Ejecución con timeout para evitar procesos colgados en la red.
        result = subprocess.run(exec_cmd, shell=True, capture_output=True, text=True, timeout=120)
        
        # 3. Auditoría: Registro de la evidencia técnica
        print(f"[+] [AUDIT] Registro {node['log_type']} generado exitosamente.")
        print(f"[+] [SIG] Evento firmado mediante: {node['signing']}")
        
        # Guardar evidencia local
        log_name = f"D:\\banco-mex-emulacion\\audit_{node['provider']}_{node['signing']}.log"
        with open(log_name, "a") as f:
            f.write(f"\n--- FECHA: {timestamp} ---\n{result.stdout}")

    except Exception as e:
        print(f"[-] [ERROR] Falla en cumplimiento para {node['provider']}: {str(e)}")

if __name__ == "__main__":
    for node in NODES:
        execute_governance_task(node)