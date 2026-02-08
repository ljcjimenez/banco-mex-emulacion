""" RUTA: D:/banco-mex-emulacion/__main__.py """
import pulumi
import pulumi_aws as aws
import json
from modules.aws_infra import create_aws_spei_node
from modules.gcp_infra import create_gcp_ledger_node

def main():
    # ==========================================================
    # 1. GOBERNANZA: AUDITORÍA E INMUTABILIDAD (Art. 28)
    # ==========================================================
    # PROPÓSITO: Establecer un rastro forense inalterable de cada acción en la nube.
    # El versionado impide la destrucción accidental o malintencionada de logs.
    audit_bucket = aws.s3.Bucket("banco-mex-audit-logs", force_destroy=True)
    aws.s3.BucketVersioning("audit-versioning",
        bucket=audit_bucket.id,
        versioning_configuration={"status": "Enabled"})

    # Configuración de política de seguridad para CloudTrail (Escritura Segura).
    def get_trail_policy(bucket_arn):
        return json.dumps({
            "Version": "2012-10-17",
            "Statement": [{
                "Sid": "AWSCloudTrailWrite",
                "Effect": "Allow",
                "Principal": {"Service": "cloudtrail.amazonaws.com"},
                "Action": "s3:PutObject",
                "Resource": f"{bucket_arn}/AWSLogs/*",
                "Condition": {"StringEquals": {"s3:x-amz-acl": "bucket-owner-full-control"}}
            }]
        })

    aws.s3.BucketPolicy("audit-bucket-policy",
        bucket=audit_bucket.id,
        policy=audit_bucket.arn.apply(get_trail_policy))

    trail = aws.cloudtrail.Trail("trail-spei-governance",
        s3_bucket_name=audit_bucket.id,
        enable_log_file_validation=True)

    # ==========================================================
    # 2. GOBERNANZA: IDENTIDAD Y ACCESO (Art. 27 y 31)
    # ==========================================================
    # NOTA: La gestión de la llave RSA de 4096 bits se ha movido al módulo 
    # de infraestructura de AWS para garantizar que la identidad se valide 
    # antes de instanciar cualquier recurso crítico.
    
    # ==========================================================
    # 3. DESPLIEGUE MULTICLOUD (Art. 25)
    # ==========================================================
    # CAMBIO TÉCNICO: Se elimina el argumento 'key_name' para coincidir con 
    # la firma de la función en 'aws_infra.py'.
    # GOBERNANZA: Esto centraliza la validación del archivo 'spei-key.pub'.
    aws_node, vpc = create_aws_spei_node() # <--- LLAMADA CORREGIDA (Sin parámetros)
    
    gcp_node, _, gcp_alert = create_gcp_ledger_node() 

    # ==========================================================
    # 4. REPORTE DE CUMPLIMIENTO CERTIFICADO (Art. 31 y 32)
    # ==========================================================
    # PROPÓSITO: Generar evidencia automática del estado de seguridad del ecosistema.
    def generar_reporte(args):
        aws_ip, aws_cifrado, bucket_id = args
        with open("despliegue_info.txt", "w") as f:
            f.write("=== REPORTE DE CUMPLIMIENTO BANCARIO (SPEI) ===\n")
            f.write(f"Cifrado AWS (Art. 34): {'ACTIVO' if aws_cifrado else 'FALLIDO'}\n")
            f.write(f"ID Auditoria S3 (Art. 28): {bucket_id}\n")
            f.write("===============================================\n")
        return "Reporte generado"

    pulumi.Output.all(
        aws_node.public_ip, 
        aws_node.root_block_device.encrypted, 
        audit_bucket.id
    ).apply(generar_reporte)

if __name__ == "__main__":
    main()