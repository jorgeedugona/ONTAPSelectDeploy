import requests
import warnings
import json
import time
import sys
import itertools
warnings.filterwarnings("ignore")
from datetime import datetime

def GetObject(Object,Name,ClusterID,NodeID,api_user_name,api_user_password,Url):

    if Object == 'hosts':
        JobURL = Url+'/hosts'+'?invalidate_cache=false'
        Value = 'name'
    elif Object == 'clusters':
        # For Clusters
        JobURL = Url+'/clusters'
        Value = 'name'
    elif Object == 'credentials':
        # Credentials
        JobURL = Url+'/security/credentials'
        Value = 'hostname'
    elif Object == 'nodes':
        #Name is the ID of the cluster
        JobURL = Url+'/clusters/'+ClusterID+'/nodes'
    elif Object == 'license':
        JobURL = Url+'/licensing/licenses'
    elif Object == 'networknodeID':
        JobURL = Url+'/clusters/'+ClusterID+'/nodes/'+NodeID+'/networks'
    
    with requests.Session() as s:
        ResponseGET = s.get(JobURL, auth=(api_user_name,api_user_password), verify=False)
        json_data = json.loads(ResponseGET.text)
        if (Object == 'hosts') or (Object == 'clusters') or (Object == 'credentials'):
            for record in json_data["records"]:
                if record[Value] == Name:
                    return record
        elif (Object == "nodes") or (Object == "license") or (Object == "networknodeID"):
            return json_data

def GetJobStatus(JobID,api_user_name,api_user_password,Url,JobMessage,Time):
    JobURL = Url+'/jobs/'+JobID
    # Wait for Time seconds
    start_time = datetime.now()
    while True:
        with requests.Session() as s:
            ResponseGET = s.get(JobURL, auth=(api_user_name,api_user_password), verify=False)
            json_data = json.loads(ResponseGET.text)
            Jobstate = json_data['record']['state']
            if Time > 2:
                time_elapsed = datetime.now()-start_time
                print(f'Time elapsed (hh:mm:ss.ms) {time_elapsed} Job is : {Jobstate} ')
                time.sleep(Time)
            if (Jobstate == 'failure' or (Jobstate == 'success')):
                break
    print(f'{JobMessage} status of Job is {Jobstate}')

def main():
    from ONTAPSelectvariables import api_user_name, api_user_password, Url, VCenter, OSPassword, \
                                 VCenterPSS, VCenterUsername, ESXhosts, OSNode, License, storagepool_name, \
                                 storagepool_capacity, new_cluster_name, ontap_version, new_cluster_gateway, \
                                 new_cluster_ip, new_cluster_netmask, ntp_servers, domain_names, dns_ips, \
                                 mgmt_net, data_net, int_net, instance_type
    
    if len(License) == 0:
        L = [ESXhosts, OSNode, storagepool_name, storagepool_capacity]
    else:
        L = [ESXhosts, OSNode, License, storagepool_name, storagepool_capacity]

    if not all([len(a)==len(b) for a,b in list(itertools.combinations(L,2))]):
        print(f' The following vectors should have the same length : ESXhost, OSNode, License, storagepool_name storagepool_capacity ')
        return
    
    # Get Credentials
    print('Checking if VCenter Credentials... ')
    ObjectCredentials = GetObject('credentials',VCenter,"","",api_user_name,api_user_password,Url)
    if not ObjectCredentials:
        jsonBody = {
            "hostname": VCenter,
            "password": VCenterPSS,
            "type": 'vcenter',
            "username": VCenterUsername
        }
        with requests.Session() as s:
            print('Adding VCenter Credentials..')
            ResponsePOST = s.post(Url+'/security/credentials', json=jsonBody, auth=(api_user_name,api_user_password), verify=False)
    else:
        print(f'VCenter Credentials for {VCenter} already present..')

    print('Checking ESXi hosts... ')
    for Host in ESXhosts:
        ObjectHosts = GetObject('hosts',Host,"","",api_user_name,api_user_password,Url)
        if not ObjectHosts:
            jsonBody = {
            "hosts": [
                {
                "credential": {
                    "password": "",
                    "username": ""
                },
                "hypervisor_type": 'ESX',
                "management_server": VCenter,
                "name": Host   
                }
            ]
            }
            with requests.Session() as s:
                JobMessage = 'Adding ESXi server'+ Host +'....'
                ResponsePOST = s.post(Url+'/hosts', json=jsonBody, auth=(api_user_name,api_user_password), verify=False)
                json_data = json.loads(ResponsePOST.text)
                JobID = json_data['job']['id']
                GetJobStatus(JobID,api_user_name,api_user_password,Url,JobMessage,1)
        else:
            print(f'Host {Host} is already present..')

    # Checking if Cluster Exists
    # Get the Clusters
    Clusters = GetObject('clusters',new_cluster_name,"","",api_user_name,api_user_password,Url)
    if not Clusters:
        jsonBody = {
            "name": new_cluster_name,
            "ontap_image_version": ontap_version,
            "ip": new_cluster_ip,
            "gateway": new_cluster_gateway,
            "netmask": new_cluster_netmask,
            "ntp_servers": ntp_servers,
            "dns_info": {
                "dns_ips": dns_ips,
                "domains": [
                    domain_names
                ]
            }
        }
        ClusterURL = Url +'/clusters?node_count='+ str(len(ESXhosts))
        with requests.Session() as s:
                JobMessage = ' Creating Ontap Select Cluster '+ new_cluster_name +'....'
                ResponsePOST = s.post(ClusterURL, json=jsonBody, auth=(api_user_name,api_user_password), verify=False)
                json_data = json.loads(ResponsePOST.text)
                # When succesfull, the Response variable is null for the above REST API - I dont know why...
    else:
        print(f'Host {Host} is already present..')

    # Get the Clusters ID of the New Cluster.
    ObjectClusters = GetObject('clusters',new_cluster_name,"","",api_user_name,api_user_password,Url)

    # Get Nodes IDs of the New Nodes.
    ObjectNodes = GetObject('nodes',"",ObjectClusters['id'],"",api_user_name,api_user_password,Url)
    NodeRecords = ObjectNodes['records']
    # When there are no License, then EVAL Capacity is selected by default.
    if len(License) == 0:
        storagepool_capacity = [2199023255552,2199023255552,2199023255552,2199023255552,2199023255552,2199023255552,2199023255552,2199023255552]
        License = []
        # Get the temp eval licenses.
        ObjectLicenses = GetObject('license',"","","",api_user_name,api_user_password,Url)
        LicenseRecords = ObjectLicenses['records']
        for Eval in LicenseRecords:
            License.append(Eval['id'])
    
    for Host, Node, LicenseID, OSNodeIP  in zip(ESXhosts, NodeRecords, License, OSNode):
        ObjectHosts = GetObject('hosts',Host,"","",api_user_name,api_user_password,Url)
        jsonBody = {
            "instance_type": instance_type,
            "ip": OSNodeIP,
            "passthrough_disks": False,
            "host": {
                "id": ObjectHosts['id']
                },
            "license": {
                "id": LicenseID
                }   
            }   
        PatchNodeUrl = Url + '/clusters/' + ObjectClusters['id'] + '/nodes/' + Node['id']
        with requests.Session() as s:
                JobMessage = ' Creating Ontap Select Cluster '+ new_cluster_name +'....'
                ResponsePATCH = s.patch(PatchNodeUrl, json=jsonBody, auth=(api_user_name,api_user_password), verify=False)
                json_data = json.loads(ResponsePATCH.text)

    #Configuring Networking
    Networks = [mgmt_net,data_net,int_net]
    for Node, storage_name, storage_capacity in zip(NodeRecords, storagepool_name, storagepool_capacity):
        NetworkID = GetObject('networknodeID',"",ObjectClusters['id'],Node['id'],api_user_name,api_user_password,Url)
        for NetworkIDObject, Network in zip(NetworkID['records'], Networks):
            jsonBody = {
                "name": Network
                }
            PatchNodeUrl = Url+'/clusters/'+ ObjectClusters['id'] + '/nodes/' + Node['id'] + '/networks/' + NetworkIDObject['id']
            with requests.Session() as s:
                NodeName = Node['name']
                print(f' Configuring { Network } in Node Name : { NodeName }')
                ResponsePATCH = s.patch(PatchNodeUrl, json=jsonBody, auth=(api_user_name,api_user_password), verify=False)
                json_data = json.loads(ResponsePATCH.text)
        
        jsonBody = {
                "pool_array": [{ 
                                "capacity": storage_capacity,
                                "name": storage_name 
                                }]
                }
        PostNodeUrl = Url + '/clusters/'+ ObjectClusters['id'] + '/nodes/' + Node['id'] + '/storage/pools'    
        with requests.Session() as s:
            print(f' Attaching Storage Pool { storage_name } to Node : { NodeName }')
            ResponsePATCH = s.post(PostNodeUrl, json=jsonBody, auth=(api_user_name,api_user_password), verify=False)
            json_data = json.loads(ResponsePATCH.text)

    #Deploying Cluster
    ClusterURL = Url + '/clusters/' + ObjectClusters['id']+'/deploy?inhibit_rollback=false'

    jsonBody = {
            "ontap_credential": {
                    "password": OSPassword    
                }            
            }
    with requests.Session() as s:
        JobMessage = ' Creating Ontap Select Cluster '+ new_cluster_name +'....'
        ResponsePOST = s.post(ClusterURL, json=jsonBody, auth=(api_user_name,api_user_password), verify=False)
        json_data = json.loads(ResponsePOST.text)
        JobID = json_data['job']['id']
        GetJobStatus(JobID,api_user_name,api_user_password,Url,JobMessage,4)

main()
