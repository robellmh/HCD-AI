# Welcome to **AI-for-HEWs** Documentation

For full documentation, clone repository and run the following command:

```bash
mkdocs serve
```

# Quick Setup with Docker Compose

## Quick setup

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
