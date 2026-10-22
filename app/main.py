from fastapi import FastAPI

app = FastAPI(
    title="OpsPilot AI",
    description="Intelligent AIOps and Incident Response Platform",
    version="1.0.0",
)


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
