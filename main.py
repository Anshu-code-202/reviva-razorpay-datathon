from fastapi import FastAPI

from app.api.routes.incidents import router as incidents_router
from app.api.routes.eligibility import router as eligibility_router
from app.api.routes.approvals import router as approvals_router
from app.api.routes.recovery import router as recovery_router

app = FastAPI(
    title="REVIVA API",
    description="Autonomous Payment Recovery & Revenue Intelligence",
    version="0.1.0",
)


app.include_router(incidents_router)
app.include_router(eligibility_router)
app.include_router(approvals_router)
app.include_router(recovery_router)


@app.get("/health")
def health():
    return {"status": "ok"}

# POST /incidents/detect
#         ↓
# FastAPI
#         ↓
# IncidentDetectionService
#         ↓
# PaymentRepository
#         ↓
# PostgreSQL