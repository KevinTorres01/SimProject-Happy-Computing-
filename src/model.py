"""
Modelo de simulacion: Happy Computing.

Problema 4 del proyecto de Simulacion basada en Eventos Discretos.
Taller de reparaciones electronicas con servicio en 2 etapas,
3 tipos de empleados, y regla de prioridad del tecnico especializado.
"""

from dataclasses import dataclass, field
from typing import List, Optional
from collections import deque
from enum import IntEnum

from src.random_vars import exponential, normal, categorical
from src.config import HappyConfig

# Tipos de servicio
class ServiceType(IntEnum):
    WARRANTY_REPAIR = 0     # Reparacion en garantia (Gratis)
    PAID_REPAIR = 1         # Reparacion fuera de garantia ($350)
    EQUIPMENT_CHANGE = 2    # Cambio de equipo ($500)
    SALE = 3                # Venta de equipos reparados ($750)

SERVICE_NAMES = {
    ServiceType.WARRANTY_REPAIR: "Reparacion garantia",
    ServiceType.PAID_REPAIR: "Reparacion pago",
    ServiceType.EQUIPMENT_CHANGE: "Cambio equipo",
    ServiceType.SALE: "Venta",
}

# Tipos de eventos
ARRIVAL = "ARRIVAL"
VENDEDOR_DONE = "VENDEDOR_DONE"
TECNICO_DONE = "TECNICO_DONE"


@dataclass
class Customer:
    """Representa un cliente en el sistema."""
    id: int
    service_type: ServiceType
    arrival_time: float

    # Etapa 1: Vendedor
    vendedor_start_time: float = None
    vendedor_end_time: float = None

    # Etapa 2: Tecnico / Especializado (None para tipo SALE)
    tecnico_queue_entry_time: float = None
    tecnico_start_time: float = None
    tecnico_end_time: float = None

    @property
    def departure_time(self) -> Optional[float]:
        if self.service_type == ServiceType.SALE:
            return self.vendedor_end_time
        return self.tecnico_end_time

    @property
    def total_wait_time(self) -> float:
        wait = 0.0
        if self.vendedor_start_time is not None:
            wait += self.vendedor_start_time - self.arrival_time
        if self.tecnico_start_time is not None and self.tecnico_queue_entry_time is not None:
            wait += self.tecnico_start_time - self.tecnico_queue_entry_time
        return wait

    @property
    def total_time_in_system(self) -> Optional[float]:
        if self.departure_time is not None:
            return self.departure_time - self.arrival_time
        return None

    @property
    def price(self) -> float:
        prices = [0.0, 350.0, 500.0, 750.0]
        return prices[self.service_type]


@dataclass
class Vendedor:
    """Representa un vendedor."""
    id: int
    busy: bool = False
    current_customer: Customer = None

    def assign(self, customer: Customer, current_time: float):
        self.busy = True
        self.current_customer = customer
        customer.vendedor_start_time = current_time

    def release(self) -> Customer:
        customer = self.current_customer
        self.busy = False
        self.current_customer = None
        return customer


@dataclass
class Tecnico:
    """Representa un tecnico regular."""
    id: int
    busy: bool = False
    current_customer: Customer = None

    def assign(self, customer: Customer, current_time: float):
        self.busy = True
        self.current_customer = customer
        customer.tecnico_start_time = current_time

    def release(self) -> Customer:
        customer = self.current_customer
        self.busy = False
        self.current_customer = None
        return customer


@dataclass
class TecnicoEspecializado:
    """Representa un tecnico especializado."""
    id: int
    busy: bool = False
    current_customer: Customer = None

    def assign(self, customer: Customer, current_time: float):
        self.busy = True
        self.current_customer = customer
        customer.tecnico_start_time = current_time

    def release(self) -> Customer:
        customer = self.current_customer
        self.busy = False
        self.current_customer = None
        return customer


class HappyComputingModel:
    """
    Modelo de simulacion de Happy Computing.

    Variables del sistema (siguiendo la estructura del libro):
    - Variable de tiempo: t (gestionada por el motor DES)
    - Variables contadoras: n_arrivals, n_departures, total_revenue
    - Variables de estado: vendedor_queue, repair_queue, change_queue,
      vendedores, tecnicos, especializado
    - Variables de salida: customers (registro completo)
    """

    def __init__(self, config: HappyConfig):
        self.config = config

        # Contadores
        self.n_arrivals = 0
        self.n_departures = 0
        self.total_revenue = 0.0

        # Empleados
        self.vendedores: List[Vendedor] = []
        self.tecnicos: List[Tecnico] = []
        self.especializado: TecnicoEspecializado = None

        # Colas
        self.vendedor_queue: deque = deque()
        self.repair_queue: deque = deque()    # tipos 0,1 esperando tecnico
        self.change_queue: deque = deque()    # tipo 2 esperando especializado

        # Clientes completados
        self.customers: List[Customer] = []

    def initialize(self, engine):
        """Inicializa empleados y programa primera llegada."""
        for i in range(self.config.num_vendedores):
            self.vendedores.append(Vendedor(id=i))

        for i in range(self.config.num_tecnicos):
            self.tecnicos.append(Tecnico(id=i))

        self.especializado = TecnicoEspecializado(id=0)

        # Primera llegada
        inter = self._generate_inter_arrival()
        if inter < self.config.total_time:
            engine.schedule_event(inter, ARRIVAL)

    def should_continue(self, event) -> bool:
        """Continuar mientras el evento este dentro de la jornada."""
        return event.time <= self.config.total_time

    def handle_event(self, engine, event):
        """Despacha el evento al handler correspondiente."""
        if event.event_type == ARRIVAL:
            self._handle_arrival(engine, event)
        elif event.event_type == VENDEDOR_DONE:
            self._handle_vendedor_done(engine, event)
        elif event.event_type == TECNICO_DONE:
            self._handle_tecnico_done(engine, event)

    # --- Generacion de llegadas ---

    def _generate_inter_arrival(self) -> float:
        """Genera tiempo inter-arribo: proceso de Poisson => Exponencial(media=lambda min)."""
        return exponential(1.0 / self.config.arrival_lambda)

    # --- Handlers de eventos ---

    def _handle_arrival(self, engine, event):
        """Maneja la llegada de un cliente al taller."""
        self.n_arrivals += 1

        stype_idx = categorical(self.config.service_probabilities)
        service_type = ServiceType(stype_idx)

        customer = Customer(
            id=self.n_arrivals,
            service_type=service_type,
            arrival_time=engine.clock,
        )

        # Programar siguiente llegada
        inter = self._generate_inter_arrival()
        next_time = engine.clock + inter
        if next_time < self.config.total_time:
            engine.schedule_event(next_time, ARRIVAL)

        # Buscar vendedor libre
        vendedor = self._find_free_vendedor()
        if vendedor is not None:
            self._start_vendedor_service(engine, vendedor, customer)
        else:
            self.vendedor_queue.append(customer)

    def _handle_vendedor_done(self, engine, event):
        """
        Vendedor termina de atender. Rutear cliente a etapa 2 o salida.
        """
        vendedor_id = event.data["vendedor_id"]
        vendedor = self.vendedores[vendedor_id]
        customer = vendedor.release()
        customer.vendedor_end_time = engine.clock

        # Rutear segun tipo de servicio
        if customer.service_type == ServiceType.SALE:
            # Tipo 4: solo necesita vendedor, sale del sistema
            self._customer_departs(customer)
        elif customer.service_type == ServiceType.EQUIPMENT_CHANGE:
            # Tipo 3: necesita tecnico especializado
            customer.tecnico_queue_entry_time = engine.clock
            self._try_assign_to_especializado(engine, customer)
        else:
            # Tipos 0,1: reparacion, necesita tecnico (regular o especializado)
            customer.tecnico_queue_entry_time = engine.clock
            self._try_assign_to_tecnico(engine, customer)

        # Vendedor libre: tomar siguiente de la cola
        if self.vendedor_queue:
            next_customer = self.vendedor_queue.popleft()
            self._start_vendedor_service(engine, vendedor, next_customer)

    def _handle_tecnico_done(self, engine, event):
        """
        Tecnico o especializado termina servicio. Cliente sale.
        """
        emp_type = event.data["employee_type"]
        emp_id = event.data["employee_id"]

        if emp_type == "tecnico":
            tecnico = self.tecnicos[emp_id]
            customer = tecnico.release()
            customer.tecnico_end_time = engine.clock
            self._customer_departs(customer)

            # Tecnico libre: tomar siguiente de repair_queue
            if self.repair_queue:
                next_customer = self.repair_queue.popleft()
                self._start_tecnico_service(engine, tecnico, next_customer)

        elif emp_type == "especializado":
            customer = self.especializado.release()
            customer.tecnico_end_time = engine.clock
            self._customer_departs(customer)

            # Especializado libre: PRIORIDAD change_queue, luego repair_queue
            if self.change_queue:
                next_customer = self.change_queue.popleft()
                self._start_especializado_service(engine, self.especializado, next_customer)
            elif self.repair_queue:
                next_customer = self.repair_queue.popleft()
                self._start_especializado_service(engine, self.especializado, next_customer)

    # --- Asignacion de empleados ---

    def _find_free_vendedor(self) -> Optional[Vendedor]:
        for v in self.vendedores:
            if not v.busy:
                return v
        return None

    def _start_vendedor_service(self, engine, vendedor: Vendedor, customer: Customer):
        vendedor.assign(customer, engine.clock)
        service_time = max(0.1, normal(
            self.config.vendedor_service_mean,
            self.config.vendedor_service_std
        ))
        engine.schedule_event(
            engine.clock + service_time,
            VENDEDOR_DONE,
            {"vendedor_id": vendedor.id}
        )

    def _try_assign_to_tecnico(self, engine, customer: Customer):
        """Asigna cliente de reparacion (tipos 0,1) a un tecnico."""
        # Primero: tecnicos regulares
        for tecnico in self.tecnicos:
            if not tecnico.busy:
                self._start_tecnico_service(engine, tecnico, customer)
                return

        # Si no hay tecnico regular libre, intentar especializado
        # SOLO si no hay clientes de cambio en cola
        if not self.especializado.busy and len(self.change_queue) == 0:
            self._start_especializado_service(engine, self.especializado, customer)
            return

        # Nadie disponible: encolar
        self.repair_queue.append(customer)

    def _try_assign_to_especializado(self, engine, customer: Customer):
        """Asigna cliente de cambio (tipo 2) al especializado."""
        if not self.especializado.busy:
            self._start_especializado_service(engine, self.especializado, customer)
        else:
            self.change_queue.append(customer)

    def _start_tecnico_service(self, engine, tecnico: Tecnico, customer: Customer):
        tecnico.assign(customer, engine.clock)
        service_time = exponential(1.0 / self.config.tecnico_service_mean)
        engine.schedule_event(
            engine.clock + service_time,
            TECNICO_DONE,
            {"employee_type": "tecnico", "employee_id": tecnico.id}
        )

    def _start_especializado_service(self, engine, esp: TecnicoEspecializado, customer: Customer):
        esp.assign(customer, engine.clock)
        if customer.service_type == ServiceType.EQUIPMENT_CHANGE:
            service_time = exponential(1.0 / self.config.especializado_service_mean)
        else:
            # Haciendo reparacion: mismo tiempo que tecnico regular
            service_time = exponential(1.0 / self.config.tecnico_service_mean)
        engine.schedule_event(
            engine.clock + service_time,
            TECNICO_DONE,
            {"employee_type": "especializado", "employee_id": esp.id}
        )

    # --- Salida de clientes ---

    def _customer_departs(self, customer: Customer):
        self.n_departures += 1
        self.total_revenue += customer.price
        self.customers.append(customer)

    # --- Finalizacion ---

    def finalize(self, engine) -> dict:
        """Calcula y retorna las metricas finales."""
        served = [c for c in self.customers if c.departure_time is not None]

        total_revenue = sum(c.price for c in served)

        wait_times = [c.total_wait_time for c in served]
        avg_wait = sum(wait_times) / len(wait_times) if wait_times else 0.0

        system_times = [c.total_time_in_system for c in served
                        if c.total_time_in_system is not None]
        avg_system = sum(system_times) / len(system_times) if system_times else 0.0

        # Conteo por tipo
        type_counts = {}
        type_revenue = {}
        for st in ServiceType:
            type_counts[st.name] = sum(1 for c in served if c.service_type == st)
            type_revenue[st.name] = sum(c.price for c in served if c.service_type == st)

        return {
            "total_arrivals": self.n_arrivals,
            "total_served": self.n_departures,
            "total_revenue": total_revenue,
            "avg_wait_time": avg_wait,
            "avg_system_time": avg_system,
            "type_counts": type_counts,
            "type_revenue": type_revenue,
            "vendedor_queue_at_end": len(self.vendedor_queue),
            "repair_queue_at_end": len(self.repair_queue),
            "change_queue_at_end": len(self.change_queue),
        }
