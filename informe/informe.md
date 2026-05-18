# Happy Computing — Simulacion de Eventos Discretos



- **Nombre y apellidos:** Kevin Alejandro Torres Perera
- **Grupo:** C-311
- **Problema:** Problema 4 — Happy Computing
- **Repositorio:** [https://github.com/KevinTorres01/SimProject-Happy-Computing-](https://github.com/KevinTorres01/SimProject-Happy-Computing-)

---

## 1. Descripcion del Problema

Happy Computing es un taller de reparaciones electronicas que opera durante una jornada de **8 horas (480 minutos)**. Los clientes llegan de forma aleatoria con un intervalo de tiempo que distribuye Poisson con λ = 20 minutos (aproximadamente 3 clientes por hora).

### 1.1 Tipos de Servicio

| Tipo de Servicio | Probabilidad | Precio | Requiere Tecnico |
|:---|:---:|:---:|:---:|
| Reparacion en garantia | 45% | $0 | Si (regular o especializado) |
| Reparacion fuera de garantia | 25% | $350 | Si (regular o especializado) |
| Cambio de equipo | 10% | $500 | Si (solo especializado) |
| Venta de equipo reparado | 20% | $750 | No |

### 1.2 Personal del Taller

| Empleado | Cantidad | Funcion | Tiempo de Servicio |
|:---|:---:|:---|:---|
| Vendedor | 2 | Atiende a todos los clientes (etapa 1) | Normal(5, 2) min |
| Tecnico regular | 3 | Realiza reparaciones | Exponencial(media = 20) min |
| Tecnico especializado | 1 | Cambios de equipo + reparaciones auxiliares | Exponencial(media = 15) min para cambios, Exponencial(media = 20) min para reparaciones |

### 1.3 Flujo del Sistema

El taller funciona como un sistema de colas con **dos etapas**:

```text
                    +--------------------------------------------------+
                    |                                                    |
  Cliente llega --> | ETAPA 1: Vendedor --> ETAPA 2: Tecnico --> Sale    |
                    |       (todos)         (rep. y cambios)             |
                    |                                                    |
                    |                  --> Venta: sale directo --> Sale   |
                    +--------------------------------------------------+
```

**Regla de prioridad del especializado:** Cuando el tecnico especializado queda libre, primero atiende cambios de equipo (cola de cambios). Solo si no hay cambios pendientes, atiende reparaciones de la cola general.

---

## 2. Interpretacion de los Parametros

### 2.1 Proceso de Llegadas (λ = 20)

El enunciado dice textualmente:

> *"los clientes arriban al local con un intervalo de tiempo que distribuye poisson con λ = 20 minutos"*

El enunciado describe un **Proceso Poisson** para las llegadas de clientes. Segun la Seccion 2.4.1 del libro de texto, un Proceso Poisson se genera mediante tiempos inter-arribo que distribuyen **Exponencial**: si se generan n uniformes U1, ..., Un, entonces Xi = -(1/λ)log(Ui) es el tiempo entre el evento i-1 y el evento i. Por lo tanto, los tiempos entre llegadas se modelan como variables aleatorias **Exponencial(media = 20 minutos)**, produciendo valores continuos con media = 20 y desviacion estandar = 20 minutos. Esto captura la variabilidad natural de un proceso de llegadas aleatorio, donde a veces llegan varios clientes en pocos minutos y otras veces hay huecos largos.

Los clientes llegan en promedio cada **20 minutos** (aproximadamente 3 por hora, ~24 por jornada), lo cual es coherente con un taller pequeno de reparaciones.

### 2.2 Nota sobre la Notacion del Parametro λ

El libro (Seccion 2.3) define la distribucion Exponencial con λ como la **frecuencia** (tasa), donde la media es 1/λ. Sin embargo, el enunciado expresa los parametros con unidades de **minutos** (por ejemplo, "λ = 20 minutos" para los tecnicos, "λ = 15 minutos" para el especializado), lo cual indica que se refiere a la **media del tiempo**, no a la tasa. Si se interpretara λ = 20 como la tasa segun la convencion del libro, la media seria 1/20 = 0.05 minutos (3 segundos), un valor absurdo para una reparacion.

Por tanto, en la implementacion se interpreta el parametro λ del enunciado como la **media** del tiempo, y se pasa 1/λ como parametro de tasa a la funcion exponencial.

---

## 3. Metodologia

### 3.1 Modelo de Simulacion de Eventos Discretos

Siguiendo la estructura formal del libro (Seccion 3.1), las variables del modelo son:

**Variable de tiempo**

- t: tiempo de simulacion transcurrido (gestionado por el motor DES).

**Variables contadoras**

- N_A: cantidad de arribos hasta el tiempo t.
- N_D: cantidad de partidas (clientes que completaron su servicio) hasta el tiempo t.
- R: ganancia acumulada hasta el tiempo t.

**Variables de estado del sistema**

- Cola de vendedores: clientes esperando ser atendidos por un vendedor.
- Cola de reparaciones: clientes de tipo 1 o 2 esperando un tecnico (regular o especializado).
- Cola de cambios: clientes de tipo 3 esperando al tecnico especializado.
- Estado de cada vendedor (libre/ocupado y cliente actual).
- Estado de cada tecnico regular (libre/ocupado y cliente actual).
- Estado del tecnico especializado (libre/ocupado y cliente actual).

**Variables de salida**

- A(i): tiempo de arribo del cliente i.
- D(i): tiempo de partida del cliente i.
- W(i): tiempo total de espera en cola del cliente i.
- S(i): tiempo total en el sistema del cliente i.

**Lista de eventos**

- t_A: tiempo de la proxima llegada.
- t_V(j): tiempo en que el vendedor j termina su servicio actual.
- t_T(k): tiempo en que el tecnico k (regular o especializado) termina su servicio actual.

El simulador utiliza un **motor de eventos discretos** basado en un heap (cola de prioridad) que avanza el reloj virtual de evento en evento, sin simular minuto a minuto. Siguiendo el libro (Seccion 3.2), despues del tiempo T = 480 minutos no se admiten nuevas llegadas, pero **los clientes que ya estan en el sistema se atienden hasta completar su servicio**. Los tres tipos de eventos son:

| Evento | Disparador | Accion |
|:---|:---|:---|
| `ARRIVAL` | Tiempo inter-arribo generado | Genera tipo de cliente, asigna vendedor o encola |
| `VENDEDOR_DONE` | Vendedor termina servicio | Rutea a tecnico (rep./cambio) o sale (venta) |
| `TECNICO_DONE` | Tecnico termina servicio | Cliente sale, tecnico toma siguiente de cola |

### 3.2 Generacion de Variables Aleatorias

| Variable | Distribucion | Metodo de Generacion |
|:---|:---|:---|
| Tiempo entre llegadas | Exponencial(media = 20) | Transformada inversa: X = -20 * ln(U) |
| Tipo de servicio | Categorica [0.45, 0.25, 0.10, 0.20] | Busqueda en intervalos acumulados |
| Tiempo vendedor | Normal(5, 2) | Box-Muller: Z = sqrt(-2 ln(U1)) * cos(2 pi U2) |
| Tiempo tecnico regular | Exponencial(media = 20) | Transformada inversa: X = -20 * ln(U) |
| Tiempo especializado (cambio) | Exponencial(media = 15) | Transformada inversa: X = -15 * ln(U) |

### 3.3 Replicas y Criterio de Parada

Se ejecutan multiples replicas independientes (minimo 30) con semillas aleatorias distintas. El proceso continua hasta que el **error estandar** del ingreso diario sea menor a $500, garantizando precision estadistica en la estimacion.

---

## 4. Resultados de la Configuracion Base

### 4.1 Metricas Generales (50 replicas, Exponencial(20))

| Metrica | Valor |
|:---|---:|
| Replicas ejecutadas | 50 |
| Clientes que llegan por dia (promedio) | 22.9 |
| Clientes atendidos por dia (promedio) | 22.9 |
| **Ganancia promedio diaria** | **$6,449** |
| Desviacion estandar | $1,741 |
| Error estandar | $246 |
| **Intervalo de confianza al 95%** | **$6,449 +/- $495** |
| Tiempo promedio de espera en cola | 0.16 min (~10 segundos) |
| Tiempo promedio total en sistema | 20.53 min |

> **Nota:** Todos los clientes que llegan son atendidos (22.9 = 22.9) porque la simulacion completa el servicio de los clientes que estan en el sistema al cierre de la jornada, segun indica el libro. El intervalo de confianza se calcula como ±t_{0.025, n-1} * SE, con t_{0.025, 49} = 2.009.

### 4.2 Desglose por Tipo de Servicio

| Tipo de Servicio | Clientes/dia | Ingreso/dia | % del Ingreso Total |
|:---|:---:|:---:|:---:|
| Reparacion en garantia | 10.5 | $0 | 0% |
| Reparacion fuera de garantia | 5.5 | $1,939 | 30% |
| Cambio de equipo | 2.4 | $1,210 | 19% |
| Venta de equipo reparado | 4.4 | $3,300 | **51%** |
| **Total** | **22.9** | **$6,449** | **100%** |

> **Observacion:** Las ventas de equipos reparados representan mas de la mitad del ingreso diario, a pesar de ser solo el 20% de los clientes. Esto se debe a su precio unitario alto ($750) y a que no requieren tecnico, lo que permite atenderlos mas rapido.

### 4.3 Utilizacion del Personal (Estimada)

| Recurso | Capacidad Total (min/dia) | Carga de Trabajo (min/dia) | Utilizacion |
|:---|:---:|:---:|:---:|
| Vendedores (2) | 960 min | ~115 min (23 clientes x 5 min) | **~12.0%** |
| Tecnicos regulares (3) | 1,440 min | ~320 min (16 reparaciones x 20 min) | **~22.2%** |
| Especializado (1) | 480 min | ~36 min (2.4 cambios x 15 min) | **~7.5%** |

> **Hallazgo critico:** La utilizacion de todos los empleados es extremadamente baja. El sistema esta muy lejos de saturarse, lo que indica que hay personal sobrante.

---

## 5. Analisis de Sensibilidad: Variacion de Personal

### 5.1 Reduccion de Personal (Poisson(20), demanda normal)

Para determinar si hay trabajadores redundantes, se ejecuto la simulacion con distintas configuraciones de personal manteniendo la demanda constante:

| Configuracion | Vendedores | Tecnicos | Espec. | Ganancia | Espera | T. Sistema | Atendidos |
|:---|:---:|:---:|:---:|---:|---:|---:|:---:|
| Base | 2 | 3 | 1 | $6,449 | 0.16 min | 20.53 min | 22.9 |
| -1 Vendedor | 1 | 3 | 1 | $6,650 | 1.10 min | 21.42 min | 23.3 |
| -1 Tecnico | 2 | 2 | 1 | $6,409 | 0.43 min | 20.89 min | 22.9 |
| -2 Tecnicos | 2 | 1 | 1 | $6,432 | 2.21 min | 22.52 min | 23.1 |
| **Reducido (1V, 2T, 1E)** | **1** | **2** | **1** | **$6,632** | **1.18 min** | **21.50 min** | **23.2** |
| Minimo (1V, 1T, 1E) | 1 | 1 | 1 | $6,764 | 2.90 min | 23.36 min | 23.3 |

### 5.2 Interpretacion

La ganancia se mantiene estable en todas las configuraciones (~$6,400-$6,800), ya que todos los clientes son atendidos sin importar la cantidad de personal. La diferencia principal esta en los **tiempos de espera**: con la configuracion reducida (1V, 2T, 1E) la espera promedio es de ~1.2 minutos, y con la minima (1V, 1T, 1E) sube a ~2.9 minutos, ambos valores aceptables para un taller.

La carga de trabajo real con ~23 clientes en 480 minutos es:

- Vendedor: 23 clientes x 5 min = 115 min de trabajo en 480 min disponibles → **un solo vendedor basta con creces**
- Tecnicos: 16 clientes x 20 min = 320 min de trabajo en 480 min disponibles → **un tecnico mas el especializado cubren facilmente**

### 5.3 Conclusion sobre Personal Sobrante

| Puesto | Cantidad Actual | Cantidad Suficiente | Sobrante |
|:---|:---:|:---:|:---:|
| Vendedores | 2 | **1** | 1 vendedor sobra |
| Tecnicos regulares | 3 | **2** | 1 tecnico sobra |
| Especializado | 1 | 1 | Ninguno (es el unico que hace cambios) |

> **Con 1 vendedor, 2 tecnicos regulares y 1 especializado (4 empleados en vez de 6), el taller genera una ganancia equivalente de ~$6,600/dia con tiempos de espera de apenas 1.2 minutos.** Se podrian ahorrar 2 salarios sin afectar significativamente el servicio ni los ingresos.

---

## 6. Analisis de Sensibilidad: Variacion de Demanda

### 6.1 Efecto de la Tasa de Llegada

Se vario el parametro lambda (tiempo medio entre llegadas) para ver como responde el sistema a diferentes niveles de demanda:

| Lambda (min) | Clientes/dia | Ganancia/dia | Espera | T. Sistema | Observacion |
|:---:|:---:|---:|---:|---:|:---|
| 10 | 48.2 | $13,933 | 1.02 min | 21.27 min | Doble demanda, sistema aun funciona |
| 15 | 30.8 | $8,770 | 0.43 min | 21.16 min | Alta demanda, sin problemas |
| **20** | **22.9** | **$6,449** | **0.16 min** | **20.53 min** | **Caso base** |
| 25 | 17.8 | $5,110 | 0.13 min | 20.04 min | Baja demanda |
| 30 | 15.1 | $4,364 | 0.30 min | 20.66 min | Muy baja demanda |
| 40 | 11.1 | $3,119 | 0.05 min | 20.64 min | Demanda minima |

> **Observacion:** Incluso duplicando la demanda (lambda = 10, ~48 clientes/dia), el sistema con la configuracion completa opera sin problemas. El tiempo en sistema permanece estable en ~20 min porque esta dominado por el servicio del tecnico, no por la espera en cola.

### 6.2 Alta Demanda con Personal Reducido

El caso critico: si la demanda aumentara al doble (lambda = 10), ¿el personal reducido aguantaria?

| Configuracion | Ganancia | Atendidos | Espera | T. Sistema |
|:---|---:|:---:|---:|---:|
| Base (2V, 3T, 1E) | $13,933 | 48.2 | 1.02 min | 21.27 min |
| 1 Vendedor (1V, 3T, 1E) | $13,728 | 48.1 | 3.81 min | 24.44 min |
| 2 Tecnicos (2V, 2T, 1E) | $13,735 | 47.0 | 2.67 min | 22.93 min |
| Reducido (1V, 2T, 1E) | $13,584 | 47.7 | 5.63 min | 26.27 min |
| Minimo (1V, 1T, 1E) | $13,563 | 47.3 | 16.58 min | 36.92 min |

> Con alta demanda, la configuracion reducida (1V, 2T, 1E) funciona razonablemente (espera ~5.6 min, atiende 47.7 de 48.2 clientes). La configuracion minima (1V, 1T, 1E) muestra degradacion severa con esperas de 16.6 minutos. **La configuracion recomendada de 1V, 2T, 1E soporta picos de demanda con esperas aceptables, aunque con mayor impacto que en el caso base.**

---

## 7. Resumen y Conclusiones

### 7.1 Sobre la Ganancia

| Escenario | Ganancia Diaria Esperada |
|:---|---:|
| Demanda normal (lambda = 20) | **$6,449 +/- $495 (IC 95%)** |
| Demanda alta (lambda = 15) | $8,770 |
| Demanda muy alta (lambda = 10) | $13,933 |

La ganancia es proporcional a la cantidad de clientes atendidos y no depende significativamente del numero de empleados, ya que con la demanda actual todos los clientes son atendidos sin importar la configuracion.

### 7.2 Sobre el Personal

1. **Hay 2 empleados sobrantes** en la configuracion actual: 1 vendedor y 1 tecnico regular.
2. La configuracion optima para la demanda actual es **1 vendedor + 2 tecnicos + 1 especializado** (4 personas).
3. El sistema esta dimensionado para manejar hasta el **doble de demanda** sin problemas con la configuracion completa, pero incluso la configuracion reducida soporta picos.
4. El tecnico especializado es necesario porque es el **unico que puede realizar cambios de equipo** (10% de los clientes, $500 cada uno).

### 7.3 Sobre la Calidad de Servicio

- Con la configuracion actual, los clientes esperan en promedio **10 segundos**. Es una calidad de servicio excesiva para el costo.
- Con la configuracion reducida recomendada (1V, 2T, 1E), los clientes esperan en promedio **1.2 minutos**, perfectamente aceptable.
- Incluso en el peor caso analizado (1V, 1T, 1E con demanda normal), la espera promedio es de **2.9 minutos**, aceptable para un taller de reparaciones.
- Bajo alta demanda (lambda = 10), la configuracion reducida produce esperas de ~5.6 minutos, aun razonable.

### 7.4 Recomendacion Final

> **El taller Happy Computing puede operar con 4 empleados en lugar de 6 sin perdida significativa de ingresos (~$6,450/dia, IC 95%: +/- $495) y manteniendo tiempos de espera aceptables (~1.2 min). Esto representa un ahorro de 2 salarios diarios.**

---

## 8. Detalles Tecnicos de Implementacion

### 8.1 Arquitectura del Simulador

```text
main.py                 -> Punto de entrada, ejecuta replicas
src/config.py           -> Parametros configurables (dataclass)
src/des_engine.py       -> Motor de eventos discretos (generico)
src/model.py            -> Modelo del taller (logica de negocio)
src/random_vars.py      -> Generadores de variables aleatorias
src/stats.py            -> Analisis estadistico y replicas
```

### 8.2 Ejecucion

```bash
python main.py
```

Ejecuta 30 replicas independientes con semilla fija (42 + i), continua si el error estandar es mayor a $500, y reporta metricas finales.
