"""Modelo físico del Simulador de Energías Mecánicas.

Este módulo no depende de Streamlit ni de la animación: solo implementa las
fórmulas del instructivo y las validaciones. g es una constante fija.
"""
from __future__ import annotations

from dataclasses import dataclass, asdict
from math import isfinite, sqrt

import pandas as pd

G = 9.8  # m/s², fija
POINTS = ("A", "B", "C", "D")
TOL = 1e-9


@dataclass(frozen=True)
class Params:
    """m [kg], h [m], d = BC [m], k [N/m], x [m]. Valores del caso de prueba."""
    m: float = 10.0
    h: float = 3.0
    d: float = 6.0
    k: float = 2250.0
    x: float = 0.3


@dataclass(frozen=True)
class PointState:
    name: str
    v: float   # velocidad [m/s]
    y: float   # altura [m]
    c: float   # compresión del resorte [m]
    ek: float
    epy: float
    epel: float

    @property
    def emec(self) -> float:
        return self.ek + self.epy + self.epel


@dataclass(frozen=True)
class Result:
    params: Params
    g: float
    v_b: float
    v_c: float
    mu: float
    e_diss: float          # energía disipada por fricción = EmecB - EmecC
    points: tuple          # tuple[PointState, ...] en orden A, B, C, D

    def point(self, name: str) -> PointState:
        return self.points[POINTS.index(name)]

    def checks(self) -> dict:
        """Comprobaciones de consistencia (True = cumple)."""
        a, b, c, d = self.points
        p = self.params
        close = lambda u, w: abs(u - w) <= 1e-9 * max(1.0, abs(u), abs(w))
        return {
            "Conservación A → B": close(a.emec, b.emec),
            "Pérdida B → C igual a μk·m·g·d": close(b.emec - c.emec, self.mu * p.m * self.g * p.d),
            "Conservación C → D": close(c.emec, d.emec),
        }


def validate_inputs(p: Params) -> list:
    """Devuelve la lista de errores de entrada (vacía si todo es válido)."""
    errs = []
    for name, val in asdict(p).items():
        if not isfinite(val):
            errs.append(f"El valor de «{name}» debe ser un número finito.")
    if errs:
        return errs
    if p.m <= 0:
        errs.append("La masa m debe ser mayor que cero.")
    if p.h < 0:
        errs.append("La altura inicial h debe ser mayor o igual a cero.")
    if p.d <= 0:
        errs.append("La longitud del tramo BC (d) debe ser mayor que cero.")
    if p.k <= 0:
        errs.append("La constante del resorte k debe ser mayor que cero.")
    if p.x < 0:
        errs.append("La compresión x debe ser mayor o igual a cero.")
    return errs


def solve(p: Params):
    """Resuelve el modelo académico. Devuelve (Result | None, errores)."""
    errs = validate_inputs(p)
    if errs:
        return None, errs

    # Coeficiente de fricción: μk = [mgh − ½kx²] / (m g d)
    e_spring = 0.5 * p.k * p.x ** 2
    mu = (p.m * G * p.h - e_spring) / (p.m * G * p.d)
    if mu < -TOL:
        return None, [
            f"Datos incompatibles con el modelo: μk = {mu:.3f} es negativo. "
            f"El resorte almacenaría más energía (½kx² = {e_spring:.2f} J) que la "
            f"disponible en A (mgh = {p.m * G * p.h:.2f} J). Aumenta h o m, o reduce k o x."
        ]
    mu = max(mu, 0.0)

    v_b = sqrt(2 * G * p.h)                 # mgh = ½ m vB²
    v_c = sqrt(p.k * p.x ** 2 / p.m)        # ½ m vC² = ½ k x²

    pts = (
        PointState("A", 0.0, p.h, 0.0, 0.0, p.m * G * p.h, 0.0),
        PointState("B", v_b, 0.0, 0.0, 0.5 * p.m * v_b ** 2, 0.0, 0.0),
        PointState("C", v_c, 0.0, 0.0, 0.5 * p.m * v_c ** 2, 0.0, 0.0),
        PointState("D", 0.0, 0.0, p.x, 0.0, 0.0, e_spring),
    )
    e_diss = pts[1].emec - pts[2].emec
    return Result(p, G, v_b, v_c, mu, e_diss, pts), []


def kinematics_table(r: Result) -> pd.DataFrame:
    return pd.DataFrame(
        {
            "Punto": [s.name for s in r.points],
            "Velocidad (m/s)": [s.v for s in r.points],
            "Altura (m)": [s.y for s in r.points],
            "Compresión (m)": [s.c for s in r.points],
        }
    )


def energy_table(r: Result) -> pd.DataFrame:
    return pd.DataFrame(
        {
            "Punto": [s.name for s in r.points],
            "Ek (J)": [s.ek for s in r.points],
            "Ep,y (J)": [s.epy for s in r.points],
            "Ep,el (J)": [s.epel for s in r.points],
            "Emec (J)": [s.emec for s in r.points],
        }
    )


def rebound(r: Result) -> dict:
    """Extensión del instructivo: el resorte devuelve el bloque.

    F_max = k·x. Al recuperar su longitud natural el resorte entrega la energía
    ½kx², así que el bloque sale hacia C con vC. En BC la fricción lo frena con a = μk·g:
    distancia de frenado = vC² / (2·μk·g). Si es mayor que d, el bloque cruza B.
    """
    p = r.params
    out = {"force_max": p.k * p.x, "v_return": r.v_c, "distance": None, "stops_in_bc": False}
    if r.v_c <= TOL:
        out.update(distance=0.0, stops_in_bc=True)
    elif r.mu > TOL:
        dist = r.v_c ** 2 / (2 * r.mu * r.g)
        out.update(distance=dist, stops_in_bc=dist <= p.d + TOL)
    return out


def sim_payload(r: Result) -> dict:
    """Datos que consume el motor de animación (solo lectura de resultados)."""
    return {
        "g": r.g, "vB": r.v_b, "vC": r.v_c, "mu": r.mu, "e_diss": r.e_diss,
        "emec": [s.emec for s in r.points],
    }
