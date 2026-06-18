from pydantic import BaseModel, Field
from typing import List


class PumpStation(BaseModel):
    id: str = Field(..., description="泵站唯一标识")
    name: str = Field(..., description="泵站名称")
    min_flow: float = Field(..., ge=0, description="最低出水量（立方米/天）")
    max_flow: float = Field(..., ge=0, description="最高出水量（立方米/天）")
    power_coefficient: float = Field(..., gt=0, description="单位耗电系数（度/立方米）")


class DispatchCalculateRequest(BaseModel):
    total_demand: float = Field(..., gt=0, description="总需水量（立方米/天）")
    pump_stations: List[PumpStation] = Field(..., min_length=1, description="泵站列表")


class DispatchResultItem(BaseModel):
    id: str = Field(..., description="泵站唯一标识")
    name: str = Field(..., description="泵站名称")
    allocated_flow: float = Field(..., description="分配的出水量（立方米/天）")
    power_consumption: float = Field(..., description="预计耗电量（度）")


class DispatchCalculateResponse(BaseModel):
    total_demand: float = Field(..., description="总需水量（立方米/天）")
    total_power_consumption: float = Field(..., description="总耗电量（度）")
    results: List[DispatchResultItem] = Field(..., description="各泵站配水方案")
    algorithm: str = Field(default="linear_weighted_optimization", description="使用的优化算法")
