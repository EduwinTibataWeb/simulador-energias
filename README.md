# Simulador de Energías Mecánicas

Bloque que desciende por una rampa sin fricción (A→B), cruza un tramo rugoso (B→C), un tramo liso (C→D) y comprime un resorte.
Python + Streamlit + Plotly; escenario animado con HTML5 Canvas (componente propio, sin dependencias extra).

## Estructura
```
app.py              Interfaz Streamlit (escenario, KPIs, tablas, gráfica)
physics.py          Fórmulas y validaciones (sin Streamlit)
visualization.py    Componente Canvas + gráfica Plotly
frontend/index.html Escenario: panel flotante, animación, controles
frontend/img/       caja.png y resorte.png (opcionales)
assets/styles.css   Estilos de la parte inferior
tests/              Pruebas del modelo físico
```

## Tus imágenes
Copia tus archivos a `frontend/img/` con estos nombres **en minúsculas**: `caja.png` y `resorte.png`
(también se aceptan `.webp`, `.jpg`, `.jpeg`). Si no están, el escenario dibuja la caja y el resorte con vectores.
En `resorte.png` la placa debe quedar a la izquierda: la app la voltea para apoyarla en la pared derecha.

## Ejecutar en local
```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```

## Pruebas
```bash
python -m unittest tests.test_physics -v
```

## Publicar
1. Sube la carpeta a un repositorio de GitHub (incluye `frontend/img/`).
2. En https://share.streamlit.io/ elige el repositorio, la rama y `app.py` como archivo principal, y pulsa Deploy.

## Modelo (según el instructivo)
g = 9.8 m/s² · vB = √(2gh) · vC = √(kx²/m) · μk = [mgh − ½kx²]/(mgd) · energía disipada = mgh − ½kx².
Si μk < 0 los datos son incompatibles y se muestra un aviso en lugar de resultados.
