# MVP Implementation Plan

## Phase 1: Basic Setup & REST APIs (Week 1)

### Day 1-2: Project Setup
- Initialize **FastAPI** project with basic structure  
- Set up **Docker** and `docker-compose` files  
- Create basic routes for **health check**  

### Day 3-4: User Authentication
- Create **user model** (in-memory to start)  
- Implement **user registration** endpoint  
- Implement **login** with JWT token generation  
- Add **authentication middleware**  

### Day 5: Conversation Management
- Create **conversation model** (in-memory)  
- Implement API to **create conversations**  
- Implement API to **list user’s conversations**  

---

## Phase 2: Basic WebSocket Implementation (Week 2)

### Day 1-2: WebSocket Setup
- Create basic **WebSocket endpoint**  
- Implement **connection handling**  
- Test basic WebSocket connectivity  

### Day 3-4: Message Handling
- Create **message model** (in-memory)  
- Implement **message sending** via WebSockets  
- Implement **storage of messages**  
- Implement API to **fetch message history**  

### Day 5: Basic UI
- Create minimal **HTML/JS interface** for testing  
- Implement basic **messaging UI**  

---

## Phase 3: Persistence (Week 3)

### Day 1-2: Database Integration
- Set up **PostgreSQL** in Docker  
- Create **database schemas**  
- Refactor in-memory models to use **database**  

### Day 3-4: Enhanced Features
- Add **group chat** functionality  
- Improve **message delivery** with proper error handling  
- Add basic **presence indicators**  

### Day 5: Testing & Documentation
- Write **integration tests**  
- Document **design decisions**  
- Create a **demo script**  

---

## Implementation Tips
For each step:
- **Focus on one feature at a time** – Get it working before moving to the next  
- **Test as you go** – Ensure each piece works before building on top of it  
- **Document challenges** – Valuable for system design interviews  
- **Reflect on design decisions** – Note why you chose specific approaches  

---

## Getting Started Right Now
Your very first steps:
1. Create a **basic project structure**:

- app/ # Main application code
- app/main.py # Entry point
- app/models/ # Data models
- app/api/ # API routes
- Dockerfile # For containerization
- docker-compose.yml # For local development

2. Create a minimal **FastAPI app** that runs in Docker  
3. Implement a **/health** endpoint returning `200 OK`  

This will give you a working foundation to build incrementally.

---

## Implementation Summary

### Core Components Implemented

Backend Architecture

- FastAPI Application: A robust web server with REST APIs and WebSocket support
- PostgreSQL Database: Persistent storage for users, conversations, and messages
- Authentication System: JWT-based authentication for secure API access
- Logging System: Structured logging with JSON format support
- Error Handling: Centralized error handling with standard error responses

Database Models
- User Model:
    - Fields: id, name, username, password (hashed), status
    - Relationships: created conversations, conversations (memberships), messages

- Conversation Model:
    - Fields: id, name, creator_id, created_at, type (group/direct)
    - Relationships: creator, members (many-to-many with users), messages

- Message Model:
    - Fields: id, sender_id, conversation_id, content, timestamp, type, status
    - Relationships: sender, conversation

REST API Endpoints

1.User Management:

- User registration (POST /v1/users/register)
- User login (POST /v1/users/login)
- Get current user info (GET /v1/users/me)
- Get all users (GET /v1/users)

2. Conversation Management:

- Create conversation (POST /v1/conversations)
- Get user's conversations (GET /v1/conversations)
- Get conversation messages (GET /v1/conversations/{id}/messages) with pagination

3. System Endpoints:

- Health check endpoint
- Root endpoint with welcome message

Real-Time Messaging

1. WebSocket Implementation:

- WebSocket endpoint (/ws/{conversation_id})
- JWT authentication for WebSocket connections
- Real-time message broadcasting to all connected users in a conversation

2. Connection Management:

- ConnectionManager class to handle WebSocket connections
- Methods for connecting, disconnecting, and broadcasting messages
- Organization of connections by conversation_id and user_id

Security & Middleware

1. Authentication:

- JWT token generation and validation
- Password hashing and verification
- User authorization for resources

2. Request Processing:

- CORS middleware to allow cross-origin requests
- Request ID middleware for tracing requests through the system

Services Layer

1. User Service:

- User registration and authentication
- User data retrieval

2. Conversation Service:

- Creating and retrieving conversations
- Access control for conversations

3. Message Service:

- Creating and retrieving messages
- Message formatting and delivery

Frontend Implementation

- Basic HTML/CSS/JS frontend for testing the APIs
- Chat interface with conversation list and message display
- Authentication system with login/register forms

### Architecture diagram

```shell
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
                                                 |
                                                 |
                                                 v
                                         +---------------+
                                         |               |
                                         |  PostgreSQL   |
                                         |  Database     |
                                         |               |
                                         +---------------+
```

### System flow

1. Authentication Flow:

- User registers via REST API
- User logs in and receives JWT token
- JWT token used for subsequent API calls and WebSocket connections

2. Conversation Flow:

- User creates a conversation with selected participants
- User fetches their conversations list
- User opens a conversation to view messages

3. Messaging Flow:

- User establishes WebSocket connection for real-time updates
- User sends messages through WebSocket
- Messages are persisted to database and broadcast to all connected users
- Users can fetch message history via REST API

### Features completed

1. User Authentication: ✅ User registration ✅ User login with JWT tokens ✅ Password security with hashing

2. Conversation Management: ✅ Create one-to-one and group conversations ✅ List conversations for a user ✅ Access control to conversations

3. Real-time Messaging: ✅ Send messages via WebSocket ✅ Broadcast messages to conversation participants ✅ Persist messages to database ✅ Fetch message history with pagination