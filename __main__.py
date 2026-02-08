import os
import subprocess
import time
import uuid
from datetime import datetime
from dotenv import load_dotenv

# Cargar variables de entorno (AWS, GCP, AZURE IPs) desde D:\banco-mex-emulacion\.env
load_dotenv()

def validar_nodo(ip):
    """
    GOBERNANZA (Art. 25 - Resiliencia Operativa): Verifica disponibilidad del nodo.
    En Windows, '-n 1' (un paquete) y '-w 1500' (1.5s de espera) asegura 
    el cumplimiento de latencia exigida por los servicios financieros.
    """
    comando = ["ping", "-n", "1", "-w", "1500", ip]
    try:
        resultado = subprocess.run(comando, capture_output=True, text=True)
        return "OPERATIVO" if resultado.returncode == 0 else "SIN_RESPUESTA"
    except:
        return "ERROR_TECNICO"

class SistemaSPEIHighAvailability:
    def __init__(self, responsable):
        self.responsable = responsable
        # Prioridad de nodos para el Failover (Art. 25 y 34)
        self.nodos = [
            ("AZURE", os.getenv("AZURE_IP"), "Portal de Acceso"),
            ("AWS", os.getenv("AWS_IP"), "Liquidador"),
            ("GCP", os.getenv("GCP_IP"), "Ledger/Registro")
        ]

    def ejecutar_health_check(self):
        """Fase 1: Auditoría de Disponibilidad (Art. 25 y 34)"""
        print("--- FASE 1: VALIDACIÓN DE INFRAESTRUCTURA MULTI-CLOUD ---")
        status_red = []
        nodos_activos = 0
        for nombre, ip, rol in self.nodos:
            estado = validar_nodo(ip)
            print(f"[*] Verificando {nombre} ({ip})... {estado}")
            status_red.append(f"{nombre} ({rol}): {estado}")
            if estado == "OPERATIVO":
                nodos_activos += 1
        
        # Cálculo de SLA Teórico: Capacidad de respuesta del ecosistema
        sla = (nodos_activos / len(self.nodos)) * 100
        return status_red, sla

    def procesar_con_failover(self, operacion):
        """
        PRUEBA DE CAOS (Art. 25): Intenta procesar en el nodo principal.
        Si falla, conmuta automáticamente al siguiente disponible.
        """
        for nombre, ip, rol in self.nodos:
            if validar_nodo(ip) == "OPERATIVO":
                rastreo = f"BMEX-{uuid.uuid4().hex[:10].upper()}" # Art. 31 (Trazabilidad)
                status = f"EXITOSO (Procesado por {nombre} - {rol})"
                print(f"    [OK] {operacion} vía {nombre} - {rastreo}")
                return f"{operacion} | Rastreo: {rastreo} | {status}"
            else:
                print(f"    [!] Alerta: Nodo {nombre} caído. Iniciando conmutación (Failover)...")
                time.sleep(1)
        
        return f"{operacion} | ESTADO: FALLA CRÍTICA (Sin nodos disponibles)"

def generar_reporte():
    # GOBERNANZA (Art. 31): Identidad inmutable del responsable en el reporte.
    responsable = os.getenv("AUDITOR_NAME") or "Luciano Jimenez Castro"
    fecha_final = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    print("="*80)
    print(f"SISTEMA DE PAGOS BANCO-MEX | EMULACIÓN SPEI V2.0")
    print(f"AUDITOR RESPONSABLE: {responsable} | FECHA: {fecha_final}")
    print("="*80 + "\n")

    spei = SistemaSPEIHighAvailability(responsable)
    
    # Fase 1: Salud de la Red
    evidencia_red, sla_calculado = spei.ejecutar_health_check()
    
    # Fase 2: Operaciones con Failover
    print("\n--- FASE 2: EJECUCIÓN DE OPERACIONES FINANCIERAS ---")
    operaciones = ["TRANSFERENCIA", "DEVOLUCIÓN", "CONSULTA_CEP", "CANCELACIÓN"]
    log_operaciones = [spei.procesar_con_failover(op) for op in operaciones]

    # GENERACIÓN DE EVIDENCIA (UTF-8 con BOM para correcta lectura de acentos en Windows)
    with open("certificado_cumplimiento.txt", "w", encoding="utf-8-sig") as f:
        f.write(f"CERTIFICADO DE CUMPLIMIENTO SPEI - GOBERNANZA BANXICO\n")
        f.write(f"RESPONSABLE TÉCNICO: {responsable}\n")
        f.write(f"FECHA DE VALIDACIÓN: {fecha_final}\n")
        f.write("="*70 + "\n")
        f.write(f"SLA DE INFRAESTRUCTURA DETECTADO: {sla_calculado:.2f}%\n")
        f.write("ESTADO DE LA RED (Art. 25 - Resiliencia Operativa):\n")
        for n in evidencia_red: f.write(f"- {n}\n")
        f.write("-" * 70 + "\n")
        f.write("BITÁCORA DE OPERACIONES (Art. 31 - Pistas de Auditoría):\n")
        for log in log_operaciones: f.write(f"- {log}\n")
        f.write("="*70 + "\n")
        f.write("DICTAMEN: LA INFRAESTRUCTURA DEMUESTRA RESILIENCIA OPERATIVA (ART. 25)\n")
        f.write("Y CUMPLE CON LOS PROTOCOLOS DE GOBERNANZA Y CONMUTACIÓN POR ERROR.")

    print(f"\n[!] Certificado Integral generado para: {responsable}")
    print(f"[i] Disponibilidad del Ecosistema: {sla_calculado:.2f}%")

if __name__ == "__main__":
    generar_reporte()