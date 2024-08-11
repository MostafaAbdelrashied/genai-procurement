--------------------------------------------
---- Reset the database --------------------
--------------------------------------------
DROP TABLE IF EXISTS procurement.messages;

DROP TABLE IF EXISTS procurement.sessions;

DROP TABLE IF EXISTS procurement.embeddings;

DROP EXTENSION IF EXISTS vector;

DROP SCHEMA IF EXISTS procurement;
--------------------------------------------
---- Create the database -------------------
--------------------------------------------

-- Create the schema
CREATE SCHEMA IF NOT EXISTS procurement;

CREATE EXTENSION IF NOT EXISTS vector;

-- Create the sessions table
CREATE TABLE IF NOT EXISTS procurement.sessions (
    session_id UUID PRIMARY KEY,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    last_updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    form_data JSONB NOT NULL
);

-- Create the messages table
CREATE TABLE IF NOT EXISTS procurement.messages (
    message_id UUID PRIMARY KEY,
    session_id UUID NOT NULL,
    prompt TEXT NOT NULL,
    response TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (session_id) REFERENCES procurement.sessions (session_id)
);

CREATE TABLE IF NOT EXISTS procurement.embeddings (
    embedding_id UUID PRIMARY KEY,
    content TEXT NOT NULL,
    embedding vector (1536),
    properties JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    last_updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for better query performance
CREATE INDEX IF NOT EXISTS idx_messages_session_id ON procurement.messages (session_id);