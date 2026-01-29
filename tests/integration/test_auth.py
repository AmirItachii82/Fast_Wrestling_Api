"""
Integration tests for authentication endpoints.
"""

import pytest
from httpx import AsyncClient

from tests.conftest import get_auth_token


class TestAuthLogin:
    """Tests for POST /auth/login."""
    
    @pytest.mark.asyncio
    async def test_login_success(self, client: AsyncClient, test_admin_user):
        """Valid credentials should return tokens."""
        response = await client.post(
            "/api/v1/auth/login",
            json={"email": "admin@test.com", "password": "admin123"},
        )
        assert response.status_code == 200
        data = response.json()
        assert "accessToken" in data
        assert "refreshToken" in data
        assert "user" in data
        assert data["user"]["role"] == "admin"
    
    @pytest.mark.asyncio
    async def test_login_invalid_email(self, client: AsyncClient):
        """Invalid email should return 401."""
        response = await client.post(
            "/api/v1/auth/login",
            json={"email": "nonexistent@test.com", "password": "password"},
        )
        assert response.status_code == 401
    
    @pytest.mark.asyncio
    async def test_login_invalid_password(self, client: AsyncClient, test_admin_user):
        """Invalid password should return 401."""
        response = await client.post(
            "/api/v1/auth/login",
            json={"email": "admin@test.com", "password": "wrongpassword"},
        )
        assert response.status_code == 401
    
    @pytest.mark.asyncio
    async def test_login_missing_fields(self, client: AsyncClient):
        """Missing fields should return 422."""
        response = await client.post(
            "/api/v1/auth/login",
            json={"email": "admin@test.com"},
        )
        assert response.status_code == 422


class TestAuthRefresh:
    """Tests for POST /auth/refresh."""
    
    @pytest.mark.asyncio
    async def test_refresh_success(self, client: AsyncClient, test_admin_user):
        """Valid refresh token should return new access token."""
        # First login
        login_response = await client.post(
            "/api/v1/auth/login",
            json={"email": "admin@test.com", "password": "admin123"},
        )
        refresh_token = login_response.json()["refreshToken"]
        
        # Then refresh
        response = await client.post(
            "/api/v1/auth/refresh",
            json={"refreshToken": refresh_token},
        )
        assert response.status_code == 200
        assert "accessToken" in response.json()
    
    @pytest.mark.asyncio
    async def test_refresh_invalid_token(self, client: AsyncClient):
        """Invalid refresh token should return 401."""
        response = await client.post(
            "/api/v1/auth/refresh",
            json={"refreshToken": "invalid.token.here"},
        )
        assert response.status_code == 401


class TestAuthLogout:
    """Tests for POST /auth/logout."""
    
    @pytest.mark.asyncio
    async def test_logout_success(self, client: AsyncClient, test_admin_user):
        """Valid logout should return success."""
        # First login
        login_response = await client.post(
            "/api/v1/auth/login",
            json={"email": "admin@test.com", "password": "admin123"},
        )
        refresh_token = login_response.json()["refreshToken"]
        
        # Then logout
        response = await client.post(
            "/api/v1/auth/logout",
            json={"refreshToken": refresh_token},
        )
        assert response.status_code == 200
        assert response.json()["success"] is True
    
    @pytest.mark.asyncio
    async def test_refresh_after_logout_fails(self, client: AsyncClient, test_admin_user):
        """Refresh token should be invalid after logout."""
        # Login
        login_response = await client.post(
            "/api/v1/auth/login",
            json={"email": "admin@test.com", "password": "admin123"},
        )
        refresh_token = login_response.json()["refreshToken"]
        
        # Logout
        await client.post(
            "/api/v1/auth/logout",
            json={"refreshToken": refresh_token},
        )
        
        # Try to refresh
        response = await client.post(
            "/api/v1/auth/refresh",
            json={"refreshToken": refresh_token},
        )
        assert response.status_code == 401
