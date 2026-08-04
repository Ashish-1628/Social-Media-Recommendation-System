from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="GraphConnect API",
    description="Backend API for the GraphConnect social network recommendation system.",
    version="1.0.0"
)

# CORS configuration
origins = [
    "http://localhost:5173", # Vite default
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health", tags=["Health"])
def health_check():
    return {"status": "ok", "message": "GraphConnect API is running."}
