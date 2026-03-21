# AI Teammate Python SDK

Official Python SDK for [AI Teammate](https://ai-teammate.net) - Build and deploy AI agents with ease.

> **v0.3.1** — End-User authentication, Google OAuth, agent documents (RAG)

## Installation

```bash
pip install ai-teammate
```

## Getting Started

### Step 1: Sign Up
1. Go to [ai-teammate.net](https://ai-teammate.net)
2. Sign up with Google or Kakao

### Step 2: Get API Key
1. Go to **Settings** (top-right)
2. Select **API Keys** tab
3. Click **Generate New Key**
4. Copy the key (`at_xxxx...` format)

> API keys are shown only once. Store it securely!

### Step 3: Install & Create Your First Agent

```bash
pip install ai-teammate
```

```python
from ai_teammate import AITeammate

client = AITeammate(api_key="at_your_key_here")

# Create an agent
agent = client.agents.create(
    name="My First Agent",
    system_prompt="You are a helpful assistant that speaks Korean.",
)
print(f"Agent created: {agent.id}")

# Chat with the agent
response = client.chat("Hello!", agent_id=agent.id)
print(response.content)
```

### Step 4: Check on Portal
Agents created via SDK appear on the [portal dashboard](https://ai-teammate.net).

---

## Features

### Agent Management

```python
# List all agents
agents = client.agents.list()

# Create an agent
agent = client.agents.create(
    name="My Assistant",
    system_prompt="You are a helpful assistant.",
)

# Update an agent
agent = client.agents.update(
    agent_id="abc123",
    name="Updated Name",
    system_prompt="New prompt",
)

# Delete an agent
client.agents.delete("abc123")
```

### Agent Documents (Shared RAG Knowledge)

Upload documents directly to an agent. These become shared knowledge available to **all users** chatting with the agent (via direct chat or share links).

```python
# Upload a document (pdf, txt, md, docx, csv)
doc = client.agents.upload_document("abc123", "./menu.txt")
print(f"Uploaded: {doc.filename} ({doc.chunk_count} chunks)")

# List documents
docs = client.agents.list_documents("abc123")
for d in docs:
    print(f"{d.filename} ({d.chunk_count} chunks)")

# Delete a document
client.agents.delete_document("abc123", doc.id)
```

> **Agent documents vs Share documents**: Agent documents (`agents.upload_document`) are shared knowledge for all users. Share documents (`shares.upload_document`) are per-user uploads scoped to a share link session.

### Chat

```python
# Simple chat
response = client.chat("What's the weather?", agent_id="abc123")
print(response.content)

# Streaming chat
for chunk in client.chat_stream("Tell me a story", agent_id="abc123"):
    if chunk.type == "text":
        print(chunk.content, end="", flush=True)

# Conversation context
context = []
response = client.chat("My name is Alice", agent_id="abc123")
context.append({"role": "user", "content": "My name is Alice"})
context.append({"role": "assistant", "content": response.content})

response = client.chat("What's my name?", agent_id="abc123", context=context)
print(response.content)  # "Alice"
```

### Team Chat

```python
# Create a team
team = client.teams.create(
    name="Dream Team",
    chat_mode="brainstorm",  # auto, round_robin, parallel, debate, brainstorm, expert
)

# Add agents to team
client.teams.add_agent(team.id, "agent_1")
client.teams.add_agent(team.id, "agent_2")

# Team chat (multi-agent discussion)
response = client.teams.chat(team.id, "Brainstorm startup ideas!")
print(response.summary)

for r in response.responses:
    print(f"[{r.agent_name}] {r.content}")
```

#### Team Chat Modes

| Mode | Description |
|------|-------------|
| `round-robin` | Agents respond sequentially, referencing previous opinions |
| `parallel` | All agents respond independently |
| `debate` | Pro/con discussion between agents |
| `brainstorm` | Idea generation with voting |
| `expert` | Auto-selects the best agent for the question |

### Share Links

Share your agent with external users via a link. Supports end-user authentication, file upload, and document-based RAG chat.

```python
# Create a share link
share = client.shares.create(
    agent_id="abc123",
    require_sign_in=True,       # Require end-user authentication
    allow_file_upload=True,     # Allow visitors to upload documents
    include_memory=False,       # Share agent memory with visitors
    max_messages=100,           # Message limit (0 = unlimited)
    expires_in_days=30,         # Link expiration (None = permanent)
)
print(f"Share URL: https://ai-teammate.net{share.share_url}")

# Get share info
info = client.shares.get_info(share.share_code)
print(f"Agent: {info.agent.name}")
print(f"File upload: {info.share.allow_file_upload}")

# Chat via share link
response = client.shares.chat(share.share_code, "Hello!")
print(response.content)

# Upload a document (triggers RAG indexing)
doc = client.shares.upload_document(share.share_code, "./report.pdf")
print(f"Uploaded: {doc.filename} ({doc.chunk_count} chunks)")

# Chat about the document (RAG search)
response = client.shares.chat(share.share_code, "Summarize the report")
print(response.content)  # Agent answers using uploaded document

# List / delete share links
shares = client.shares.list("abc123")
client.shares.delete("abc123", share.id)
```

#### Full Flow: Create Agent → Share → Upload → RAG Chat

```python
from ai_teammate import AITeammate

client = AITeammate(api_key="at_your_api_key")

# 1. Create an agent
agent = client.agents.create(
    name="Customer Support Bot",
    system_prompt="You are a friendly customer support agent.",
)

# 2. Create a share link
share = client.shares.create(
    agent_id=agent.id,
    allow_file_upload=True,
    require_sign_in=False,
    max_messages=100,
)
print(f"Share URL: https://ai-teammate.net{share.share_url}")

# 3. Upload FAQ document
doc = client.shares.upload_document(share.share_code, "./faq.pdf")
print(f"Indexed: {doc.chunk_count} chunks")

# 4. Chat — agent answers using the uploaded document
response = client.shares.chat(share.share_code, "What is the refund policy?")
print(response.content)
```

### End-User Authentication

When a share link has `require_sign_in=True`, visitors must register and log in. The SDK provides a complete end-user auth flow.

#### Email Registration

```python
# 1. Register (sends verification code to email)
result = client.end_users.register(
    agent_id="abc123",
    name="John",
    email="john@example.com",
)

# 2. Verify email with code
result = client.end_users.verify(
    agent_id="abc123",
    email="john@example.com",
    code="123456",
)

# 3. Set password → get auth token
auth = client.end_users.set_password(
    agent_id="abc123",
    email="john@example.com",
    password="secure_password",
)
token = auth.token

# 4. Chat with end-user token
response = client.shares.chat(share_code, "Hello!", end_user_token=token)
```

#### Login

```python
auth = client.end_users.login(
    agent_id="abc123",
    email="john@example.com",
    password="secure_password",
)
token = auth.token
```

#### Google OAuth

```python
# Get Google OAuth URL
result = client.end_users.google_auth_url(
    agent_id="abc123",
    source="my-app",
    return_url="https://myapp.com/callback",
)
print(result["url"])  # Redirect user to this URL

# Exchange code for token (in your callback handler)
auth = client.end_users.google_callback(
    agent_id="abc123",
    code="google_auth_code",
)
token = auth.token
print(f"New user: {auth.is_new}")
```

#### Token Validation & Password Reset

```python
# Validate token
result = client.end_users.validate(agent_id="abc123", token=token)
print(f"Valid: {result.valid}, User: {result.end_user.name}")

# Forgot password (sends reset code)
client.end_users.forgot_password(agent_id="abc123", email="john@example.com")
```

### Memories

```python
# Add memory to agent
memory = client.memories.create(
    agent_id="abc123",
    content="User prefers concise responses",
    category="preferences",
)

# List memories
memories = client.memories.list(agent_id="abc123")

# Search memories
results = client.memories.search(agent_id="abc123", query="preferences")
```

## API Key Types

| Type | Issued From | Scope |
|------|------------|-------|
| **Global** | Settings page | All operations |
| **Agent-scoped** | Agent settings | Chat, read, memory for that agent only |
| **Team-scoped** | Team settings | Chat, read for that team only |

> Agent/Team scoped keys are useful for embedding agents in external apps with restricted access.

## Async Support

All methods have async versions prefixed with `a`:

```python
import asyncio

async def main():
    async with AITeammate(api_key="at_xxx") as client:
        # Async chat
        response = await client.achat("Hello!", agent_id="abc123")

        # Async streaming
        async for chunk in client.achat_stream("Tell me a story", agent_id="abc123"):
            print(chunk.content, end="")

asyncio.run(main())
```

## Error Handling

```python
from ai_teammate import (
    AITeammateError,
    AuthenticationError,
    RateLimitError,
    NotFoundError,
)

try:
    response = client.chat("Hello!", agent_id="invalid_id")
except NotFoundError as e:
    print(f"Agent not found: {e}")
except RateLimitError as e:
    print(f"Rate limited. Retry after {e.retry_after} seconds")
except AuthenticationError as e:
    print(f"Invalid API key: {e}")
except AITeammateError as e:
    print(f"Error: {e}")
```

## Configuration

```python
client = AITeammate(
    api_key="at_xxx",
    base_url="https://ai-teammate.net/api",  # Custom API URL
    timeout=30.0,  # Request timeout in seconds
)
```

## API Reference

### Client Methods

| Method | Description |
|--------|-------------|
| `chat(message, agent_id)` | Chat with an agent |
| `chat_stream(message, agent_id)` | Stream chat response |
| `achat(message, agent_id)` | Async chat |
| `achat_stream(message, agent_id)` | Async stream |

### Resources

| Resource | Methods |
|----------|---------|
| `agents` | `list`, `get`, `create`, `update`, `delete`, `upload_document`, `list_documents`, `delete_document` |
| `teams` | `list`, `get`, `create`, `delete`, `add_agent`, `remove_agent`, `list_agents`, `chat` |
| `memories` | `list`, `get`, `create`, `delete`, `search` |
| `shares` | `create`, `list`, `delete`, `get_info`, `chat`, `upload_document`, `get_history` |
| `end_users` | `register`, `verify`, `set_password`, `login`, `validate`, `forgot_password`, `google_auth_url`, `google_callback` |

## License

MIT License - see [LICENSE](LICENSE) for details.

## Links

- [AI Teammate Platform](https://ai-teammate.net)
- [API Documentation](https://ai-teammate.net/docs)
- [PyPI Package](https://pypi.org/project/ai-teammate/)
- [Issue Tracker](https://github.com/mobiolabs2025/ai-teammate-python/issues)
