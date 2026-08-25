from fastapi import FastAPI

app=FastAPI(
     title="Reviva",
    description="Payment incident detection and resolution platform",
    version="0.1.0",

)

@app.get("/health")
def health_check():
    return{"status ok"}
