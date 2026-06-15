# telemetry.py

from datetime import datetime

class Telemetry:
    def __init__(self):
        self.events = []

    def log_event(self, event_type: str, details: dict) -> None:
        """Registra un evento con el tipo y detalles proporcionados."""
        timestamp = datetime.now().isoformat()
        event = {
            "timestamp": timestamp,
            "type": event_type,
            "details": details
        }
        self.events.append(event)

    def log_metric(self, metric_name: str, value: float) -> None:
        """Registra una métrica con el nombre y valor proporcionados."""
        timestamp = datetime.now().isoformat()
        metric = {
            "timestamp": timestamp,
            "name": metric_name,
            "value": value
        }
        self.events.append(metric)

    def send_to_server(self, server_url: str) -> None:
        """Envía la telemetría al servidor especificado."""
        import requests
        try:
            response = requests.post(server_url, json=self.events)
            if response.status_code == 200:
                print("Telemetría enviada con éxito.")
            else:
                print(f"Error al enviar telemetría: {response.status_code}")
        except requests.exceptions.RequestException as e:
            print(f"Error al enviar telemetría: {e}")

    def clear_events(self) -> None:
        """Limpia la lista de eventos."""
        self.events = []

# Bucle principal del juego
hora_global = 12  # Inicia en mediodía
telemetry = Telemetry()

while True:
    dt = ...  # Tiempo transcurrido desde la última iteración (por ejemplo, 0.01667 para 60 FPS)
    hora_global += dt / 60.0

    # Registrar evento de tick del NPC
    if npc.id in player_actions:
        telemetry.log_event("npc_action", {
            "npc_id": npc.id,
            "action": player_actions[npc.id],
            "timestamp": datetime.now().isoformat()
        })

    # Otros procesos del juego...

    # Enviar telemetría al servidor cada 60 segundos
    if hora_global % 60 == 0:
        telemetry.send_to_server("http://example.com/telemetry")

# Pruebas adicionales
def test_telemetry():
    telemetry = Telemetry()

    # Registrar eventos y métricas
    telemetry.log_event("test_event", {"message": "This is a test event"})
    telemetry.log_metric("test_metric", 123.45)

    # Enviar telemetría (simulado)
    print(telemetry.events)
    telemetry.send_to_server("http://example.com/telemetry")

    # Limpiar eventos
    telemetry.clear_events()
    assert not telemetry.events, "Event list should be empty after clearing"

# Ejecutar las pruebas
test_telemetry()

# telemetry.py

telemetry = Telemetry()

def log_game_event(event_type: str, details: dict):
    telemetry.log_event(event_type, details)

def send_telemetry(server_url: str):
    telemetry.send_to_server(server_url)


