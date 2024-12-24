# HaveBlue installation Notes
This is my dumping ground for notes about the various deployments of HaveBlue. This first section will be dedicated to the staging (test) deployment.

## Stage Deployment:
This data is volatile and may be deleted at any time. I will be putting everything into docker containers that we will store on Azure in a new container registry.

### Azure resourceGroup
Created via wb portal:
subscription ID 308e9c06-d90f-43ae-af52-557ede3534ce

### Postgres app services
https://docs.microsoft.com/en-us/azure/app-service/tutorial-python-postgresql-app?tabs=bash%2Cclone
az login
az extension add --name db-up
az postgres up --resource-group HaveBlue \
   --location westus2 --sku-name B_Gen5_1 \
   --server-name  HaveBlueDevDB \
   --database-name HaveBlueDevDB \
   --admin-user  HaveBlueDBAdmin\
   --admin-password HaveBlueP4ss! \
   --ssl-enforcement Enabled

### container registry
Created via web portal:
 - Login server: havebluecontainers.azurecr.io
 - Subscription ID: 308e9c06-d90f-43ae-af52-557ede3534ce

### django docker creation + upload to container registry
new Dockerfile created for this job

### File bucket
### react container creation + upload to registry
