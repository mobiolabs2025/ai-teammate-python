"""AI Teammate SDK Types"""

from datetime import datetime
from typing import Optional, List, Dict, Any, Literal
from pydantic import BaseModel, Field


class Agent(BaseModel):
    """AI Agent"""
    id: str
    name: str
    description: Optional[str] = None
    system_prompt: Optional[str] = None
    model: Optional[str] = None
    avatar_url: Optional[str] = None
    is_public: bool = False
    enabled_skills: List[str] = Field(default_factory=list)
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    class Config:
        extra = "ignore"


class AgentCreate(BaseModel):
    """Create agent request"""
    name: str
    description: Optional[str] = None
    system_prompt: Optional[str] = None
    model: Optional[str] = None
    is_public: bool = False


class AgentUpdate(BaseModel):
    """Update agent request"""
    name: Optional[str] = None
    description: Optional[str] = None
    system_prompt: Optional[str] = None
    model: Optional[str] = None
    is_public: Optional[bool] = None


class Team(BaseModel):
    """AI Team"""
    id: str
    name: str
    description: Optional[str] = None
    avatar_url: Optional[str] = None
    chat_mode: str = "auto"
    created_at: Optional[datetime] = None
    
    class Config:
        extra = "ignore"


class TeamCreate(BaseModel):
    """Create team request"""
    name: str
    description: Optional[str] = None
    chat_mode: str = "auto"


class Message(BaseModel):
    """Chat message"""
    role: Literal["user", "assistant", "system"]
    content: str
    timestamp: Optional[datetime] = None
    
    class Config:
        extra = "ignore"


class ToolCall(BaseModel):
    """Tool call in response"""
    name: str
    args: Dict[str, Any] = Field(default_factory=dict)
    result: Optional[str] = None


class ChatResponse(BaseModel):
    """Chat response"""
    content: str
    agent_id: Optional[str] = None
    agent_name: Optional[str] = None
    tool_calls: List[ToolCall] = Field(default_factory=list)
    usage: Optional[Dict[str, int]] = None
    
    class Config:
        extra = "ignore"


class StreamChunk(BaseModel):
    """Streaming chunk"""
    type: Literal["text", "tool_start", "tool_end", "error", "done"]
    content: Optional[str] = None
    tool: Optional[str] = None
    args: Optional[Dict[str, Any]] = None


class Memory(BaseModel):
    """Agent memory/bookmark"""
    id: str
    content: str
    category: Optional[str] = None
    url: Optional[str] = None
    tags: List[str] = Field(default_factory=list)
    created_at: Optional[datetime] = None
    
    class Config:
        extra = "ignore"


class MemoryCreate(BaseModel):
    """Create memory request"""
    content: str
    category: Optional[str] = None
    url: Optional[str] = None
    tags: List[str] = Field(default_factory=list)


class Skill(BaseModel):
    """Available skill"""
    id: str
    name: str
    description: Optional[str] = None
    is_enabled: bool = False
    
    class Config:
        extra = "ignore"


class PaginatedResponse(BaseModel):
    """Paginated list response"""
    items: List[Any]
    total: int
    page: int = 1
    per_page: int = 20
    has_more: bool = False
