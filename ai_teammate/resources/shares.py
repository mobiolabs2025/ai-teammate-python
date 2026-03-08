"""Shares Resource — manage and use shared agent links"""

from pathlib import Path
from typing import Optional, List, TYPE_CHECKING

from ..types import (
    ShareLink,
    ShareInfo,
    ChatResponse,
    Document,
)

if TYPE_CHECKING:
    from ..client import AITeammate


class SharesResource:
    """
    Create, manage, and use shared agent links.

    Owner operations (require API key):
        share = client.shares.create("agent_id", require_sign_in=True, allow_file_upload=True)
        shares = client.shares.list("agent_id")
        client.shares.delete("agent_id", share.id)

    Public operations (no API key needed):
        info = client.shares.get_info("share_code")
        response = client.shares.chat("share_code", "Hello!")
        doc = client.shares.upload_document("share_code", "/path/to/file.pdf")
    """

    def __init__(self, client: "AITeammate"):
        self._client = client

    # ------------------------------------------------------------------
    # Owner operations (API key required)
    # ------------------------------------------------------------------

    def create(
        self,
        agent_id: str,
        include_memory: bool = False,
        memory_sharing: Optional[dict] = None,
        max_messages: int = 100,
        expires_in_days: Optional[int] = None,
        require_sign_in: bool = True,
        allow_file_upload: bool = False,
    ) -> ShareLink:
        """
        Create a share link for an agent.

        Args:
            agent_id: The agent ID to share
            include_memory: Share agent memory with visitors
            memory_sharing: Fine-grained memory sharing config {"enabled": bool, "categories": []}
            max_messages: Max messages allowed (0 = unlimited)
            expires_in_days: Link expiration (None = permanent)
            require_sign_in: Require end-user authentication
            allow_file_upload: Allow visitors to upload documents
        """
        data = {
            "include_memory": include_memory,
            "max_messages": max_messages,
            "require_end_user_auth": require_sign_in,
            "allow_file_upload": allow_file_upload,
        }
        if memory_sharing is not None:
            data["memory_sharing"] = memory_sharing
        if expires_in_days is not None:
            data["expires_in_days"] = expires_in_days

        response = self._client.request(
            "POST", f"/agents/{agent_id}/share", json=data,
        )
        return ShareLink(**response)

    async def acreate(self, agent_id: str, **kwargs) -> ShareLink:
        """Async version of create()"""
        data = {
            "include_memory": kwargs.get("include_memory", False),
            "max_messages": kwargs.get("max_messages", 100),
            "require_end_user_auth": kwargs.get("require_sign_in", True),
            "allow_file_upload": kwargs.get("allow_file_upload", False),
        }
        if kwargs.get("memory_sharing") is not None:
            data["memory_sharing"] = kwargs["memory_sharing"]
        if kwargs.get("expires_in_days") is not None:
            data["expires_in_days"] = kwargs["expires_in_days"]

        response = await self._client.arequest(
            "POST", f"/agents/{agent_id}/share", json=data,
        )
        return ShareLink(**response)

    def list(self, agent_id: str) -> List[ShareLink]:
        """List all share links for an agent."""
        response = self._client.request("GET", f"/agents/{agent_id}/shares")
        items = response if isinstance(response, list) else response.get("items", [])
        return [ShareLink(**s) for s in items]

    async def alist(self, agent_id: str) -> List[ShareLink]:
        """Async version of list()"""
        response = await self._client.arequest("GET", f"/agents/{agent_id}/shares")
        items = response if isinstance(response, list) else response.get("items", [])
        return [ShareLink(**s) for s in items]

    def delete(self, agent_id: str, share_id: str) -> bool:
        """Delete a share link."""
        self._client.request("DELETE", f"/agents/{agent_id}/shares/{share_id}")
        return True

    async def adelete(self, agent_id: str, share_id: str) -> bool:
        """Async version of delete()"""
        await self._client.arequest("DELETE", f"/agents/{agent_id}/shares/{share_id}")
        return True

    # ------------------------------------------------------------------
    # Public operations (share_code, no API key needed)
    # ------------------------------------------------------------------

    def get_info(self, share_code: str) -> ShareInfo:
        """
        Get public info about a shared agent.

        Args:
            share_code: The share code from the URL
        """
        response = self._client.request("GET", f"/shared/{share_code}/info")
        return ShareInfo(**response)

    async def aget_info(self, share_code: str) -> ShareInfo:
        """Async version of get_info()"""
        response = await self._client.arequest("GET", f"/shared/{share_code}/info")
        return ShareInfo(**response)

    def chat(
        self,
        share_code: str,
        message: str,
        end_user_token: Optional[str] = None,
    ) -> ChatResponse:
        """
        Chat with a shared agent.

        Args:
            share_code: The share code
            message: Message to send
            end_user_token: Optional end-user auth token (for history persistence)
        """
        data: dict = {"message": message}
        if end_user_token:
            data["end_user_token"] = end_user_token

        response = self._client.request(
            "POST", f"/shared/{share_code}/chat", json=data,
        )
        return ChatResponse(**response)

    async def achat(
        self,
        share_code: str,
        message: str,
        end_user_token: Optional[str] = None,
    ) -> ChatResponse:
        """Async version of chat()"""
        data: dict = {"message": message}
        if end_user_token:
            data["end_user_token"] = end_user_token

        response = await self._client.arequest(
            "POST", f"/shared/{share_code}/chat", json=data,
        )
        return ChatResponse(**response)

    def upload_document(
        self,
        share_code: str,
        file_path: str,
    ) -> Document:
        """
        Upload a document to a shared agent (must have allow_file_upload enabled).

        Args:
            share_code: The share code
            file_path: Local path to the file (pdf, txt, md, docx, csv)
        """
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        with open(path, "rb") as f:
            response = self._client.request(
                "POST",
                f"/shared/{share_code}/documents/upload",
                content=None,
                json=None,
                files={"file": (path.name, f)},
            )
        return Document(**response)

    async def aupload_document(
        self,
        share_code: str,
        file_path: str,
    ) -> Document:
        """Async version of upload_document()"""
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        with open(path, "rb") as f:
            response = await self._client.arequest(
                "POST",
                f"/shared/{share_code}/documents/upload",
                content=None,
                json=None,
                files={"file": (path.name, f)},
            )
        return Document(**response)

    def get_history(
        self,
        share_code: str,
        end_user_token: str,
    ) -> List[dict]:
        """
        Get chat history for an authenticated end-user.

        Args:
            share_code: The share code
            end_user_token: End-user auth token
        """
        response = self._client.request(
            "GET",
            f"/shared/{share_code}/history",
            headers={"Authorization": f"Bearer {end_user_token}"},
        )
        return response.get("messages", [])

    async def aget_history(
        self,
        share_code: str,
        end_user_token: str,
    ) -> List[dict]:
        """Async version of get_history()"""
        response = await self._client.arequest(
            "GET",
            f"/shared/{share_code}/history",
            headers={"Authorization": f"Bearer {end_user_token}"},
        )
        return response.get("messages", [])
