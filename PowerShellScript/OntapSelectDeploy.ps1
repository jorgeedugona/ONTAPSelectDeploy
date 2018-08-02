
##########################################################
##########################################################
##########################################################
# Copyright (c) 2018 NetApp, Inc. All rights reserved.
# Specifications subject to change without notice.
#
# This sample code is provided AS IS, with no support or
# warranties of any kind, including but not limited to
# warranties of merchantability or fitness of any kind,
# expressed or implied.
# 
# Requirements:
# ONTAP Deploy 2.8 or newer.
# its been tested in Centos 7.5
# Datastores need to be presented to VMware before hand. 
# PowerShell Version = 6.0 Co
# 
#
# Author: Jorge E Gomez Navarrete gjorge@netapp.com
##########################################################
##########################################################
##########################################################


Function Get-JobStatus([string]$JobID,[System.Management.Automation.PSCredential]$Cred,[string]$Url,[string]$JobMessage,[Int]$Time){
$JobURL= $Url+'/jobs/'+$JobID
$StopWatch = New-Object -TypeName System.Diagnostics.Stopwatch
do{
$ResponseGET = Invoke-RestMethod -Method Get -Uri $JobURL -SkipCertificateCheck -Credential $Cred
if($Time -gt 1500){
$StopWatch.Start()
Write-Host "Time: " $StopWatch.Elapsed.Minutes "Min : " $StopWatch.Elapsed.Seconds " Sec $JobMessage Job is :" $ResponseGET.record.state
}
Start-Sleep -Milliseconds $Time
}while(($ResponseGET.record.state -eq "queued") -or ($ResponseGET.record.state -eq "running") )
Write-Host "$JobMessage status of Job is " $ResponseGET.record.state
$StopWatch.Stop()
}

Function Get-Object([string]$Object,[string]$Name,[string]$ClusterID,[string]$NodeID,[System.Management.Automation.PSCredential]$Cred,[string]$Url){
if($Object -eq "hosts"){
  # For Hosts
  $JobURL = $Url+'/hosts'+'?invalidate_cache=false'
  $Value = 'name' 
  }elseif($Object -eq "clusters"){
  # For Clusters
  $JobURL = $Url+'/clusters'
  $Value = 'name'
  }elseif($Object -eq "credentials"){
  # Credentials
  $JobURL = $Url+'/security/credentials'
  $Value = 'hostname'
  }elseif($Object -eq "nodes"){
  #Name is the ID of the cluster
  $JobURL = $Url+'/clusters/'+$ClusterID+'/nodes'
  }elseif($Object -eq "license"){
  $JobURL = $Url+'/licensing/licenses'
  }elseif($Object -eq "networknodeID"){
  $JobURL = $Url+'/clusters/'+$ClusterID+'/nodes/'+$NodeID+'/networks'
  }

$ResponseGET = Invoke-RestMethod -Method Get -Uri $JobURL -SkipCertificateCheck -Credential $Cred
if(($Object -eq "hosts")-or($Object -eq "clusters")-or($Object -eq "credentials")){
foreach($Record in $ResponseGET.records){ if($Record.$Value -eq $Name){
    $Record.Id #Returning ID of the object.
    $Record.Name #Returing the name also.
    }
}}elseif(($Object -eq "nodes") -or ($Object -eq "license") -or ($Object -eq "networknodeID")){
$ResponseGET.records #Returning all the ID objects of the nodes.
}
}

Function main(){

# Importing Variables 
. "$PSScriptRoot/OntapSelectVariables.ps1"

$secpasswd = ConvertTo-SecureString $PasswordDeploy -AsPlainText -Force
$Cred = New-Object System.Management.Automation.PSCredential ($UserDeploy, $secpasswd)

if($License.Length -eq 0){
$L = @($ESXhosts, $OSNode, $storagepool_name)
}else{
$L = @($ESXhosts, $OSNode, $License, $storagepool_name, $storagepool_capacity)
}

$Size = $OSNode.Length
foreach($Element in $L){
        if($Element.length -ne $Size){
        Write-Host "The following vectors should have the same length : ESXhost, OSNode, License, storagepool_name storagepool_capacity" -ForegroundColor Red
        return
        }
}

[System.Net.ServicePointManager]::ServerCertificateValidationCallback = { $True }
$ObjectCredentials = Get-Object -Object "credentials" -Name $VCenter -Cred $Cred -Url $Url
if(!$ObjectCredentials){
# Adding VCenter Credentials.
$JsonBody = @{
  hostname = $VCenter
  password = $VCenterPSS
  type = "vcenter"
  username = $VCenterUsername
} | ConvertTo-Json
$Response = Invoke-RestMethod -Method Post -Uri "$Url/security/credentials" -SkipCertificateCheck -Credential $Cred -Body $JsonBody `
                              -ContentType "application/json"
$JobMessage = "Adding VCenter Credentials "
Get-JobStatus -JobID $Response.job.id -Cred $Cred -Url $Url -JobMessage $JobMessage -Time 1000
}else{
Write-Host "VCenter Credentials for $VCenter already present..."
}
# Adding hosts  VCenter = 10.67.12.20 Host = 10.67.12.65
 foreach($ESX in $ESXhosts){
 $ObjectHosts = Get-Object -Object hosts -Name $ESX -Cred $Cred -Url $Url
 if(!$ObjectHosts){
    $JsonBody = @{   
        hosts = @(
                @{
                credential = @{password = ""
                               username = ""}
                hypervisor_type = 'ESX'
                management_server = $VCenter
                name = $ESX
                }
        ) 
} | ConvertTo-Json -Depth 4
$Response = Invoke-RestMethod -Method Post -Uri "$Url/hosts" -SkipCertificateCheck -Credential $Cred -Body $JsonBody `
                              -ContentType "application/json"
$JobMessage = "Adding ESXi Server $ESX "
Get-JobStatus -JobID $Response.job.id -Cred $Cred -Url $Url -JobMessage $JobMessage -Time 1000
 }else{
 Write-Host "Host $ESX is already present..."
 }
}

#Checking if Cluster Exists
$ObjectCluster = Get-Object -Object "clusters" -Name $new_cluster_name -Cred $Cred -Url $Url
if(!$ObjectCluster){
$JsonBody = @{
             name = $new_cluster_name
             ontap_image_version = $ontap_version
             ip = $new_cluster_ip
             gateway = $new_cluster_gateway
             netmask = $new_cluster_netmask
             ntp_servers = $ntp_servers
             dns_info = @{  
                         dns_ips = $dns_ips
                         domains = @($domain_names)
                         }
             } | ConvertTo-Json -Depth 4
$number_node_count = $OSNode.Length
$node_count = [string]$number_node_count

$ClusterUrl = $Url+'/clusters?node_count='+$node_count
Write-Host "Creating Ontap Select Cluster $new_cluster_name "
$Response = Invoke-RestMethod -Method Post -Uri $ClusterUrl -SkipCertificateCheck -Credential $Cred `
                              -Body $JsonBody -ContentType "application/json"
# When succesfull, the Response variable is null for the above REST API - I dont know why... 
}else{
Write-Host "Cluster $new_cluster_name is already present...."
Exit
}

$ObjectCluster = Get-Object -Object "clusters" -Name $new_cluster_name -Cred $Cred -Url $Url
$ObjectNodes = Get-Object -Object "nodes" -ClusterID $ObjectCluster[0] -Cred $Cred -Url $Url

# This Section is for EVAL only deployments as $License length is 0
if($License.Length -eq 0){
$storagepool_capacity = @(2199023255552,2199023255552,2199023255552,2199023255552,2199023255552,2199023255552,2199023255552,2199023255552)
$ObjectLicense = Get-Object -Object "license" -ClusterID $ObjectCluster[0] -Cred $Cred -Url $Url
$License = New-Object System.Collections.ArrayList -InformationAction Ignore -WarningAction Ignore
foreach($L in $ObjectLicense){
        $License.Add($L.id)
}
}

#Nodes Counter.
$H = 0
foreach($ESXhost in $ESXhosts){
$ObjectHosts = Get-Object -Object "hosts" -Name $ESXhost -Cred $Cred -Url $Url
$JsonBody = @{
             instance_type = $instance_type
             host = @{
                     id = $ObjectHosts[0]
                     }        
             ip = $OSNode[$H]
             passthrough_disks = $false
             license = @{
                        id = $License[$H]
                        }
             } | ConvertTo-Json -Depth 4
$PatchNodeUrl = $Url+'/clusters/'+$ObjectCluster[0]+'/nodes/'+$ObjectNodes[$H].id
$Response = Invoke-RestMethod -Method Patch -Uri $PatchNodeUrl -SkipCertificateCheck -Credential $Cred `
                              -Body $JsonBody -ContentType "application/json"
$H++ #Increasing the value of H to select another host. 
}

#Configuring Networking
$Networks = ("$mgmt_net","$data_net","$int_net")
$C = 0 #Nodes Counter 
foreach($Node in $ObjectNodes){
$ObjectNetworkNodesID = Get-Object -Object "networknodeID" -ClusterID $ObjectCluster[0] -NodeID $Node.id -Cred $Cred -Url $Url
$H =0 # Node counter
foreach($NetworkNodeID in $ObjectNetworkNodesID){

$JsonBody = @{
             name = $Networks[$H]
             } | ConvertTo-Json -Depth 4

$PatchNodeUrl = $Url+'/clusters/'+$ObjectCluster[0]+'/nodes/'+$Node.id+'/networks/'+$NetworkNodeID[0].id

Write-Host "Configuring $Networks[$H] in Node Name : "$Node.Name
$Response = Invoke-RestMethod -Method Patch -Uri $PatchNodeUrl -SkipCertificateCheck -Credential $Cred `
                              -Body $JsonBody -ContentType "application/json"
$H++
}

$JsonBody = @{
              pool_array = @(
                            @{ capacity = $storagepool_capacity[$C]
                              name = $storagepool_name[$C] 
                             }
                            )
             } | ConvertTo-Json -Depth 4

Write-Host "Attaching Storage Pool for Node : "$Node.Name
$PatchNodeUrl = $Url+'/clusters/'+$ObjectCluster[0]+'/nodes/'+$Node.id+'/storage/pools'

$Response = Invoke-RestMethod -Method Post -Uri $PatchNodeUrl -SkipCertificateCheck -Credential $Cred `
                              -Body $JsonBody -ContentType "application/json"
$C++
}
#Deploying Cluster
$PatchNodeUrl = $Url+'/clusters/'+$ObjectCluster[0]+'/deploy?inhibit_rollback=false'
$JsonBody = @{
              ontap_credential = @{
                password = $OSPassword    
              }            
             } | ConvertTo-Json -Depth 4

$Response = Invoke-RestMethod -Method Post -Uri $PatchNodeUrl -SkipCertificateCheck -Credential $Cred `
                              -Body $JsonBody -ContentType "application/json"
$JobMessage = "Deploying the Cluster $new_cluster_name "

Get-JobStatus -JobID $Response.job.id -Cred $Cred -Url $Url -JobMessage $JobMessage -Time 2000


}

main

