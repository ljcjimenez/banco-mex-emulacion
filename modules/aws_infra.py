""" 
RUTA: D:/banco-mex-emulacion/modules/aws_infra.py 
PROYECTO: Emulación Ecosistema SPEI - Nodo de Firmado (AWS)
"""
import pulumi
import pulumi_aws as aws

def create_aws_spei_node():
    # ==========================================================
    # 1. GOBERNANZA: CONTROL DE ACCESO E IDENTIDAD (Art. 31)
    # ==========================================================
    # PROPÓSITO: Garantizar el acceso exclusivo mediante la llave RSA de 4096 bits.
    # COMANDO: Carga 'spei-key.pub' para inyectar la identidad del administrador.
    try:
        with open("spei-key.pub", "r") as key_file:
            public_key_content = key_file.read()
    except FileNotFoundError:
        raise Exception("Error: No se encontró spei-key.pub. Verifique la ruta del proyecto.")

    # Registro de la llave en AWS para cumplimiento normativo de identidad.
    key_pair = aws.ec2.KeyPair("spei-key-aws",
        public_key=public_key_content)

    # ==========================================================
    # 2. GOBERNANZA: AISLAMIENTO Y SEGMENTACIÓN DE RED (Art. 25)
    # ==========================================================
    # PROPÓSITO: Crear un entorno virtual aislado para el procesamiento de firmas.
    vpc = aws.ec2.Vpc("vpc-aws-spei", 
        cidr_block="10.0.2.0/24", 
        enable_dns_hostnames=True,
        tags={"Name": "vpc-spei-firmado"})

    igw = aws.ec2.InternetGateway("igw-aws", vpc_id=vpc.id)

    # CORRECCIÓN TÉCNICA (Resegmentación): Se cambia el CIDR a .128/26 para evitar
    # el error 'InvalidSubnet.Conflict' con la subred previa en proceso de borrado.
    # GOBERNANZA (Art. 32): Asegura la disponibilidad del hardware t3.medium en us-east-1a.
    public_subnet = aws.ec2.Subnet("subnet-aws-public-v3", # <--- NUEVA VERSIÓN
        vpc_id=vpc.id, 
        cidr_block="10.0.2.128/26", # <--- NUEVO SEGMENTO (Solución al conflicto)
        map_public_ip_on_launch=True,
        availability_zone="us-east-1a")

    # ==========================================================
    # 3. GOBERNANZA: PROTECCIÓN DE DATOS Y CIFRADO (Art. 34)
    # ==========================================================
    # PROPÓSITO: Cifrar el almacenamiento de certificados SPEI en reposo.
    # COMANDO: 'RunInstances' con volumen EBS cifrado.
    instance = aws.ec2.Instance("srv-aws-firmado",
        instance_type="t3.medium",
        ami="ami-0c101f26f147fa7fd", 
        subnet_id=public_subnet.id,
        key_name=key_pair.key_name,  # Vinculación obligatoria de identidad (Art. 31)
        root_block_device={
            "volume_size": 20,
            "encrypted": True,       # CIFRADO ACTIVO (Requisito Banxico)
            "delete_on_termination": False # Preservación de logs para auditoría
        },
        tags={
            "Name": "srv-aws-firmado", 
            "Proyecto": "SPEI-Emulacion",
            "Seguridad": "Hardened-Required"
        })
    
    # Exposición de la IP pública para el orquestador y acceso administrativo.
    pulumi.export('aws_public_ip', instance.public_ip)
    
    return instance, vpc