# Form-filling Chatbot

## Description

This is a siple solution for facilitating for filling using GenAI. It helps people who are often creating new request by enabling them to insert multiple fields at once, asking questions about the form if it is not clear. This solution is production-ready by using FastAPI, PostgreSQL, and Docker. it can be scaled horizontally by running multiple instances of the application behind a load balancer.

Additionally, it uses the vector extension for PostgreSQL to store and search for similar questions in vector databases.

## How to run

1. Create an .env file with OpenAI API key and DB connection parameters

    ```bash
    cp .env.example .env
    ```

    Make sure to add all necessary secrets to  the .env.

2. Install app dependencies (remove --with dev if you don't want to install dev dependencies)

    Poetry

    ```bash
    poetry install --with dev
    poetry run app
    ```

    Docker

    ```bash
    docker compose up --build
    ```

    visit <http://localhost:8089> for a simple UI or <http://localhost:8089/docs> for FastAPI endpoints

## Project Structure

```bash
.
├── Dockerfile
├── README.md
├── docker-compose.dev.yml      # Only use for development
├── docker-compose.yml          # deployment docker
├── flowchart.jpg               # Visual representation of the application flow
├── pip.conf                    # for docker to use nexus pip index
├── pyproject.toml              # Poetry configuration file
├── ruff.toml                   # Configuration file for Ruff (Python linter)
└── form
    ├── __init__.py
    ├── main.py                 # Main entry point of the application (FastAPI app)
    ├── agents
    │   ├── __init__.py
    │   ├── agents_manager.py   # Manages different types of agents
    │   ├── base_agent.py       # Base class for all agents
    │   ├── conversation_agent.py
    │   ├── intent_agent.py
    │   └── note_taking_agent.py
    ├── api                     s
    │   ├── __init__.py
    │   ├── api_router.py       # Main API router
    │   ├── deps.py             # Dependency injection for API (Database connection)
    │   └── endpoints           # Individual API endpoints
    │       ├── __init__.py
    │       ├── chat.py
    │       ├── check.py
    │       ├── sessions.py
    │       └── uuid.py
    ├── db
    │   ├── __init__.py         # initiate an async database connection
    │   ├── db_check.py         # Database health check
    │   ├── db_operations.py    # CRUD operations
    │   ├── db_tables.py        # Database table definitions
    │   └── init.pgsql          # Initial SQL for database setup
    ├── models
    │   ├── __init__.py
    │   ├── exceptions.py       # Custom exception classes
    │   ├── requests.py         # Request models
    │   └── responses.py        # Response models
    ├── schemas
    │   └── form.json           # Form schema
    │   └── form_val.json       # schema validation rules to be followed
    ├── static                  # UI
    │   ├── script.js
    │   └── styles.css
    ├── templates               # UI
    │   └── index.html
    └── utils
        ├── __init__.py
        ├── config.py           # Secret configuration
        ├── form_handler.py
        └── text_handler.py
```


## Stack

- FastAPI
- OpenAI (no LangChain)
- PostgreSQL (with vector extension)
- Docker
- Poetry
- Ruff (Python linter)
- Pydantic (for data validation)
- Uvicorn (ASGI server)
- Pytest (testing)

## Available Endpoints

All endpoints [here](./ENDPOINTS.md)

## Agents Infractions

The agents infractions are as follows:
- `IntentAgent`: This agent is responsible for identifying the user's intention based on the input prompt.
- `NoteTakingAgent`: This agent is responsible for filling in the form fields based on the user's input prompt.
- `SpecialistAgent`: This agent is responsible for handling specialist queries.
- `ConversationAgent`: This agent is responsible for moving the conversation forward by asking the user for the next field to fill in the form.
SpecialistAgent and ConversationAgent are run in parallel to handle the user's input prompt.
