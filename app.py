"""Oil & Gas Engineering Dashboard - Streamlit Community Cloud entry point."""

from pathlib import Path

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
import streamlit.components.v1 as components

from calculations import composite_ipr, hydrostatic_pressure, volumetric_oip


BASE_DIR = Path(__file__).parent
st.set_page_config(page_title="Oil & Gas Engineering Dashboard", page_icon="🛢️", layout="wide")


def load_css():
    """Carga los estilos locales sin impedir el arranque si el archivo falta."""
    css_file = BASE_DIR / "styles.css"
    if css_file.is_file():
        st.markdown(f"<style>{css_file.read_text(encoding='utf-8')}</style>", unsafe_allow_html=True)
    else:
        # La aplicación se mantiene operativa mientras se corrige el contenido del repositorio.
        st.warning("No se encontró styles.css. La aplicación funciona, pero sin la personalización visual completa.")


def card(title: str, value: str, unit: str = ""):
    st.markdown(
        f'<div class="metric-card"><h3>{title}</h3><div class="metric-value">{value}</div>'
        f'<div class="metric-unit">{unit}</div></div>', unsafe_allow_html=True
    )


def status(message: str, kind: str):
    st.markdown(f'<div class="status {kind}">{message}</div>', unsafe_allow_html=True)


def hero(title: str, description: str, eyebrow: str = "Bootcamp Data Analytics for Oil & Gas"):
    st.markdown(
        f'<section class="hero"><div class="eyebrow">{eyebrow}</div><h1>{title}</h1><p>{description}</p></section>',
        unsafe_allow_html=True,
    )


def javascript_microinteraction():
    """Componente JavaScript visible: cambia un insight operativo al presionar el botón."""
    components.html(
        """<div style="font-family:Arial,sans-serif;background:#e8f2f8;border-radius:12px;padding:16px 20px;"
        "color:#082e59;border-left:4px solid #0b70b8;display:flex;align-items:center;justify-content:space-between;gap:12px">
        <span id="insight" style="font-weight:600">Insight operativo listo para explorar.</span>
        <button onclick="nextInsight()" style="cursor:pointer;border:0;border-radius:7px;padding:9px 12px;background:#0b70b8;color:#fff;font-weight:700">Nuevo insight</button>
        </div><script>
        const insights=['La IPR identifica el régimen de flujo respecto a Pb.','TVD, no MD, controla la presión hidrostática.','POES no equivale a reservas: el factor de recobro las vincula.'];
        let index=0; function nextInsight(){index=(index+1)%insights.length;document.getElementById('insight').textContent=insights[index];}
        </script>""",
        height=76,
    )


def home():
    hero("Oil & Gas Engineering Dashboard", "Una aplicación técnica para interpretar el desempeño de producción, el balance hidrostático de perforación y el potencial volumétrico de un reservorio.")
    left, right = st.columns([1.2, 1])
    with left:
        st.markdown('<div class="section-kicker">Aplicación de ingeniería</div>', unsafe_allow_html=True)
        st.markdown("## Decisiones mejor informadas desde los datos")
        st.write("Este tablero integra cálculos fundamentales de ingeniería de petróleos en una experiencia visual clara, trazable y orientada a la toma de decisiones técnicas.")
        javascript_microinteraction()
    with right:
        st.markdown("<div class='info-card'><h3>Participante</h3><p><b>Alan López</b><br>Ingeniero de Petróleos</p></div>", unsafe_allow_html=True)
        st.markdown("<div style='height:.6rem'></div>", unsafe_allow_html=True)
        st.markdown("<div class='info-card'><h3>Programa</h3><p>Bootcamp Data Analytics for Oil & Gas<br><br>Society of Petroleum Engineers - Ecuador Section</p></div>", unsafe_allow_html=True)
    st.markdown("<br><div class='section-kicker'>Módulos técnicos</div>", unsafe_allow_html=True)
    cols = st.columns(3)
    modules = [("Producción", "IPR compuesta y comportamiento alrededor del punto de burbuja."), ("Perforación", "Presión hidrostática, TVD y condición de balance."), ("Reservorios", "POES volumétrico y volumen potencialmente recuperable.")]
    for column, (title, detail) in zip(cols, modules):
        with column:
            st.markdown(f"<div class='info-card'><h3>{title}</h3><p>{detail}</p></div>", unsafe_allow_html=True)


def production_tab():
    st.subheader("IPR compuesta con punto de burbuja")
    st.caption("Yacimiento inicialmente subsaturado: régimen lineal por encima de Pb y Vogel por debajo de Pb.")
    a, b, c, d = st.columns(4)
    pr = a.number_input("Pr - Presión de reservorio [psi]", min_value=1.0, value=3500.0, step=100.0)
    pb = b.number_input("Pb - Presión de burbuja [psi]", min_value=1.0, value=2200.0, step=100.0)
    j = c.number_input("J - Índice de productividad [STB/d/psi]", min_value=0.01, value=1.2, step=0.1)
    pwf = d.number_input("Pwf - Presión de fondo fluyente [psi]", min_value=0.0, value=1500.0, step=100.0)
    st.markdown("<div class='formula'>qₒ = J(Pr - Pwf) si Pwf ≥ Pb &nbsp; | &nbsp; Modelo de Vogel compuesto si Pwf &lt; Pb</div>", unsafe_allow_html=True)
    if pb >= pr or pwf > pr:
        st.error("Validación física: debe cumplirse Pr > Pb y Pwf ≤ Pr.")
        return
    q_user, qb, qmax = composite_ipr(pr, pb, j, pwf)
    if pwf >= pb:
        status("OPERACIÓN POR ENCIMA DE Pb - flujo monofásico, comportamiento lineal.", "good")
    else:
        status("OPERACIÓN POR DEBAJO DE Pb - régimen bifásico, respuesta no lineal de Vogel.", "warn")
    x, y, z = st.columns(3)
    with x: card("Caudal actual qₒ", f"{float(q_user):,.0f}", "STB/d")
    with y: card("Caudal a Pb qᵦ", f"{qb:,.0f}", "STB/d")
    with z: card("Máximo teórico qₒ,max", f"{qmax:,.0f}", "STB/d")
    pwf_curve = np.linspace(0, pr, 150)
    rates, _, _ = composite_ipr(pr, pb, j, pwf_curve)
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=rates, y=pwf_curve, mode="lines", name="IPR compuesta", line=dict(color="#0b70b8", width=4)))
    fig.add_trace(go.Scatter(x=[float(q_user)], y=[pwf], mode="markers", name="Condición seleccionada", marker=dict(color="#e77c1b", size=13)))
    fig.add_hline(y=pb, line_dash="dash", line_color="#16846b", annotation_text="Pb")
    fig.update_layout(template="plotly_white", height=420, xaxis_title="Caudal de petróleo qₒ [STB/d]", yaxis_title="Pwf [psi]", margin=dict(l=10, r=10, t=30, b=10), legend=dict(orientation="h", y=1.08))
    st.plotly_chart(fig, use_container_width=True)


def drilling_tab():
    st.subheader("Presión hidrostática del lodo")
    st.caption("La presión de la columna de lodo depende de la profundidad vertical verdadera (TVD).")
    a, b, c, d = st.columns(4)
    mw = a.number_input("MW - Peso del lodo [ppg]", min_value=0.01, value=10.5, step=0.1)
    md = b.number_input("MD - Profundidad medida [ft]", min_value=1.0, value=10000.0, step=100.0)
    tvd = c.number_input("TVD - Profundidad vertical [ft]", min_value=1.0, value=8500.0, step=100.0)
    pform = d.number_input("Pform - Presión de formación [psi]", min_value=0.0, value=4500.0, step=100.0)
    st.markdown("<div class='formula'>Gₕ = 0.052 × MW &nbsp; | &nbsp; Pₕ = 0.052 × MW × TVD</div>", unsafe_allow_html=True)
    if tvd > md:
        st.error("Validación geométrica: TVD no puede ser mayor que MD.")
        return
    gradient, pressure, differential = hydrostatic_pressure(mw, tvd, pform)
    tolerance = 50
    if differential > tolerance:
        status("SOBREBALANCE - la presión hidrostática es mayor que la presión de formación.", "good")
    elif differential < -tolerance:
        status("BAJO BALANCE - existe un diferencial negativo frente a la formación.", "bad")
    else:
        status("BALANCE APROXIMADO - diferencial dentro de ±50 psi.", "warn")
    x, y, z = st.columns(3)
    with x: card("Gradiente Gₕ", f"{gradient:.3f}", "psi/ft")
    with y: card("Presión hidrostática Pₕ", f"{pressure:,.0f}", "psi a TVD")
    with z: card("Diferencial ΔP", f"{differential:+,.0f}", "psi vs. Pform")
    depth = np.linspace(0, tvd, 100)
    fig = go.Figure(go.Scatter(x=gradient * depth, y=depth, mode="lines", name="Columna de lodo", line=dict(color="#0b70b8", width=4)))
    fig.add_trace(go.Scatter(x=[pressure], y=[tvd], mode="markers", name="Profundidad actual", marker=dict(color="#e77c1b", size=13)))
    fig.update_layout(template="plotly_white", height=420, xaxis_title="Presión hidrostática [psi]", yaxis_title="TVD [ft]", yaxis=dict(autorange="reversed"), margin=dict(l=10, r=10, t=30, b=10), legend=dict(orientation="h", y=1.08))
    st.plotly_chart(fig, use_container_width=True)


def reservoirs_tab():
    st.subheader("Estimación volumétrica del POES")
    st.caption("El POES representa el volumen original en sitio; no equivale a reservas recuperables.")
    row1 = st.columns(4)
    area = row1[0].number_input("A - Área [acres]", min_value=0.01, value=640.0, step=10.0)
    h = row1[1].number_input("h - Espesor bruto [ft]", min_value=0.01, value=60.0, step=1.0)
    ntg = row1[2].number_input("NTG [fracción]", min_value=0.01, max_value=1.0, value=0.70, step=0.01)
    phi = row1[3].number_input("φ - Porosidad efectiva [fracción]", min_value=0.01, max_value=1.0, value=0.18, step=0.01)
    row2 = st.columns(3)
    swi = row2[0].number_input("Swi - Saturación inicial de agua [fracción]", min_value=0.0, max_value=0.99, value=0.25, step=0.01)
    boi = row2[1].number_input("Boi - Factor volumétrico [rb/STB]", min_value=0.01, value=1.25, step=0.01)
    recovery = row2[2].number_input("FR - Factor de recobro [fracción]", min_value=0.0, max_value=1.0, value=0.30, step=0.01)
    st.markdown("<div class='formula'>POES = [7758 × A × (h × NTG) × φ × (1 - Swi)] / Boi</div>", unsafe_allow_html=True)
    net_h, oip, recoverable = volumetric_oip(area, h, ntg, phi, swi, boi, recovery)
    x, y, z = st.columns(3)
    with x: card("Espesor neto hₙ", f"{net_h:,.1f}", "ft")
    with y: card("POES", f"{oip / 1e6:,.2f}", f"MMSTB ({oip:,.0f} STB)")
    with z: card("Recuperable estimado", f"{recoverable / 1e6:,.2f}", f"MMSTB ({recoverable:,.0f} STB)")
    fig = go.Figure(go.Bar(x=["POES", "Recuperable estimado"], y=[oip / 1e6, recoverable / 1e6], marker_color=["#0b70b8", "#16846b"], text=[f"{oip / 1e6:.2f}", f"{recoverable / 1e6:.2f}"], textposition="outside"))
    fig.update_layout(template="plotly_white", height=390, yaxis_title="Volumen [MMSTB]", margin=dict(l=10, r=10, t=30, b=10), showlegend=False)
    st.plotly_chart(fig, use_container_width=True)


def exercises():
    hero("Módulo de ejercicios", "Ajusta las variables operativas para observar su impacto inmediato en las métricas y visualizaciones técnicas.", "Herramientas de ingeniería")
    production, drilling, reservoirs = st.tabs(["📈 Producción", "⚙️ Perforación", "🧱 Reservorios"])
    with production: production_tab()
    with drilling: drilling_tab()
    with reservoirs: reservoirs_tab()


load_css()
with st.sidebar:
    logo_file = BASE_DIR / "assets" / "spe_ecuador_section.png"
    if logo_file.is_file():
        st.image(str(logo_file), width=185)
    st.markdown("### Engineering Dashboard")
    st.caption("SPE Ecuador Section")
    page = st.radio("Navegación principal", ["Home", "Ejercicios"], label_visibility="collapsed")
    st.markdown("---")
    st.caption("Módulo 1 · Data Analytics for Oil & Gas")

if page == "Home":
    home()
else:
    exercises()
