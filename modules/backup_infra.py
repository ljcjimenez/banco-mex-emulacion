import pulumi
import pulumi_aws as aws
import pulumi_gcp as gcp
from pulumi_azure_native import compute
from datetime import datetime, timedelta

def create_multicloud_snapshots(aws_node, azure_node, gcp_node):
    """
    Crea snapshots con sellado de tiempo y define una política de retención.
    """
    # 1. Preparación de marcas de tiempo
    ahora = datetime.now()
    timestamp = ahora.strftime("%Y%m%d-%H%M")
    # Definimos que el snapshot "expira" en 7 días para auditoría
    expiracion = (ahora + timedelta(days=7)).strftime("%Y-%m-%d")
    
    pulumi.log.info(f"--- Iniciando Ciclo de Vida de Backup [{timestamp}] ---")

    # --- AWS: AMI con Tag de Expiración ---
    # Creamos la imagen y le añadimos el metadato de cuándo debe borrarse
    aws_snapshot = aws.ec2.AmiFromInstance(f"snapshot-aws-{timestamp}",
        source_instance_id=aws_node.id,
        snapshot_without_reboot=True,
        tags={
            "Proyecto": "Banca-SPEI",
            "ExpiresOn": expiracion,
            "Tipo": "Auto-Backup"
        })

    # --- AZURE: Snapshot con Metadata de Retención ---
    # Usamos el Resource Group rg-azure-spei152472de en Canada Central
    azure_snapshot = compute.Snapshot(f"snapshot-azure-{timestamp}",
        resource_group_name="rg-azure-spei152472de", 
        location="canadacentral",
        creation_data=compute.CreationDataArgs(
            create_option="Copy",
            source_resource_id=azure_node.storage_profile.os_disk.managed_disk.id,
        ),
        tags={
            "RetentionPolicy": "7-Days",
            "CreationDate": timestamp
        },
        sku=compute.SnapshotSkuArgs(name="Standard_LRS"))

    # --- GCP: Snapshot con Labels de Control ---
    gcp_snapshot = gcp.compute.Snapshot(f"snapshot-gcp-{timestamp}",
        source_disk=gcp_node.name, 
        zone="us-central1-a",
        labels={
            "auto_delete": "true",
            "created_at": timestamp
        })

    pulumi.log.info(f"✔ Snapshots creados. Política de retención aplicada hasta: {expiracion}")

    return {
        "timestamp": timestamp,
        "aws_ami": aws_snapshot.id,
        "azure_name": azure_snapshot.name,
        "gcp_id": gcp_snapshot.id,
        "fecha_expiracion": expiracion
    }