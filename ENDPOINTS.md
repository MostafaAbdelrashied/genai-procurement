
## API Endpoints

### Chat

#### Chat with GPT

**Description:** Chat with GPT

- **URL:** `/chat/message`
- **Method:** `POST`
- **Parameters:**
  - `session_id` (query, required, UUID): Session Id
- **Request Body:**
  - `message` (string, required): The user's input message
- **Responses:**
  - `200`: Successful Response
  - `422`: Validation Error

### Sessions

#### Create Session

**Description:** Create a new session in the database

- **URL:** `/sessions/create_session`
- **Method:** `POST`
- **Parameters:**
  - `session_id` (query, required, UUID): Session Id
- **Responses:**
  - `200`: Successful Response
  - `422`: Validation Error

#### Get All Sessions

**Description:** Get all available sessions from the database

- **URL:** `/sessions/get_all_sessions`
- **Method:** `GET`
- **Responses:**
  - `200`: Successful Response

#### Get Session

**Description:** Get session data from the database

- **URL:** `/sessions/get_session_data/{session_id}`
- **Method:** `GET`
- **Parameters:**
  - `session_id` (path, required, UUID): Session Id
- **Responses:**
  - `200`: Successful Response
  - `422`: Validation Error

#### Get Session Messages

**Description:** Get all messages for a session from the database

- **URL:** `/sessions/get_messages_history/{session_id}`
- **Method:** `GET`
- **Parameters:**
  - `session_id` (path, required, UUID): Session Id
- **Responses:**
  - `200`: Successful Response
  - `422`: Validation Error

#### Update Session

**Description:** Update session data in the database

- **URL:** `/sessions/update_session_form/{session_id}`
- **Method:** `PUT`
- **Parameters:**
  - `session_id` (path, required, UUID): Session Id
  - `create_if_not_exists` (query, optional, boolean): Create If Not Exists
- **Request Body:**
  - `form_data` (object, required): The form data to be updated
- **Responses:**
  - `200`: Successful Response
  - `422`: Validation Error

#### Delete Session

**Description:** Delete a session from the database

- **URL:** `/sessions/delete_session/{session_id}`
- **Method:** `DELETE`
- **Parameters:**
  - `session_id` (path, required, UUID): Session Id
- **Responses:**
  - `204`: Successful Response
  - `422`: Validation Error

### Vectorstore

#### Upsert Embedding

**Description:** Upsert an embedding in the database

- **URL:** `/vectorstore/upsert_embedding`
- **Method:** `PUT`
- **Request Body:**
  - `content` (string, required): The content to be embedded
  - `properties` (object, optional): The properties for embedding
- **Responses:**
  - `204`: Successful Response
  - `422`: Validation Error

#### Upsert Embeddings

**Description:** Upsert multiple embeddings in the database

- **URL:** `/vectorstore/upsert_embeddings`
- **Method:** `PUT`
- **Request Body:**
  - `embeddings` (array of objects, required): Array of contents and their properties
- **Responses:**
  - `204`: Successful Response
  - `422`: Validation Error

#### Get All Embeddings

**Description:** Get all available embeddings from the database

- **URL:** `/vectorstore/get_all_embeddings`
- **Method:** `GET`
- **Responses:**
  - `200`: Successful Response

#### Get Embedding

**Description:** Get embedding data from the database

- **URL:** `/vectorstore/get_embedding/{embedding_id}`
- **Method:** `GET`
- **Parameters:**
  - `embedding_id` (path, required, UUID): Embedding Id
- **Responses:**
  - `200`: Successful Response
  - `422`: Validation Error

#### Get Embeddings

**Description:** Get multiple embeddings from the database

- **URL:** `/vectorstore/get_embeddings/`
- **Method:** `GET`
- **Parameters:**
  - `embedding_id` (query, required, array of UUIDs): Embedding Ids
- **Responses:**
  - `200`: Successful Response
  - `422`: Validation Error

#### Delete Embedding

**Description:** Delete an embedding from the database

- **URL:** `/vectorstore/delete_embedding/{embedding_id}`
- **Method:** `DELETE`
- **Parameters:**
  - `embedding_id` (path, required, UUID): Embedding Id
- **Responses:**
  - `204`: Successful Response
  - `422`: Validation Error

#### Delete Embeddings

**Description:** Delete multiple embeddings from the database

- **URL:** `/vectorstore/delete_embeddings`
- **Method:** `DELETE`
- **Parameters:**
  - `embedding_id` (query, optional, array of UUIDs): Embedding Ids
- **Responses:**
  - `204`: Successful Response
  - `422`: Validation Error

#### Get Embedding By Content

**Description:** Get embedding data from the database by content

- **URL:** `/vectorstore/get_embedding_by_content`
- **Method:** `GET`
- **Parameters:**
  - `content` (query, required, string): Content
- **Responses:**
  - `200`: Successful Response
  - `422`: Validation Error

#### Get Nearest Embeddings

**Description:** Get nearest embeddings from the database

- **URL:** `/vectorstore/get_nearest_embeddings`
- **Method:** `GET`
- **Parameters:**
  - `query` (query, required, string): Query
  - `limit` (query, optional, integer): Limit of results
  - `distance_type` (query, optional, string): Type of distance
- **Responses:**
  - `200`: Successful Response
  - `422`: Validation Error

#### Get Embeddings Within Distance

**Description:** Get embeddings within a certain distance from the database

- **URL:** `/vectorstore/get_embeddings_within_distance`
- **Method:** `GET`
- **Parameters:**
  - `query` (query, required, string): Query
  - `distance` (query, required, number): Distance
  - `distance_type` (query, optional, string): Type of distance
- **Responses:**
  - `200`: Successful Response
  - `422`: Validation Error

#### Embed Query

**Description:** Get embedding for a query

- **URL:** `/vectorstore/embed_query/{query}`
- **Method:** `GET`
- **Parameters:**
  - `query` (path, required, string): Query
- **Responses:**
  - `200`: Successful Response
  - `422`: Validation Error

#### Embed Queries

**Description:** Get embeddings for multiple queries

- **URL:** `/vectorstore/embed_queries`
- **Method:** `GET`
- **Parameters:**
  - `queries` (query, optional, array of strings): Queries
- **Responses:**
  - `200`: Successful Response
  - `422`: Validation Error

### UUID

#### Convert To UUID

**Description:** Convert a string ID to UUID

- **URL:** `/uuid/convert-string/{string_id}`
- **Method:** `GET`
- **Parameters:**
  - `string_id` (path, required, string): String Id
- **Responses:**
  - `200`: Successful Response
  - `422`: Validation Error

### Checks

#### Health Check

**Description:** Health check

- **URL:** `/check_health`
- **Method:** `GET`
- **Responses:**
  - `200`: Successful Response

#### Check DB Connection

**Description:** Check DB connection

- **URL:** `/check_db`
- **Method:** `GET`
- **Responses:**
  - `200`: Successful Response

#### Check Table

**Description:** Check if a table exists in the database

- **URL:** `/check_table/{table_name}`
- **Method:** `GET`
- **Parameters:**
  - `table_name` (path, required, string): Table Name
- **Responses:**
  - `200`: Successful Response
  - `422`: Validation Error

#### Check Tables

**Description:** Check if tables exist in the database

- **URL:** `/check_tables`
- **Method:** `GET`
- **Responses:**
  - `200`: Successful Response