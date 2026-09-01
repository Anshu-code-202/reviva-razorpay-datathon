from fastapi import FastAPI

app = FastAPI(
    title="REVIVA API",
    description="Autonomous Payment Recovery & Revenue Intelligence",
    version="0.1.0",
)


@app.get("/health")
def health():
    return {"status": "ok"}