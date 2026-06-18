import numpy as np
from typing import List
from app.schemas.dispatch import PumpStation, DispatchResultItem, DispatchCalculateResponse

_FEASIBILITY_TOLERANCE = 1e-6


class DispatchOptimizer:
    def __init__(self):
        self.algorithm_name = "linear_weighted_optimization"

    def calculate_optimal_dispatch(
        self,
        total_demand: float,
        pump_stations: List[PumpStation]
    ) -> DispatchCalculateResponse:
        self._validate_and_check_feasibility(total_demand, pump_stations)

        n = len(pump_stations)
        ids = [ps.id for ps in pump_stations]
        names = [ps.name for ps in pump_stations]
        min_flows = np.array([ps.min_flow for ps in pump_stations], dtype=np.float64)
        max_flows = np.array([ps.max_flow for ps in pump_stations], dtype=np.float64)
        power_coeffs = np.array([ps.power_coefficient for ps in pump_stations], dtype=np.float64)

        allocated_flows = self._greedy_optimize(
            total_demand, min_flows, max_flows, power_coeffs
        )

        self._verify_allocation(total_demand, allocated_flows, min_flows, max_flows, names)

        power_consumptions = allocated_flows * power_coeffs
        total_power = float(np.sum(power_consumptions))

        results = []
        for i in range(n):
            results.append(DispatchResultItem(
                id=ids[i],
                name=names[i],
                allocated_flow=float(allocated_flows[i]),
                power_consumption=float(power_consumptions[i])
            ))

        return DispatchCalculateResponse(
            total_demand=total_demand,
            total_power_consumption=total_power,
            results=results,
            algorithm=self.algorithm_name
        )

    def _validate_and_check_feasibility(
        self, total_demand: float, pump_stations: List[PumpStation]
    ) -> None:
        if total_demand <= 0:
            raise ValueError("总需水量必须大于0")
        if not pump_stations:
            raise ValueError("泵站列表不能为空")

        total_min = 0.0
        total_max = 0.0
        for ps in pump_stations:
            if ps.min_flow < 0:
                raise ValueError(f"泵站 {ps.name} 的最低出水量不能为负数")
            if ps.max_flow < ps.min_flow:
                raise ValueError(f"泵站 {ps.name} 的最高出水量不能小于最低出水量")
            if ps.power_coefficient <= 0:
                raise ValueError(f"泵站 {ps.name} 的单位耗电系数必须大于0")
            total_min += ps.min_flow
            total_max += ps.max_flow

        if total_demand < total_min - _FEASIBILITY_TOLERANCE:
            raise ValueError(
                f"当前泵站配置无法满足总需水量：总需水量({total_demand})"
                f"小于所有泵站最低出水量之和({total_min})"
            )
        if total_demand > total_max + _FEASIBILITY_TOLERANCE:
            raise ValueError(
                "当前泵站配置无法满足总需水量：总需水量({})大于所有泵站最高出水量之和({})".format(
                    total_demand, total_max
                )
            )

    def _greedy_optimize(
        self,
        total_demand: float,
        min_flows: np.ndarray,
        max_flows: np.ndarray,
        power_coeffs: np.ndarray
    ) -> np.ndarray:
        allocated = min_flows.copy()
        remaining = total_demand - float(np.sum(min_flows))
        sorted_indices = np.argsort(power_coeffs)

        for idx in sorted_indices:
            if remaining <= _FEASIBILITY_TOLERANCE:
                break
            capacity = max_flows[idx] - min_flows[idx]
            add_flow = min(capacity, remaining)
            allocated[idx] += add_flow
            remaining -= add_flow

        return allocated

    def _verify_allocation(
        self,
        total_demand: float,
        allocated: np.ndarray,
        min_flows: np.ndarray,
        max_flows: np.ndarray,
        names: List[str]
    ) -> None:
        allocated_sum = float(np.sum(allocated))
        if abs(allocated_sum - total_demand) > _FEASIBILITY_TOLERANCE:
            raise ValueError(
                "当前泵站配置无法满足总需水量：分配总量({})与需水量({})不一致".format(
                    allocated_sum, total_demand
                )
            )
        for i in range(len(allocated)):
            if allocated[i] < min_flows[i] - _FEASIBILITY_TOLERANCE:
                raise ValueError(
                    "当前泵站配置无法满足总需水量：泵站 {} 分配量低于最低限额".format(names[i])
                )
            if allocated[i] > max_flows[i] + _FEASIBILITY_TOLERANCE:
                raise ValueError(
                    "当前泵站配置无法满足总需水量：泵站 {} 分配量超过最高限额".format(names[i])
                )
