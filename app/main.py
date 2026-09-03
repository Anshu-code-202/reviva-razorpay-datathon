from fastapi import FastAPI

from app.api.routes.incidents import router as incidents_router
from app.api.routes.eligibility import router as eligibility_router
from app.api.routes.approvals import router as approvals_router
from app.api.routes.recovery import router as recovery_router

from fastapi.middleware.cors import CORSMiddleware

from app.api.routes.simulator import router as simulator_router

app = FastAPI(
    title="REVIVA API",
    description="Autonomous Payment Recovery & Revenue Intelligence",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



app.include_router(incidents_router)
app.include_router(eligibility_router)
app.include_router(approvals_router)
app.include_router(recovery_router)
app.include_router(simulator_router)


@app.get("/health")
def health():
    return {"status": "ok"}
