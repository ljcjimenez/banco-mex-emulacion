""" RUTA: D:/banco-mex-emulacion/modules/gcp_infra.py """
import pulumi
from pulumi_gcp import compute, monitoring

def create_gcp_ledger_node():
    net = compute.Network("vpc-gcp-spei", auto_create_subnetworks=True)
    instance = compute.Instance("srv-gcp-ledger",
        machine_type="e2-micro",
        boot_disk={"initialize_params": {"image": "debian-cloud/debian-11"}},
        network_interfaces=[{"network": net.id, "access_configs": [{}]}]
    )

    # --- GOBERNANZA: CONTINUIDAD (Art. 32) ---
    # REQUISITO: Vigilancia proactiva. Se añade 'timeout' y 'combiner' obligatorios.
    uptime_check = monitoring.UptimeCheckConfig("check-ledger",
        display_name="Auditoria de Disponibilidad Ledger",
        period="60s", timeout="10s",
        tcp_check={"port": 5432},
        monitored_resource={
            "type": "gce_instance",
            "labels": {
                "instance_id": instance.instance_id,
                "project_id": instance.project,
                "zone": "us-central1-a"
            }
        })

    email_channel = monitoring.NotificationChannel("email-admin-luciano",
        display_name="Alerta SPEI - Luciano",
        type="email",
        labels={"email_address": "ljcluciano@gmail.com"})

    alert_policy = monitoring.AlertPolicy("alerta-ledger-spei",
        display_name="CRITICO: Ledger SPEI fuera de linea",
        combiner="OR", # Lógica de activación.
        conditions=[{
            "display_name": "Falla de Uptime Check > 120s",
            "condition_threshold": {
                "filter": uptime_check.uptime_check_id.apply(
                    lambda id: f'resource.type="gce_instance" AND metric.type="monitoring.googleapis.com/uptime_check/check_passed" AND metric.labels.check_id="{id.split("/")[-1]}"'),
                "duration": "120s",
                "comparison": "COMPARISON_LT",
                "threshold_value": 1,
                "aggregations": [{"alignment_period": "60s", "per_series_aligner": "ALIGN_FRACTION_TRUE"}]
            }
        }],
        notification_channels=[email_channel.name])
    
    return instance, uptime_check, alert_policy