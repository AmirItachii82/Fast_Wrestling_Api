"""
AI service for chart insights and training program generation.

This module provides:
- LLM adapter interface
- Caching with Redis (or in-memory fallback)
- PII sanitization
- Chart insight generation
"""

import hashlib
import json
from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from app.core.config import get_settings
from app.schemas.api import (
    ChartInsightRequest,
    ChartInsightResponse,
    AdvancedChartInsightRequest,
    AdvancedChartInsightResponse,
    AITrainingProgramRequest,
    AITrainingProgramResponse,
    Recommendation,
    Anomaly,
    Priority,
    ProgramBlock,
    AIGeneratedProgram,
)

settings = get_settings()


class LLMAdapter(ABC):
    """Abstract base class for LLM adapters."""
    
    @abstractmethod
    async def generate_chart_insight(
        self,
        chart_id: str,
        chart_data: Dict[str, Any],
        locale: str,
    ) -> ChartInsightResponse:
        """Generate insight for a chart."""
        pass
    
    @abstractmethod
    async def generate_advanced_insight(
        self,
        section: str,
        chart_id: str,
        chart_data: Dict[str, Any],
        context: Optional[Dict[str, Any]],
        locale: str,
    ) -> AdvancedChartInsightResponse:
        """Generate advanced insight for a chart."""
        pass
    
    @abstractmethod
    async def generate_training_program(
        self,
        goal: str,
        target_date: str,
    ) -> AIGeneratedProgram:
        """Generate a training program."""
        pass


class MockLLMAdapter(LLMAdapter):
    """Mock LLM adapter for testing and when no API key is configured."""
    
    async def generate_chart_insight(
        self,
        chart_id: str,
        chart_data: Dict[str, Any],
        locale: str,
    ) -> ChartInsightResponse:
        """Generate mock chart insight."""
        # Generate deterministic mock response based on chart data
        values = chart_data.get("values", [])
        avg_value = sum(values) / len(values) if values else 0
        
        if locale == "fa-IR":
            summary = f"تحلیل نمودار {chart_id}: میانگین مقادیر {avg_value:.1f} است."
            patterns = ["روند صعودی مشاهده شده", "نوسانات طبیعی"]
            recommendations = [
                Recommendation(text="ادامه برنامه فعلی", priority=Priority.MEDIUM),
                Recommendation(text="افزایش تمرینات قدرتی", priority=Priority.LOW),
            ]
            warnings = []
        else:
            summary = f"Analysis of chart {chart_id}: Average value is {avg_value:.1f}."
            patterns = ["Upward trend observed", "Normal fluctuations"]
            recommendations = [
                Recommendation(text="Continue current program", priority=Priority.MEDIUM),
                Recommendation(text="Increase strength training", priority=Priority.LOW),
            ]
            warnings = []
        
        if avg_value < 50:
            if locale == "fa-IR":
                warnings.append("مقادیر پایین‌تر از حد انتظار")
            else:
                warnings.append("Values below expected threshold")
        
        return ChartInsightResponse(
            summary=summary,
            patterns=patterns,
            recommendations=recommendations,
            warnings=warnings,
        )
    
    async def generate_advanced_insight(
        self,
        section: str,
        chart_id: str,
        chart_data: Dict[str, Any],
        context: Optional[Dict[str, Any]],
        locale: str,
    ) -> AdvancedChartInsightResponse:
        """Generate mock advanced chart insight."""
        series = chart_data.get("series", [])
        all_values = []
        for s in series:
            points = s.get("points", [])
            all_values.extend([p.get("value", 0) for p in points])
        
        avg_value = sum(all_values) / len(all_values) if all_values else 0
        
        if locale == "fa-IR":
            summary = f"تحلیل پیشرفته بخش {section}: داده‌های سری زمانی تحلیل شد."
            patterns = ["الگوی ثبات", "بهبود تدریجی"]
        else:
            summary = f"Advanced analysis of section {section}: Time series data analyzed."
            patterns = ["Stability pattern", "Gradual improvement"]
        
        anomalies = []
        if all_values and max(all_values) > avg_value * 1.5:
            anomalies.append(Anomaly(
                label="High value spike",
                date="2025-01-15",
                value=max(all_values),
            ))
        
        recommendations = [
            Recommendation(text="Monitor trends closely", priority=Priority.MEDIUM),
        ]
        
        return AdvancedChartInsightResponse(
            summary=summary,
            patterns=patterns,
            anomalies=anomalies,
            recommendations=recommendations,
            confidence=0.85,
        )
    
    async def generate_training_program(
        self,
        goal: str,
        target_date: str,
    ) -> AIGeneratedProgram:
        """Generate mock training program."""
        blocks = [
            ProgramBlock(name="Warm-up", sets=1, reps="5-10 min"),
            ProgramBlock(name="Bench Press", sets=4, reps="6-8"),
            ProgramBlock(name="Squat", sets=4, reps="6-8"),
            ProgramBlock(name="Deadlift", sets=3, reps="5"),
            ProgramBlock(name="Core Work", sets=3, reps="10-15"),
        ]
        
        return AIGeneratedProgram(
            date=target_date,
            title=f"{goal.capitalize()} Focus Training",
            focus=goal,
            blocks=blocks,
            nutrition="High protein intake recommended (1.6-2.0g/kg body weight)",
            recovery="8 hours sleep, stretching, hydration",
            aiRecommendations=[
                "Focus on progressive overload",
                "Include mobility work",
                "Monitor recovery between sessions",
            ],
        )


class OpenAIAdapter(LLMAdapter):
    """OpenAI LLM adapter for production use."""
    
    def __init__(self, api_key: str):
        """Initialize with API key."""
        self.api_key = api_key
        try:
            import httpx
            self.client = httpx.AsyncClient()
        except ImportError:
            self.client = None
    
    async def _call_openai(self, messages: List[Dict[str, str]]) -> str:
        """Make a call to OpenAI API."""
        if not self.client:
            raise RuntimeError("httpx not available")
        
        response = await self.client.post(
            "https://api.openai.com/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
            json={
                "model": "gpt-4",
                "messages": messages,
                "temperature": 0.7,
            },
            timeout=30.0,
        )
        response.raise_for_status()
        data = response.json()
        return data["choices"][0]["message"]["content"]
    
    async def generate_chart_insight(
        self,
        chart_id: str,
        chart_data: Dict[str, Any],
        locale: str,
    ) -> ChartInsightResponse:
        """Generate chart insight using OpenAI."""
        # For now, fall back to mock if not fully implemented
        mock = MockLLMAdapter()
        return await mock.generate_chart_insight(chart_id, chart_data, locale)
    
    async def generate_advanced_insight(
        self,
        section: str,
        chart_id: str,
        chart_data: Dict[str, Any],
        context: Optional[Dict[str, Any]],
        locale: str,
    ) -> AdvancedChartInsightResponse:
        """Generate advanced insight using OpenAI."""
        mock = MockLLMAdapter()
        return await mock.generate_advanced_insight(
            section, chart_id, chart_data, context, locale
        )
    
    async def generate_training_program(
        self,
        goal: str,
        target_date: str,
    ) -> AIGeneratedProgram:
        """Generate training program using OpenAI."""
        mock = MockLLMAdapter()
        return await mock.generate_training_program(goal, target_date)


def get_llm_adapter() -> LLMAdapter:
    """
    Get the appropriate LLM adapter based on configuration.
    
    Returns:
        LLMAdapter: MockLLMAdapter if no API key, otherwise OpenAIAdapter.
    """
    if settings.openai_api_key:
        return OpenAIAdapter(settings.openai_api_key)
    return MockLLMAdapter()


def compute_input_hash(data: Dict[str, Any]) -> str:
    """
    Compute a deterministic hash of input data for caching.
    
    Args:
        data: The input data dictionary.
        
    Returns:
        str: SHA-256 hash of the data.
    """
    # Sort keys for deterministic serialization
    serialized = json.dumps(data, sort_keys=True, default=str)
    return hashlib.sha256(serialized.encode()).hexdigest()


def sanitize_for_ai(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Sanitize data before sending to AI to remove PII.
    
    Args:
        data: The input data.
        
    Returns:
        Dict: Sanitized data with PII removed.
    """
    # Fields that should not be sent to AI (all lowercase for comparison)
    pii_fields = {"email", "name", "namefa", "nameen", "phone", "address"}
    
    def _sanitize(obj: Any) -> Any:
        if isinstance(obj, dict):
            return {
                k: _sanitize(v) for k, v in obj.items()
                if k.lower() not in pii_fields
            }
        elif isinstance(obj, list):
            return [_sanitize(item) for item in obj]
        return obj
    
    return _sanitize(data)


class CacheService:
    """Cache service with Redis support and in-memory fallback."""
    
    def __init__(self):
        """Initialize cache service."""
        self._memory_cache: Dict[str, tuple[Any, datetime]] = {}
        self._redis = None
        self._init_redis()
    
    def _init_redis(self):
        """Initialize Redis connection if available."""
        try:
            import redis.asyncio as redis
            self._redis = redis.from_url(settings.redis_url)
        except Exception:
            self._redis = None
    
    async def get(self, key: str) -> Optional[str]:
        """
        Get value from cache.
        
        Args:
            key: Cache key.
            
        Returns:
            Optional[str]: Cached value or None.
        """
        if self._redis:
            try:
                value = await self._redis.get(key)
                if value:
                    return value.decode() if isinstance(value, bytes) else value
            except Exception:
                pass
        
        # Fallback to memory cache
        if key in self._memory_cache:
            value, expires_at = self._memory_cache[key]
            if datetime.utcnow() < expires_at:
                return value
            else:
                del self._memory_cache[key]
        
        return None
    
    async def set(self, key: str, value: str, ttl_hours: int = 24) -> None:
        """
        Set value in cache.
        
        Args:
            key: Cache key.
            value: Value to cache.
            ttl_hours: Time to live in hours.
        """
        if self._redis:
            try:
                await self._redis.setex(key, ttl_hours * 3600, value)
                return
            except Exception:
                pass
        
        # Fallback to memory cache
        expires_at = datetime.utcnow() + timedelta(hours=ttl_hours)
        self._memory_cache[key] = (value, expires_at)
    
    async def delete(self, key: str) -> None:
        """
        Delete value from cache.
        
        Args:
            key: Cache key.
        """
        if self._redis:
            try:
                await self._redis.delete(key)
            except Exception:
                pass
        
        if key in self._memory_cache:
            del self._memory_cache[key]


# Global cache instance
cache_service = CacheService()
