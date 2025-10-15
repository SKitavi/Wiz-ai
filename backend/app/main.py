from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="WizAI API",
    version="0.1.0",
    description="Intelligent Student Life Organizer Backend"
)

# Allow CORS (you’ll refine this later)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "WizAI API"}
