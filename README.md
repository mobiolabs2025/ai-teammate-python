# AI Teammate Python SDK

Official Python SDK for [AI Teammate](https://agent.mobiolabs.net) - Build and deploy AI agents with ease.

## Installation

```bash
pip install ai-teammate
```

## 🚀 Getting Started

### Step 1: 회원가입
1. [agent.mobiolabs.net](https://agent.mobiolabs.net) 접속
2. Google 또는 Kakao로 간편 가입

### Step 2: API 키 발급
1. 로그인 후 우측 상단 **Settings** 클릭
2. **API Keys** 탭 선택
3. **Generate New Key** 클릭
4. 생성된 키 복사 (`at_xxxx...` 형식)

> ⚠️ API 키는 한 번만 표시됩니다. 안전한 곳에 보관하세요!

### Step 3: SDK 설치 & 첫 에이전트 만들기

```bash
pip install ai-teammate
```

```python
from ai_teammate import AITeammate

# API 키로 클라이언트 초기화
client = AITeammate(api_key="at_your_key_here")

# 첫 에이전트 만들기
agent = client.agents.create(
    name="My First Agent",
    system_prompt="You are a helpful assistant that speaks Korean.",
)
print(f"✅ 에이전트 생성 완료! ID: {agent.id}")

# 에이전트와 대화
response = client.chat("안녕하세요!", agent_id=agent.id)
print(f"🤖 {response.content}")
```

### Step 4: 포털에서 확인
SDK로 생성한 에이전트는 [포털 대시보드](https://agent.mobiolabs.net)에서 확인하고 관리할 수 있습니다.

---

## Quick Start

```python
from ai_teammate import AITeammate

# Initialize client
client = AITeammate(api_key="at_your_api_key")

# Chat with an agent
response = client.chat("Hello!", agent_id="your_agent_id")
print(response.content)
```

## Features

### 🤖 Agent Management

```python
# List all agents
agents = client.agents.list()

# Create an agent
agent = client.agents.create(
    name="My Assistant",
    system_prompt="You are a helpful assistant.",
    model="claude-3-sonnet",
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

### 💬 Chat

```python
# Simple chat
response = client.chat("What's the weather?", agent_id="abc123")
print(response.content)

# Streaming chat
for chunk in client.chat_stream("Tell me a story", agent_id="abc123"):
    if chunk.type == "text":
        print(chunk.content, end="", flush=True)
```

### 👥 Team Chat

```python
# Create a team
team = client.teams.create(
    name="Dream Team",
    chat_mode="brainstorm",  # auto, round_robin, parallel, debate, brainstorm, expert
)

# Add agents to team
client.teams.add_agent(team.id, "agent_1")
client.teams.add_agent(team.id, "agent_2")

# Team chat
response = client.teams.chat(team.id, "Brainstorm startup ideas!")
print(response.content)
```

### 🧠 Memories

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
    base_url="https://agent.mobiolabs.net/api",  # Custom API URL
    timeout=30.0,  # Request timeout
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
| `agents` | `list`, `get`, `create`, `update`, `delete`, `chat` |
| `teams` | `list`, `get`, `create`, `delete`, `add_agent`, `remove_agent`, `chat` |
| `memories` | `list`, `get`, `create`, `delete`, `search` |

## License

MIT License - see [LICENSE](LICENSE) for details.

## Links

- 🌐 [AI Teammate Platform](https://agent.mobiolabs.net)
- 📚 [API Documentation](https://agent.mobiolabs.net/docs)
- 🐛 [Issue Tracker](https://github.com/mobiolabs2025/ai-teammate-python/issues)
