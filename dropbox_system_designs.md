### Production System Workflows

#### Complete File Sync Workflow
```
Client A                API Gateway        Auth Service      Metadata Service    Storage Service    Sync Engine       Client B
   |                         |                    |                |                   |                |               |
   |-- File Modified ------->|                    |                |                   |                |               |
   |                         |-- Validate Auth -->|                |                   |                |               |
   |                         |<-- Token Valid ----|                |                   |                |               |
   |                         |-- Get File Meta ---|--------------->|                   |                |               |
   |                         |<-- Metadata -------|<---------------|                   |                |               |
   |                         |-- Calculate Delta--|----------------|------------------>|                |               |
   |                         |<-- Delta Info -----|<---------------|<------------------|                |               |
   |                         |-- Queue Sync ------|----------------|-------------------|--------------->|               |
   |<-- Upload Started ------|                    |                |                   |                |               |
   |                         |                    |                |                   |                |-- Notify ---->|
   |                         |                    |                |                   |                |               |-- Download Delta
   |-- Upload Delta -------->|-- Store Delta -----|----------------|------------------>|                |               |
   |<-- Upload Complete -----|<-- Stored ---------|<---------------|<------------------|                |               |
   |                         |-- Update Meta -----|--------------->|                   |                |               |
   |                         |<-- Updated --------|<---------------|                   |                |               |
   |                         |-- Sync Complete ---|----------------|-------------------|--------------->|               |
   |                         |                    |                |                   |                |<-- Confirm ---|
```

#### Conflict Resolution Workflow
```
Client A        Conflict Service      Version Service       Notification Service     Client B
   |                   |                     |                       |                  |
   |-- Upload v1 ----->|                     |                       |                  |
   |                   |<-- Upload v2 -------|-----------------------|------------------| 
   |                   |                     |                       |                  |
   |                   |-- Detect Conflict --|                       |                  |
   |                   |-- Analyze Changes -->|                      |                  |
   |                   |<-- Analysis --------|                      |                  |
   |                   |-- Create Version -->|                      |                  |
   |                   |<-- Version Created -|                      |                  |
   |                   |-- Notify Users -----|--------------------->|                  |
   |<-- Conflict Alert-|                     |                      |-- Alert ------->|
   |                   |                     |                      |                  |
   |-- Resolution Choice >|                  |                      |                  |
   |                   |-- Apply Resolution ->|                     |                  |
   |                   |<-- Resolution Applied|                     |                  |
   |<-- Final Version --|-- Sync Final -------|----------------------|-- Final Version->|
```

#### End-to-End Encryption Workflow
```
Client A          Encryption Service    Key Management      Storage Service      Client B
   |                      |                    |                   |                |
   |-- Generate FEK ----->|                    |                   |                |
   |<-- FEK Generated ----|                    |                   |                |
   |-- Encrypt File ----->|                    |                   |                |
   |<-- Encrypted File ---|                    |                   |                |
   |-- Get User B Key ----|------------------>|                   |                |
   |<-- Public Key -------|<------------------|                   |                |
   |-- Encrypt FEK ------>|                    |                   |                |
   |<-- Encrypted FEK ----|                    |                   |                |
   |-- Store File --------|--------------------|------------------->|                |
   |<-- Stored ------------|<------------------|<------------------|                |
   |                      |                    |                   |-- Notify ----->|
   |                      |                    |                   |                |-- Get File
   |                      |                    |                   |<-- File Data --|
   |                      |<-- Decrypt FEK ----|-------------------|                |
   |                      |-- Decrypt File --->|                   |                |
   |                      |<-- Plaintext ------|                   |                |
```

#### Real-time Collaboration Workflow
```
User A           WebSocket Gateway      OT Service       State Manager       User B
   |                     |                 |               |                 |
   |-- Edit Text ------->|                 |               |                 |
   |                     |-- Transform --->|               |                 |
   |                     |<-- Operation ---|               |                 |
   |                     |-- Update State--|-------------->|                 |
   |                     |<-- State OK ----|<--------------|                 |
   |                     |-- Broadcast ----|---------------|---------------->|
   |<-- Ack -------------|                 |               |                 |-- Apply Change
   |                     |                 |               |                 |
   |                     |<-- Edit Text ---|---------------|<----------------|
   |                     |-- Transform --->|               |                 |
   |                     |<-- Operation ---|               |                 |
   |-- Apply Change <----|-- Send Change --|               |                 |
```

### Implementation Roadmap

#### Phase 1: Foundation (Months 1-3)
**Sprint 1-2: Core Infrastructure**
- Set up Kubernetes cluster and CI/CD pipeline
- Implement Authentication Service with JWT
- Create basic API Gateway with rate limiting
- Set up PostgreSQL cluster and Redis cache
- Basic file upload/download functionality

**Sprint 3-4: Basic Sync**
- Implement File Watcher Service with WebSocket
- Create Metadata Service for file tracking
- Basic Storage Service with local file system
- Simple sync engine with polling mechanism
- Basic web client interface

**Sprint 5-6: MVP Features**
- User registration and login system
- File sharing capabilities
- Basic conflict resolution (last-write-wins)
-# Dropbox-like System Designs

## Design 1: Minimal Viable System (MVP)

### Detailed Component Breakdown

### Architecture Overview
```
[Client A] ←→ [Server] ←→ [Client B]
```

#### Server Components

##### 1. File Watcher API
**Purpose**: Track and manage file system events from clients
**Tasks**:
- **Event Reception**: Receive file change notifications from clients via REST API
- **Event Validation**: Validate incoming events (file exists, user permissions, size limits)
- **Event Storage**: Store events in SQLite database with timestamps
- **Event Broadcasting**: Notify other connected clients about changes
- **Rate Limiting**: Prevent spam by limiting events per user per minute

**Implementation Details**:
```javascript
// Event Structure
{
  user_id: "user123",
  file_path: "/documents/file.txt",
  event_type: "create|modify|delete|move",
  timestamp: "2025-06-26T12:00:00Z",
  file_hash: "sha256hash",
  file_size: 1024
}
```

**Database Schema**:
```sql
CREATE TABLE file_events (
  id INTEGER PRIMARY KEY,
  user_id TEXT NOT NULL,
  file_path TEXT NOT NULL,
  event_type TEXT NOT NULL,
  timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
  file_hash TEXT,
  file_size INTEGER,
  processed BOOLEAN DEFAULT FALSE
);
```

##### 2. Basic Storage Manager
**Purpose**: Handle file storage and retrieval operations
**Tasks**:
- **File Upload**: Accept multipart file uploads, validate file types and sizes
- **File Storage**: Save files to disk with organized directory structure
- **File Retrieval**: Serve files to authorized clients
- **Metadata Tracking**: Store file metadata (size, type, creation date)
- **Cleanup Operations**: Remove orphaned files and temporary uploads

**Implementation Details**:
```
Storage Structure:
/storage/
  ├── users/
  │   ├── user123/
  │   │   ├── documents/
  │   │   │   └── file.txt
  │   │   └── images/
  │   └── user456/
  ├── temp/
  │   └── uploads/
  └── metadata/
      └── file_metadata.db
```

**File Operations**:
- Upload: `POST /api/files/upload` with multipart form data
- Download: `GET /api/files/{user_id}/{file_path}`
- Delete: `DELETE /api/files/{user_id}/{file_path}`
- List: `GET /api/files/{user_id}?path=/folder`

##### 3. Simple Sync Engine
**Purpose**: Synchronize files between clients
**Tasks**:
- **Change Detection**: Compare local and remote file states
- **Sync Queue Management**: Queue files that need synchronization
- **File Transfer**: Upload/download files between clients and server
- **Progress Tracking**: Monitor sync progress and report to clients
- **Error Handling**: Retry failed transfers with exponential backoff

**Sync Algorithm**:
```
1. Client requests sync status: GET /api/sync/status
2. Server returns list of changed files since last sync
3. Client compares with local files
4. Client uploads new/modified files
5. Client downloads remote changes
6. Update sync timestamp
```

**Sync State Tracking**:
```sql
CREATE TABLE sync_state (
  user_id TEXT PRIMARY KEY,
  last_sync_timestamp DATETIME,
  sync_in_progress BOOLEAN DEFAULT FALSE,
  pending_uploads INTEGER DEFAULT 0,
  pending_downloads INTEGER DEFAULT 0
);
```

##### 4. Basic Conflict Resolution
**Purpose**: Handle conflicts when same file is modified on multiple clients
**Tasks**:
- **Conflict Detection**: Compare file timestamps and hashes
- **Conflict Resolution**: Apply last-write-wins or create conflict copies
- **User Notification**: Inform users about conflicts
- **Conflict History**: Track resolved conflicts for auditing

**Conflict Resolution Logic**:
```
1. Detect conflict: same file modified on different clients
2. Compare timestamps
3. If within 5 minutes: create conflict copy
4. Rename older version: "file_conflict_2025-06-26_12-00-00.txt"
5. Keep newer version as main file
6. Notify both clients
```

#### Client Components

##### 1. File System Monitor
**Purpose**: Watch local file system for changes
**Tasks**:
- **Directory Watching**: Monitor specified folders for changes
- **Event Filtering**: Filter out temporary files and system files
- **Batch Processing**: Group rapid changes to avoid spam
- **Network Communication**: Send events to server via HTTP
- **Retry Logic**: Handle network failures with retry mechanism

**Implementation Details**:
```python
# Pseudo-code for file watcher
import watchdog

class FileWatcher:
    def __init__(self, watch_path, server_url):
        self.watch_path = watch_path
        self.server_url = server_url
        self.event_queue = []
        
    def on_file_created(self, file_path):
        self.queue_event("create", file_path)
        
    def on_file_modified(self, file_path):
        self.queue_event("modify", file_path)
        
    def on_file_deleted(self, file_path):
        self.queue_event("delete", file_path)
        
    def queue_event(self, event_type, file_path):
        event = {
            "type": event_type,
            "path": file_path,
            "timestamp": datetime.now(),
            "hash": calculate_hash(file_path) if event_type != "delete" else None
        }
        self.event_queue.append(event)
        
    def flush_events(self):
        # Send batched events to server
        requests.post(f"{self.server_url}/api/events", json=self.event_queue)
        self.event_queue.clear()
```

##### 2. Basic Sync Client
**Purpose**: Synchronize local files with server
**Tasks**:
- **Periodic Sync**: Check for changes every 30 seconds
- **File Comparison**: Compare local files with server state
- **Upload/Download**: Transfer files to/from server
- **Local State Management**: Track sync state in local database
- **User Interface**: Show sync progress and status

**Sync Process**:
```
1. Compare local file timestamps with server
2. Identify files to upload (newer locally)
3. Identify files to download (newer on server)
4. Execute uploads first, then downloads
5. Update local sync state
6. Handle any conflicts
```

### MVP Workflow Diagrams

#### File Upload Workflow
```
Client A                    Server                    Client B
   |                         |                         |
   |-- File Created -------->|                         |
   |                         |-- Store File ---------->|
   |                         |-- Update Database ---->|
   |                         |-- Notify Client B ---->|
   |                         |                         |-- Download File
   |<-- Upload Complete -----|                         |
   |                         |<-- Download Complete ---|
```

#### Sync Workflow
```
Client                      Server
   |                         |
   |-- GET /sync/status ---->|
   |<-- Changed Files -------|
   |                         |
   |-- Upload New Files ---->|
   |<-- Upload Complete -----|
   |                         |
   |-- Download Changes ---->|
   |<-- Files Downloaded ----|
   |                         |
   |-- Update Sync State --->|
   |<-- Sync Complete -------|
```

#### Conflict Resolution Workflow
```
Client A        Server        Client B
   |              |              |
   |-- Upload v1--|              |
   |              |--Upload v2 --|
   |              |              |
   |              |-- Detect Conflict
   |              |-- Rename v1 to conflict
   |              |-- Keep v2 as main
   |              |              |
   |<-- Notify ---|-- Notify --->|
   |              |              |
   |-- Download --|-- Download --|
   |    Conflict  |    Latest    |
```

### Tech Stack
- **Backend**: Node.js/Express or Python/Flask
- **Database**: SQLite for metadata
- **Storage**: Local filesystem
- **Protocol**: HTTP/HTTPS
- **Client**: Python/Node.js scripts

### Key Limitations
- No encryption
- No versioning
- Basic conflict resolution
- Single server (no scaling)
- No offline support
- No delta sync

---

## Design 2: Full Production System

### Architecture Overview
```
[Client A] ←→ [Load Balancer] ←→ [API Gateway] ←→ [Microservices] ←→ [Storage Layer]
                                                        ↓
[Client B] ←→ [CDN/Cache] ←→ [Message Queue] ←→ [Database Cluster]
```

### Core Microservices

#### 1. **Authentication Service**
```
Components:
- JWT token management
- OAuth integration
- User session handling
- API key management

Database: PostgreSQL (user credentials, sessions)
```

#### 2. **File Watcher Service**
```
Components:
- Real-time file system monitoring
- Event aggregation and deduplication
- Change detection algorithms
- WebSocket connections for real-time updates

Tech Stack:
- WebSocket servers (Socket.io/WebSockets)
- Redis for real-time event streaming
- Event sourcing pattern
```

#### 3. **Metadata Service**
```
Components:
- File metadata management
- Folder structure tracking
- Permission management
- Sharing and collaboration settings

Database: PostgreSQL with JSONB for flexible metadata
Cache: Redis for frequently accessed metadata
```

#### 4. **Storage Service**
```
Components:
- Multi-tier storage (hot/warm/cold)
- Content-addressable storage
- Deduplication at block level
- Compression algorithms

Storage Backend:
- Primary: Amazon S3/Google Cloud Storage
- Cache: Redis/Memcached
- CDN: CloudFront/CloudFlare for global distribution
```

#### 5. **Sync Engine Service**
```
Components:
- Delta sync algorithms (rsync-like)
- Change propagation logic
- Sync queue management
- Bandwidth optimization

Message Queue: Apache Kafka/RabbitMQ
Algorithms: Binary diff, block-level sync
```

#### 6. **Version Control Service**
```
Components:
- Git-like versioning system
- Snapshot management
- History tracking
- Rollback capabilities

Database: PostgreSQL for version metadata
Storage: Separate versioned storage backend
```

#### 7. **Conflict Resolution Service**
```
Components:
- Conflict detection algorithms
- Resolution strategies (auto/manual)
- Merge capabilities for text files
- User notification system

Strategies:
- Operational Transform for real-time collaboration
- Three-way merge for offline conflicts
- User-defined resolution policies
```

#### 8. **Encryption Service**
```
Components:
- End-to-end encryption key management
- Client-side encryption/decryption
- Key rotation and recovery
- Zero-knowledge architecture

Security:
- AES-256 for file encryption
- RSA/ECDH for key exchange
- Hardware Security Modules (HSM)
```

### Advanced Features

#### Real-time Collaboration
```
Components:
- Operational Transform (OT) algorithms
- Conflict-free Replicated Data Types (CRDTs)
- Real-time cursor tracking
- Live editing sessions

Tech: WebRTC for peer-to-peer, WebSockets for server relay
```

#### Offline Support
```
Components:
- Local change tracking
- Conflict queue management
- Sync prioritization
- Background sync

Storage: Local SQLite database for offline state
```

#### Performance Optimizations
```
Components:
- Block-level deduplication
- Intelligent prefetching
- Adaptive sync algorithms
- Bandwidth throttling

Techniques:
- Content-defined chunking
- Bloom filters for deduplication
- Machine learning for usage prediction
```

### Infrastructure Design

#### Database Architecture
```
Primary Database: PostgreSQL Cluster
- Master-slave replication
- Read replicas for scaling
- Connection pooling

Caching Layer:
- Redis Cluster for session data
- Memcached for file metadata
- CDN for static content

Message Queue:
- Apache Kafka for event streaming
- RabbitMQ for service communication
- Dead letter queues for error handling
```

#### Deployment Architecture
```
Container Orchestration: Kubernetes
- Microservices in separate pods
- Auto-scaling based on load
- Service mesh (Istio) for communication

Monitoring:
- Prometheus + Grafana for metrics
- ELK stack for logging
- Distributed tracing (Jaeger)

CI/CD:
- GitLab CI/CD or GitHub Actions
- Blue-green deployments
- Automated testing pipeline
```

### Security Architecture

#### End-to-End Encryption Flow
```
1. Client generates file encryption key
2. File encrypted locally with AES-256
3. Encryption key encrypted with user's public key
4. Encrypted file + encrypted key sent to server
5. Server stores without access to plaintext
6. Other clients decrypt key with private key
7. Use decrypted key to decrypt file
```

#### Zero-Knowledge Architecture
```
- Server never sees unencrypted content
- Client-side key derivation
- Secure key sharing between devices
- Key recovery through secure questions/backup keys
```

### API Design

#### REST APIs
```
Authentication:
POST /auth/login
POST /auth/refresh
DELETE /auth/logout

Files:
GET /files/{path}
POST /files/{path}
PUT /files/{path}
DELETE /files/{path}

Sync:
GET /sync/changes?since={timestamp}
POST /sync/upload
GET /sync/download/{file_id}

Versions:
GET /files/{path}/versions
POST /files/{path}/restore/{version}
```

#### WebSocket Events
```
file:created
file:modified
file:deleted
file:moved
sync:started
sync:completed
conflict:detected
```

### Scalability Considerations

#### Horizontal Scaling
- Stateless microservices
- Database sharding by user ID
- CDN for global file distribution
- Load balancing with sticky sessions for WebSocket

#### Performance Targets
- < 100ms API response time
- < 5s sync time for small files
- 99.9% uptime SLA
- Support for 1M+ concurrent users

### Implementation Phases

#### Phase 1 (Months 1-3)
- Core file upload/download
- Basic sync functionality
- User authentication
- Simple web interface

#### Phase 2 (Months 4-6)
- Real-time sync
- Conflict resolution
- Mobile apps
- Sharing features

#### Phase 3 (Months 7-9)
- End-to-end encryption
- Version control
- Advanced collaboration
- Performance optimization

#### Phase 4 (Months 10-12)
- Enterprise features
- Advanced analytics
- Machine learning features
- Global scaling