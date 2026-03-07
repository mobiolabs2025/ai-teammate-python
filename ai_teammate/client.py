"""AI Teammate SDK Client"""

from typing import Optional, Iterator, AsyncIterator
import httpx

from .exceptions import (
    AITeammateError,
    AuthenticationError,
    RateLimitError,
    NotFoundError,
    ValidationError,
    ServerError,
)
from .resources.agents import AgentsResource
from .resources.teams import TeamsResource
from .resources.memories import MemoriesResource


DEFAULT_BASE_URL = "https://ai-teammate.net/api"
DEFAULT_TIMEOUT = 30.0


class AITeammate:
    """
    AI Teammate Python SDK Client
    
    Usage:
        client = AITeammate(api_key="at_xxx")
        
        # Chat with an agent
        response = client.chat("Hello!", agent_id="abc123")
        print(response.content)
        
        # Stream chat
        for chunk in client.chat_stream("Tell me a story", agent_id="abc123"):
            print(chunk.content, end="", flush=True)
        
        # Manage agents
        agents = client.agents.list()
        agent = client.agents.create(name="My Agent", system_prompt="You are helpful.")
        
        # Team chat
        response = client.teams.chat("Brainstorm ideas", team_id="xyz")
    """
    
    def __init__(
        self,
        api_key: str,
        base_url: str = DEFAULT_BASE_URL,
        timeout: float = DEFAULT_TIMEOUT,
    ):
        """
        Initialize AI Teammate client.
        
        Args:
            api_key: Your AI Teammate API key (starts with 'at_')
            base_url: API base URL (default: https://ai-teammate.net/api)
            timeout: Request timeout in seconds
        """
        if not api_key:
            raise AuthenticationError("API key is required")
        
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        
        # HTTP clients
        self._client = httpx.Client(
            base_url=self.base_url,
            headers=self._default_headers(),
            timeout=timeout,
        )
        self._async_client: Optional[httpx.AsyncClient] = None
        
        # Resources
        self.agents = AgentsResource(self)
        self.teams = TeamsResource(self)
        self.memories = MemoriesResource(self)
    
    def _default_headers(self) -> dict:
        """Default request headers"""
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "User-Agent": "ai-teammate-python/0.1.0",
        }
    
    def _get_async_client(self) -> httpx.AsyncClient:
        """Get or create async client"""
        if self._async_client is None:
            self._async_client = httpx.AsyncClient(
                base_url=self.base_url,
                headers=self._default_headers(),
                timeout=self.timeout,
            )
        return self._async_client
    
    def _handle_response(self, response: httpx.Response) -> dict:
        """Handle API response and raise appropriate exceptions"""
        if response.status_code == 200:
            return response.json()
        
        try:
            error_data = response.json()
            message = error_data.get("detail", error_data.get("message", "Unknown error"))
        except Exception:
            message = response.text or "Unknown error"
        
        if response.status_code == 401:
            raise AuthenticationError(message, status_code=401)
        elif response.status_code == 403:
            raise AuthenticationError(message, status_code=403)
        elif response.status_code == 404:
            raise NotFoundError(message)
        elif response.status_code == 422:
            raise ValidationError(message)
        elif response.status_code == 429:
            retry_after = response.headers.get("Retry-After")
            raise RateLimitError(
                message,
                retry_after=int(retry_after) if retry_after else None
            )
        elif response.status_code >= 500:
            raise ServerError(message, status_code=response.status_code)
        else:
            raise AITeammateError(message, status_code=response.status_code)
    
    def request(
        self,
        method: str,
        path: str,
        **kwargs,
    ) -> dict:
        """Make a synchronous API request"""
        response = self._client.request(method, path, **kwargs)
        return self._handle_response(response)
    
    async def arequest(
        self,
        method: str,
        path: str,
        **kwargs,
    ) -> dict:
        """Make an asynchronous API request"""
        client = self._get_async_client()
        response = await client.request(method, path, **kwargs)
        return self._handle_response(response)
    
    def chat(
        self,
        message: str,
        agent_id: str,
        context: Optional[list] = None,
    ) -> "ChatResponse":
        """
        Send a chat message to an agent.
        
        Args:
            message: The message to send
            agent_id: The agent ID to chat with
            context: Optional conversation context (list of previous messages)
        
        Returns:
            ChatResponse with the agent's reply
        """
        from .types import ChatResponse
        
        data = {
            "message": message,
            "agent_id": agent_id,
        }
        if context:
            data["context"] = context
        
        response = self.request("POST", "/chat", json=data)
        return ChatResponse(**response)
    
    async def achat(
        self,
        message: str,
        agent_id: str,
        context: Optional[list] = None,
    ) -> "ChatResponse":
        """Async version of chat()"""
        from .types import ChatResponse
        
        data = {
            "message": message,
            "agent_id": agent_id,
        }
        if context:
            data["context"] = context
        
        response = await self.arequest("POST", "/chat", json=data)
        return ChatResponse(**response)
    
    def chat_stream(
        self,
        message: str,
        agent_id: str,
        context: Optional[list] = None,
    ) -> Iterator["StreamChunk"]:
        """
        Stream a chat response from an agent.
        
        Args:
            message: The message to send
            agent_id: The agent ID to chat with
            context: Optional conversation context
        
        Yields:
            StreamChunk objects with response fragments
        """
        from .types import StreamChunk
        import json
        
        data = {
            "message": message,
            "agent_id": agent_id,
        }
        if context:
            data["context"] = context
        
        with self._client.stream(
            "POST",
            "/chat/stream",
            json=data,
        ) as response:
            if response.status_code != 200:
                self._handle_response(response)
            
            for line in response.iter_lines():
                if line.startswith("data: "):
                    try:
                        chunk_data = json.loads(line[6:])
                        yield StreamChunk(**chunk_data)
                    except json.JSONDecodeError:
                        continue
    
    async def achat_stream(
        self,
        message: str,
        agent_id: str,
        context: Optional[list] = None,
    ) -> AsyncIterator["StreamChunk"]:
        """Async version of chat_stream()"""
        from .types import StreamChunk
        import json
        
        data = {
            "message": message,
            "agent_id": agent_id,
        }
        if context:
            data["context"] = context
        
        client = self._get_async_client()
        async with client.stream(
            "POST",
            "/chat/stream",
            json=data,
        ) as response:
            if response.status_code != 200:
                self._handle_response(response)
            
            async for line in response.aiter_lines():
                if line.startswith("data: "):
                    try:
                        chunk_data = json.loads(line[6:])
                        yield StreamChunk(**chunk_data)
                    except json.JSONDecodeError:
                        continue
    
    def close(self):
        """Close HTTP clients"""
        self._client.close()
        if self._async_client:
            # Note: async client should be closed with await
            pass
    
    async def aclose(self):
        """Close async HTTP client"""
        if self._async_client:
            await self._async_client.aclose()
            self._async_client = None
    
    def __enter__(self):
        return self
    
    def __exit__(self, *args):
        self.close()
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, *args):
        await self.aclose()
