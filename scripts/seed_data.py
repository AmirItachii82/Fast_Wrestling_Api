"""
Seed script for populating initial data.

This script creates:
- Sample users (admin, coach, athlete)
- Sample team
- Sample wrestlers with metrics
"""

import asyncio
from datetime import date, datetime, timedelta
import uuid

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlmodel import SQLModel

from app.core.config import get_settings
from app.core.security import get_password_hash
from app.models import (
    User,
    UserRole,
    Team,
    Wrestler,
    WrestlerStatus,
    OverviewMetrics,
    OverviewSeries,
    BodyCompositionMetrics,
    BloodworkMetrics,
    RecoveryMetrics,
    SupplementsMetrics,
    PerformanceMetrics,
    SectionScore,
    Grade,
)

settings = get_settings()


async def seed_database():
    """Seed the database with sample data."""
    engine = create_async_engine(settings.database_url, echo=True)
    
    async_session = sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )
    
    async with async_session() as session:
        # Create team
        team = Team(
            id=str(uuid.uuid4()),
            name="Iranian National Wrestling Team",
        )
        session.add(team)
        
        # Create wrestlers
        wrestlers_data = [
            {
                "name_fa": "حسن یزدانی",
                "name_en": "Hassan Yazdani",
                "weight_class": 86,
                "status": WrestlerStatus.COMPETITION_READY,
            },
            {
                "name_fa": "امیرحسین زارع",
                "name_en": "Amirhossein Zare",
                "weight_class": 125,
                "status": WrestlerStatus.NORMAL,
            },
            {
                "name_fa": "رحمان عموزاد",
                "name_en": "Rahman Amouzad",
                "weight_class": 65,
                "status": WrestlerStatus.ATTENTION,
            },
        ]
        
        wrestlers = []
        for data in wrestlers_data:
            wrestler = Wrestler(
                id=str(uuid.uuid4()),
                team_id=team.id,
                **data,
            )
            session.add(wrestler)
            wrestlers.append(wrestler)
        
        # Create users
        # Admin user
        admin_user = User(
            id=str(uuid.uuid4()),
            email="admin@wrestling.com",
            password_hash=get_password_hash("admin123"),
            name="System Admin",
            role=UserRole.ADMIN,
        )
        session.add(admin_user)
        
        # Coach user
        coach_user = User(
            id=str(uuid.uuid4()),
            email="coach@wrestling.com",
            password_hash=get_password_hash("coach123"),
            name="Head Coach",
            role=UserRole.COACH,
            team_id=team.id,
        )
        session.add(coach_user)
        
        # Athlete user (linked to first wrestler)
        athlete_user = User(
            id=str(uuid.uuid4()),
            email="athlete@wrestling.com",
            password_hash=get_password_hash("athlete123"),
            name="Hassan Yazdani",
            role=UserRole.ATHLETE,
            wrestler_id=wrestlers[0].id,
        )
        session.add(athlete_user)
        
        await session.flush()
        
        # Add metrics for each wrestler
        for wrestler in wrestlers:
            # Overview metrics
            overview = OverviewMetrics(
                wrestler_id=wrestler.id,
                overall_score=86,
                msi=92,
                mes=78,
                api=420,
                vo2max=55,
                frr=84,
                acs=72,
                bos=4,
            )
            session.add(overview)
            
            # Overview radar chart series
            radar_labels = ["کمر", "سینه", "پاها", "بازوها", "شانه‌ها", "میان‌تنه"]
            radar_values = [92, 85, 78, 48, 80, 55]
            for label, value in zip(radar_labels, radar_values):
                series = OverviewSeries(
                    wrestler_id=wrestler.id,
                    label=label,
                    value=value,
                )
                session.add(series)
            
            # Body composition metrics
            body_comp = BodyCompositionMetrics(
                wrestler_id=wrestler.id,
                weight=wrestler.weight_class,
                body_fat_percent=8.5,
                muscle_mass=76.2,
                bmr=2150,
                power_to_weight=1.92,
                intracellular_water=28.2,
                extracellular_water=14.1,
                visceral_fat_level=7.8,
                phase_angle=7.2,
            )
            session.add(body_comp)
            
            # Bloodwork metrics
            bloodwork = BloodworkMetrics(
                wrestler_id=wrestler.id,
                hemoglobin=16.2,
                hematocrit=47.5,
                testosterone=720,
                status="optimal",
                last_test_date=date.today() - timedelta(days=7),
            )
            session.add(bloodwork)
            
            # Recovery metrics
            recovery = RecoveryMetrics(
                wrestler_id=wrestler.id,
                sleep_quality=88,
                hrv_score=72,
                fatigue_level=22,
                hydration_level=85,
                readiness_score=87,
            )
            session.add(recovery)
            
            # Supplements metrics
            supplements = SupplementsMetrics(
                wrestler_id=wrestler.id,
                adherence_rate=92,
                monthly_progress="+8%",
                performance_corr=0.85,
                total_supplements=8,
                creatine_daily_grams=5,
                protein_daily_grams=180,
                hydration_liters=3.0,
            )
            session.add(supplements)
            
            # Performance metrics
            performance = PerformanceMetrics(
                wrestler_id=wrestler.id,
                bench_max=330,
                squat_max=460,
                deadlift_max=520,
                vo2max=53.7,
                body_fat_percent=13.5,
                performance_score=87,
            )
            session.add(performance)
            
            # Section scores
            sections = [
                ("overview", 86),
                ("body_composition", 84),
                ("bloodwork", 88),
                ("recovery", 87),
                ("supplements", 80),
                ("bodybuilding_performance", 87),
            ]
            for section_key, score in sections:
                section_score = SectionScore(
                    wrestler_id=wrestler.id,
                    section_key=section_key,
                    score=score,
                    grade=Grade.GOOD if score >= 80 else Grade.WARNING,
                )
                session.add(section_score)
        
        await session.commit()
        
        print("✅ Database seeded successfully!")
        print(f"   - Created team: {team.name}")
        print(f"   - Created {len(wrestlers)} wrestlers")
        print("   - Created users:")
        print(f"     - Admin: admin@wrestling.com / admin123")
        print(f"     - Coach: coach@wrestling.com / coach123")
        print(f"     - Athlete: athlete@wrestling.com / athlete123")


if __name__ == "__main__":
    asyncio.run(seed_database())
