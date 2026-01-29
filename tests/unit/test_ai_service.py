"""
Unit tests for AI service.
"""

import pytest

from app.services.ai_service import (
    compute_input_hash,
    sanitize_for_ai,
    MockLLMAdapter,
)
from app.schemas.api import Priority


class TestComputeInputHash:
    """Tests for input hash computation."""
    
    def test_same_input_same_hash(self):
        """Same input should produce same hash."""
        data = {"chart_id": "test", "values": [1, 2, 3]}
        hash1 = compute_input_hash(data)
        hash2 = compute_input_hash(data)
        assert hash1 == hash2
    
    def test_different_input_different_hash(self):
        """Different input should produce different hash."""
        data1 = {"chart_id": "test", "values": [1, 2, 3]}
        data2 = {"chart_id": "test", "values": [1, 2, 4]}
        hash1 = compute_input_hash(data1)
        hash2 = compute_input_hash(data2)
        assert hash1 != hash2
    
    def test_order_independent(self):
        """Dictionary key order should not affect hash."""
        data1 = {"a": 1, "b": 2}
        data2 = {"b": 2, "a": 1}
        hash1 = compute_input_hash(data1)
        hash2 = compute_input_hash(data2)
        assert hash1 == hash2
    
    def test_returns_string(self):
        """Hash should be a string."""
        data = {"test": "value"}
        result = compute_input_hash(data)
        assert isinstance(result, str)
        assert len(result) == 64  # SHA-256 hex digest


class TestSanitizeForAI:
    """Tests for PII sanitization."""
    
    def test_removes_email(self):
        """Should remove email field."""
        data = {"email": "test@example.com", "value": 123}
        result = sanitize_for_ai(data)
        assert "email" not in result
        assert result["value"] == 123
    
    def test_removes_name_fields(self):
        """Should remove name fields."""
        data = {"name": "John", "nameFa": "حسن", "nameEn": "Hassan", "score": 85}
        result = sanitize_for_ai(data)
        assert "name" not in result
        assert "nameFa" not in result
        assert "nameEn" not in result
        assert result["score"] == 85
    
    def test_handles_nested_data(self):
        """Should handle nested dictionaries."""
        data = {
            "wrestler": {
                "email": "test@example.com",
                "metrics": {
                    "score": 90,
                    "name": "Test",
                },
            },
        }
        result = sanitize_for_ai(data)
        assert "email" not in result.get("wrestler", {})
        assert result["wrestler"]["metrics"]["score"] == 90
    
    def test_handles_lists(self):
        """Should handle lists of dictionaries."""
        data = {
            "items": [
                {"email": "a@b.com", "value": 1},
                {"email": "c@d.com", "value": 2},
            ]
        }
        result = sanitize_for_ai(data)
        for item in result["items"]:
            assert "email" not in item


class TestMockLLMAdapter:
    """Tests for mock LLM adapter."""
    
    @pytest.mark.asyncio
    async def test_generate_chart_insight(self):
        """Should generate mock chart insight."""
        adapter = MockLLMAdapter()
        result = await adapter.generate_chart_insight(
            chart_id="test-chart",
            chart_data={"labels": ["A", "B"], "values": [80, 90]},
            locale="en-US",
        )
        assert result.summary
        assert len(result.patterns) > 0
        assert len(result.recommendations) > 0
    
    @pytest.mark.asyncio
    async def test_generate_chart_insight_farsi(self):
        """Should generate Farsi insight."""
        adapter = MockLLMAdapter()
        result = await adapter.generate_chart_insight(
            chart_id="test-chart",
            chart_data={"labels": ["A", "B"], "values": [80, 90]},
            locale="fa-IR",
        )
        # Check for Persian characters in summary
        assert any(ord(c) > 1500 for c in result.summary)
    
    @pytest.mark.asyncio
    async def test_generate_advanced_insight(self):
        """Should generate mock advanced insight."""
        adapter = MockLLMAdapter()
        result = await adapter.generate_advanced_insight(
            section="body_composition",
            chart_id="weight-trend",
            chart_data={
                "series": [
                    {"name": "weight", "points": [{"date": "2025-01-01", "value": 85}]}
                ]
            },
            context=None,
            locale="en-US",
        )
        assert result.summary
        assert 0 <= result.confidence <= 1
    
    @pytest.mark.asyncio
    async def test_generate_training_program(self):
        """Should generate mock training program."""
        adapter = MockLLMAdapter()
        result = await adapter.generate_training_program(
            goal="strength",
            target_date="2025-02-01",
        )
        assert result.date == "2025-02-01"
        assert result.title
        assert len(result.blocks) > 0
        assert len(result.aiRecommendations) > 0
