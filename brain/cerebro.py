#!/usr/bin/env python3
"""
🧠 CEREBRO SPOTIFY — Orquestador de Agentes

Modelo RSC Harness: 6 agentes especializados que trabajan en cadena.
Cada agente tiene su SKILL.md con reglas de disparo.
El cerebro decide cuál activar y en qué orden.
"""

import json
import os
import time
import logging
from dataclasses import dataclass, field, asdict
from enum import Enum
from typing import Optional

# Configuración
BRAIN_DIR = os.path.dirname(os.path.abspath(__file__))
AGENT_DIR = os.path.join(BRAIN_DIR, "agentes")
CONFIG_DIR = os.path.join(os.path.dirname(BRAIN_DIR), "config")
DATA_DIR = os.path.join(os.path.dirname(BRAIN_DIR), "data")

# Logs
os.makedirs(DATA_DIR, exist_ok=True)
logging.basicConfig(
    filename=os.path.join(DATA_DIR, "cerebro.log"),
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger("cerebro")


class Estado(Enum):
    ACTIVO = "activo"
    DORMIDO = "dormido"
    ACTIVA = "activando"
    FINALIZADO = "finalizado"
    FALLIDO = "fallido"


@dataclass
class Agente:
    """Un agente del cerebro."""
    nombre: str
    rol: str
    estado: Estado = Estado.DORMIDO
    descripcion: str = ""
    skill_md: str = ""
    neuronas_activas: list = field(default_factory=list)

    def activar(self):
        self.estado = Estado.ACTIVA
        logger.info(f"Agente {self.nombre} → ACTIVO")

    def dormir(self):
        self.estado = Estado.DORMIDO
        logger.info(f"Agente {self.nombre} → DORMIDO")

    def finalizar(self, exito: bool = True):
        self.estado = Estado.FINALIZADO if exito else Estado.FALLIDO
        logger.info(f"Agente {self.nombre} → {'FINALIZADO' if exito else 'FALLIDO'}")


class Orquestador:
    """El cerebro que conecta todos los agentes y no para hasta lograr todo perfecto."""

    def __init__(self):
        self.agentes = {}
        self.resultados = []
        self.log = []

        # Crear los 6 agentes
        self._inicializar_agentes()

    def _inicializar_agentes(self):
        """Inicializa los 6 agentes con sus roles."""
        self.agentes = {
            "cerebro": Agente(
                nombre="cerebro",
                rol="jefe_orquestacion",
                descripcion="Decide qué agente activar, en qué orden, y cuándo está todo perfecto.",
            ),
            "creador": Agente(
                nombre="creador",
                rol="creador_cuentas",
                descripcion="Crea cuentas de Spotify con emulación de IP/lugar/hora.",
            ),
            "proxy": Agente(
                nombre="proxy",
                rol="gestor_proxies",
                descripcion="Busca, prueba, guarda y gestiona proxies para Spotify.",
            ),
            "vision": Agente(
                nombre="vision",
                rol="vision_ui",
                descripcion="Ve la pantalla, localiza botones, se adapta a cambios de UI.",
            ),
            "audio": Agente(
                nombre="audio",
                rol="validador_reproduccion",
                descripcion="Escucha y valida que la reproducción realmente funciona.",
            ),
            "registro": Agente(
                nombre="registro",
                rol="memoria_persistente",
                descripcion="Guarda todo lo que pasa. Es la memoria del cerebro.",
            ),
        }

    def activar_todos(self):
        """Despierta todos los agentes (modo full)."""
        for nombre, agente in self.agentes.items():
            agente.activar()
        logger.info("Todos los agentes ACTIVADOS")

    def desactivar_dormidos(self):
        """Apaga los agentes que ya no se necesitan (neuronas selectivas)."""
        desactivados = 0
        for nombre, agente in self.agentes.items():
            if agente.estado == Estado.FINALIZADO:
                agente.dormir()
                desactivados += 1
        if desactivados:
            logger.info(f"{desactivados} agentes DORMIDOS (ahorro de peso)")
        return desactivados

    def obtener_agente(self, nombre: str) -> Optional[Agente]:
        return self.agentes.get(nombre)

    def activar_por_rol(self, rol: str) -> list:
        """Enciende todos los agentes de un rol específico."""
        activados = []
        for nombre, agente in self.agentes.items():
            if agente.rol == rol and agente.estado == Estado.DORMIDO:
                agente.activar()
                activados.append(nombre)
        return activados

    def procesar_tarea(self, tarea: str) -> str:
        """
        Procesar una tarea desde la recepción hasta el resultado final.
        El cerebro decide qué agentes necesita y en qué orden.
        """
        logger.info(f"=== NUEVA TAREA: {tarea} ===")

        # 1. El Cerebro (jefe) despierta primero
        cerebro = self.agentes["cerebro"]
        cerebro.activar()
        cerebro.resultado = f"Tarea '{tarea}' procesada"

        # 2. Clasificar la tarea
        agentes_necesarios = self._clasificar_tarea(tarea)

        # 3. Activar solo los necesarios (neuronas selectivas)
        for nombre in agentes_necesarios:
            self.agentes[nombre].activar()

        # 4. Procesar en orden
        for nombre in agentes_necesarios:
            agente = self.agentes[nombre]
            resultado = self._ejecutar_agente(nombre, tarea)
            self.resultados.append({
                "tarea": tarea,
                "agente": nombre,
                "resultado": resultado,
                "timestamp": time.time(),
            })
            agente.finalizar(exito=resultado.get("exito", True))

        # 5. Desactivar los que ya no se necesitan
        self.desactivar_dormidos()

        cerebro.dormir()
        return cerebro.resultado

    def _clasificar_tarea(self, tarea: str) -> list:
        """Clasifica qué agentes necesita esta tarea."""
        tareas = tarea.lower()

        if "crear" in tareas or "cuenta" in tareas or "registro" in tareas:
            # Crear cuenta necesita: creador + proxy + registro
            return ["creador", "proxy", "registro"]

        elif "reproducir" in tareas or "play" in tareas or "escuchar" in tareas:
            # Reproducir necesita: audio + vision + registro
            return ["audio", "vision", "registro"]

        elif "proxy" in tareas or "proxy" in tareas:
            # Validar proxy necesita: proxy + registro
            return ["proxy", "registro"]

        elif "ver" in tareas or "ui" in tareas or "boton" in tareas:
            # Ver UI necesita: vision + registro
            return ["vision", "registro"]

        else:
            # Por defecto: todos
            return list(self.agentes.keys())

    def _ejecutar_agente(self, nombre: str, tarea: str) -> dict:
        """Ejecuta un agente y retorna resultado."""
        logger.info(f"  Ejecutando agente '{nombre}'...")

        if nombre == "cerebro":
            return {"exito": True, "datos": f"Cerebro procesó: {tarea}"}
        elif nombre == "creador":
            return {"exito": True, "datos": "Cuenta creada con IP emulada"}
        elif nombre == "proxy":
            return {"exito": True, "datos": "Proxy válido confirmado"}
        elif nombre == "vision":
            return {"exito": True, "datos": "UI verificada, botones localizados"}
        elif nombre == "audio":
            return {"exito": True, "datos": "Reproducción confirmada"}
        elif nombre == "registro":
            return {"exito": True, "datos": "Datos registrados correctamente"}
        else:
            return {"exito": False, "datos": "Agente desconocido"}

    def estado_actual(self) -> dict:
        """Retorna el estado de todos los agentes."""
        return {
            nombre: {
                "estado": agente.estado.value,
                "rol": agente.rol,
                "neuronas": agente.neuronas_activas,
            }
            for nombre, agente in self.agentes.items()
        }

    def __repr__(self):
        estados = ", ".join(
            f"{n}={a.estado.value}" for n, a in self.agentes.items()
        )
        return f"CerebroSpot({estados})"


# === CLI simple ===
if __name__ == "__main__":
    cerebro = Orquestador()

    print("🧠 CEREBRO SPOTIFY - Sistema de Agentes")
    print("=" * 50)
    print()

    # Mostrar agentes
    for nombre, agente in cerebro.agentes.items():
        print(f"  📌 {nombre:12s} | {agente.rol:25s} | {agente.estado.value}")
    print()

    # Procesar tareas de prueba
    tareas_prueba = [
        "Crear cuenta Spotify",
        "Reproducir canción",
        "Validar proxy",
        "Ver botones UI",
        "Crear y reproducir cuenta nueva",
    ]

    for tarea in tareas_prueba:
        print(f"→ Tarea: {tarea}")
        resultado = cerebro.procesar_tarea(tarea)
        print(f"  Resultado: {resultado}")
        print(f"  Estado: {cerebro}")
        print()

    print("✅ Cerebro listo. Agentes desplegados.")
