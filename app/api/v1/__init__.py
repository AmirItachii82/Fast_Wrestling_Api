"""API v1 router initialization."""

from fastapi import APIRouter

from app.api.v1 import auth, wrestlers, overview, body_composition, bloodwork
from app.api.v1 import recovery, supplements, performance, training, calendar
from app.api.v1 import teams, ai, scores, legacy_data

router = APIRouter()

# Include all routers
router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
router.include_router(wrestlers.router, prefix="/wrestlers", tags=["Wrestlers"])
router.include_router(overview.router, prefix="/wrestlers", tags=["Overview"])
router.include_router(body_composition.router, prefix="/wrestlers", tags=["Body Composition"])
router.include_router(bloodwork.router, prefix="/wrestlers", tags=["Bloodwork"])
router.include_router(recovery.router, prefix="/wrestlers", tags=["Recovery"])
router.include_router(supplements.router, prefix="/wrestlers", tags=["Supplements"])
router.include_router(performance.router, prefix="/wrestlers", tags=["Performance"])
router.include_router(training.router, prefix="/wrestlers", tags=["Training Program"])
router.include_router(calendar.router, prefix="/wrestlers", tags=["Calendar"])
router.include_router(teams.router, prefix="/teams", tags=["Teams"])
router.include_router(ai.router, prefix="/ai", tags=["AI"])
router.include_router(scores.router, prefix="/wrestlers", tags=["Scores"])
router.include_router(legacy_data.router, prefix="/data", tags=["Legacy Data"])
