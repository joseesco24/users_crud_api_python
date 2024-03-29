# Users Crud Api Python

A really simple CRUD GraphQL API based on Docker and Python.

**Note:** In develop mode and running locally the docs are available at this [**url**](http://localhost:10048/graphql)

<br/>

## Project Commands

**Note:** Before running any of these commands be sure that your **CWD** is **users_crud_api_python** directory.

### Clean Python Cache Using Grep

```bash
find . | grep -E "(/__pycache__$|\.pyc$|\.pyo$)" | xargs rm -rf
```

### Install Python Dependencies

```bash
poetry install
```

### Change Poetry Venv Version To 3.11

```bash
poetry env use 3.11
```

### Export The Dev And App Dependencies With Poetry

```bash
poetry export --without-hashes --format=requirements.txt > requirements.app.txt
```

```bash
poetry export --without-hashes --only dev --format=requirements.txt > requirements.dev.txt
```

### Update The Depedencies With Poetry

**Note:** Before running this command you need to install the dev dependencies.

```bash
poetry update
```

### Check The Depedencies With Poetry

**Note:** Before running this command you need to install the dev dependencies.

```bash
poetry show
```

```bash
poetry show -l
```

### Format The Code Using Black

**Note:** Before running this command you need to install the dev dependencies.

```bash
black ./src --line-length=150
```

### Lint The Code Using Flake8

**Note:** Before running this command you need to install the dev dependencies.

```bash
flake8 ./src --max-line-length=150
```

### Check Static Types Using Mypy

**Note:** Before running this command you need to install the dev dependencies.

```bash
mypy --explicit-package-bases ./src
```

### Run On Development Mode

```bash
ENVIRONMENT_MODE=development python src/main.py
```

### Run On Testing Mode

```bash
ENVIRONMENT_MODE=testing python src/main.py
```

### Run On Production Mode

```bash
ENVIRONMENT_MODE=production python src/main.py
```

<br/>

## Docker Project Commands

**Note:** Before running any of these commands be sure that your **CWD** is **users_crud_api_python** directory.

### Docker App Building Without Cache

```bash
docker build --no-cache --tag ghcr.io/joseesco24/users_crud_api_python:latest .
```

### Docker App Building With Cache

```bash
docker build --tag ghcr.io/joseesco24/users_crud_api_python:latest .
```

### Docker App Deployment Without Detach

```bash
docker run --rm --name users_crud_api_python_app --publish 10048:10048 --env-file ./.env --env ENVIRONMENT_MODE=production ghcr.io/joseesco24/users_crud_api_python:latest
```

### Docker App Deployment With Detach

```bash
docker run --detach --rm --name users_crud_api_python_app --publish 10048:10048 --env-file ./.env --env ENVIRONMENT_MODE=production ghcr.io/joseesco24/users_crud_api_python:latest
```

### Docker Access To The Container Terminal

```bash
docker exec -it users_crud_api_python_app /bin/bash
```

### Docker Killing Containerized App

```bash
docker kill users_crud_api_python_app
```

### Docker Login Into Github Container Registry

```bash
docker login -u joseesco24 -p < authentication token > ghcr.io
```

### Docker Push The Image To Github Container Registry

```bash
docker push ghcr.io/joseesco24/users_crud_api_python:latest
```

### Docker Pull The Image From Github Container Registry

```bash
docker pull ghcr.io/joseesco24/users_crud_api_python:latest
```

<br/>

## Docker Compose Project Commands

**Note:** Before running any of these commands be sure that your **CWD** is **users_crud_api_python** directory.

### Docker Compose Build Image Using Compose File

```bash
docker-compose -f compose.build.yaml build
```

### Docker Compose Start Dbs Services Using Compose File

```bash
docker-compose -f compose.databases.yaml up
```

### Docker Compose Stop Dbs Services Using Compose File

```bash
docker-compose -f compose.databases.yaml down
```

### Docker Compose Start Project Using Compose File

```bash
docker-compose -f compose.project.yaml up
```

### Docker Compose Stop Project Using Compose File

```bash
docker-compose -f compose.project.yaml down
```

<br/>
