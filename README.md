# ONTAPSelectDeploy
Deploy ONTAP Select using Python or PowerShell 

# Python Requirements:

•	ONTAP Deploy 2.8 or newer.  
•	It has been tested with Python 3.7

# Notes: 
• "ONTAPSelectvariables.py" is used to store all varibles needed for the deployment.  
• To use eval licenses, the vector named "License" needs to be emtpy , **Licence=[]**.   
• The following vectors must be same size : 
  "OSNode", "ESXhost", "storagepool_name", "storage_capacity" and "License". The size of these vectors will determine the number of nodes of the cluster (e.g 1, 2, 4, 8).  
• To execute just run "OntapSelectDeploy.py", variables from "ONTAPSelectvariables.py" will be imported. 
