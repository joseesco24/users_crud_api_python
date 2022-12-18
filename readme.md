# Users Crud Api Python

A really simple CRUD REST API based on Docker and Python.

<br/>

## Project commands

**Note:** Before running any of these commands be sure that your **CWD** is **users_crud_api_python** directory.

### Clean Python Cache Using Grep

```bash
find . | grep -E "(/__pycache__$|\.pyc$|\.pyo$)" | xargs rm -rf
```

### Upgrade Python Venv Base Dependencies

```bash
pip install --no-cache --upgrade pip wheel setuptools
```

### Installing The Dev And App Dependencies

```bash
pip install --no-cache -r requirements.dev.txt
pip install --no-cache -r requirements.app.txt

```

### Upgrade The Dependencies Using Pip Upgrader

**Note:** Before running this command you need to install the dev dependencies.

```bash
pip-upgrade requirements.dev.txt
pip-upgrade requirements.app.txt
```

### Format The Code Using Black

**Note:** Before running this command you need to install the dev dependencies.

```bash
black ./src
```

### Lint The Code Using Pylint

**Note:** Before running this command you need to install the dev dependencies.

```bash
pylint --fail-under=10 --rcfile=.pylintrc ./src
```

### Check Static Types Using Mypy

**Note:** Before running this command you need to install the dev dependencies.

```bash
mypy --explicit-package-bases ./src
```

### Run On development Mode

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

## Docker Project commands

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

### Docker Login Into GitHub Container Registry

```bash
docker login -u joseesco24 -p < authentication token > ghcr.io
```

### Docker Push The Image To GitHub Container Registry

```bash
docker push ghcr.io/joseesco24/users_crud_api_python:latest
```

### Docker Compose Build Image Using Compose File

```bash
docker-compose -f compose.project.yaml build
```

### Docker Compose Start Dbs Services Using Compose File

```bash
docker-compose -f compose.databases.yaml up
```

### Docker Compose Stop Dbs Services Using Compose File

```bash
docker-compose -f compose.databases.yaml down
```

<br/>
