# Architecture

A multi-client TCP chat built on Python's `socket` and `threading` modules. One server relays every message to all other connected clients.

## 1. System Overview

```mermaid
flowchart LR
    subgraph Clients
        C1[Client A]
        C2[Client B]
        C3[Client C]
    end
    S[(Server<br/>127.0.0.1:65432)]

    C1 <-- TCP --> S
    C2 <-- TCP --> S
    C3 <-- TCP --> S
```

- **Topology:** star. Clients never talk to each other directly.
- **Transport:** TCP (`SOCK_STREAM`), IPv4.
- **Server role:** accept connections, relay each received chunk to every client except the sender.
- **Client role:** send user input, print incoming messages.

## 2. Components

```mermaid
classDiagram
    class Server {
        +host: str
        +port: int
        +clients: list~socket~
        +start()
        +handle_client(conn, addr)
    }
    class Client {
        +username: str
        +host: str
        +port: int
        +running: bool
        +s: socket
        +connect()
        +receive_messages()
    }
    Server "1" o-- "*" Client : relays between
```

| Component | Responsibility |
|---|---|
| `Server.start()` | Binds, listens, accepts connections in a loop (1s timeout so Ctrl+C is responsive), spawns one thread per client |
| `Server.handle_client()` | Reads from one client, broadcasts to all others, cleans up on disconnect |
| `Client.connect()` | Connects, sends join message, starts receiver thread, runs the input loop on the main thread |
| `Client.receive_messages()` | Background thread that prints incoming data |

## 3. Threading Model

```mermaid
flowchart TB
    subgraph Server Process
        M[Main thread<br/>accept loop]
        H1[Handler thread: Client A]
        H2[Handler thread: Client B]
        L[(self.clients)]
        M -- spawns --> H1
        M -- spawns --> H2
        M -- append --> L
        H1 -- remove / read copy --> L
        H2 -- remove / read copy --> L
    end

    subgraph Client Process
        CM[Main thread<br/>input loop, sendall]
        CR[Receiver thread<br/>recv, print]
    end
```

- **Server:** thread-per-connection. All handler threads are daemons.
- **Client:** main thread blocks on `input()`; a daemon thread blocks on `recv()`.
- **Shared state:** `Server.clients`. Broadcast iterates over `.copy()` to avoid mutation during iteration. There is currently no lock.

## 4. Sequence: Join, Chat, Leave

```mermaid
sequenceDiagram
    participant A as Client A
    participant S as Server
    participant B as Client B

    A->>S: connect()
    S->>S: accept, add conn to clients, spawn handler
    A->>S: "A joined"
    S->>B: "A joined"

    B->>S: "B: hello"
    S->>A: "B: hello"

    A->>S: "A: hi"
    S->>B: "A: hi"

    Note over A: user types "close"
    A->>S: "A dissconected"
    S->>B: "A dissconected"
    A--xS: socket closed
    S->>S: recv() returns b"", remove conn, close
```

## 5. Server Connection Lifecycle

```mermaid
stateDiagram-v2
    [*] --> Listening
    Listening --> Connected: accept()
    Connected --> Relaying: handler thread started
    Relaying --> Relaying: recv() data, broadcast to others
    Relaying --> CleanedUp: recv() returns empty / OSError
    CleanedUp --> [*]: remove from clients, close conn
    Listening --> ShuttingDown: KeyboardInterrupt
    ShuttingDown --> [*]: close all clients
```

## 6. Wire Protocol

Plain UTF-8 text. No framing, no headers.

| Event | Payload (sent by client, relayed verbatim) |
|---|---|
| Join | `<username> joined \n \n` |
| Message | `<username>: <text>\n` |
| Leave | `<username> dissconected \n` |

The server does not parse messages. It forwards raw bytes.

## 7. Configuration

Loaded from `.env` via `python-dotenv`.

| Variable | Used by | Default |
|---|---|---|
| `SERVER_HOST` | server | `127.0.0.1` |
| `SERVER_PORT` | server | `65432` |
| `CLIENT_HOST` | client | `127.0.0.1` |
| `CLIENT_PORT` | client | `65432` |

## 8. Known Limitations

| Area | Issue |
|---|---|
| Framing | TCP is a byte stream. `recv(2048)` may return partial or merged messages |
| Concurrency | `clients` list is mutated across threads without a lock |
| Identity | Server doesn't know usernames. Clients format messages, so spoofing is possible |
| Disconnects | Leave notice is client-sent. A crashed client is never announced |
| Backpressure | A slow client blocks broadcast (`sendall` is blocking) |
| UI | Incoming prints can interleave with the `input()` prompt |
| Scale | Thread-per-client doesn't scale to thousands of connections |

## 9. Target Architecture (Planned)

```mermaid
flowchart LR
    A[Client] -- "newline-framed<br/>messages" --> S
    subgraph S[Server]
        direction TB
        P[Parse + handshake]
        R[(conn → username map<br/>+ Lock)]
        B[Broadcast<br/>server-formatted]
        P --> R --> B
    end
    S -- "'X left' on disconnect" --> A
```

Planned changes, in order:

1. Newline framing with per-connection buffers.
2. Server-side usernames; server formats and broadcasts join/leave.
3. `threading.Lock` around `clients`.
4. Rewrite with `asyncio` streams or `selectors` for comparison.
5. JSON or length-prefixed protocol, then TLS.
