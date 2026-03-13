import streamlit as st
import numpy as np
import pandas as pd
import math
import matplotlib.pyplot as plt

st.title("Simulación de Eventos Discretos – Sistema de Atención Clínica")

st.sidebar.header("Parámetros del sistema")

lambda_rate = st.sidebar.slider("Tasa de llegadas λ (pacientes/hora)", 1.0, 10.0, 5.0)
service_minutes = st.sidebar.slider("Tiempo promedio de servicio (minutos)", 5.0, 30.0, 10.0)
num_patients = st.sidebar.slider("Número de pacientes a simular", 20, 100000, 1000)
servers = st.sidebar.selectbox("Número de médicos", [1,2])

mu = 60/service_minutes
rho = lambda_rate/(servers*mu)

st.subheader("Parámetros derivados")
st.write(f"μ = {mu:.2f} pacientes/hora")
st.write(f"Utilización ρ = {rho:.3f}")

if rho >= 1:
    st.error("Sistema inestable: ρ ≥ 1")

rng = np.random.default_rng()

arrival_times = np.cumsum(rng.exponential(1/lambda_rate, num_patients))
service_times = rng.exponential(1/mu, num_patients)

start_service = np.zeros(num_patients)
finish_service = np.zeros(num_patients)

if servers == 1:
    for i in range(num_patients):
        if i == 0:
            start_service[i] = arrival_times[i]
        else:
            start_service[i] = max(arrival_times[i], finish_service[i-1])
        finish_service[i] = start_service[i] + service_times[i]

else:
    server_free = [0]*servers

    for i in range(num_patients):
        next_server = np.argmin(server_free)
        start_service[i] = max(arrival_times[i], server_free[next_server])
        finish_service[i] = start_service[i] + service_times[i]
        server_free[next_server] = finish_service[i]

wait_time = start_service - arrival_times
system_time = finish_service - arrival_times

results = pd.DataFrame({
    "Llegada": arrival_times,
    "Servicio": service_times,
    "Inicio Servicio": start_service,
    "Fin Servicio": finish_service,
    "Espera Cola": wait_time,
    "Tiempo Sistema": system_time
})

st.subheader("Tabla de simulación (primeros 20 pacientes)")
st.dataframe(results.head(20))

avg_wait = wait_time.mean()
avg_system = system_time.mean()

st.subheader("Resultados de simulación")
st.write(f"Tiempo promedio en cola Wq: {avg_wait:.4f} horas")
st.write(f"Tiempo promedio en sistema W: {avg_system:.4f} horas")

if servers == 1 and rho < 1:
    Wq_theory = rho/(mu-lambda_rate)
    W_theory = 1/(mu-lambda_rate)

    st.subheader("Comparación con teoría M/M/1")

    st.write(f"Wq teórico: {Wq_theory:.4f} horas")
    st.write(f"W teórico: {W_theory:.4f} horas")


if servers == 2:

    a = lambda_rate/mu

    sum_terms = sum((a**n)/math.factorial(n) for n in range(servers))

    last = (a**servers)/(math.factorial(servers)*(1-rho))

    P0 = 1/(sum_terms + last)

    Lq = (P0*(a**servers)*rho)/(math.factorial(servers)*(1-rho)**2)

    Wq_theory = Lq/lambda_rate

    W_theory = Wq_theory + 1/mu

    st.subheader("Comparación con teoría M/M/2")

    st.write(f"Wq teórico: {Wq_theory:.4f} horas")
    st.write(f"W teórico: {W_theory:.4f} horas")


st.subheader("Convergencia del tiempo de espera")

cum_wait = np.cumsum(wait_time)/np.arange(1,num_patients+1)

fig, ax = plt.subplots()
ax.plot(cum_wait)
ax.set_xlabel("Pacientes simulados")
ax.set_ylabel("Promedio acumulado espera")

st.pyplot(fig)

st.subheader("Análisis económico (si hay 2 médicos)")

cost_wait = wait_time.sum()*25
cost_doctor = 40 if servers==2 else 0

st.write(f"Costo total espera pacientes: ${cost_wait:.2f}")
st.write(f"Costo médico adicional por hora: ${cost_doctor}")
