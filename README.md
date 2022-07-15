# GreenChain Explorer
GreenChain Explorer Application

## Full deployment
The following steps will run a full explorer stack that harvests blocks from a new local network.

### Step 1: Clone repository: 
```bash
git clone git@github.com:decooio/greenchain-explorer.git
```
### Step 2: Change directory: 
```bash
cd greenchain-explorer
```
### Step 3: During the first run let MySQL initialize (wait for about a minute)
```bash
docker-compose -p greenchain -f docker-compose.greenchain.local.yml up -d mysql
```
### Step 4: Logon to MySQL, and update root plugin to 'mysql_native_password'
```bash
alter user root@'%' identified with mysql_native_password by 'root';

# note: to update root password:
alter user 'root'@'%' identified with mysql_native_password BY '...';
flush privileges;
```
### Step 5: Then build and start the other services
```bash
docker-compose -p greenchain -f docker-compose.greenchain.local.yml up --build
```

**Note**
- Need create an `.env` file based on `env.sample`
- To run other services in background, and tail logs:
  ```bash
  docker-compose -p greenchain -f docker-compose.greenchain.local.yml up -d --build
  docker-compose -p greenchain -f docker-compose.greenchain.local.yml logs --follow
  ```


## Add DB migration scripts
```bash
cd harvester
# install alembic if havn't
pip3 install alembic  
alembic revision -m "[message]"
```

## Add custom types for Substrate Node Template

* Modify `harvester/app/type_registry/substrate-node-template.json` to match the introduced types of the custom chain
* Truncate `runtime` and `runtime_*` tables on database
* Start harvester
* Check http://127.0.0.1:8080/node-template/runtime-type if all type are now correctly supported
* Monitor http://127.0.0.1:8080/node-template/harvester/admin if blocks are being processed and try to restart by pressing "Process blocks in harvester queue" if process is interupted.

## Cleanup Docker
Use the following commands with caution to cleanup your Docker environment.

### Prune images
```bash
docker system prune
```

### Prune images (force)
```bash
docker system prune -a
```

### Prune volumes
```bash
docker volume prune
```

## Cleanup MySQL only

### Option1: Drop and recreate 'polkascan' database

#### Step1: Start MySQL
```bash
docker-compose -p greenchain -f docker-compose.greenchain.local.yml up -d mysql
```

#### Step2: Logon, drop and re-create database
```sql
DROP DATABASE `polkascan`;
CREATE DATABASE `polkascan` DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT ENCRYPTION='N';
```

#### Step3: Run harvester-api to let alembic migrate database
```bash
docker-compose -p greenchain -f docker-compose.greenchain.local.yml up harvester-api
```

#### Step4: Restart MySQL and all services
```bash
docker-compose -p greenchain -f docker-compose.greenchain.local.yml down
docker-compose -p greenchain -f docker-compose.greenchain.local.yml up -d mysql
docker-compose -p greenchain -f docker-compose.greenchain.local.yml up --build
```

### Option2: Rebuild MySQL image

#### Step1: Remove MySQL container
```bash
docker container ls -a
docker container rm [mysql-container-id]
```

#### Step2: Remove MySQL image
```bash
docker image ls
docker image rm [mysql-image-id]
```

#### Step3: Remove MySQL data volume
```bash
docker volume rm greenchain_db-data
```

#### Step4: Rebuild and start MySQL 
```bash
docker-compose -p greenchain -f docker-compose.greenchain.local.yml up -d mysql
```
This will also create the default 'polkascan' database.

Logon to MySQL, and update root plugin to 'mysql_native_password'
```bash
alter user root@'%' identified with mysql_native_password by 'root';
```

#### Step5: Start harvester-api to let alembic migrate database
```bash
docker-compose -p greenchain -f docker-compose.greenchain.local.yml up harvester-api
```

#### Step6: Restart all services
```bash
docker-compose -p greenchain -f docker-compose.greenchain.local.yml down
docker-compose -p greenchain -f docker-compose.greenchain.local.yml up -d mysql
docker-compose -p greenchain -f docker-compose.greenchain.local.yml up --build
```


## Links to applications
* GreenChain Explorer GUI: http://127.0.0.1:8080
* Monitor harvester progress: http://127.0.0.1:8080/greenchain/harvester/admin
* Harvester Task Monitor: http://127.0.0.1:5555
* GreenChain JS Apps: http://127.0.0.1:8081

## Other networks

* GreenChain Local Node: Use `docker-compose.greenchain.local.yml`
* GreenChain Test Node: Use `docker-compose.greenchain-test.yml`
