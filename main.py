"""
Punto de entrada: Simulacion de Happy Computing.

Ejecuta las 3 interpretaciones de 'distribuye Poisson con lambda=20'
y compara los resultados.
"""

from src.config import HappyConfig, ArrivalInterpretation
from src.stats import run_replications


def print_sep():
    print("=" * 70)


def print_results(title: str, results: dict):
    print(f"\n  {title}")
    print(f"  {'-' * len(title)}")
    print(f"  Replicas ejecutadas:            {results['num_replications']}")
    print(f"  Clientes llegados (promedio):   {results['avg_customers_arrived']:.1f}")
    print(f"  Clientes atendidos (promedio):  {results['avg_customers_served']:.1f}")
    print(f"  Ganancia promedio del dia:      ${results['mean_revenue']:.2f}")
    print(f"  Desviacion estandar:            ${results['std_revenue']:.2f}")
    print(f"  Error estandar:                 ${results['se_revenue']:.2f}")
    print(f"  Tiempo promedio de espera:      {results['avg_wait_time']:.2f} min")
    print(f"  Tiempo promedio en sistema:     {results['avg_system_time']:.2f} min")


def print_comparison(all_results):
    print_sep()
    print("  COMPARACION DE INTERPRETACIONES")
    print_sep()

    header = f"  {'Metrica':<35} {'Interp A':>12} {'Interp B':>12} {'Interp C':>12}"
    print(f"\n{header}")
    print(f"  {'-'*35} {'-'*12} {'-'*12} {'-'*12}")

    a = all_results["A"]
    b = all_results["B"]
    c = all_results["C"]

    metrics = [
        ("Clientes llegados/dia", "avg_customers_arrived", ".1f"),
        ("Clientes atendidos/dia", "avg_customers_served", ".1f"),
        ("Ganancia ($)", "mean_revenue", ".0f"),
        ("Espera promedio (min)", "avg_wait_time", ".2f"),
        ("Tiempo en sistema (min)", "avg_system_time", ".2f"),
    ]

    for label, key, fmt in metrics:
        va = format(a[key], fmt)
        vb = format(b[key], fmt)
        vc = format(c[key], fmt)
        print(f"  {label:<35} {va:>12} {vb:>12} {vc:>12}")


def main():
    print_sep()
    print("  HAPPY COMPUTING - Simulacion de Eventos Discretos")
    print("  Problema 4 - Taller de reparacion de electronica")
    print("  Analisis de 3 interpretaciones del enunciado")
    print_sep()

    interpretations = [
        (ArrivalInterpretation.EXPONENTIAL_MEAN_20,
         "A: Exponencial con media = 20 min (interpretacion probable)"),
        (ArrivalInterpretation.EXPONENTIAL_RATE_20,
         "B: Exponencial con tasa = 20/min (media = 3 seg)"),
        (ArrivalInterpretation.POISSON_DISCRETE_20,
         "C: Poisson(20) discreto (media = 20 min, entero)"),
    ]

    all_results = {}
    for interp, description in interpretations:
        config = HappyConfig(
            arrival_interpretation=interp,
            num_replications=30,
            seed=42,
        )
        print(f"\n  Ejecutando Interpretacion {interp.value}: ...")
        results = run_replications(config)
        all_results[interp.value] = results
        print_results(description, results)

    print_comparison(all_results)

    print(f"\n  CONCLUSIONES:")
    print(f"  {'-' * 60}")
    print(f"  1. La Interpretacion B genera un volumen de clientes absurdo")
    print(f"     (~9,600/dia con media de 3 seg entre llegadas).")
    print(f"     Esto satura completamente el sistema.")
    print()
    print(f"  2. Las Interpretaciones A y C producen resultados similares")
    print(f"     (~24 clientes/dia) y son fisicamente razonables para")
    print(f"     un taller de reparaciones.")
    print()
    print(f"  3. La diferencia entre A (continua) y C (discreta) es minima,")
    print(f"     ya que Poisson(20) tiene varianza=20 (std~4.5 min) y media")
    print(f"     identica a la Exponencial en A.")
    print()
    print(f"  4. El enunciado dice 'distribuye Poisson' pero la distribucion")
    print(f"     Poisson es discreta y modela conteos, no tiempos.")
    print(f"     La interpretacion correcta es probablemente A:")
    print(f"     un proceso de Poisson donde los inter-arribos distribuyen")
    print(f"     Exponencial con media = 20 minutos.")
    print()
    print_sep()


if __name__ == "__main__":
    main()
