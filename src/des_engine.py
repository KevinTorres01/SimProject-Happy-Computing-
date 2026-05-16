"""
Motor generico de Simulacion basada en Eventos Discretos.

Referencia: Capitulo 3 - Temas de Simulacion (UH)

El motor mantiene una lista de eventos ordenada por tiempo
y delega el procesamiento de cada evento al modelo.
"""

import heapq
from dataclasses import dataclass, field
from typing import Any, Dict, Optional


@dataclass(order=False)
class Event:
    """Representa un evento programado en la simulacion."""
    time: float
    event_type: str
    data: Dict[str, Any] = field(default_factory=dict)

    def __repr__(self):
        return f"Event({self.event_type}, t={self.time:.2f})"


class DESEngine:
    """
    Motor de simulacion por eventos discretos.

    Mantiene un reloj de simulacion y una lista de eventos futuros
    implementada como min-heap. Delega el manejo de eventos al modelo.
    """

    def __init__(self):
        self.clock: float = 0.0
        self._event_list: list = []
        self._tiebreaker: int = 0

    def schedule_event(self, time: float, event_type: str, data: Optional[Dict] = None):
        """Programa un evento en la lista de eventos futuros."""
        event = Event(time, event_type, data or {})
        heapq.heappush(self._event_list, (time, self._tiebreaker, event))
        self._tiebreaker += 1

    def next_event(self) -> Event:
        """Extrae y retorna el proximo evento (el de menor tiempo)."""
        time, _, event = heapq.heappop(self._event_list)
        self.clock = time
        return event

    def has_events(self) -> bool:
        """Verifica si hay eventos pendientes."""
        return len(self._event_list) > 0

    def run(self, model):
        """
        Bucle principal de simulacion.

        1. Inicializa el modelo
        2. Procesa eventos hasta que no queden mas o el modelo indique parar
        3. Finaliza el modelo para recoger resultados
        """
        model.initialize(self)
        while self.has_events():
            event = self.next_event()
            if not model.should_continue(event):
                break
            model.handle_event(self, event)
        return model.finalize(self)
