import subprocess
import platform

# Diccionario de nodos con las IPs públicas confirmadas en tu último despliegue exitoso
# Estas IPs son los puntos de terminación para la comunicación SPEI
nodos = {
    "AWS-Firmado": "100.24.64.132",
    "Azure-Portal": "20.151.107.156",
    "GCP-Ledger": "136.115.253.23"
}

def verificar_conexion(nombre, ip):
    # 'platform.system()' detecta si estás en Windows para usar '-n' en lugar de '-c' (Linux)
    # Este comando envía un solo paquete ICMP para una validación rápida
    parametro = '-n' if platform.system().lower() == 'windows' else '-c'
    comando = ['ping', parametro, '1', ip]
    
    print(f"Probando enlace hacia {nombre} en {ip}...")
    
    # 'subprocess.run' ejecuta el comando del sistema y captura el resultado
    resultado = subprocess.run(comando, capture_output=True, text=True)
    
    # El código de retorno 0 significa que el host respondió correctamente
    if resultado.returncode == 0:
        print(f"✅ ESTADO: Enlace Activo.")
        # Buscamos la línea que contiene el tiempo de respuesta (latencia)
        for linea in resultado.stdout.splitlines():
            if "tiempo=" in linea.lower() or "time=" in linea.lower():
                print(f"   {linea.strip()}")
    else:
        # Si falla, es probable que un Security Group o Firewall esté bloqueando el tráfico
        print(f"❌ ESTADO: Nodo Inalcanzable. Revisar reglas de seguridad en la consola.")
    print("-" * 60)

if __name__ == "__main__":
    print("=== MONITOR DE CONECTIVIDAD MULTICLOUD SPEI ===")
    for nombre, ip in nodos.items():
        verificar_conexion(nombre, ip)