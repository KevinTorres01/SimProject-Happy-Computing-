"""
Configuracion de la simulacion de Happy Computing.

Incluye un enum para las 3 interpretaciones del enunciado
'distribuye Poisson con lambda=20 minutos'.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import List


class ArrivalInterpretation(Enum):
    """Tres interpretaciones de 'distribuye Poisson con lambda=20'."""
    EXPONENTIAL_MEAN_20 = "A"       # Exp(1/20), media=20 min
    EXPONENTIAL_RATE_20 = "B"       # Exp(20), media=1/20 min = 3 seg
    POISSON_DISCRETE_20 = "C"       # Poisson(20), media=20 min (entero)


@dataclass
class HappyConfig:
    """Parametros de simulacion de Happy Computing."""

    # Duracion de la jornada laboral (minutos)
    total_time: float = 480.0   # 8 horas

    # Interpretacion del arribo de clientes
    arrival_interpretation: ArrivalInterpretation = ArrivalInterpretation.EXPONENTIAL_MEAN_20

    # Parametro lambda del enunciado (minutos)
    arrival_lambda: float = 20.0

    # Probabilidades de tipo de servicio [garantia, pago, cambio, venta]
    service_probabilities: List[float] = field(
        default_factory=lambda: [0.45, 0.25, 0.10, 0.20]
    )

    # Precios por tipo de servicio
    prices: List[float] = field(
        default_factory=lambda: [0.0, 350.0, 500.0, 750.0]
    )

    # Tiempo de servicio del vendedor: Normal(mu, sigma)
    vendedor_service_mean: float = 5.0    # minutos
    vendedor_service_std: float = 2.0     # minutos

    # Tiempo de servicio del tecnico: Exponencial con media (minutos)
    tecnico_service_mean: float = 20.0

    # Tiempo de servicio del especializado para cambio: Exponencial con media (minutos)
    especializado_service_mean: float = 15.0

    # Cantidad de empleados
    num_vendedores: int = 2
    num_tecnicos: int = 3
    num_especializado: int = 1

    # Replicas para analisis estadistico
    num_replications: int = 30

    # Precision deseada para el error estandar (en pesos)
    precision_d: float = 500.0

    # Semilla aleatoria (None = no fijar)
    seed: int = None
