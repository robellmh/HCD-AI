### Architecture Overview

This project follows a modular architecture, visualized in the hcd_architecture.excalidraw file located at the root of this repository. To view this file, you can use the Excalidraw VSCode extension or open it in any Excalidraw-compatible editor. It outlines the relationships between key components such as the backend, database, and Redis services.

## Quick Start with Docker

This project is configured to run with Docker Compose for ease of setup and management. Follow the steps below to get started:

#### Prerequisites:
-  Docker and Docker Compose installed on your machine.
-  Familiarity with Docker commands.

#### Step 1:
Prepare Environment Files Navigate to the docker-compose directory:

`cd docker-compose`

Copy the template environment files:

`cp template.base.env .base.env`
`cp template.backend.env .backend.env`

Edit the .backend.env file to customize the environment variables for your setup, ensuring you remove any `#pragma: allowlist secret` comments before running the application.

#### Step 2: Spin Up Services

To start the application, run the following command: `docker-compose -f docker-compose.yml -f docker-compose.dev. up -d`

You can then ccess the Swagger UI at: http://localhost:8000/docs (you'll need your API key to test out endpoints; see more on this below).


#### Step 3: Stopping the Services
To bring the services down (for both configurations):
`docker-compose -f docker-compose.yml -f docker-compose.dev.yml down`

#### API Access in Swagger UI:

Once the services are running, you can explore the API at http://localhost:8000/docs API Key Verification: Many API calls require an API key for authentication. The default API key is: `"my_secret_key"`. To change the key, set the `API_SECRET_KEY` environment variable in `.backend.env`.

**Additional Notes:**

 The backend service will automatically rebuild on changes to the source code in development mode (enabled by the `develop` section in `docker-compose.dev.yml`).

 For debugging the database, PostgreSQL is exposed on port `5434` (development mode).
