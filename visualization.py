"""Componente de simulación (Canvas) y gráfica de energías (Plotly)."""
from __future__ import annotations

from dataclasses import asdict
from pathlib import Path

import plotly.graph_objects as go
import streamlit.components.v1 as components

from physics import POINTS, Params, Result, sim_payload

_FRONTEND = Path(__file__).parent / "frontend"
_sim = components.declare_component("energy_simulator", path=str(_FRONTEND))

SERIES = (  # (atributo, etiqueta, color)
    ("ek", "Ek · cinética", "#22d3ee"),
    ("epy", "Ep,y · gravitacional", "#3b82f6"),
    ("epel", "Ep,el · elástica", "#34d399"),
    ("emec", "Emec · mecánica", "#a78bfa"),
)


def simulator(params: Params, result: Result | None, errors: list):
    """Dibuja el escenario. Devuelve los parámetros editados en el panel (dict) o None."""
    return _sim(
        params=asdict(params),
        defaults=asdict(Params()),
        result=sim_payload(result) if result else None,
        errors=errors,
        key="simulator",
        default=None,
    )


def energy_chart(result: Result) -> go.Figure:
    fig = go.Figure()
    for attr, label, color in SERIES:
        ys = [getattr(s, attr) for s in result.points]
        fig.add_bar(
            x=list(POINTS), y=ys, name=label, marker_color=color,
            text=[f"{v:.1f}" for v in ys], textposition="outside", cliponaxis=False,
            textfont=dict(size=11, color="#c7d4ea"),
            hovertemplate=f"<b>{label}</b><br>Punto %{{x}}: %{{y:.3f}} J<extra></extra>",
        )
    fig.update_layout(
        barmode="group", bargap=0.22, bargroupgap=0.06, height=470,
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter, system-ui, sans-serif", color="#c7d4ea"),
        margin=dict(l=10, r=10, t=40, b=10),
        legend=dict(orientation="h", y=1.1, x=0),
        xaxis=dict(title="Punto de la trayectoria", showgrid=False, linecolor="rgba(140,170,220,.25)"),
        yaxis=dict(title="Energía (J)", gridcolor="rgba(140,170,220,.12)", zerolinecolor="rgba(140,170,220,.3)"),
        hoverlabel=dict(bgcolor="#0b1730", font_size=13),
    )
    return fig
