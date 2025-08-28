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