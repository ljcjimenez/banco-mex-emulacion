import pulumi
from pulumi_azure_native import resources, network, compute

def create_azure_mgmt_node():
    # 1. Definición del Grupo de Recursos (Resource Group)
    # HISTÓRICO DE FALLOS DE CAPACIDAD (SkuNotAvailable):
    # - eastus/eastus2/westus2/southcentralus: Serie B agotada.
    # - brazilsouth: Serie D agotada.
    # CAMBIO ACTUAL: Migración a 'canadacentral' para asegurar disponibilidad de Serie D.
    rg = resources.ResourceGroup("rg-azure-spei", location="canadacentral") 

    # 2. Infraestructura de Red Virtual (VNet)
    vnet = network.VirtualNetwork("vnet-azure", 
        resource_group_name=rg.name, 
        location=rg.location,
        address_space={"address_prefixes": ["10.0.2.0/24"]})

    # 3. Creación de la Subred (Subnet)
    snet = network.Subnet("snet-azure", 
        resource_group_name=rg.name, 
        virtual_network_name=vnet.name, 
        address_prefix="10.0.2.0/27")

    # 4. Asignación de IP Pública (Standard SKU)
    pip = network.PublicIPAddress("pip-azure", 
        resource_group_name=rg.name, 
        location=rg.location, 
        public_ip_allocation_method="Static", 
        sku=network.PublicIPAddressSkuArgs(name="Standard"))

    # 5. Adaptador de Red (Network Interface)
    nic = network.NetworkInterface("nic-azure", 
        resource_group_name=rg.name, 
        location=rg.location,
        ip_configurations=[{
            "name": "ipconfig1", 
            "subnet": {"id": snet.id}, 
            "public_ip_address": {"id": pip.id}
        }])

    # 6. Despliegue de la Máquina Virtual (Standard_D2s_v3)
    # Serie D en Canadá tiene una de las tasas de disponibilidad más altas de Azure.
    vm = compute.VirtualMachine("vm-azure-portal",
        resource_group_name=rg.name,
        location=rg.location,
        hardware_profile={"vm_size": "Standard_D2s_v3"}, 
        network_profile={"network_interfaces": [{"id": nic.id}]},
        storage_profile={
            "image_reference": {
                "publisher": "Canonical", 
                "offer": "0001-com-ubuntu-server-jammy", 
                "sku": "22_04-lts", 
                "version": "latest"
            },
            "os_disk": {
                "create_option": "FromImage", 
                "managed_disk": {"storage_account_type": "Standard_LRS"}
            }
        },
        os_profile={
            "admin_username": "admin_spei", 
            "computer_name": "azure-portal", 
            "admin_password": "PasswordBancario123!" 
        })
    
    pulumi.export("azure_ip", pip.ip_address)
    return vm