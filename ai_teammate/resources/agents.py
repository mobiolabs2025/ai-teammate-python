"""Agents Resource"""

from pathlib import Path
from typing import Optional, List, TYPE_CHECKING

from ..types import Agent, AgentCreate, AgentUpdate, ChatResponse, StreamChunk, Document

if TYPE_CHECKING:
    from ..client import AITeammate


class AgentsResource:
    """
    Manage AI Agents
    
    Usage:
        # List agents
        agents = client.agents.list()
        
        # Get agent
        agent = client.agents.get("agent_id")
        
        # Create agent
        agent = client.agents.create(
            name="My Agent",
            system_prompt="You are a helpful assistant.",
        )
        
        # Update agent
        agent = client.agents.update("agent_id", name="New Name")
        
        # Delete agent
        client.agents.delete("agent_id")
        
        # Chat with agent
        response = client.agents.chat("agent_id", "Hello!")
    """
    
    def __init__(self, client: "AITeammate"):
        self._client = client
    
    def list(
        self,
        page: int = 1,
        per_page: int = 20,
    ) -> List[Agent]:
        """
        List all agents.
        
        Args:
            page: Page number (default: 1)
            per_page: Items per page (default: 20)
        
        Returns:
            List of Agent objects
        """
        response = self._client.request(
            "GET",
            "/agents",
            params={"page": page, "per_page": per_page},
        )
        agents_data = response if isinstance(response, list) else response.get("agents", response.get("items", []))
        return [Agent(**a) for a in agents_data]

    async def alist(
        self,
        page: int = 1,
        per_page: int = 20,
    ) -> List[Agent]:
        """Async version of list()"""
        response = await self._client.arequest(
            "GET",
            "/agents",
            params={"page": page, "per_page": per_page},
        )
        agents_data = response if isinstance(response, list) else response.get("agents", response.get("items", []))
        return [Agent(**a) for a in agents_data]
    
    def get(self, agent_id: str) -> Agent:
        """
        Get an agent by ID.
        
        Args:
            agent_id: The agent ID
        
        Returns:
            Agent object
        """
        response = self._client.request("GET", f"/agents/{agent_id}")
        return Agent(**response)
    
    async def aget(self, agent_id: str) -> Agent:
        """Async version of get()"""
        response = await self._client.arequest("GET", f"/agents/{agent_id}")
        return Agent(**response)
    
    def create(
        self,
        name: str,
        description: Optional[str] = None,
        system_prompt: Optional[str] = None,
        model: Optional[str] = None,
        is_public: bool = False,
    ) -> Agent:
        """
        Create a new agent.
        
        Args:
            name: Agent name
            description: Agent description
            system_prompt: System prompt for the agent
            model: LLM model to use
            is_public: Whether the agent is public
        
        Returns:
            Created Agent object
        """
        data = AgentCreate(
            name=name,
            description=description,
            system_prompt=system_prompt,
            model=model,
            is_public=is_public,
        )
        response = self._client.request(
            "POST",
            "/agents",
            json=data.model_dump(exclude_none=True),
        )
        return Agent(**response)
    
    async def acreate(
        self,
        name: str,
        description: Optional[str] = None,
        system_prompt: Optional[str] = None,
        model: Optional[str] = None,
        is_public: bool = False,
    ) -> Agent:
        """Async version of create()"""
        data = AgentCreate(
            name=name,
            description=description,
            system_prompt=system_prompt,
            model=model,
            is_public=is_public,
        )
        response = await self._client.arequest(
            "POST",
            "/agents",
            json=data.model_dump(exclude_none=True),
        )
        return Agent(**response)
    
    def update(
        self,
        agent_id: str,
        name: Optional[str] = None,
        description: Optional[str] = None,
        system_prompt: Optional[str] = None,
        model: Optional[str] = None,
        is_public: Optional[bool] = None,
    ) -> Agent:
        """
        Update an agent.
        
        Args:
            agent_id: The agent ID to update
            name: New name
            description: New description
            system_prompt: New system prompt
            model: New model
            is_public: New public status
        
        Returns:
            Updated Agent object
        """
        data = AgentUpdate(
            name=name,
            description=description,
            system_prompt=system_prompt,
            model=model,
            is_public=is_public,
        )
        response = self._client.request(
            "PUT",
            f"/agents/{agent_id}",
            json=data.model_dump(exclude_none=True),
        )
        return Agent(**response)
    
    async def aupdate(
        self,
        agent_id: str,
        **kwargs,
    ) -> Agent:
        """Async version of update()"""
        data = AgentUpdate(**kwargs)
        response = await self._client.arequest(
            "PUT",
            f"/agents/{agent_id}",
            json=data.model_dump(exclude_none=True),
        )
        return Agent(**response)
    
    def delete(self, agent_id: str) -> bool:
        """
        Delete an agent.
        
        Args:
            agent_id: The agent ID to delete
        
        Returns:
            True if successful
        """
        self._client.request("DELETE", f"/agents/{agent_id}")
        return True
    
    async def adelete(self, agent_id: str) -> bool:
        """Async version of delete()"""
        await self._client.arequest("DELETE", f"/agents/{agent_id}")
        return True
    
    def chat(
        self,
        agent_id: str,
        message: str,
        context: Optional[list] = None,
    ) -> ChatResponse:
        """
        Chat with an agent.
        
        Args:
            agent_id: The agent ID
            message: The message to send
            context: Optional conversation context
        
        Returns:
            ChatResponse with the agent's reply
        """
        return self._client.chat(message, agent_id=agent_id, context=context)
    
    async def achat(
        self,
        agent_id: str,
        message: str,
        context: Optional[list] = None,
    ) -> ChatResponse:
        """Async version of chat()"""
        return await self._client.achat(message, agent_id=agent_id, context=context)
    
    def chat_stream(
        self,
        agent_id: str,
        message: str,
        context: Optional[list] = None,
    ):
        """
        Stream chat with an agent.
        
        Args:
            agent_id: The agent ID
            message: The message to send
            context: Optional conversation context
        
        Yields:
            StreamChunk objects
        """
        return self._client.chat_stream(message, agent_id=agent_id, context=context)
    
    async def achat_stream(
        self,
        agent_id: str,
        message: str,
        context: Optional[list] = None,
    ):
        """Async version of chat_stream()"""
        async for chunk in self._client.achat_stream(message, agent_id=agent_id, context=context):
            yield chunk

    # ------------------------------------------------------------------
    # Document management (RAG)
    # ------------------------------------------------------------------

    def upload_document(self, agent_id: str, file_path: str) -> Document:
        """
        Upload a document for agent RAG.
        Uploaded documents are indexed and available to all users chatting with this agent.

        Args:
            agent_id: The agent ID
            file_path: Local path to the file (pdf, txt, md, docx, csv)
        """
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        with open(path, "rb") as f:
            response = self._client.request(
                "POST",
                f"/agents/{agent_id}/documents/upload",
                content=None,
                json=None,
                files={"file": (path.name, f)},
            )
        return Document(**response)

    async def aupload_document(self, agent_id: str, file_path: str) -> Document:
        """Async version of upload_document()"""
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        with open(path, "rb") as f:
            response = await self._client.arequest(
                "POST",
                f"/agents/{agent_id}/documents/upload",
                content=None,
                json=None,
                files={"file": (path.name, f)},
            )
        return Document(**response)

    def list_documents(self, agent_id: str) -> List[Document]:
        """List all documents for an agent."""
        response = self._client.request("GET", f"/agents/{agent_id}/documents")
        items = response if isinstance(response, list) else response.get("documents", response.get("items", []))
        return [Document(**d) for d in items]

    async def alist_documents(self, agent_id: str) -> List[Document]:
        """Async version of list_documents()"""
        response = await self._client.arequest("GET", f"/agents/{agent_id}/documents")
        items = response if isinstance(response, list) else response.get("documents", response.get("items", []))
        return [Document(**d) for d in items]

    def delete_document(self, agent_id: str, doc_id: str) -> bool:
        """Delete a document from an agent."""
        self._client.request("DELETE", f"/agents/{agent_id}/documents/{doc_id}")
        return True

    async def adelete_document(self, agent_id: str, doc_id: str) -> bool:
        """Async version of delete_document()"""
        await self._client.arequest("DELETE", f"/agents/{agent_id}/documents/{doc_id}")
        return True
