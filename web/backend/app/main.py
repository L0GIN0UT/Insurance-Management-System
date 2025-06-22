from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer
import uvicorn

from app.core.config import get_settings
from app.routers import contracts, claims, clients, analytics, users, products
from app.utils.auth import verify_token
from app.db.database import create_tables

# Initialize FastAPI app
app = FastAPI(
    title="Insurance Management System API",
    description="Backend API for Insurance Company Management System",
    version="1.0.0"
)

# Security
security = HTTPBearer()

# CORS middleware - allow all origins for development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create database tables on startup
@app.on_event("startup")
async def startup_event():
    create_tables()

# Include routers
app.include_router(contracts.router, prefix="/api/v1/contracts", tags=["contracts"])
app.include_router(claims.router, prefix="/api/v1/claims", tags=["claims"])
app.include_router(clients.router, prefix="/api/v1/clients", tags=["clients"])
app.include_router(analytics.router, prefix="/api/v1/analytics", tags=["analytics"])
app.include_router(users.router, prefix="/api/v1/users", tags=["users"])
app.include_router(products.router, prefix="/api/v1/products", tags=["products"])

@app.get("/")
async def root():
    return {"message": "Insurance Management System API"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "insurance-backend"}

if __name__ == "__main__":
    settings = get_settings()
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    ) 