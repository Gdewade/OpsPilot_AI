from fastapi import FastAPI
from app.api.incidents import router as incidents_router
from app.api.runbooks import router as runbooks_router

app = FastAPI(
    title="OpsPilot AI",
    description="Intelligent AIOps and Incident Response Platform",
    version="1.0.0",
)

app.include_router(incidents_router)
app.include_router(runbooks_router)

@app.get("/")
def home():
    return {
        "message": "Welcome to OpsPilot AI",
        "status": "running",
    }


@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": "OpsPilot AI",
    }
