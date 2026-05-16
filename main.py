"""
Punto de entrada: Simulacion de Happy Computing.

Ejecuta la simulacion del taller de reparaciones electronicas
y reporta las metricas estadisticas de la jornada laboral.
"""

from src.config import HappyConfig
from src.stats import run_replications


def print_sep():
    print("=" * 70)


def print_results(results: dict):
    print(f"  Replicas ejecutadas:            {results['num_replications']}")
    print(f"  Clientes llegados (promedio):   {results['avg_customers_arrived']:.1f}")
    print(f"  Clientes atendidos (promedio):  {results['avg_customers_served']:.1f}")
    print(f"  Ganancia promedio del dia:      ${results['mean_revenue']:.2f}")
    print(f"  Desviacion estandar:            ${results['std_revenue']:.2f}")
    print(f"  Error estandar:                 ${results['se_revenue']:.2f}")
    print(f"  Tiempo promedio de espera:      {results['avg_wait_time']:.2f} min")
    print(f"  Tiempo promedio en sistema:     {results['avg_system_time']:.2f} min")


def main():
    print_sep()
    print("  HAPPY COMPUTING - Simulacion de Eventos Discretos")
    print("  Problema 4 - Taller de reparacion de electronica")
    print_sep()

    config = HappyConfig(num_replications=30, seed=42)

    print("\n  Ejecutando simulacion...")
    results = run_replications(config)

    print("\n  RESULTADOS")
    print(f"  {'-' * 40}")
    print_results(results)
    print_sep()


if __name__ == "__main__":
    main()
