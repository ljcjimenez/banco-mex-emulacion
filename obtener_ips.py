"""
NOMBRE: obtener_ips.py
RUTA: r'D:\banco-mex-emulacion\obtener_ips.py'
DESCRIPCIÓN: Script de monitoreo multicloud con ingreso interactivo de secretos.
             Extrae IPs de AWS, Azure y GCP de forma segura.
"""

import subprocess  # COMANDO: Permite ejecutar procesos del sistema (Pulumi CLI)
import json        # COMANDO: Formatea y lee datos en formato JSON para Python
import os          # COMANDO: Gestiona variables de entorno temporales
import getpass     # COMANDO: Captura la contraseña de forma oculta en la terminal

def get_pulumi_output(output_name, passphrase):
    """
    Intenta extraer el valor de salida de Pulumi usando la contraseña proveída.
    """
    # Creamos un entorno temporal para no exponer la contraseña permanentemente en el SO
    env_vars = os.environ.copy()
    env_vars["PULUMI_CONFIG_PASSPHRASE"] = passphrase

    try:
        # COMANDO: Ejecuta 'pulumi stack output [nombre] --json'
        # env=env_vars inyecta la contraseña solo para este comando
        result = subprocess.check_output(
            ["pulumi", "stack", "output", output_name, "--json"],
            env=env_vars,
            stderr=subprocess.STDOUT
        )
        return json.loads(result)
    except subprocess.CalledProcessError as e:
        # COMANDO: Captura errores de autenticación si la clave es errónea
        if b"incorrect passphrase" in e.output:
            return "ERROR: Contraseña de cifrado incorrecta."
        return "Pendiente (Verifica el despliegue con 'pulumi up')"

def mostrar_ips_bancarias():
    print("="*60)
    print("      SISTEMA DE GESTIÓN DE SECRETOS - BANCO DE MÉXICO (SPEI)     ")
    print("="*60)

    # COMANDO getpass: Solicita la clave sin mostrar los caracteres en pantalla
    pass_input = getpass.getpass("Ingrese la PULUMI_CONFIG_PASSPHRASE para desbloquear el Stack: ")

    print("\nConsultando el estado de los nodos multicloud...\n")

    # Invocación de las IPs exportadas en tus archivos de la carpeta modules/
    aws_ip   = get_pulumi_output("aws_ip", pass_input)
    azure_ip = get_pulumi_output("azure_ip", pass_input)
    gcp_ip   = get_pulumi_output("gcp_ip", pass_input)

    print(f" [AWS]   IP Nodo Firmado:   {aws_ip}")
    print(f" [Azure] IP Portal Gestión: {azure_ip}")
    print(f" [GCP]   IP Ledger Datos:   {gcp_ip}")
    
    print("\n" + "-"*60)
    print(" NOTA: Sesión de seguridad finalizada.")
    print("="*60)

if __name__ == "__main__":
    mostrar_ips_bancarias()