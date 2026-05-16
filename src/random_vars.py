"""
Generacion de variables aleatorias usando el metodo de la transformada inversa.

Referencia: Capitulo 2 - Temas de Simulacion (UH)
Solo se usa random.random() como fuente de U(0,1).
"""

import math
import random


def uniform(a: float, b: float) -> float:
    """
    Genera una variable aleatoria con distribucion Uniforme(a, b).

    X = a + (b - a) * U, donde U ~ Uniform(0, 1)
    Seccion 2.2 del libro.
    """
    u = random.random()
    return a + (b - a) * u


def exponential(lam: float) -> float:
    """
    Genera una variable aleatoria con distribucion Exponencial.

    lam: tasa (frecuencia lambda), media = 1/lam
    X = -(1/lam) * ln(U), donde U ~ Uniform(0, 1)
    Seccion 2.3 del libro.
    """
    u = random.random()
    return -(1.0 / lam) * math.log(u)


def bernoulli(p: float) -> bool:
    """
    Genera una variable aleatoria Bernoulli.
    Retorna True con probabilidad p.
    """
    return random.random() < p


def normal(mu: float, sigma: float) -> float:
    """
    Genera una variable aleatoria con distribucion Normal(mu, sigma).

    Usa la transformada de Box-Muller:
    Z = sqrt(-2 * ln(U1)) * cos(2 * pi * U2)
    X = mu + sigma * Z

    donde U1, U2 ~ Uniform(0, 1).
    """
    u1 = random.random()
    u2 = random.random()
    z = math.sqrt(-2.0 * math.log(u1)) * math.cos(2.0 * math.pi * u2)
    return mu + sigma * z


def categorical(probabilities: list) -> int:
    """
    Genera una variable aleatoria categorica (discreta).

    probabilities: lista de probabilidades [p0, p1, ..., pk]
    Retorna el indice i seleccionado con probabilidad p_i.
    Usa el metodo de la transformada inversa para distribuciones discretas.
    Seccion 2.1 del libro.
    """
    u = random.random()
    cumulative = 0.0
    for i, p in enumerate(probabilities):
        cumulative += p
        if u < cumulative:
            return i
    return len(probabilities) - 1


def poisson_variate(lam: float) -> int:
    """
    Genera una variable aleatoria Poisson con parametro lam.

    Usa el metodo multiplicativo de la Seccion 2.4 del libro:
    genera uniformes sucesivas hasta que su producto sea menor que e^{-lam}.
    N = min{n : U1 * ... * Un < e^{-lam}} - 1
    """
    L = math.exp(-lam)
    k = 0
    p = 1.0
    while True:
        k += 1
        p *= random.random()
        if p < L:
            return k - 1


