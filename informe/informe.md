# Informe de Proyecto: Simulacion basada en Eventos Discretos

## Happy Computing - Taller de Reparaciones Electronicas

---

## 1. Generales del Estudiante

- **Nombre y apellidos:** [Nombre del estudiante]
- **Grupo:** [Grupo]
- **Asignatura:** Simulacion
- **Facultad:** Matematica y Computacion, Universidad de La Habana

---

## 2. Orden del Problema Asignado

**Problema 4: Happy Computing**

Happy Computing es un taller de reparaciones electronicas que ofrece 4 servicios:

- Reparacion por garantia (gratis, 45% de los clientes)
- Reparacion fuera de garantia ($350, 25%)
- Cambio de equipo ($500, 10%)
- Venta de equipos reparados ($750, 20%)

El taller cuenta con 2 vendedores, 3 tecnicos y 1 tecnico especializado. Se desea simular la ganancia de una jornada laboral de 8 horas.

---

## 3. Analisis del Enunciado: El Error Conceptual

### 3.1 El Problema

El enunciado dice:

> *"los clientes arriban al local con un intervalo de tiempo que distribuye Poisson con lambda = 20 minutos"*

Esto contiene un **error conceptual**: la distribucion de Poisson es discreta y modela la **cantidad** de eventos en un intervalo fijo de tiempo. Por definicion, una variable Poisson toma valores en {0, 1, 2, ...} y no puede representar directamente un tiempo de espera continuo.

En un **proceso de Poisson** con tasa λ, lo que distribuye Poisson(λt) es el *numero de llegadas* en el intervalo [0, t]. Los **tiempos entre llegadas consecutivas** distribuyen **Exponencial(λ)**, con media 1/λ.

Por tanto, la frase correcta habria sido: *"los clientes arriban segun un proceso de Poisson con tasa λ"*, o equivalentemente, *"los tiempos entre llegadas distribuyen Exponencial con media 20 minutos"*.

### 3.2 Tres Interpretaciones Implementadas

Para evidenciar las consecuencias del error, se implementaron 3 lecturas posibles del enunciado:

**Interpretacion A: Exponencial con media = 20 minutos**

Es la intencion mas probable del autor. El parametro 20 se toma como la **media** del tiempo entre llegadas. Se genera:

```
X = -(1/lambda) * ln(U),  con lambda = 1/20
```

Esto equivale a decir que los clientes llegan segun un proceso de Poisson con tasa 3 clientes/hora, lo cual es razonable para un taller de reparaciones.

**Interpretacion B: Exponencial con tasa = 20 por minuto**

Sigue literalmente la notacion del libro (Seccion 2.3): *"distribucion exponencial con frecuencia lambda tiene media 1/lambda"*. Si lambda = 20, entonces media = 1/20 min = **3 segundos**. Se genera:

```
X = -(1/20) * ln(U)
```

Esto implica 1200 llegadas por hora, absurdo para un taller de reparaciones.

**Interpretacion C: Poisson(20) discreto**

Toma literalmente el enunciado: el tiempo inter-arribo (en minutos) toma el valor de una variable Poisson con parametro 20. Se usa el metodo multiplicativo (Seccion 2.4):

```
N = min{k : U_1 * U_2 * ... * U_k < e^{-20}} - 1
```

Genera valores enteros con media = 20 min y varianza = 20, produciendo resultados similares a la Interpretacion A.

### 3.3 Razonamiento para Seleccionar la Interpretacion Correcta

Las tres interpretaciones se implementaron y ejecutaron. La comparacion de resultados permite descartar por absurdo:

- **Interpretacion B** genera ~9,600 llegadas/dia con esperas de ~224 minutos. Un taller con 6 empleados que atiende al 1.4% de sus clientes no es un modelo viable.
- **Interpretaciones A y C** generan ~23 clientes/dia con esperas de menos de 1 minuto, coherente con la capacidad del taller.

La misma logica aplica a los tiempos de servicio de los tecnicos ("exponencial con lambda=20 minutos"): una media de 20 minutos por reparacion es razonable; una de 3 segundos no lo es.

---

## 4. Principales Ideas para la Solucion

### 4.1 Enfoque General

Se modelo el problema como un **sistema de colas en dos etapas**:

- **Etapa 1:** Todo cliente es atendido primero por un vendedor (atiende los 4 tipos de servicio).
- **Etapa 2:** Segun el tipo de servicio, puede necesitar a continuacion un tecnico (reparacion) o tecnico especializado (cambio de equipo). Las ventas salen del sistema tras la Etapa 1.

Este diseno se justifica porque el vendedor actua como punto de clasificacion: determina que necesita el cliente y lo deriva al recurso correspondiente.

### 4.2 Generacion de Variables Aleatorias

Todas las distribuciones se implementaron desde cero usando el **metodo de la transformada inversa** (Capitulo 2 del libro de referencia). El principio es: si U ~ Uniform(0,1) y F es la CDF de la distribucion objetivo, entonces X = F^{-1}(U) tiene distribucion F.

**Uniforme(a, b):**

La CDF es F(x) = (x-a)/(b-a), su inversa es F^{-1}(u) = a + (b-a)*u. Por tanto:

```
X = a + (b - a) * U
```

**Exponencial(lambda):**

La CDF es F(x) = 1 - e^{-lambda*x}, su inversa es F^{-1}(u) = -ln(1-u)/lambda. Como 1-U tiene la misma distribucion que U:

```
X = -(1/lambda) * ln(U)
```

**Normal(mu, sigma):**

La CDF Normal no tiene inversa en forma cerrada. Se usa la transformada de **Box-Muller**: si U1, U2 ~ Uniform(0,1) independientes, entonces:

```
Z = sqrt(-2*ln(U1)) * cos(2*pi*U2)
X = mu + sigma * Z
```

Z tiene distribucion Normal(0,1). Esta tecnica se deriva de la propiedad de que la transformacion polar de dos normales independientes produce variables con distribucion uniforme en angulo y Rayleigh en radio.

Para evitar tiempos negativos (que son fisicamente imposibles) se aplica `max(0.1, Normal(5, 2))`.

**Categorica(probs):**

Se acumulan las probabilidades y se busca el primer indice cuya probabilidad acumulada supere U:

```
i = min{k : p_0 + p_1 + ... + p_k > U}
```

**Poisson(lambda):**

Se usa el metodo multiplicativo de la Seccion 2.4: el numero de llegadas en [0,1] de un proceso de Poisson(lambda) es el mayor N tal que el producto de N uniformes sea mayor o igual que e^{-lambda}:

```
N = min{k : U_1 * ... * U_k < e^{-lambda}} - 1
```

---

## 5. Modelo de Simulacion de Eventos Discretos

### 5.1 Variables del Sistema

**Variable de tiempo:** `t` (reloj de simulacion, en minutos desde la apertura)

**Variables contadoras:**

- `N_A`: cantidad de llegadas al taller
- `N_D`: cantidad de clientes que completaron su servicio
- `total_revenue`: ganancia acumulada en pesos

**Variables de estado:**

- `vendedor_queue`: cola FIFO de clientes esperando vendedor
- `repair_queue`: cola FIFO de clientes (tipos 0 y 1) esperando tecnico
- `change_queue`: cola FIFO de clientes tipo 2 esperando especializado
- Estado de cada empleado: libre u ocupado, y cliente que esta atendiendo

### 5.2 Entidades

- **Customer:** identificador, tipo de servicio, timestamps de cada etapa (llegada, inicio con vendedor, fin con vendedor, entrada a cola tecnico, inicio con tecnico, fin con tecnico). Permite calcular tiempos de espera y tiempo total en el sistema.
- **Vendedor:** identificador, estado (libre/ocupado), cliente actual.
- **Tecnico:** identificador, estado, cliente actual.
- **TecnicoEspecializado:** igual que Tecnico, pero con regla de prioridad al momento de seleccionar el proximo cliente.

### 5.3 Tipos de Eventos

| Evento | Descripcion |
| ------ | ----------- |
| ARRIVAL | Un cliente llega al taller |
| VENDEDOR_DONE | Un vendedor termina de atender (rutear a etapa 2 o salida) |
| TECNICO_DONE | Un tecnico o especializado termina (cliente sale del sistema) |

### 5.4 Flujo del Cliente

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

### 5.5 Regla de Prioridad del Tecnico Especializado

El enunciado establece:

> *"Un tecnico especializado solo realizara Reparaciones si no hay ningun cliente que desee un cambio de equipo en la cola."*

Esta regla tiene sentido practico: el especializado es el unico que puede atender cambios de equipo, por lo que no debe quedar bloqueado por reparaciones cuando haya clientes de cambio esperando.

La implementacion refleja esto en dos momentos:

1. Cuando llega un cliente de reparacion y todos los tecnicos regulares estan ocupados, el especializado solo lo toma si `change_queue` esta vacia.
2. Cuando el especializado termina un servicio, revisa `change_queue` primero; solo si esta vacia toma de `repair_queue`.

### 5.6 Motor de Simulacion

El motor (`des_engine.py`) mantiene una **lista de eventos ordenada por tiempo** usando un heap (cola de prioridad). En cada paso:

1. Extrae el evento con menor tiempo.
2. Avanza el reloj al tiempo de ese evento.
3. Invoca `handle_event` del modelo.

Los eventos se almacenan como tuplas `(tiempo, desempate, evento)`. El campo de desempate es un contador incremental que evita comparar objetos Event directamente cuando dos eventos tienen el mismo tiempo.

El motor es completamente generico: recibe cualquier objeto que implemente la interfaz `initialize`, `handle_event`, `should_continue` y `finalize`. Esto desacopla el algoritmo de simulacion del modelo especifico.

### 5.7 Arquitectura del Software

```text
main.py           --> Punto de entrada (ejecuta las 3 interpretaciones)
src/config.py     --> Parametros de configuracion + enum de interpretaciones
src/model.py      --> Modelo de Happy Computing (logica del negocio)
src/stats.py      --> Runner de replicas + funciones estadisticas
src/random_vars.py --> Generadores de variables aleatorias
src/des_engine.py  --> Motor generico de eventos discretos
```

---

## 6. Analisis Estadistico

### 6.1 Razonamiento para Usar Replicas

Una sola corrida de la simulacion produce un resultado aleatorio que depende de la semilla utilizada. Para obtener estimaciones confiables de las metricas de interes (ganancia esperada, tiempo de espera) se realizan multiples **replicas independientes**, cada una con una semilla diferente.

Dado que las replicas son i.i.d., el **Teorema Central del Limite** garantiza que la media muestral converge a la esperanza real. Se usa el **error estandar** como criterio de parada:

```text
SE = S / sqrt(n)
```

donde S es la desviacion estandar muestral y n el numero de replicas. Se continuan las replicas mientras SE >= precision_d (500 pesos). Esto asegura que el intervalo de confianza tenga un ancho controlado antes de reportar resultados.

### 6.2 Configuracion Experimental

- Minimo 30 replicas por interpretacion (criterio estadistico de muestra grande)
- Criterio de parada: error estandar de la ganancia < $500
- Semilla base = 42 (reproducibilidad)
- Jornada laboral: 8 horas (480 minutos)

### 6.3 Tabla Comparativa de Resultados

| Metrica | Interp A | Interp B | Interp C |
| ------- | -------- | -------- | -------- |
| Clientes llegados/dia | ~23 | ~9,600 | ~23 |
| Clientes atendidos/dia | ~22 | ~135 | ~23 |
| Ganancia ($) | ~$6,200 | ~$46,800 | ~$6,600 |
| Espera promedio (min) | ~0.1 | ~224 | ~0.08 |
| Tiempo en sistema (min) | ~20 | ~243 | ~20 |

### 6.4 Analisis por Interpretacion

**Interpretacion A (Exponencial, media = 20 min):**

Con ~23 clientes por dia y ganancia ~$6,200, el tiempo de espera es practicamente nulo (~6 segundos). Esto indica que el sistema tiene capacidad suficiente: los 6 empleados no se saturan con esta tasa de llegadas. El tiempo promedio en el sistema (~20 min) corresponde al tiempo de servicio del tecnico, lo que confirma que la espera en cola es despreciable.

**Interpretacion B (Exponencial, tasa = 20/min):**

Con ~9,600 llegadas pero solo ~135 atendidos (el 1.4%), el sistema colapsa completamente. Las esperas de ~224 minutos superan el tiempo total de la jornada. Aunque la ganancia parece alta ($46,800), se debe a que los pocos clientes que logran ser atendidos pagan precios elevados mientras el resto abandona o espera indefinidamente. Este resultado es fisicamente absurdo para un taller de reparaciones.

**Interpretacion C (Poisson(20) discreto):**

Los resultados son casi identicos a la Interpretacion A (~23 clientes/dia, ~$6,600). La diferencia se explica porque Poisson(20) tiene media = 20 y desviacion estandar = sqrt(20) ≈ 4.5 minutos, valores proximos a los de una Exponencial con media 20. La discrecion de los tiempos (enteros) no afecta significativamente el comportamiento del sistema.

---

## 7. Conclusiones

1. **El enunciado contiene un error conceptual**: la distribucion Poisson no modela tiempos entre llegadas. Lo correcto seria decir "proceso de Poisson con tasa λ" o "tiempos inter-arribo con distribucion Exponencial de media λ".

2. **La interpretacion correcta es A**: los inter-arribos distribuyen Exponencial con media = 20 minutos, equivalente a un proceso de Poisson con tasa de 3 clientes/hora.

3. **La Interpretacion B es fisicamente absurda**: un cliente cada 3 segundos en un taller de reparaciones es imposible. La simulacion lo confirma: el sistema colapsa con esperas de casi 4 horas.

4. **La misma ambiguedad aplica a los tiempos de servicio**: "exponencial con lambda = 20 minutos" para los tecnicos se interpreta como media = 20 min (razonable) y no como tasa = 20/min (media = 3 seg, absurdo).

5. **Con la interpretacion correcta el taller es rentable**: ~$6,200-$6,600 diarios con una configuracion de 2 vendedores, 3 tecnicos y 1 especializado. El sistema no esta saturado (esperas menores a 1 minuto), lo que sugiere que la dotacion de personal es adecuada para la demanda real.

---

## 8. Enlace al Repositorio

**GitHub:** [Insertar enlace al repositorio]

---

## Referencias

- *Temas de Simulacion.* Dr. Luciano Garcia Garrido, Lic. Luis Marti Orosa, Lic. Luis Perez Sanchez. Facultad de Matematica y Computacion, Universidad de La Habana.
- *Proyecto de Simulacion basada en Eventos Discretos.* Colectivo de Simulacion, MatCom UH.
