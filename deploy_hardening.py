import subprocess
import os

# Configuración de Infraestructura Multi-Cloud
# He incluido tu IP de AWS y los usuarios específicos que mencionaste
NODES = [
    {
        "name": "AWS-Production",
        "ip": "18.209.211.215",
        "user": "ec2-user",
        "key": "spei-key"
    },
    {
        "name": "Azure-Node",
        "ip": "REEMPLAZA_CON_IP_AZURE", # Pon la IP de Azure aquí
        "user": "ec2-user",
        "key": "id_rsa_azure"
    },
    {
        "name": "GCP-Node",
        "ip": "REEMPLAZA_CON_IP_GCP",   # Pon la IP de GCP aquí
        "user": "gcpuser",
        "key": "spei-key"
    }
]

FILENAME = "hardening_aws.sh"
SOURCE_PATH = f"D:\\banco-mex-emulacion\\{FILENAME}"

def run_cmd(description, command):
    print(f"  {description}...", end=" ", flush=True)
    try:
        subprocess.run(command, shell=True, check=True, capture_output=True)
        print("✅")
    except subprocess.CalledProcessError as e:
        print(f"❌\n    Error: {e.stderr.decode().strip()}")

def main():
    if not os.path.exists(SOURCE_PATH):
        print(f"Error: No se encuentra el archivo {FILENAME} en {os.path.dirname(SOURCE_PATH)}")
        return

    print(f"🚀 Iniciando despliegue de seguridad en infraestructura de emulación...")

    for node in NODES:
        if "REEMPLAZA" in node["ip"]:
            print(f"\n⚠️ Saltando {node['name']}: IP no configurada.")
            continue

        target = f"{node['user']}@{node['ip']}"
        print(f"\n📦 Nodo: {node['name']} ({target})")

        # 1. Copiar archivo mediante SCP
        scp_cmd = f"scp -i {node['key']} \"{SOURCE_PATH}\" {target}:/home/{node['user']}/"
        run_cmd("Copiando script de hardening", scp_cmd)

        # 2. Asignar permisos mediante SSH
        ssh_cmd = f"ssh -i {node['key']} {target} \"chmod +x /home/{node['user']}/{FILENAME}\""
        run_cmd("Asignando permisos de ejecución", ssh_cmd)

    print("\n✨ Proceso finalizado.")

if __name__ == "__main__":
    main()