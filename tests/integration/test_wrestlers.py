"""
Integration tests for wrestler endpoints.
"""

import pytest
from httpx import AsyncClient


class TestListWrestlers:
    """Tests for GET /wrestlers."""
    
    @pytest.mark.asyncio
    async def test_list_wrestlers_authenticated(
        self, client: AsyncClient, test_admin_user, test_wrestler
    ):
        """Authenticated user should get wrestler list."""
        # Login
        login_response = await client.post(
            "/api/v1/auth/login",
            json={"email": "admin@test.com", "password": "admin123"},
        )
        token = login_response.json()["accessToken"]
        
        # Get wrestlers
        response = await client.get(
            "/api/v1/wrestlers",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 200
        data = response.json()
        assert "wrestlers" in data
        assert len(data["wrestlers"]) >= 1
    
    @pytest.mark.asyncio
    async def test_list_wrestlers_unauthenticated(self, client: AsyncClient):
        """Unauthenticated request should return 401/403."""
        response = await client.get("/api/v1/wrestlers")
        assert response.status_code in [401, 403]
    
    @pytest.mark.asyncio
    async def test_list_wrestlers_pagination(
        self, client: AsyncClient, test_admin_user, test_wrestler
    ):
        """Pagination should work correctly."""
        login_response = await client.post(
            "/api/v1/auth/login",
            json={"email": "admin@test.com", "password": "admin123"},
        )
        token = login_response.json()["accessToken"]
        
        response = await client.get(
            "/api/v1/wrestlers?limit=1&offset=0",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 200


class TestGetWrestler:
    """Tests for GET /wrestlers/{wrestlerId}."""
    
    @pytest.mark.asyncio
    async def test_get_wrestler_success(
        self, client: AsyncClient, test_admin_user, test_wrestler
    ):
        """Should return wrestler details."""
        login_response = await client.post(
            "/api/v1/auth/login",
            json={"email": "admin@test.com", "password": "admin123"},
        )
        token = login_response.json()["accessToken"]
        
        response = await client.get(
            f"/api/v1/wrestlers/{test_wrestler.id}",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == test_wrestler.id
        assert data["nameEn"] == test_wrestler.name_en
    
    @pytest.mark.asyncio
    async def test_get_wrestler_not_found(
        self, client: AsyncClient, test_admin_user
    ):
        """Should return 404 for non-existent wrestler."""
        login_response = await client.post(
            "/api/v1/auth/login",
            json={"email": "admin@test.com", "password": "admin123"},
        )
        token = login_response.json()["accessToken"]
        
        response = await client.get(
            "/api/v1/wrestlers/non-existent-id",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 404


class TestWrestlerRoleAccess:
    """Tests for role-based access control on wrestler endpoints."""
    
    @pytest.mark.asyncio
    async def test_coach_can_access_team_wrestler(
        self, client: AsyncClient, test_coach_user, test_wrestler
    ):
        """Coach should access wrestlers in their team."""
        login_response = await client.post(
            "/api/v1/auth/login",
            json={"email": "coach@test.com", "password": "coach123"},
        )
        token = login_response.json()["accessToken"]
        
        response = await client.get(
            f"/api/v1/wrestlers/{test_wrestler.id}",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 200
    
    @pytest.mark.asyncio
    async def test_athlete_can_access_own_data(
        self, client: AsyncClient, test_athlete_user, test_wrestler
    ):
        """Athlete should access their own data."""
        login_response = await client.post(
            "/api/v1/auth/login",
            json={"email": "athlete@test.com", "password": "athlete123"},
        )
        token = login_response.json()["accessToken"]
        
        response = await client.get(
            f"/api/v1/wrestlers/{test_wrestler.id}",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 200
