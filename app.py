"""Simulador de Energías Mecánicas — interfaz principal (Streamlit)."""
from __future__ import annotations

from pathlib import Path

import streamlit as st

from physics import Params, Result, energy_table, kinematics_table, rebound, solve
from visualization import energy_chart, simulator

st.set_page_config(
    page_title="Simulador de Energías Mecánicas",
    page_icon=None,
    layout="wide",
    initial_sidebar_state="collapsed",
)
st.markdown(f"<style>{(Path(__file__).parent / 'assets' / 'styles.css').read_text(encoding='utf-8')}</style>",
            unsafe_allow_html=True)


# ---------- Estado: los parámetros viven en session_state ----------
def coerce(value) -> Params | None:
    try:
        return Params(**{k: float(value[k]) for k in ("m", "h", "d", "k", "x")})
    except (KeyError, TypeError, ValueError):
        return None


def table_html(df, decimals: int) -> str:
    head = "".join(f"<th>{c}</th>" for c in df.columns)
    rows = "".join(
        "<tr>" + "".join(
            f"<td>{v}</td>" if isinstance(v, str) else f"<td>{v:.{decimals}f}</td>" for v in row
        ) + "</tr>"
        for row in df.itertuples(index=False)
    )
    return f"<div class='tbl-wrap'><table class='tbl'><thead><tr>{head}</tr></thead><tbody>{rows}</tbody></table></div>"


def kpi(name: str, value: str, unit: str, desc: str, cls: str = "") -> str:
    return (f"<div class='kpi {cls}'><div class='n'>{name}</div>"
            f"<div class='v'>{value}<em>{unit}</em></div><div class='d'>{desc}</div></div>")


def plotly_full_width(fig) -> None:
    try:
        st.plotly_chart(fig, width="stretch", config={"displaylogo": False})
    except Exception:  # versiones antiguas de Streamlit
        st.plotly_chart(fig, use_container_width=True, config={"displaylogo": False})


def show_results(r: Result) -> None:
    st.markdown("<div class='sec'>Resultados<small>Se actualizan con cada cambio de parámetros</small></div>",
                unsafe_allow_html=True)
    st.markdown(
        "<div class='kpis'>"
        + kpi("Coeficiente de fricción", f"{r.mu:.3f}", "μk", "Calculado con μk = [mgh − ½kx²] / (mgd).", "fr")
        + kpi("Velocidad en B", f"{r.v_b:.2f}", "m/s", "Final de la rampa: vB = √(2gh).")
        + kpi("Velocidad en C", f"{r.v_c:.2f}", "m/s", "Final de la fricción: vC = √(kx²/m).")
        + kpi("Energía disipada", f"{r.e_diss:.2f}", "J", "Trabajo de la fricción entre B y C.", "fr")
        + "</div>",
        unsafe_allow_html=True,
    )
    chips = "".join(f"<span class='chip {'' if ok else 'bad'}'>{name}</span>" for name, ok in r.checks().items())
    st.markdown(f"<div class='chips'>{chips}</div>", unsafe_allow_html=True)
    rb = rebound(r)
    if rb["distance"] is None:
        tail = "Sin fricción no pierde energía: el bloque vuelve a subir la curva y el movimiento se repite."
    elif rb["stops_in_bc"]:
        tail = f"En BC la fricción lo frena y se detiene a <b>{rb['distance']:.2f} m</b> de C."
    else:
        tail = f"Frenaría en {rb['distance']:.2f} m, más que BC: cruza B y sube de nuevo por la curva."
    st.markdown(
        f"<div class='note'><b>Rebote del resorte</b> (extensión del modelo): fuerza máxima F = kx = "
        f"<b>{rb['force_max']:.1f} N</b>. Al descomprimirse devuelve el bloque con <b>{rb['v_return']:.2f} m/s</b>. {tail}</div>",
        unsafe_allow_html=True)

    st.markdown("<div class='sec'>Magnitudes físicas por punto</div>", unsafe_allow_html=True)
    st.markdown(table_html(kinematics_table(r), 3), unsafe_allow_html=True)
    st.markdown("<div class='sec'>Energías por punto<small>Ek + Ep,y + Ep,el = Emec</small></div>",
                unsafe_allow_html=True)
    st.markdown(table_html(energy_table(r), 3), unsafe_allow_html=True)
    st.markdown("<div class='sec'>Comparación de energías</div>", unsafe_allow_html=True)
    plotly_full_width(energy_chart(r))


# ---------- Flujo ----------
if "params" not in st.session_state:
    st.session_state.params = Params()

params: Params = st.session_state.params
result, errors = solve(params)

st.markdown("<div class='app-title'><h1>Simulador de Energías Mecánicas</h1>"
            "<span>Melissa Leonela Montaña Urrego</span></div>", unsafe_allow_html=True)

edited = simulator(params, result, errors)

# El valor del componente persiste entre reruns: solo se aplica cuando cambia.
if edited is not None and edited != st.session_state.get("last_edit"):
    st.session_state.last_edit = edited
    new = coerce(edited)
    if new is not None and new != params:
        st.session_state.params = new
        st.rerun()

if errors:
    for msg in errors:
        st.warning(msg)
else:
    show_results(result)
