# Include environment variables for Docker Compose
include ./deployment/docker-compose/.backend.env
include ./deployment/docker-compose/.base.env

PROJECT_NAME=hew-ai
# Conda activate command adapted for Windows
CONDA_ACTIVATE=conda activate $(PROJECT_NAME)
ENDPOINT_URL=localhost:8000

# Guard function for environment variables (Linux)
# guard-%:
# 	@if [ -z '${${*}}' ]; then echo 'ERROR: environment variable $* not set' && exit 1; fi

# Guard function for environment variables (Windows)
guard-windows-%:
	@if not defined $(*) (echo ERROR: environment variable $* not set && exit 1)

# Fresh environment setup (Linux)
fresh-env:
	conda remove --name $(PROJECT_NAME) --all -y
	conda create --name $(PROJECT_NAME) python=3.12 -y
	$(CONDA_ACTIVATE) && pip install -r backend/requirements.txt --ignore-installed
	$(CONDA_ACTIVATE) && pip install -r requirements-dev.txt --ignore-installed
	$(CONDA_ACTIVATE) && pre-commit install

	@if "$(psycopg2-binary)" == "true" (
		$(CONDA_ACTIVATE) && pip uninstall -y psycopg2==2.9.9
		$(CONDA_ACTIVATE) && pip install psycopg2-binary==2.9.9
	)

# Fresh environment setup (Windows)
fresh-env-windows:
	conda remove --name $(PROJECT_NAME) --all -y
	conda create --name $(PROJECT_NAME) python=3.12 -y
	$(CONDA_ACTIVATE) && pip install -r backend/requirements.txt --ignore-installed
	$(CONDA_ACTIVATE) && pip install -r requirements-dev.txt --ignore-installed
	$(CONDA_ACTIVATE) && pre-commit install

	@if "$(psycopg2-binary)" == "true" (
		$(CONDA_ACTIVATE) && pip uninstall -y psycopg2==2.9.9
		$(CONDA_ACTIVATE) && pip install psycopg2-binary==2.9.9
	)

# Setup PostgreSQL (Linux)
setup-db: guard-POSTGRES_USER guard-POSTGRES_PASSWORD guard-POSTGRES_DB
	@docker stop pg-hew-ai-local || echo "Container not found, skipping stop."
	@docker rm pg-hew-ai-local || echo "Container not found, skipping remove."
	@docker system prune -f
	@sleep 2
	@docker run --name pg-hew-ai-local -e POSTGRES_USER=$(POSTGRES_USER) -e POSTGRES_PASSWORD=$(POSTGRES_PASSWORD) -e POSTGRES_DB=$(POSTGRES_DB) -p 5432:5432 -d pgvector/pgvector:pg16
	@sleep 5
	set -a && \
    source "$(CURDIR)/deployment/docker-compose/.base.env" && \
    source "$(CURDIR)/deployment/docker-compose/.backend.env" && \
    set +a && \
	cd backend && \
	python -m alembic upgrade head

# Setup PostgreSQL (Windows)
setup-db-windows: guard-windows-POSTGRES_USER guard-windows-POSTGRES_PASSWORD guard-windows-POSTGRES_DB
	@docker stop pg-hew-ai-local || echo "Container not found, skipping stop."
	@docker rm pg-hew-ai-local || echo "Container not found, skipping remove."
	@docker system prune -f
	@timeout /t 2
	@docker run --name pg-hew-ai-local -e POSTGRES_USER=$(POSTGRES_USER) -e POSTGRES_PASSWORD=$(POSTGRES_PASSWORD) -e POSTGRES_DB=$(POSTGRES_DB) -p 5432:5432 -d pgvector/pgvector:pg16
	@timeout /t 5
	migrate

# Teardown PostgreSQL (Linux)
teardown-db:
	@docker stop pg-hew-ai-local || echo "Container not found, skipping stop."
	@docker rm pg-hew-ai-local || echo "Container not found, skipping remove."

# Teardown PostgreSQL (Windows)
teardown-db-windows:
	@docker stop pg-hew-ai-local || echo "Container not found, skipping stop."
	@docker rm pg-hew-ai-local || echo "Container not found, skipping remove."

# Setup Redis (Linux)
setup-redis:
	@docker stop redis-hew-ai-local || echo "Container not found, skipping stop."
	@docker rm redis-hew-ai-local || echo "Container not found, skipping remove."
	@docker system prune -f
	@sleep 2
	@docker run --name redis-hew-ai-local -p 6379:6379 -d redis:6.0-alpine

# Setup Redis (Windows)
setup-redis-windows:
	@docker stop redis-hew-ai-local || echo "Container not found, skipping stop."
	@docker rm redis-hew-ai-local || echo "Container not found, skipping remove."
	@docker system prune -f
	@timeout /t 2
	@docker run --name redis-hew-ai-local -p 6379:6379 -d redis:6.0-alpine

# Teardown Redis (Linux)
teardown-redis:
	@docker stop redis-hew-ai-local || echo "Container not found, skipping stop."
	@docker rm redis-hew-ai-local || echo "Container not found, skipping remove."

# Teardown Redis (Windows)
teardown-redis-windows:
	@docker stop redis-hew-ai-local || echo "Container not found, skipping stop."
	@docker rm redis-hew-ai-local || echo "Container not found, skipping remove."

migrate:
	@echo "Running migration..."
    powershell -Command "$baseEnv = Get-Content '$(CURDIR)/deployment/docker-compose/.base.env'; \
                         $backendEnv = Get-Content '$(CURDIR)/deployment/docker-compose/.backend.env'; \
                         foreach ($line in $baseEnv) { if ($line -match '^(.*?)=(.*)$') { [System.Environment]::SetEnvironmentVariable($matches[1], $matches[2]) } }; \
                         foreach ($line in $backendEnv) { if ($line -match '^(.*?)=(.*)$') { [System.Environment]::SetEnvironmentVariable($matches[1], $matches[2]) } }"
