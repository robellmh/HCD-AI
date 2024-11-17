## Pre-requisites

To deploy the HCD-AI stack, you need to have the following services running:
* Docker
* Docker-compose

## Quick setup

!!! warning "You need to have installed [Docker](https://docs.docker.com/get-docker/)"

**Step 1:** Clone the [HCD-AI](https://github.com/robellmh/HCD-AI) repository.

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

??? note "Which LLM to use"
    You can either use models available on [Ollama](https://ollama.com) or use OpenAI models.
    Set `LLM_MODEL` to `ollama/<model-name>` to use Ollama models or `openai/<model-name>` to use OpenAI models.
    To use OpenAI models, you also need to set the `OPENAI_API_KEY` in the `.backend.env` file.

**Step 5:** Run docker-compose

```shell
docker compose -f docker-compose.yml -f docker-compose.dev.yml -p hew-ai-stack up -d --build
```

??? note "What components does this start"
    The command will start a stack with a `backend` FastAPI container, a `postgres` database container, a `redis` container. See [dev setup](./contribute/dev-setup.md) for other options

You can now view the the API documentation at
`http://$DOMAIN:8000/docs` (you can also test the endpoints here).

**Step 5:** Shutdown containers

```shell
docker compose -f docker-compose.yml -f docker-compose.dev.yml -p hew-ai-stack down
```
