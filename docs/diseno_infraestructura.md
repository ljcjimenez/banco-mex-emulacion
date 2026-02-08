# Documentación de Infraestructura: Emulación SPEI Multicloud

## 1. Resumen del Proyecto
Este proyecto consiste en una emulación técnica del Sistema de Pagos Electrónicos Interbancarios (SPEI) utilizando una arquitectura multicloud. El objetivo es validar la interoperabilidad, seguridad y resiliencia entre los tres principales proveedores de nube (AWS, Azure, GCP) bajo un esquema de costos cero (Free Tier).

## 2. Diagrama Lógico de la Red
La topología sigue un modelo de **Microservicios Distribuidos** donde cada nube cumple una función crítica en el ciclo de vida de una transacción bancaria.



### Componentes por Proveedor:
* **Azure (Capa de Acceso y Gestión):** Punto de entrada para administradores y gestión de identidades (Entra ID).
* **AWS (Capa de Aplicación y Seguridad):** Procesamiento de la lógica SPEI y simulación de firmado digital de mensajes.
* **GCP (Capa de Persistencia):** Almacenamiento de saldos y log transaccional (Ledger).

---

## 3. Diseño de Redes y Segmentación (Diagrama Físico)

Para mantener el proyecto dentro del **Free Tier**, se ha diseñado una segmentación de red que evita el uso de Gateways pagados, utilizando reglas de Firewall (Security Groups) de alta restricción.

### Tabla de Direccionamiento IP (Simulado)
| Proveedor | Recurso | Región | Rango CIDR | Tipo de Instancia |
| :--- | :--- | :--- | :--- | :--- |
| **AWS** | VPC-SPEI-PROD | us-east-1 | 10.0.1.0/24 | t2.micro |
| **Azure** | VNet-SPEI-MGMT | East US | 10.0.2.0/24 | Standard B1s |
| **GCP** | VPC-SPEI-DATA | us-central1 | 10.0.3.0/24 | e2-micro |



---

## 4. Flujo de Comunicación y Seguridad
La comunicación entre nubes se realiza mediante **Public IP Whitelisting**:
1. El servidor en Azure solo permite tráfico SSH desde la IP administrativa del desarrollador.
2. El servidor en AWS solo acepta peticiones en el puerto 443 (HTTPS) provenientes de la IP pública de Azure.
3. El servidor en GCP solo acepta conexiones de base de datos provenientes de la IP pública de AWS.

### Mecanismos de Seguridad:
* **Cifrado:** TLS 1.3 para datos en tránsito.
* **Identidad:** Service Accounts con privilegios mínimos (Principle of Least Privilege).
* **IaC:** Todo el despliegue está versionado en Git y orquestado por Pulumi para asegurar la repetibilidad.

---

## 5. Limitaciones y Supuestos Técnicos
* **Costo:** Se limita el uso a instancias micro para no exceder la capa gratuita.
* **Conectividad:** Se asume conectividad vía Internet Pública con filtrado de IPs en lugar de Direct Connect/ExpressRoute por razones presupuestarias.
* **Alta Disponibilidad:** Simulada mediante scripts de recuperación en Pulumi, no mediante balanceadores de carga multi-zona (evitando costos de transferencia de datos).