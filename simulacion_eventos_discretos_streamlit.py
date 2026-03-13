import streamlit as st
import random
import math
import pandas as pd

st.set_page_config(page_title="Simulación de Eventos Discretos - Sistema de Pacientes", layout="wide")

st.title("Simulación de Eventos Discretos - Sistema de Atención de Pacientes")

st.markdown("---")

# =========================
# PARTE A: DEFINICIONES TEÓRICAS
# =========================

st.header("1️⃣ Modelo Conceptual del Sistema")

st.subheader("a) Estado del sistema")
st.write("""
El estado del sistema en cualquier instante t está definido por:
- Número de pacientes en cola
- Estado del servidor (0 = libre, 1 = ocupado)
- Tiempo actual de simulación
""")

st.subheader("b) Eventos")
st.write("""
Eventos considerados:
1. Llegada de paciente
2. Inicio de atención
3. Fin de atención (salida del sistema)
""")

st.subheader("c) Lista de Eventos Futuros (FEL)")
st.write("""
La FEL contiene:
- Próxima llegada
- Próximo fin de servicio

Siempre se ejecuta el evento con menor tiempo programado.
""")

st.subheader("d) Variables estadísticas acumulativas")
st.write("""
- Tiempo total en cola
- Tiempo total en sistema
- Área bajo la curva del número en cola
- Utilización del servidor
""")

st.markdown("---")

# =========================
# PARTE B: PARÁMETROS
# =========================

st.header("2️⃣ Parámetros del Modelo M/M/1")

col1, col2 = st.columns(2)

with col1:
    lam = st.number_input("Tasa de llegada (λ)", value=0.8)
with col2:
    mu = st.number_input("Tasa de servicio (μ)", value=1.2)

n_pacientes = st.number_input("Número de pacientes (mínimo 10)", min_value=10, value=10)

if lam >= mu:
    st.error("El sistema no es estable (λ debe ser menor que μ)")

st.markdown("---")

# =========================
# PARTE C: SIMULACIÓN MANUAL PASO A PASO
# =========================

st.header("3️⃣ Simulación Paso a Paso")

if st.button("Ejecutar Simulación"):

    random.seed(42)

    llegada = []
    servicio = []
    inicio = []
    fin = []
    tiempo_cola = []
    tiempo_sistema = []

    tiempo_actual = 0

    for i in range(n_pacientes):
        interarrival = -math.log(1 - random.random()) / lam
        tiempo_servicio = -math.log(1 - random.random()) / mu

        if i == 0:
            llegada.append(interarrival)
        else:
            llegada.append(llegada[i-1] + interarrival)

        servicio.append(tiempo_servicio)

        if i == 0:
            inicio.append(llegada[i])
        else:
            inicio.append(max(llegada[i], fin[i-1]))

        fin.append(inicio[i] + servicio[i])
        tiempo_cola.append(inicio[i] - llegada[i])
        tiempo_sistema.append(fin[i] - llegada[i])

    df = pd.DataFrame({
        "Paciente": range(1, n_pacientes+1),
        "Tiempo Llegada": llegada,
        "Tiempo Servicio": servicio,
        "Inicio Atención": inicio,
        "Fin Atención": fin,
        "Tiempo en Cola": tiempo_cola,
        "Tiempo en Sistema": tiempo_sistema
    })

    st.dataframe(df)

    # =========================
    # MÉTRICAS SIMULADAS
    # =========================

    Wq_sim = sum(tiempo_cola) / n_pacientes
    W_sim = sum(tiempo_sistema) / n_pacientes
    utilizacion_sim = sum(servicio) / fin[-1]

    st.subheader("📊 Métricas Simuladas")
    st.write(f"Tiempo promedio en cola (Wq): {Wq_sim:.4f}")
    st.write(f"Tiempo promedio en sistema (W): {W_sim:.4f}")
    st.write(f"Utilización del servidor: {utilizacion_sim:.4f}")

    # =========================
    # RESULTADOS ANALÍTICOS M/M/1
    # =========================

    rho = lam / mu
    Wq_teo = rho / (mu - lam)
    W_teo = 1 / (mu - lam)

    st.subheader("📘 Resultados Analíticos (Modelo M/M/1)")
    st.write(f"ρ (Utilización teórica): {rho:.4f}")
    st.write(f"Wq teórico: {Wq_teo:.4f}")
    st.write(f"W teórico: {W_teo:.4f}")

    st.subheader("📌 Comparación")
    st.write("Diferencias pueden deberse al tamaño pequeño de muestra y al comportamiento transitorio inicial.")

st.markdown("---")

# =========================
# PARTE D: EXPLICACIÓN TEÓRICA
# =========================

st.header("4️⃣ Comportamiento Transitorio vs Estacionario")

st.write("""
🔹 Comportamiento Transitorio:
Es la fase inicial de la simulación donde el sistema aún no ha alcanzado equilibrio.
Los indicadores cambian significativamente y no representan el comportamiento
real a largo plazo.

🔹 Comportamiento Estacionario:
Es la condición donde las métricas del sistema se estabilizan y oscilan
alrededor de valores constantes. En esta fase los resultados convergen
a los valores analíticos del modelo M/M/1.

En simulaciones con pocos pacientes (como 10), domina el efecto transitorio.
Para aproximarse al comportamiento estacionario se requieren muchas más observaciones.
""")

st.markdown("---")
st.success("Aplicación lista para publicar en Streamlit Cloud 🚀")
