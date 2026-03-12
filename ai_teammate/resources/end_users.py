"""End-Users Resource — register, login, and manage end-user authentication"""

from typing import Optional, TYPE_CHECKING

from ..types import AuthResult, VerifyResult, ValidationResult, EndUser

if TYPE_CHECKING:
    from ..client import AITeammate


class EndUsersResource:
    """
    End-User authentication for shared agents.

    End-Users are visitors who interact with agents via share links.
    When a share link has `require_sign_in=True`, end-users must
    register and log in before chatting.

    Registration flow:
        # 1. Register (sends email verification code)
        result = client.end_users.register(agent_id, name="John", email="john@example.com")

        # 2. Verify email
        result = client.end_users.verify(agent_id, email="john@example.com", code="123456")

        # 3. Set password
        auth = client.end_users.set_password(agent_id, email="john@example.com", password="secret")
        token = auth.token  # save this for chat

    Login flow:
        auth = client.end_users.login(agent_id, email="john@example.com", password="secret")
        token = auth.token

    Chat with token:
        response = client.shares.chat(share_code, "Hello!", end_user_token=token)
    """

    def __init__(self, client: "AITeammate"):
        self._client = client

    # ------------------------------------------------------------------
    # Registration
    # ------------------------------------------------------------------

    def register(
        self,
        agent_id: str,
        *,
        name: str,
        email: str,
        birth_date: Optional[str] = None,
        gender: Optional[str] = None,
        agreed_terms: bool = True,
        agreed_privacy: bool = True,
    ) -> AuthResult:
        """
        Register a new end-user. Sends a verification code to the email.

        Args:
            agent_id: The agent ID
            name: User's display name
            email: User's email address
            birth_date: Date of birth (YYYY-MM-DD format, optional)
            gender: Gender ("male" or "female", optional)
            agreed_terms: Agreed to terms of service
            agreed_privacy: Agreed to privacy policy
        """
        data = {
            "name": name,
            "email": email,
            "agreed_terms": agreed_terms,
            "agreed_privacy": agreed_privacy,
        }
        if birth_date:
            data["birth_date"] = birth_date
        if gender:
            data["gender"] = gender

        response = self._client.request(
            "POST", f"/end-user/auth/{agent_id}/register", json=data,
        )
        return AuthResult(**response)

    async def aregister(self, agent_id: str, **kwargs) -> AuthResult:
        """Async version of register()"""
        data = {
            "name": kwargs["name"],
            "email": kwargs["email"],
            "agreed_terms": kwargs.get("agreed_terms", True),
            "agreed_privacy": kwargs.get("agreed_privacy", True),
        }
        if kwargs.get("birth_date"):
            data["birth_date"] = kwargs["birth_date"]
        if kwargs.get("gender"):
            data["gender"] = kwargs["gender"]

        response = await self._client.arequest(
            "POST", f"/end-user/auth/{agent_id}/register", json=data,
        )
        return AuthResult(**response)

    # ------------------------------------------------------------------
    # Verification
    # ------------------------------------------------------------------

    def verify(
        self,
        agent_id: str,
        *,
        email: str,
        code: str,
    ) -> VerifyResult:
        """
        Verify email with the 6-digit code sent during registration.

        Args:
            agent_id: The agent ID
            email: The email to verify
            code: 6-digit verification code
        """
        response = self._client.request(
            "POST", f"/end-user/auth/{agent_id}/verify",
            json={"email": email, "code": code},
        )
        return VerifyResult(**response)

    async def averify(self, agent_id: str, *, email: str, code: str) -> VerifyResult:
        """Async version of verify()"""
        response = await self._client.arequest(
            "POST", f"/end-user/auth/{agent_id}/verify",
            json={"email": email, "code": code},
        )
        return VerifyResult(**response)

    # ------------------------------------------------------------------
    # Set Password
    # ------------------------------------------------------------------

    def set_password(
        self,
        agent_id: str,
        *,
        email: str,
        password: str,
    ) -> AuthResult:
        """
        Set password after email verification. Returns auth token.

        Args:
            agent_id: The agent ID
            email: Verified email address
            password: Password to set (min 6 characters)
        """
        response = self._client.request(
            "POST", f"/end-user/auth/{agent_id}/set-password",
            json={"email": email, "password": password},
        )
        return AuthResult(**response)

    async def aset_password(self, agent_id: str, *, email: str, password: str) -> AuthResult:
        """Async version of set_password()"""
        response = await self._client.arequest(
            "POST", f"/end-user/auth/{agent_id}/set-password",
            json={"email": email, "password": password},
        )
        return AuthResult(**response)

    # ------------------------------------------------------------------
    # Login
    # ------------------------------------------------------------------

    def login(
        self,
        agent_id: str,
        *,
        email: str,
        password: str,
    ) -> AuthResult:
        """
        Log in an existing end-user. Returns auth token.

        Args:
            agent_id: The agent ID
            email: Email address
            password: Password
        """
        response = self._client.request(
            "POST", f"/end-user/auth/{agent_id}/login",
            json={"email": email, "password": password},
        )
        return AuthResult(**response)

    async def alogin(self, agent_id: str, *, email: str, password: str) -> AuthResult:
        """Async version of login()"""
        response = await self._client.arequest(
            "POST", f"/end-user/auth/{agent_id}/login",
            json={"email": email, "password": password},
        )
        return AuthResult(**response)

    # ------------------------------------------------------------------
    # Validate Token
    # ------------------------------------------------------------------

    def validate(
        self,
        agent_id: str,
        *,
        token: str,
    ) -> ValidationResult:
        """
        Validate an end-user token.

        Args:
            agent_id: The agent ID
            token: End-user JWT token to validate
        """
        response = self._client.request(
            "GET", f"/end-user/auth/{agent_id}/validate",
            headers={"Authorization": f"Bearer {token}"},
        )
        return ValidationResult(**response)

    async def avalidate(self, agent_id: str, *, token: str) -> ValidationResult:
        """Async version of validate()"""
        response = await self._client.arequest(
            "GET", f"/end-user/auth/{agent_id}/validate",
            headers={"Authorization": f"Bearer {token}"},
        )
        return ValidationResult(**response)

    # ------------------------------------------------------------------
    # Forgot Password
    # ------------------------------------------------------------------

    def forgot_password(
        self,
        agent_id: str,
        *,
        email: str,
    ) -> AuthResult:
        """
        Send a password reset verification code.

        Args:
            agent_id: The agent ID
            email: Email address
        """
        response = self._client.request(
            "POST", f"/end-user/auth/{agent_id}/forgot-password",
            json={"email": email},
        )
        return AuthResult(**response)

    async def aforgot_password(self, agent_id: str, *, email: str) -> AuthResult:
        """Async version of forgot_password()"""
        response = await self._client.arequest(
            "POST", f"/end-user/auth/{agent_id}/forgot-password",
            json={"email": email},
        )
        return AuthResult(**response)

    # ------------------------------------------------------------------
    # Google OAuth
    # ------------------------------------------------------------------

    def google_auth_url(
        self,
        agent_id: str,
        *,
        source: Optional[str] = None,
        redirect_uri: Optional[str] = None,
        return_url: Optional[str] = None,
    ) -> dict:
        """
        Get Google OAuth URL for end-user login/registration.

        Args:
            agent_id: The agent ID
            source: Signup source identifier (e.g. "kiosk:burger-palace")
            redirect_uri: Custom OAuth redirect URI (optional)
            return_url: URL to redirect after auth with token in query params (optional)

        Returns:
            dict with ``url`` (Google OAuth URL) and ``state``
        """
        params: dict = {}
        if source:
            params["source"] = source
        if redirect_uri:
            params["redirect_uri"] = redirect_uri
        if return_url:
            params["return_url"] = return_url

        return self._client.request(
            "GET", f"/end-user/auth/{agent_id}/google", params=params,
        )

    async def agoogle_auth_url(
        self,
        agent_id: str,
        *,
        source: Optional[str] = None,
        redirect_uri: Optional[str] = None,
        return_url: Optional[str] = None,
    ) -> dict:
        """Async version of google_auth_url()"""
        params: dict = {}
        if source:
            params["source"] = source
        if redirect_uri:
            params["redirect_uri"] = redirect_uri
        if return_url:
            params["return_url"] = return_url

        return await self._client.arequest(
            "GET", f"/end-user/auth/{agent_id}/google", params=params,
        )

    def google_callback(
        self,
        agent_id: str,
        *,
        code: str,
        source: Optional[str] = None,
        redirect_uri: Optional[str] = None,
    ) -> AuthResult:
        """
        Exchange Google OAuth code for end-user token.

        Args:
            agent_id: The agent ID
            code: Authorization code from Google
            source: Signup source identifier
            redirect_uri: The redirect_uri used in the auth request

        Returns:
            AuthResult with token, end_user, and is_new flag
        """
        data: dict = {"code": code, "agent_id": agent_id}
        if source:
            data["source"] = source
        if redirect_uri:
            data["redirect_uri"] = redirect_uri

        response = self._client.request(
            "POST", "/end-user/auth/google/callback", json=data,
        )
        return AuthResult(**response)

    async def agoogle_callback(
        self,
        agent_id: str,
        *,
        code: str,
        source: Optional[str] = None,
        redirect_uri: Optional[str] = None,
    ) -> AuthResult:
        """Async version of google_callback()"""
        data: dict = {"code": code, "agent_id": agent_id}
        if source:
            data["source"] = source
        if redirect_uri:
            data["redirect_uri"] = redirect_uri

        response = await self._client.arequest(
            "POST", "/end-user/auth/google/callback", json=data,
        )
        return AuthResult(**response)
