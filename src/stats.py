"""
Analisis estadistico de los resultados de simulacion.

Referencia: Capitulo 4 - Temas de Simulacion (UH)
Calculo de media muestral, varianza y criterio de parada.
"""

import math
import random
from typing import List, Dict

from src.des_engine import DESEngine
from src.model import HappyComputingModel
from src.config import HappyConfig


def sample_mean(values: List[float]) -> float:
    """Calcula la media muestral: X_bar = sum(X_i) / n"""
    return sum(values) / len(values)


def sample_variance(values: List[float]) -> float:
    """Calcula la varianza muestral: S^2 = sum((X_i - X_bar)^2) / (n-1)"""
    mean = sample_mean(values)
    return sum((x - mean) ** 2 for x in values) / (len(values) - 1)


def sample_std(values: List[float]) -> float:
    """Calcula la desviacion estandar muestral."""
    return math.sqrt(sample_variance(values))


def standard_error(values: List[float]) -> float:
    """Calcula el error estandar: S / sqrt(n)"""
    return sample_std(values) / math.sqrt(len(values))


def run_single_simulation(config: HappyConfig) -> Dict:
    """Ejecuta una sola corrida de simulacion."""
    engine = DESEngine()
    model = HappyComputingModel(config)
    return engine.run(model)


def run_replications(config: HappyConfig) -> Dict:
    """
    Ejecuta multiples replicas de la simulacion.

    Metrica principal: total_revenue (ganancia del dia).
    Continua hasta que el error estandar sea menor a config.precision_d.
    """
    results = []
    revenue_values = []

    for i in range(config.num_replications):
        if config.seed is not None:
            random.seed(config.seed + i)
        result = run_single_simulation(config)
        results.append(result)
        revenue_values.append(result["total_revenue"])

    # Continuar si el error estandar es mayor al deseado
    i = config.num_replications
    while len(revenue_values) > 1 and standard_error(revenue_values) >= config.precision_d:
        if config.seed is not None:
            random.seed(config.seed + i)
        result = run_single_simulation(config)
        results.append(result)
        revenue_values.append(result["total_revenue"])
        i += 1
        if i > 500:
            break

    mean_rev = sample_mean(revenue_values)
    std_rev = sample_std(revenue_values) if len(revenue_values) > 1 else 0.0
    se_rev = standard_error(revenue_values) if len(revenue_values) > 1 else 0.0

    return {
        "num_replications": len(results),
        "mean_revenue": mean_rev,
        "std_revenue": std_rev,
        "se_revenue": se_rev,
        "avg_customers_arrived": sample_mean([r["total_arrivals"] for r in results]),
        "avg_customers_served": sample_mean([r["total_served"] for r in results]),
        "avg_wait_time": sample_mean([r["avg_wait_time"] for r in results]),
        "avg_system_time": sample_mean([r["avg_system_time"] for r in results]),
        "raw_results": results,
    }
