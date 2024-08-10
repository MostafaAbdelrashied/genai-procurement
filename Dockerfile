# get lightest ubuntu image
FROM ubuntu:22.04 AS base
RUN apt update
RUN apt install -y python3.11 python3-pip

ENV PYTHONUNBUFFERED 1
ENV PYTHONPATH="/app"

WORKDIR /app

# Copy project files
COPY . .


RUN pip3 install poetry
RUN poetry lock --no-update
RUN poetry install

# Verify Uvicorn installation
RUN poetry run uvicorn --version

# Expose the port
EXPOSE 8080

# Run the server
CMD ["poetry", "run", "app"]