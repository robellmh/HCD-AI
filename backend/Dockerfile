# Stage 1: Build environment
FROM python:3.12-slim-bullseye as build

LABEL maintainer="LMH, IDinsight"

# Define build arguments
ARG NAME=HCD-AI
ARG HOME_DIR=/usr/src/${NAME}

# Set up the build environment
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc libpq-dev python3-dev dos2unix ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Set up the home directory and permissions
RUN useradd -ms /bin/bash -d ${HOME_DIR} container_user \
    && mkdir -p ${HOME_DIR} /tmp/prometheus \
    && chown -R container_user: ${HOME_DIR} /tmp/prometheus

# Copy requirements and install Python dependencies
COPY requirements.txt /requirements.txt
RUN pip install --no-cache-dir -r /requirements.txt

# Copy the application source code
COPY . ${HOME_DIR}

# Convert line endings
RUN find ${HOME_DIR} -type f -print0 | xargs -0 dos2unix

# Ensure startup script is executable
RUN chmod +x ${HOME_DIR}/startup.sh

# Stage 2: Final image
FROM python:3.12-slim-bullseye

# Define runtime arguments
ARG NAME=HCD-AI
ARG PORT=8000
ARG HOME_DIR=/usr/src/${NAME}

# Install required shared libraries
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Copy the Python packages and other dependencies from the build stage
COPY --from=build /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=build /usr/local/bin /usr/local/bin

# Copy the application files and directories from the build stage
COPY --from=build ${HOME_DIR} ${HOME_DIR}
COPY --from=build /tmp/prometheus /tmp/prometheus

# Set environment variables
ENV PYTHONPATH="${PYTHONPATH}:${HOME_DIR}"
ENV PORT=${PORT}
RUN python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('Alibaba-NLP/gte-base-en-v1.5', trust_remote_code=True )"
# Set working directory and expose the port
WORKDIR ${HOME_DIR}
EXPOSE ${PORT}

# Define the command to run the application
CMD ["./startup.sh"]
