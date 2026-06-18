import numpy as np
from typing import List, Tuple, Dict
from app.schemas.dispatch import PumpStation, DispatchResultItem, DispatchCalculateResponse


class DispatchOptimizer:
    def __init__(self):
        self.algorithm_name = "linear_weighted_optimization"

    def calculate_optimal_dispatch(
        self,
        total_demand: float,
        pump_stations: List[PumpStation]
    ) -> DispatchCalculateResponse:
        self._validate_input(total_demand, pump_stations)

        n = len(pump_stations)
        ids = np.array([ps.id for ps in pump_stations])
        names = np.array([ps.name for ps in pump_stations])
        min_flows = np.array([ps.min_flow for ps in pump_stations], dtype=np.float64)
        max_flows = np.array([ps.max_flow for ps in pump_stations], dtype=np.float64)
        power_coeffs = np.array([ps.power_coefficient for ps in pump_stations], dtype=np.float64)

        total_min = np.sum(min_flows)
        total_max = np.sum(max_flows)

        if total_demand < total_min:
            raise ValueError(
                f"总需水量({total_demand})小于所有泵站最低出水量之和({total_min})，无法满足"
            )
        if total_demand > total_max:
            raise ValueError(
                f"总需水量({total_demand})大于所有泵站最高出水量之和({total_max})，无法满足"
            )

        allocated_flows = self._greedy_optimize(
            total_demand, min_flows, max_flows, power_coeffs
        )

        power_consumptions = allocated_flows * power_coeffs
        total_power = float(np.sum(power_consumptions))

        results = []
        for i in range(n):
            results.append(DispatchResultItem(
                id=str(ids[i]),
                name=str(names[i]),
                allocated_flow=float(allocated_flows[i]),
                power_consumption=float(power_consumptions[i])
            ))

        return DispatchCalculateResponse(
            total_demand=total_demand,
            total_power_consumption=total_power,
            results=results,
            algorithm=self.algorithm_name
        )

    def _validate_input(self, total_demand: float, pump_stations: List[PumpStation]) -> None:
        if total_demand <= 0:
            raise ValueError("总需水量必须大于0")
        if not pump_stations:
            raise ValueError("泵站列表不能为空")

        for ps in pump_stations:
            if ps.min_flow < 0:
                raise ValueError(f"泵站 {ps.name} 的最低出水量不能为负数")
            if ps.max_flow < ps.min_flow:
                raise ValueError(f"泵站 {ps.name} 的最高出水量不能小于最低出水量")
            if ps.power_coefficient <= 0:
                raise ValueError(f"泵站 {ps.name} 的单位耗电系数必须大于0")

    def _greedy_optimize(
        self,
        total_demand: float,
        min_flows: np.ndarray,
        max_flows: np.ndarray,
        power_coeffs: np.ndarray
    ) -> np.ndarray:
        n = len(power_coeffs)
        allocated = min_flows.copy()
        remaining = total_demand - np.sum(min_flows)

        sorted_indices = np.argsort(power_coeffs)

        for idx in sorted_indices:
            if remaining <= 0:
                break
            capacity = max_flows[idx] - min_flows[idx]
            add_flow = min(capacity, remaining)
            allocated[idx] += add_flow
            remaining -= add_flow

        return allocated
