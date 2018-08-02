# ONTAPSelectDeploy
Deploy ONTAP Select using Python or PowerShell 

# Requirements for the Python script:

•	ONTAP Deploy 2.8 or newer.  
•	Python 3.7.  
• Request module.

# Requirements for the PowerShell script:

•	ONTAP Deploy 2.8 or newer.  
•	PowerShell 6.0.

# Notes: 
• "ONTAPSelectVariables" file is used to store all varibles needed for the deployment.  
• To use eval licenses, the vector named "License" needs to be emtpy , **Licence=[]**.   
• The following vectors must be same size : 
  "OSNode", "ESXhost", "storagepool_name", "storage_capacity" and "License". The size of these vectors will determine the number of nodes of the cluster (e.g 1, 2, 4, 8).  
• To execute just run "OntapSelectDeploy", variables from "ONTAPSelectvariables" will be imported.   
• Datastores need be presented to VMware before hand.



