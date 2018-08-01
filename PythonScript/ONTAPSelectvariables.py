# Variables to deploy ONTAP Select with Python.
# The following vectors must be same size :
# OSNode, ESXhost, storagepool_name, storage_capacity and License. 
api_user_name = "admin" #USER Account of Deploy.
api_user_password = "password123" # Password of the user account of Deploy.
Url = "https://192.168.0.10/api/v3" # IP address of the Deploy VM
VCenter = "192.168.0.100" # VCenter IP Address.
VCenterUsername = "Administrator@vsphere.local" # VMware Account.
VCenterPSS = "password123" # Password of the VMware Account.
OSPassword = "password123" # Password of the ONTAP Select instance.
ESXhosts = ["ESXi1","ESXi2","ESXi3","ESXi4"] # Hostnames of the ESXi servers.
OSNode = ["192.168.0.160","192.168.0.161","192.168.0.162","192.168.0.163"] # IP Addresses of ONTAP Nodes.
#License = ["320000001","320000002","320000003","320000004"] # Array of Licenses, If this is empty - EVAL license will be used. 
License = [] # Needed when EVAL license are used. 
storagepool_name = ["Infra_OTS_A","Infra_OTS_B","Infra_OTS_A","Infra_OTS_B"]  # Name of storage pools in VMware.
storagepool_capacity = [2528876743940,2528876743940,2528876743940,2528876743940]  # Sizes in (Bytes) of the storage pools, this will be ignored if Eval license are used
new_cluster_name = "AnsibleONTAPSelect"
ontap_version = "9.4" # Version of ONTAP
new_cluster_gateway = "192.168.0.1" # Default Gateway 
new_cluster_ip = "192.168.0.78" # management IP Address of the new ONTAP Select Cluster. 
new_cluster_netmask = "255.255.255.0" # Subnet of the management network
ntp_servers = ["192.168.0.25","192.168.0.45"]
domain_names = "example.co.uk" # Domain Name 
dns_ips = ["192.168.0.25","192.168.0.45"] # DNS ip addresses
mgmt_net= "magement_network" # Name of the Management Network
data_net= "data_network" # Name of the Data Network
int_net=  "internal_network" # Name of the Internal Network
instance_type = "small" # Type of instances (e.g. small or medium)