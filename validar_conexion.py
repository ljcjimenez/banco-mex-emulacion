import os
import subprocess

def obtener_ips_pulumi():
    """Obtiene las IPs públicas exportadas por Pulumi."""
    print("Obteniendo IPs desde Pulumi...")
    try:
        # Ejecutamos el comando de stack output para traer las IPs
        aws_ip = subprocess.check_output(["pulumi", "stack", "output", "aws_node_public_ip"]).decode().strip()
        azure_ip = subprocess.check_output(["pulumi", "stack", "output", "azure_portal_ip"]).decode().strip()
        gcp_ip = subprocess.check_output(["pulumi", "stack", "output", "gcp_ledger_ip"]).decode().strip()
        return {"AWS": aws_ip, "Azure": azure_ip, "GCP": gcp_ip}
    except Exception as e:
        print(f"Error: Asegúrate de que 'pulumi up' terminó correctamente. {e}")
        return None

def test_ping(servidores):
    """Realiza un ping a cada IP para validar conectividad básica."""
    print("\n--- Iniciando prueba de conectividad (ICMP) ---")
    for nombre, ip in servidores.items():
        print(f"Probando conexión con {nombre} ({ip})...")
        # -n 2 hace 2 intentos de ping
        respuesta = os.system(f"ping -n 2 {ip} > nul")
        
        if respuesta == 0:
            print(f"  [OK] {nombre} es alcanzable.")
        else:
            print(f"  [ERROR] {nombre} no responde. Revisa los Security Groups/Firewalls.")

if __name__ == "__main__":
    ips = obtener_ips_pulumi()
    if ips:
        test_ping(ips)