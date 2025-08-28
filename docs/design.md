# Designing the app

Once we have all the functional and non functional requirements listed out, we proceed with the design of the app. We first will list down the data models of our app.

## Data models

### User

The user data model will represent the user of our system. It will have below fields

- id: Unique user id
- name: Name of the user
- email: Email address of the user
- password: Password for the user
- status: Online/Offline (For later than MVP)
- createdAt: Timestamp at which the user is created

### Message

The message data model will represent the message in our system. It will have below fields

- id: Unique message id
- sender_id: Id of the user who sent the message
- timestamp: The time at which the message was sent
- content: Textual content of the message
- type: Type of message (Text, image etc)
- conversation_id: The id of the conversation to which the message is sent.
- status: Delivery status of the message

### Group

The group data model will represent the group chats in our system. It will have below fields

- id: Unique conversation id
- name: Name of the group chat (optional for direct messages)
- creator_id: ID of the user who created the group
- member_ids: List of user IDs who are part of this conversation
- created_at: When the conversation was created
- is_group: Boolean to distinguish between direct messages and group chats

We can later add media files and attachment support to the message data model.

For our MVP in phase 1, I think these data models will suffice, we can always comeback and iterate to add on fields to it or modify it.

## Database Design

Once we have data models decided for our app, we will go ahead and plan and decide on the database schema. Firstly we need to decide on the database to work with. Lets tackle that next.

### Choice of database

Now this is a tricky part, we can choose any of SQL or No SQL databases. Lets walkthrough some of them to understand what they offer and then choose one for our app.

#### SQL

Like - SQL Server, Postgres, MySQL
Pros

- Structured format in terms of rows and columns in tables
- Fixed schema for data
- Strong ACID guarantees

Cons

- Not horizontally scalable, good choice for medium to high workloads
- Does not support flexible schema, can be difficult to evolve later
- Queries can involve joins which can increase latency of the system

#### NO SQL

Like - DynamoDB, Cassandra, Graph DBs, Mongod Dbs,

Pros

- Flexible schema, easy to evolve later
- Can be scaled horizontally
- Support very high workloads and user bases

Cons

- Does not support strong ACID guarantees
- No structured format, not suitable for apps that want a fixed schema for the data

What do we choose ?

As per our scale estimates for MVP which are:

- Estimated no of daily users - 20M, for MVP we can have 20K users
- Estimated no of messages/day - 2000 Million messages per day if each users send 100 messages daily on average, For MVP it can be 2000K messages/day

Think we can go with PostgreSQL as it will support our use case.
If see increase in load on the database, we can add caching via redis to decrease latency and load on the main database.

Even after caching, if load keeps increasing on the main database, we can migrate to no sql databases like DynamoDB. But for now, we can stick to PostgreSQL. I know schema evolution will be a challenge when we move from MVP to add online/offline status to user table etc., but we will face it and address it.

### Schema

Now since we have decided to go ahead with Postgres as the database, we will quickly jot down the schema for the different tables for the MVP version of our app.

#### User

- id (PK)
- name (add max length check constraint)
- password (Store in hashed format)
- email
- createdAt (time column)
- status

#### Conversation

- id (PK)
- name (add max length check constraint)
- creator_id (FK to User table)
- createdAt (time column)
- is_group (boolean to indicate if it is a group of 1-1 convo)

#### User_Conversation_Membership

- user_id (FK to User table) (Indexed)
- conversation_id (FK to conversation table)

#### Message

- id (PK)
- sender_id (FK to User table)
- timestamp (time column)
- content (add max length check constraint)
- type (textual for MVP)
- conversation_id (FK to conversation table) (Indexed)
- status

Now we had to add a table like User_Conversation_Membership as we can't store multiple member ids in same row for conversation table. If we would have chosen No SQL like mongoDB we could have an array for storing it. Lets leave it for now.

## API Design

Once we have the data models, choice of DB and Database schema decided, we can next look at and design the API's for out app.

- Endpoint to register user

```json
POST /v1/users/register

{
    "name": "John Doe",
    "password": "<>",
    "email": "johndoe@gmail.com",
}

Response
201 Created : Success with user object with id and createdAt fields populated from server
400 Bad request: If validation fails
500 Internal server error: if something goes wrong in server side
```

- Endpoint to login user

```json
POST /v1/users/login

{
    "password": "<>",
    "email": "johndoe@gmail.com",
}

Response
200 OK : Success with jwt token to be used for subsequent requests.
400 Bad request: If validation fails
500 Internal server error: if something goes wrong in server side
401 Unauthorized: If Auth fails
```

- Endpoint to create conversation

```json
POST /v1/conversations

{
    "name": "Group chat",
    "memberIds": [],
    "isGroup" : true
}

Response
201 Created : Success with conversation object having id and other fields populated
400 Bad request: If validation fails
500 Internal server error: if something goes wrong in server side
```

- Endpoint to send messages

```json

POST /v1/conversations/<id of convo>/messages

{
    "content": ""
}

Response
200 Ok : Success if message is delivered
400 Bad request: If validation fails
500 Internal server error: if something goes wrong in server side
```

- Endpoint to fetch user's conversations

```json

GET /v1/conversations/

header
Authorization: <Bearer JWT>

{
    [
        List of conversation objects
    ]
}

Response
200 Ok : Return the list of conversation objects
400 Bad request: If validation fails
500 Internal server error: if something goes wrong in server side
```

- Endpoint to fetch messages of a conversations

```json

GET /v1/conversations/<id of convo>/messages?limit=20&before={timestamp}

header
Authorization: <Bearer JWT>

{
    [
        List of message objects
    ]
}

Response
200 Ok : Return the list of message objects
400 Bad request: If validation fails
500 Internal server error: if something goes wrong in server side
```

## High level architecture

Next up, we will design the high level architecture for our app.

### Core Components

- **Client**: Web browser or console application that connects to our servers
- **Server**: FastAPI application server which handles requests and WebSocket connections
- **Database**: PostgreSQL database to store users, conversations, and messages
- **Redis Cache**: To store latest messages (e.g., 50 per conversation) for faster retrieval

### System Architecture Diagram

+-----------------+      HTTP/REST       +------------------+
|                 |  ----------------->  |                  |
|                 |                      |                  |
|     Client      |                      |    FastAPI       |
|   (Browser/     |                      |    Server        |
|    Console)     |                      |                  |
|                 |     WebSockets       |                  |
|                 |  <---------------->  |                  |
+-----------------+                      +------------------+
                                                 |
                                                 |
                    +---------------+            |
                    |               |            |
                    |  Redis Cache  | <--------> |
                    |  (Messages)   |            |
                    |               |            |
                    +---------------+            |
                                                 |
                                                 v
                                         +---------------+
                                         |               |
                                         |  PostgreSQL   |
                                         |  Database     |
                                         |               |
                                         +---------------+

### User Flow

1. **Authentication & Setup**:
   - Users register via the `/users/register` endpoint
   - Users login via the `/users/login` endpoint to receive a JWT token
   - Users can create conversations (1:1 or groups) via the `/conversations` endpoint

2. **WebSocket Connection**:
   - After login, client establishes a persistent WebSocket connection
   - Connection includes the JWT token for authentication
   - Server maintains a mapping of user_id to active WebSocket connections

3. **Messaging Flow**:
   - When a user sends a message through the WebSocket:
     1. Server validates the user and permissions
     2. Message is saved to the database
     3. Server broadcasts the message to all recipients who are connected
     4. For offline users, messages are stored and delivered when they connect

4. **Data Retrieval**:
   - Users can fetch their conversation list via REST API
   - Users can fetch message history with pagination via REST API
   - Redis cache will be used to quickly serve recent messages

### Connection Management

The server will maintain WebSocket connections with the following considerations:

1. **Authentication**: Each connection must be authenticated via JWT token
2. **Connection Tracking**: Server tracks which user is connected to which conversation
3. **Reconnection Handling**: Support for clients that temporarily disconnect and reconnect
4. **Presence Updates**: Notify other users when someone connects/disconnects

### Implementation Strategy

For our FastAPI implementation, we'll create:

- A WebSocket endpoint for real-time messaging:

```python
@app.websocket("/ws/{conversation_id}")
async def websocket_endpoint(websocket: WebSocket, conversation_id: str):
    # Authenticate from token in query params or headers
    # Add to active connections
    # Listen for messages and broadcast
```

- A connection manager class to handle WebSocket state:

```python
class ConnectionManager:
    def __init__(self):
        self.active_connections = {}  # conversation_id -> [(user_id, websocket),...]
    
    async def connect(self, websocket, conversation_id, user_id):
        # Add connection
    
    async def disconnect(self, websocket, conversation_id):
        # Remove connection
    
    async def broadcast(self, message, conversation_id, sender_id):
        # Send to all connections in a conversation
```

### Scaling Considerations

As we scale beyond the MVP:

- Multiple server instances will require a message broker (like Redis pub/sub)
- WebSocket connections will need to be balanced across servers
- Session affinity might be needed for WebSocket connections
- Cache warming strategies for frequently accessed conversations
