# Happy Computing — Simulacion de Eventos Discretos

## Problema 4: Taller de Reparaciones Electronicas

Happy Computing es un taller que ofrece cuatro tipos de servicio:

- Reparacion en garantia (gratis, 45% de los clientes)
- Reparacion fuera de garantia ($350, 25%)
- Cambio de equipo ($500, 10%)
- Venta de equipos reparados ($750, 20%)

El taller tiene 2 vendedores, 3 tecnicos regulares y 1 tecnico especializado. El objetivo es simular la ganancia de una jornada de 8 horas.

---

## 1. Analisis del Enunciado

El enunciado indica que los clientes arriban con un intervalo de tiempo que distribuye Poisson con lambda = 20 minutos. El problema se interpreto como un **proceso de Poisson**: los clientes llegan de forma aleatoria e independiente a una tasa constante, con una media de 20 minutos entre llegadas. Se consideraron dos lecturas posibles:

### Interpretacion A — Proceso de Poisson, inter-arribo Exponencial *(la implementada)*

En un proceso de Poisson con tasa λ, el tiempo entre llegadas consecutivas distribuye **Exponencial con media 1/λ**. Tomando media = 20 min, el tiempo inter-arribo se genera como:

```math
X = -(1/lambda) * ln(U),  con lambda = 1/20
```

Esto da ~3 clientes por hora, una tasa razonable para un taller de reparaciones.

### Interpretacion B — Poisson(20) discreto

El tiempo inter-arribo (en minutos) se toma directamente como una variable aleatoria Poisson con parametro 20. Se genera con el metodo multiplicativo:

```math
N = min{k : U_1 * U_2 * ... * U_k < e^{-20}} - 1
```

Da valores enteros con media = 20 min. Los resultados son practicamente iguales a la Interpretacion A porque Poisson(20) tiene media 20 y desviacion estandar ~4.5 min, muy similar a Exponencial(media=20).

### Por que se eligio la Interpretacion A

En un proceso de Poisson los tiempos entre llegadas son continuos y distribuyen Exponencial. Se eligio la Interpretacion A por ser la que corresponde directamente a ese modelo.

---

## 2. Generacion de Variables Aleatorias

Todas las distribuciones se generaron desde cero usando la **transformada inversa**: si U ~ Uniforme(0,1) y F es la funcion de distribucion acumulada, entonces X = F⁻¹(U) tiene distribucion F.

### Uniforme(a, b)

```math
X = a + (b - a) * U
```

### Exponencial(lambda)

La inversa de F(x) = 1 - e^{-lambda*x} es F⁻¹(u) = -ln(1-u)/lambda. Como 1-U tiene la misma distribucion que U:

```math
X = -(1/lambda) * ln(U)
```

### Normal(mu, sigma)

La Normal no tiene inversa en forma cerrada. Se usa la transformada de Box-Muller con dos uniformes independientes:

```math
Z = sqrt(-2*ln(U1)) * cos(2*pi*U2)
X = mu + sigma * Z
```

Para los tiempos del vendedor se aplica `max(0.1, Normal(5, 2))` para evitar valores negativos.

### Categorica(probs)

Se acumulan las probabilidades y se toma el primer indice cuya acumulada supere U:

```math
i = min{k : p_0 + p_1 + ... + p_k > U}
```

---

## 3. Modelo de Simulacion

### Variables del sistema

- **Reloj:** `t`, en minutos desde la apertura del taller
- **Contadores:** llegadas totales, clientes atendidos, ganancia acumulada
- **Estado:** colas de espera para vendedor, tecnico y especializado; estado libre/ocupado de cada empleado

### Entidades

Cada cliente guarda el registro completo de su paso por el sistema: tiempo de llegada, inicio y fin con el vendedor, entrada a la cola de tecnico, inicio y fin con el tecnico. Con eso se calculan el tiempo de espera y el tiempo total en el sistema.

### Eventos

| Evento | Que ocurre |
| --- | --- |
| ARRIVAL | Llega un cliente al taller |
| VENDEDOR_DONE | Un vendedor termina; el cliente pasa a la segunda etapa o sale |
| TECNICO_DONE | Un tecnico o especializado termina; el cliente sale del sistema |

### Flujo del cliente

```text
ARRIVAL --> Cola Vendedor --> Vendedor (Normal(5,2) min)
                                         |
                     +-------------------+-------------------+
                     |                   |                   |
                Tipo 0, 1            Tipo 2              Tipo 3
            (Reparacion)         (Cambio equipo)         (Venta)
                     |                   |                   |
            Cola Tecnico        Cola Especializado         SALIDA
                     |                   |
         Tecnico/Especializado      Especializado
          (Exp media=20 min)       (Exp media=15 min)
                     |                   |
                     +--------+----------+
                              |
                           SALIDA
```

### Regla de prioridad del especializado

El enunciado dice que el tecnico especializado solo hace reparaciones si no hay nadie esperando un cambio de equipo. Esto se implementa en dos momentos:

1. Cuando un cliente de reparacion necesita tecnico y todos los regulares estan ocupados, el especializado lo atiende solo si la cola de cambios esta vacia.
2. Cuando el especializado queda libre, revisa primero la cola de cambios; si esta vacia, atiende reparaciones.

### Motor de simulacion

El motor mantiene una lista de eventos futuros ordenada por tiempo (implementada como heap). En cada paso extrae el evento mas proximo, avanza el reloj y lo procesa. El motor es completamente generico: no sabe nada del taller, solo ejecuta el bucle y delega el manejo al modelo.

---

## 4. Analisis Estadistico

Una sola corrida da un resultado aleatorio. Para estimar la ganancia esperada con confianza se hacen multiples **replicas independientes**, cada una con semilla diferente. Como las replicas son independientes, el Teorema Central del Limite garantiza que la media muestral converge a la esperanza real.

Se usa el **error estandar** como criterio de parada:

```text
SE = S / sqrt(n)
```

Se continuan las replicas mientras SE >= $500. Con 30 replicas ya se alcanzo la precision deseada.

### Resultados

| Metrica | Valor |
| --- | --- |
| Clientes llegados/dia | ~23 |
| Clientes atendidos/dia | ~22 |
| Ganancia promedio ($) | ~$6,200 |
| Error estandar ($) | ~$328 |
| Espera promedio (min) | ~0.09 |
| Tiempo en sistema (min) | ~20 |

El tiempo de espera es practicamente nulo (~5 segundos). El sistema no esta saturado: los empleados tienen capacidad suficiente para la demanda. El tiempo promedio en el sistema coincide casi exactamente con el tiempo de servicio del tecnico (~20 min), lo que confirma que los clientes casi no esperan en cola.

---

## 5. Conclusiones

El taller genera alrededor de $6,200 por jornada con la configuracion actual. El sistema tiene holgura: con ~23 clientes al dia y 6 empleados, las colas rara vez se forman. Si la demanda creciera significativamente, el cuello de botella seria el tecnico especializado, que es el unico que puede atender cambios de equipo.

La interpretacion del enunciado no afecta los resultados: modelar los inter-arribos como Exponencial (proceso de Poisson) o como Poisson discreto da numeros casi identicos, porque ambas distribuciones tienen la misma media y una varianza similar.
