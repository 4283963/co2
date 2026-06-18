from fastapi import APIRouter, HTTPException
from app.schemas.dispatch import DispatchCalculateRequest, DispatchCalculateResponse
from app.core.optimizer import DispatchOptimizer

router = APIRouter(prefix="/dispatch", tags=["配水调度"])

optimizer = DispatchOptimizer()


@router.post(
    "/calculate",
    response_model=DispatchCalculateResponse,
    summary="计算最优配水方案",
    description="根据总需水量和各泵站参数，计算最省电的配水方案"
)
async def calculate_dispatch(request: DispatchCalculateRequest):
    try:
        result = optimizer.calculate_optimal_dispatch(
            total_demand=request.total_demand,
            pump_stations=request.pump_stations
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"计算出错: {str(e)}")
