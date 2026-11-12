# WireTalk

A simple learning project about real-time terminal-based messaging application built using Python TCP sockets and multithreading.

WireTalk allows multiple clients to connect to a central server and communicate with each other through message broadcasting.

## Features

- Multiple simultaneous clients.
- Real-time message broadcasting.
- Username identification.
- Join and leave notifications.
- TCP socket communication.
- Multithreaded server and client.
- LAN and VPN connectivity.
- Environment-based configuration.

## Technologies

- Python
- Socket Programming (TCP)
- Threading
- python-dotenv

## Project Structure

```text
WireTalk/
│
├── server.py
├── client.py
├── .env
├── .gitignore
├── architecture.md
└── README.md

```

## Getting Started

### 1. Clone the repository

```bash
git clone <repository-url>
cd WireTalk
```

### 2. Install dependencies

```bash
pip install python-dotenv
```

### 3. Configure environment variables

Create a `.env` file:

```env
SERVER_HOST=0.0.0.0
SERVER_PORT=65432

CLIENT_HOST=127.0.0.1
CLIENT_PORT=65432
```

For LAN or VPN connections, change `CLIENT_HOST` to the server computer's reachable IP address.

### 4. Start the server

```bash
python server.py
```

### 5. Start clients

Open another terminal:

```bash
python client.py
```

Enter a username and start chatting!

## Architecture

WireTalk follows a client-server architecture.

The server listens for incoming TCP connections and creates a separate thread for every connected client.

When a client sends a message, the server receives it and broadcasts it to the other connected clients.

See [ARCHITECTURE.md](ARCHITECTURE.md) for more details.

## Roadmap

### Stage 1 — Basic Messaging

- [x] TCP client-server communication
- [x] Multiple simultaneous clients
- [x] Message broadcasting
- [x] Username identification
- [x] Join/leave notifications

### Stage 2 — Authentication & Database

- [ ] User registration
- [ ] User login and authentication
- [ ] SQL database integration
- [ ] Password hashing
- [ ] Private messaging
- [ ] Persistent message history

### Future Improvements

- [ ] WebSocket implementation
- [ ] Improved message handling
- [ ] Better concurrency management
- [ ] Graphical user interface

## Learning Objectives

This project is intended to explore:

- TCP/IP networking
- Client-server architecture
- Multithreading and concurrency
- Socket programming
- Database integration
- Backend development

---

**Status:** Stage 1 — Basic Messaging
