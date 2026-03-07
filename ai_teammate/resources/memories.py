"""Memories Resource"""

from typing import Optional, List, TYPE_CHECKING

from ..types import Memory, MemoryCreate

if TYPE_CHECKING:
    from ..client import AITeammate


class MemoriesResource:
    """
    Manage Agent Memories (Bookmarks)
    
    Usage:
        # List memories
        memories = client.memories.list(agent_id="abc123")
        
        # Create memory
        memory = client.memories.create(
            agent_id="abc123",
            content="Important information",
            category="notes",
        )
        
        # Delete memory
        client.memories.delete(agent_id="abc123", memory_id="mem_123")
    """
    
    def __init__(self, client: "AITeammate"):
        self._client = client
    
    def list(
        self,
        agent_id: str,
        category: Optional[str] = None,
        page: int = 1,
        per_page: int = 50,
    ) -> List[Memory]:
        """
        List memories for an agent.
        
        Args:
            agent_id: The agent ID
            category: Filter by category
            page: Page number
            per_page: Items per page
        
        Returns:
            List of Memory objects
        """
        params = {"page": page, "per_page": per_page}
        if category:
            params["category"] = category
        
        response = self._client.request(
            "GET",
            f"/agents/{agent_id}/memories",
            params=params,
        )
        memories_data = response.get("memories", response.get("items", []))
        return [Memory(**m) for m in memories_data]
    
    async def alist(
        self,
        agent_id: str,
        category: Optional[str] = None,
        page: int = 1,
        per_page: int = 50,
    ) -> List[Memory]:
        """Async version of list()"""
        params = {"page": page, "per_page": per_page}
        if category:
            params["category"] = category
        
        response = await self._client.arequest(
            "GET",
            f"/agents/{agent_id}/memories",
            params=params,
        )
        memories_data = response.get("memories", response.get("items", []))
        return [Memory(**m) for m in memories_data]
    
    def get(self, agent_id: str, memory_id: str) -> Memory:
        """
        Get a specific memory.
        
        Args:
            agent_id: The agent ID
            memory_id: The memory ID
        
        Returns:
            Memory object
        """
        response = self._client.request(
            "GET",
            f"/agents/{agent_id}/memories/{memory_id}",
        )
        return Memory(**response)
    
    async def aget(self, agent_id: str, memory_id: str) -> Memory:
        """Async version of get()"""
        response = await self._client.arequest(
            "GET",
            f"/agents/{agent_id}/memories/{memory_id}",
        )
        return Memory(**response)
    
    def create(
        self,
        agent_id: str,
        content: str,
        category: Optional[str] = None,
        url: Optional[str] = None,
        tags: Optional[List[str]] = None,
    ) -> Memory:
        """
        Create a new memory for an agent.
        
        Args:
            agent_id: The agent ID
            content: Memory content
            category: Category name
            url: Associated URL
            tags: List of tags
        
        Returns:
            Created Memory object
        """
        data = MemoryCreate(
            content=content,
            category=category,
            url=url,
            tags=tags or [],
        )
        response = self._client.request(
            "POST",
            f"/agents/{agent_id}/memories",
            json=data.model_dump(exclude_none=True),
        )
        return Memory(**response)
    
    async def acreate(
        self,
        agent_id: str,
        content: str,
        category: Optional[str] = None,
        url: Optional[str] = None,
        tags: Optional[List[str]] = None,
    ) -> Memory:
        """Async version of create()"""
        data = MemoryCreate(
            content=content,
            category=category,
            url=url,
            tags=tags or [],
        )
        response = await self._client.arequest(
            "POST",
            f"/agents/{agent_id}/memories",
            json=data.model_dump(exclude_none=True),
        )
        return Memory(**response)
    
    def delete(self, agent_id: str, memory_id: str) -> bool:
        """
        Delete a memory.
        
        Args:
            agent_id: The agent ID
            memory_id: The memory ID to delete
        
        Returns:
            True if successful
        """
        self._client.request(
            "DELETE",
            f"/agents/{agent_id}/memories/{memory_id}",
        )
        return True
    
    async def adelete(self, agent_id: str, memory_id: str) -> bool:
        """Async version of delete()"""
        await self._client.arequest(
            "DELETE",
            f"/agents/{agent_id}/memories/{memory_id}",
        )
        return True
    
    def search(
        self,
        agent_id: str,
        query: str,
        limit: int = 10,
    ) -> List[Memory]:
        """
        Search memories by content.
        
        Args:
            agent_id: The agent ID
            query: Search query
            limit: Max results
        
        Returns:
            List of matching Memory objects
        """
        response = self._client.request(
            "GET",
            f"/agents/{agent_id}/memories/search",
            params={"q": query, "limit": limit},
        )
        memories_data = response.get("memories", response.get("items", []))
        return [Memory(**m) for m in memories_data]
    
    async def asearch(
        self,
        agent_id: str,
        query: str,
        limit: int = 10,
    ) -> List[Memory]:
        """Async version of search()"""
        response = await self._client.arequest(
            "GET",
            f"/agents/{agent_id}/memories/search",
            params={"q": query, "limit": limit},
        )
        memories_data = response.get("memories", response.get("items", []))
        return [Memory(**m) for m in memories_data]
