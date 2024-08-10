--------------------------------------------
---- Reset the database --------------------
--------------------------------------------
DROP TABLE IF EXISTS front_door.messages;

DROP TABLE IF EXISTS front_door.sessions;

DROP TABLE IF EXISTS front_door.embeddings;

DROP EXTENSION IF EXISTS vector;

DROP SCHEMA IF EXISTS front_door;
--------------------------------------------
---- Create the database -------------------
--------------------------------------------

-- Create the schema
CREATE SCHEMA IF NOT EXISTS front_door;

CREATE EXTENSION IF NOT EXISTS vector SCHEMA front_door;

-- Create the sessions table
CREATE TABLE front_door.sessions (
    session_id UUID PRIMARY KEY,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    last_updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    form_data JSONB NOT NULL
);

-- Create the messages table
CREATE TABLE front_door.messages (
    message_id UUID PRIMARY KEY,
    session_id UUID NOT NULL,
    prompt TEXT NOT NULL,
    response TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (session_id) REFERENCES front_door.sessions (session_id)
);

CREATE TABLE front_door.embeddings (
    embedding_id UUID PRIMARY KEY,
    content TEXT NOT NULL,
    embedding vector (1536),
    properties JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    last_updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for better query performance
CREATE INDEX idx_messages_session_id ON front_door.messages (session_id);