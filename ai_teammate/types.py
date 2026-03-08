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
    content: Optional[str] = Field(None, alias="response")
    response: Optional[str] = None
    agent_id: Optional[str] = None
    agent_name: Optional[str] = None
    tool_calls: List[ToolCall] = Field(default_factory=list)
    usage: Optional[Dict[str, int]] = None

    def __init__(self, **data: Any):
        # Normalize: accept both 'content' and 'response' fields
        if "response" in data and "content" not in data:
            data["content"] = data["response"]
        elif "content" in data and "response" not in data:
            data["response"] = data["content"]
        super().__init__(**data)

    class Config:
        extra = "ignore"
        populate_by_name = True


class AgentResponse(BaseModel):
    """Individual agent response in team chat"""
    agent_id: str
    agent_name: str
    content: str
    avatar_url: Optional[str] = None

    class Config:
        extra = "ignore"


class TeamChatResponse(BaseModel):
    """Team chat response with multiple agent responses"""
    responses: List[AgentResponse] = Field(default_factory=list)
    summary: Optional[str] = None
    mode: Optional[str] = None
    auto_selected: bool = False
    memory_saved: bool = False
    byok_error: Optional[str] = None

    @property
    def content(self) -> Optional[str]:
        """Get summary as content for convenience"""
        return self.summary

    class Config:
        extra = "ignore"


class StreamChunk(BaseModel):
    """Streaming chunk"""
    type: str  # text, tool_start, tool_end, error, done, meta, etc.
    content: Optional[str] = None
    tool: Optional[str] = None
    args: Optional[Dict[str, Any]] = None

    class Config:
        extra = "ignore"


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


class ShareLink(BaseModel):
    """Shared agent link"""
    id: str
    agent_id: str
    share_code: str
    share_url: Optional[str] = None
    include_memory: bool = False
    memory_sharing: Dict[str, Any] = Field(default_factory=dict)
    max_messages: int = 100
    require_end_user_auth: bool = True
    allow_file_upload: bool = False
    is_active: bool = True
    view_count: int = 0
    message_count: int = 0
    created_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None

    class Config:
        extra = "ignore"


class ShareAgentInfo(BaseModel):
    """Agent info returned from share info endpoint"""
    id: str
    name: str
    description: Optional[str] = None
    avatar_url: Optional[str] = None

    class Config:
        extra = "ignore"


class ShareSettings(BaseModel):
    """Share settings returned from share info endpoint"""
    max_messages: int = 100
    message_count: int = 0
    expires_at: Optional[str] = None
    require_end_user_auth: bool = False
    allow_file_upload: bool = False

    class Config:
        extra = "ignore"


class ShareInfo(BaseModel):
    """Public info about a shared agent"""
    agent: ShareAgentInfo
    share: ShareSettings

    class Config:
        extra = "ignore"


class Document(BaseModel):
    """Uploaded document"""
    id: str
    filename: str
    file_type: str
    file_size: int
    status: str = "processing"
    chunk_count: int = 0
    agent_id: Optional[str] = None

    class Config:
        extra = "ignore"


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
