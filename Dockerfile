FROM container-registry.ubs.net/ubuntu:22.04 AS base

RUN apt update
RUN apt install -y python3.11 python3-pip

ENV PYTHONUNBUFFERED 1
ENV PYTHONPATH="/app"

WORKDIR /app

# Copy project files
COPY . .

# Install dependencies
COPY pip.conf /root/.config/pip/pip.conf

RUN pip3 install poetry
RUN poetry config certificates.nexus.cert false
RUN poetry lock --no-update
RUN poetry install

# Verify Uvicorn installation
RUN poetry run uvicorn --version

# Expose the port
EXPOSE 8089

# Run the server
CMD ["poetry", "run", "app"]