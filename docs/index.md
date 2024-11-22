# Welcome to **AI-for-HEWs** Documentation

This solution deploy a RAG-based service for Health Extension Worker in Ethiopia.


### Quick setup

!!! warning "You need to have installed [Docker](https://docs.docker.com/get-docker/)"

**Step 1:** Clone the [HCD-AI](git@github.com:robellmh/HCD-AI.git) repository.

```shell
git clone git@github.com:robellmh/HCD-AI.git
```

**Step 2:** Navigate to the `deployment/docker-compose/` subfolder.

```shell
cd deployment/docker-compose/
```

**Step 3:** Copy `template.*.env` files to `.*.env`:

```shell
cp template.base.env .base.env
cp template.backend.env .backend.env
```

**Step 4:** Edit the `.base.env` and `.backend.env` files to set the environment variables.

All the variables must be set. The default values will work for a local deployment but should
be updated when deploying in production.

**Step 5:** Run docker-compose

```shell
docker compose -f docker-compose.yml -f docker-compose.dev.yml -p hew-ai-stack up -d --build
```

You can now view the the API documentation at
`http://$DOMAIN:8000/docs` (you can also test the endpoints here).

**Step 5:** Shutdown containers

```shell
docker compose -f docker-compose.yml -f docker-compose.dev.yml -p hew-ai-stack down
```

### Development setup

1. Ensure you have `conda` installed
2. Run `make fresh-env` to create a new conda environment and install the dependencies
3. Switch to the new environment

```shell
conda activate hew-ai
```

4. Install pre-commit

```shell
pre-commit install
```

5. Run `make setup-dev` to start containers for postgres
6. Navigate to `backend` and run `python main.py` to start the FastAPI backend server
