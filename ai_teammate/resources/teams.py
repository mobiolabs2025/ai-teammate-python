"""Teams Resource"""

from typing import Optional, List, TYPE_CHECKING, Literal

from ..types import Team, TeamCreate, ChatResponse, Agent

if TYPE_CHECKING:
    from ..client import AITeammate


ChatMode = Literal["auto", "round_robin", "parallel", "debate", "brainstorm", "expert"]


class TeamsResource:
    """
    Manage AI Teams
    
    Usage:
        # List teams
        teams = client.teams.list()
        
        # Create team
        team = client.teams.create(name="My Team")
        
        # Add agent to team
        client.teams.add_agent("team_id", "agent_id")
        
        # Team chat
        response = client.teams.chat("team_id", "Brainstorm ideas!")
    """
    
    def __init__(self, client: "AITeammate"):
        self._client = client
    
    def list(self) -> List[Team]:
        """
        List all teams.
        
        Returns:
            List of Team objects
        """
        response = self._client.request("GET", "/teams")
        teams_data = response if isinstance(response, list) else response.get("teams", response.get("items", []))
        return [Team(**t) for t in teams_data]

    async def alist(self) -> List[Team]:
        """Async version of list()"""
        response = await self._client.arequest("GET", "/teams")
        teams_data = response if isinstance(response, list) else response.get("teams", response.get("items", []))
        return [Team(**t) for t in teams_data]
    
    def get(self, team_id: str) -> Team:
        """
        Get a team by ID.
        
        Args:
            team_id: The team ID
        
        Returns:
            Team object
        """
        response = self._client.request("GET", f"/teams/{team_id}")
        return Team(**response)
    
    async def aget(self, team_id: str) -> Team:
        """Async version of get()"""
        response = await self._client.arequest("GET", f"/teams/{team_id}")
        return Team(**response)
    
    def create(
        self,
        name: str,
        description: Optional[str] = None,
        chat_mode: ChatMode = "auto",
    ) -> Team:
        """
        Create a new team.
        
        Args:
            name: Team name
            description: Team description
            chat_mode: Chat mode (auto, round_robin, parallel, debate, brainstorm, expert)
        
        Returns:
            Created Team object
        """
        data = TeamCreate(
            name=name,
            description=description,
            chat_mode=chat_mode,
        )
        response = self._client.request(
            "POST",
            "/teams",
            json=data.model_dump(exclude_none=True),
        )
        return Team(**response)
    
    async def acreate(
        self,
        name: str,
        description: Optional[str] = None,
        chat_mode: ChatMode = "auto",
    ) -> Team:
        """Async version of create()"""
        data = TeamCreate(
            name=name,
            description=description,
            chat_mode=chat_mode,
        )
        response = await self._client.arequest(
            "POST",
            "/teams",
            json=data.model_dump(exclude_none=True),
        )
        return Team(**response)
    
    def delete(self, team_id: str) -> bool:
        """
        Delete a team.
        
        Args:
            team_id: The team ID to delete
        
        Returns:
            True if successful
        """
        self._client.request("DELETE", f"/teams/{team_id}")
        return True
    
    async def adelete(self, team_id: str) -> bool:
        """Async version of delete()"""
        await self._client.arequest("DELETE", f"/teams/{team_id}")
        return True
    
    def get_agents(self, team_id: str) -> List[Agent]:
        """
        Get agents in a team.
        
        Args:
            team_id: The team ID
        
        Returns:
            List of Agent objects
        """
        response = self._client.request("GET", f"/teams/{team_id}/agents")
        agents_data = response if isinstance(response, list) else response.get("agents", response.get("items", []))
        return [Agent(**a) for a in agents_data]

    async def aget_agents(self, team_id: str) -> List[Agent]:
        """Async version of get_agents()"""
        response = await self._client.arequest("GET", f"/teams/{team_id}/agents")
        agents_data = response if isinstance(response, list) else response.get("agents", response.get("items", []))
        return [Agent(**a) for a in agents_data]
    
    def add_agent(
        self,
        team_id: str,
        agent_id: str,
        role: Optional[str] = None,
    ) -> bool:
        """
        Add an agent to a team.
        
        Args:
            team_id: The team ID
            agent_id: The agent ID to add
            role: Optional role for the agent in the team
        
        Returns:
            True if successful
        """
        data = {"agent_id": agent_id}
        if role:
            data["role"] = role
        self._client.request("POST", f"/teams/{team_id}/agents", json=data)
        return True
    
    async def aadd_agent(
        self,
        team_id: str,
        agent_id: str,
        role: Optional[str] = None,
    ) -> bool:
        """Async version of add_agent()"""
        data = {"agent_id": agent_id}
        if role:
            data["role"] = role
        await self._client.arequest("POST", f"/teams/{team_id}/agents", json=data)
        return True
    
    def remove_agent(self, team_id: str, agent_id: str) -> bool:
        """
        Remove an agent from a team.
        
        Args:
            team_id: The team ID
            agent_id: The agent ID to remove
        
        Returns:
            True if successful
        """
        self._client.request("DELETE", f"/teams/{team_id}/agents/{agent_id}")
        return True
    
    async def aremove_agent(self, team_id: str, agent_id: str) -> bool:
        """Async version of remove_agent()"""
        await self._client.arequest("DELETE", f"/teams/{team_id}/agents/{agent_id}")
        return True
    
    def chat(
        self,
        team_id: str,
        message: str,
        mode: Optional[ChatMode] = None,
    ) -> ChatResponse:
        """
        Chat with a team.
        
        Args:
            team_id: The team ID
            message: The message to send
            mode: Override chat mode for this message
        
        Returns:
            ChatResponse with the team's reply
        """
        data = {"message": message}
        if mode:
            data["mode"] = mode
        response = self._client.request("POST", f"/teams/{team_id}/chat", json=data)
        return ChatResponse(**response)

    async def achat(
        self,
        team_id: str,
        message: str,
        mode: Optional[ChatMode] = None,
    ) -> ChatResponse:
        """Async version of chat()"""
        data = {"message": message}
        if mode:
            data["mode"] = mode
        response = await self._client.arequest("POST", f"/teams/{team_id}/chat", json=data)
        return ChatResponse(**response)
