Thank you for considering to contribute to this project. This page shows you how to setup your local
development environment.

### [Pre-requisite] Install Docker

If you have Docker installed, you can skip this step.

To install Docker, follow the instructions on the [official website](https://docs.docker.com/get-docker/).

### [Pre-requisite] Install Docker Compose

If you have Docker Compose installed, you can skip this step.
After installing Docker, you can install Docker Compose by following the instructions on the [official website](https://docs.docker.com/compose/install/).

### Clone the repository

Clone the [HCD-AI](https://github.com/robellmh/HCD-AI) repository.

```shell
git clone git@github.com:robellmh/HCD-AI.git
```

### Create a virtual environment

Navigate to the root of the project and create a virtual environment.
if you are happy using `conda`, you can create it using the following command:

```shell
make fresh-env
```

This will install the dependencies in `requirements.txt` and `requirements-dev.txt` in a new conda environment called `hew-ai`.

Now active the environment:

```shell
conda activate hew-ai
```

### Setup pre-commit hooks

To setup pre-commit hooks, run the following command:

```shell
pre-commit install
```

### Setup environment variables


Navigate to the `deployment/docker-compose/` subfolder.

```shell
cd deployment/docker-compose/
```

Copy `template.*.env` files to `.*.env`:

```shell
cp template.base.env .base.env
cp template.backend.env .backend.env
```

Edit the `.base.env` and `.backend.env` files to set the environment variables.

All the variables must be set. The default values will work for a local deployment but should
be updated when deploying in production.

!!! note
    You can set which language model to use by setting the `LLM_MODEL` environment variable in the `.backend.env` file.

    - If using OpenAI models,
        - Set `LLM_MODEL` to the model name. E.g. `gpt-4o-mini`
        - Set `OPENAI_API_KEY` to your OpenAI API key.
    - If using Ollama models,
        - Set `LLM_MODEL` to `ollama/<model-name>`. E.g. `ollama/llama3.2:1b`
        - Set `LLM_API_BASE` to the base URL of the Ollama API. E.g. `https://my.ollama.server:11434`

### Run docker-compose

```shell
docker compose -f docker-compose.yml -f docker-compose.dev.yml -p hew-ai-stack watch
```

If you want to run a local Ollama server as well, use the following commands:

```shell
docker compose -f docker-compose.yml -f docker-compose.dev.yml --profile ollama -p hew-ai-stack watch
```

Note that this will start the Ollama server on port 11434 with the model you set in LLM_MODEL pre-loaded.


You can now view the the API documentation at
`http://$DOMAIN:8000/docs` (you can also test the endpoints here).

??? note "What my API secret key?"
    You'll need a secret key to call most of the API endpoints. You can set your API_SECRET_KEY in the `.backend.env` file. If you haven't set it, it will default to `my_secret_key`. You should update this to a more secure value.

### Stopping the containers

You can stop the containers by running the following command:

```shell
docker compose -f docker-compose.yml -f docker-compose.dev.yml -p hew-ai-stack down
```

## Testing

You can run tests by navigating to `/backend` and running the following command:

```shell
make tests
```

## Other ways to setup

You can run the FastAPI directly in shell as well. But you need to make sure you have the right database accessible
and the right environment variables set.

We don't show this setup here since it requires manual management of dependencies. But if you do choose to go with this setup, the following command can help setup the postgres database and redis cache:

```
make setup-dev
```
