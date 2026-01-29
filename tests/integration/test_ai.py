"""
Integration tests for AI endpoints.
"""

import pytest
from httpx import AsyncClient
from unittest.mock import patch, AsyncMock


class TestChartInsight:
    """Tests for POST /ai/chart-insight."""
    
    @pytest.mark.asyncio
    async def test_chart_insight_success(
        self, client: AsyncClient, test_admin_user, test_wrestler
    ):
        """Should return AI insight for chart."""
        login_response = await client.post(
            "/api/v1/auth/login",
            json={"email": "admin@test.com", "password": "admin123"},
        )
        token = login_response.json()["accessToken"]
        
        response = await client.post(
            "/api/v1/ai/chart-insight",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "wrestlerId": test_wrestler.id,
                "chartId": "overview-radar",
                "chartData": {
                    "labels": ["A", "B", "C"],
                    "values": [80, 85, 90],
                },
                "locale": "en-US",
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert "summary" in data
        assert "patterns" in data
        assert "recommendations" in data
    
    @pytest.mark.asyncio
    async def test_chart_insight_caching(
        self, client: AsyncClient, test_admin_user, test_wrestler
    ):
        """Same request should return cached result."""
        login_response = await client.post(
            "/api/v1/auth/login",
            json={"email": "admin@test.com", "password": "admin123"},
        )
        token = login_response.json()["accessToken"]
        
        request_data = {
            "wrestlerId": test_wrestler.id,
            "chartId": "test-cache-chart",
            "chartData": {"labels": ["X"], "values": [50]},
            "locale": "en-US",
        }
        
        # First request
        response1 = await client.post(
            "/api/v1/ai/chart-insight",
            headers={"Authorization": f"Bearer {token}"},
            json=request_data,
        )
        assert response1.status_code == 200
        
        # Second request (should be cached)
        response2 = await client.post(
            "/api/v1/ai/chart-insight",
            headers={"Authorization": f"Bearer {token}"},
            json=request_data,
        )
        assert response2.status_code == 200
        assert response1.json()["summary"] == response2.json()["summary"]
    
    @pytest.mark.asyncio
    async def test_chart_insight_unauthenticated(self, client: AsyncClient):
        """Unauthenticated request should fail."""
        response = await client.post(
            "/api/v1/ai/chart-insight",
            json={
                "wrestlerId": "test",
                "chartId": "test",
                "chartData": {"labels": [], "values": []},
            },
        )
        assert response.status_code in [401, 403]


class TestAdvancedChartInsight:
    """Tests for POST /ai/chart-insight/advanced."""
    
    @pytest.mark.asyncio
    async def test_advanced_insight_success(
        self, client: AsyncClient, test_admin_user, test_wrestler
    ):
        """Should return advanced AI insight."""
        login_response = await client.post(
            "/api/v1/auth/login",
            json={"email": "admin@test.com", "password": "admin123"},
        )
        token = login_response.json()["accessToken"]
        
        response = await client.post(
            "/api/v1/ai/chart-insight/advanced",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "wrestlerId": test_wrestler.id,
                "section": "body_composition",
                "chartId": "weight-trend",
                "chartData": {
                    "series": [
                        {
                            "name": "weight",
                            "points": [
                                {"date": "2025-01-01", "value": 85},
                                {"date": "2025-01-15", "value": 86},
                            ],
                        }
                    ]
                },
                "locale": "en-US",
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert "summary" in data
        assert "confidence" in data
        assert 0 <= data["confidence"] <= 1


class TestAITrainingProgram:
    """Tests for POST /ai/training-program."""
    
    @pytest.mark.asyncio
    async def test_training_program_generation(
        self, client: AsyncClient, test_admin_user, test_wrestler
    ):
        """Should generate AI training program."""
        login_response = await client.post(
            "/api/v1/auth/login",
            json={"email": "admin@test.com", "password": "admin123"},
        )
        token = login_response.json()["accessToken"]
        
        response = await client.post(
            "/api/v1/ai/training-program",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "wrestlerId": test_wrestler.id,
                "goal": "strength",
                "date": "2025-02-01",
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert "program" in data
        assert data["program"]["date"] == "2025-02-01"
        assert len(data["program"]["blocks"]) > 0
