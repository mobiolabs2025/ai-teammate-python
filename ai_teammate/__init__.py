"""
AI Teammate Python SDK

Build and deploy AI agents with ease.

Usage:
    from ai_teammate import AITeammate
    
    client = AITeammate(api_key="at_xxx")
    response = client.chat("Hello!", agent_id="abc123")
"""

from .client import AITeammate
from .exceptions import (
    AITeammateError,
    AuthenticationError,
    RateLimitError,
    NotFoundError,
    ValidationError,
)
from .types import (
    Agent,
    Team,
    Message,
    ChatResponse,
    TeamChatResponse,
    AgentResponse,
    Memory,
    ShareLink,
    ShareInfo,
    Document,
)

__version__ = "0.2.0"
__all__ = [
    "AITeammate",
    "AITeammateError",
    "AuthenticationError",
    "RateLimitError",
    "NotFoundError",
    "ValidationError",
    "Agent",
    "Team",
    "Message",
    "ChatResponse",
    "TeamChatResponse",
    "AgentResponse",
    "Memory",
    "ShareLink",
    "ShareInfo",
    "Document",
]
