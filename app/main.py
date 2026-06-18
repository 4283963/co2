from fastapi import FastAPI
from app.api.v1.router import api_router

app = FastAPI(
    title="水库配水调度优化 API",
    description="基于 FastAPI 和 NumPy 的水库配水调度优化服务，提供最省电的配水方案计算",
    version="1.0.0"
)

app.include_router(api_router)


@app.get("/", tags=["健康检查"])
async def root():
    return {
        "status": "running",
        "service": "水库配水调度优化服务",
        "version": "1.0.0"
    }


@app.get("/health", tags=["健康检查"])
async def health_check():
    return {"status": "healthy"}
