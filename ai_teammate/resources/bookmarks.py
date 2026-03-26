"""End-User Bookmarks Resource — save, list, and delete bookmarks scoped per agent"""

from typing import Optional, List, TYPE_CHECKING

from ..types import Bookmark, BookmarkCreate

if TYPE_CHECKING:
    from ..client import AITeammate


class BookmarksResource:
    """
    Manage end-user bookmarks (unified API).

    Bookmarks are scoped per agent — the same end-user can have
    different bookmarks under different agents.

    Usage:
        # Save a bookmark
        bm = client.bookmarks.save(
            agent_id="abc123",
            url="https://example.com/recipe",
            title="Chicken Recipe",
            tags=["recipes", "chicken"],
            end_user_token="eyJ...",
        )

        # List bookmarks
        bookmarks = client.bookmarks.list(
            agent_id="abc123",
            end_user_token="eyJ...",
        )

        # Delete bookmark
        client.bookmarks.delete(
            agent_id="abc123",
            bookmark_id=bm.id,
            end_user_token="eyJ...",
        )
    """

    def __init__(self, client: "AITeammate"):
        self._client = client

    def _headers(self, end_user_token: str) -> dict:
        return {"Authorization": f"Bearer {end_user_token}"}

    # ── Save ────────────────────────────────────────────

    def save(
        self,
        agent_id: str,
        url: str,
        end_user_token: str,
        title: Optional[str] = None,
        tags: Optional[List[str]] = None,
    ) -> Bookmark:
        """
        Save a bookmark. OG metadata is auto-extracted from the URL.

        Args:
            agent_id: The agent ID
            url: URL to bookmark
            end_user_token: End-user JWT token
            title: Optional title (auto-extracted if omitted)
            tags: Optional list of tags

        Returns:
            Created Bookmark object
        """
        data = BookmarkCreate(url=url, title=title, tags=tags)
        response = self._client.request(
            "POST",
            f"/bookmarks/end-user/{agent_id}",
            json=data.model_dump(exclude_none=True),
            headers=self._headers(end_user_token),
        )
        return Bookmark(**response.get("bookmark", response))

    async def asave(
        self,
        agent_id: str,
        url: str,
        end_user_token: str,
        title: Optional[str] = None,
        tags: Optional[List[str]] = None,
    ) -> Bookmark:
        """Async version of save()"""
        data = BookmarkCreate(url=url, title=title, tags=tags)
        response = await self._client.arequest(
            "POST",
            f"/bookmarks/end-user/{agent_id}",
            json=data.model_dump(exclude_none=True),
            headers=self._headers(end_user_token),
        )
        return Bookmark(**response.get("bookmark", response))

    # ── List ────────────────────────────────────────────

    def list(
        self,
        agent_id: str,
        end_user_token: str,
        page: int = 1,
        page_size: int = 20,
        tag: Optional[str] = None,
        search: Optional[str] = None,
    ) -> List[Bookmark]:
        """
        List end-user bookmarks for an agent.

        Args:
            agent_id: The agent ID
            end_user_token: End-user JWT token
            page: Page number
            page_size: Items per page
            tag: Filter by tag
            search: Search query

        Returns:
            List of Bookmark objects
        """
        params: dict = {"page": page, "page_size": page_size}
        if tag:
            params["tag"] = tag
        if search:
            params["search"] = search

        response = self._client.request(
            "GET",
            f"/bookmarks/end-user/{agent_id}",
            params=params,
            headers=self._headers(end_user_token),
        )
        return [Bookmark(**b) for b in response.get("bookmarks", [])]

    async def alist(
        self,
        agent_id: str,
        end_user_token: str,
        page: int = 1,
        page_size: int = 20,
        tag: Optional[str] = None,
        search: Optional[str] = None,
    ) -> List[Bookmark]:
        """Async version of list()"""
        params: dict = {"page": page, "page_size": page_size}
        if tag:
            params["tag"] = tag
        if search:
            params["search"] = search

        response = await self._client.arequest(
            "GET",
            f"/bookmarks/end-user/{agent_id}",
            params=params,
            headers=self._headers(end_user_token),
        )
        return [Bookmark(**b) for b in response.get("bookmarks", [])]

    # ── Delete ──────────────────────────────────────────

    def delete(
        self,
        agent_id: str,
        bookmark_id: str,
        end_user_token: str,
    ) -> bool:
        """
        Delete a bookmark.

        Args:
            agent_id: The agent ID
            bookmark_id: The bookmark ID
            end_user_token: End-user JWT token

        Returns:
            True if successful
        """
        self._client.request(
            "DELETE",
            f"/bookmarks/end-user/{agent_id}/{bookmark_id}",
            headers=self._headers(end_user_token),
        )
        return True

    async def adelete(
        self,
        agent_id: str,
        bookmark_id: str,
        end_user_token: str,
    ) -> bool:
        """Async version of delete()"""
        await self._client.arequest(
            "DELETE",
            f"/bookmarks/end-user/{agent_id}/{bookmark_id}",
            headers=self._headers(end_user_token),
        )
        return True
