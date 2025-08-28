# Requirements of the app

We will begin with defining the functional and non functional requirements of the system.
We will begin with a very small scope and gradually add complexity learning concepts of system design and how they map to real systems.

## Functional requirements

- Users should be able to register
- Users should be able to login to system
- Profile management (Optional for initial design, can be added later)

- Users should be able to send messages to each other
- Users should be able to receive messages
- Users should be able to create group chats
- Users should be able to send and receive attachments (This can be excluded for min scope)
- User should be able to see typing indicator (Again can be excluded for min scope)
- User should be able to see online/offline status of other users

## Non functional requirements

- System should support large no of users (Should be scalable)
- System should support low latency for message delivery (< 500 ms)
- System should ensure reliable message delivery (Should be fault tolerant to network glitches and errors)

## Estimation

- Estimated no of daily users - 20M, for MVP we can have 20K users
- Estimated no of messages/day - 2000 Million messages per day if each users send 100 messages daily on average, For MVP it can be 2000K messages/day
- We can store messages for a week to begin with which can be gradually increased as we iterate. Moreover we can also have backup functionality. (This can be out of scope)

## Technical constraints

- We will use python FAST API to build the backend
- We will use docker containers to run the app
- We will begin with console based front end, then add minimal front end using javascript/React.

## Plan

We will begin with a small scope and then gradually build on top of those.

For MVP, we will support these

- Users should be able to register
- Users should be able to login to system

- Users should be able to send messages to each other
- Users should be able to receive messages
- Users should be able to create group chats

Later on, we will add these

- Profile management
- Users should be able to send and receive attachments (This can be excluded for min scope)
- User should be able to see typing indicator (Again can be excluded for min scope)
- User should be able to see online/offline status of other users.
