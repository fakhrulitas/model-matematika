import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import pulp
from math import sqrt
from scipy.optimize import linprog
import sympy as sp

st.set_page_config(page_title="Industrial Math Models", layout="wide")

# Sidebar Dokumentasi
st.sidebar.header("Panduan Aplikasi")
st.sidebar.markdown("""
**1. Optimasi Produksi**:
- Masukkan koefisien fungsi tujuan dan kendala
- Sistem akan menampilkan solusi optimal

**2. Model Persediaan**:
- Input parameter permintaan dan biaya
- Hitung EOQ dan biaya total optimal

**3. Model Antrian**:
- Simulasikan sistem antrian M/M/1
- Visualisasi panjang antrian dan kinerja sistem

**4. Break-even Point**:
- Analisis titik impas produksi
- Visualisasi pendapatan dan biaya
""")

tab1, tab2, tab3, tab4 = st.tabs([
    "Optimasi Produksi", "Model Persediaan", "Model Antrian", "Break-even Point"
])

with tab1:
    st.title("🏭 Optimasi Produksi - PT. Sinar Terang")
    st.markdown("""
    Aplikasi ini membantu menentukan jumlah produksi optimal untuk dua produk:
    - Produk A: Blender
    - Produk B: Pemanggang Roti

    Tujuannya adalah untuk memaksimalkan keuntungan, dengan batasan waktu mesin yang tersedia per minggu.
    """)

    with st.form("input_form"):
        st.subheader("🔧 Masukkan Parameter Produksi")

        col1, col2 = st.columns(2)

        with col1:
            profit_A = st.number_input("Keuntungan per unit Blender (Rp)", value=70000, step=1000, min_value=0)
            time_A = st.number_input("Jam mesin per unit Blender", value=2.0, step=0.1, min_value=0.1)

        with col2:
            profit_B = st.number_input("Keuntungan per unit Pemanggang Roti (Rp)", value=80000, step=1000, min_value=0)
            time_B = st.number_input("Jam mesin per unit Pemanggang Roti", value=3.0, step=0.1, min_value=0.1)

        total_time = st.number_input("Total jam mesin tersedia per minggu", value=100.0, step=1.0, min_value=1.0)

        submitted = st.form_submit_button("🔍 Hitung Produksi Optimal")

    if submitted:
        c = [-profit_A, -profit_B]
        A = [[time_A, time_B]]
        b = [total_time]
        bounds = [(0, None), (0, None)]

        result = linprog(c, A_ub=A, b_ub=b, bounds=bounds, method='highs')

        st.subheader("📊 Hasil Optimasi")

        if result.success:
            x = result.x[0]
            y = result.x[1]
            max_profit = -result.fun

            st.success("Solusi optimal ditemukan ✅")
            st.write(f"🔹 Jumlah Blender (Produk A): **{x:.2f} unit**")
            st.write(f"🔹 Jumlah Pemanggang Roti (Produk B): **{y:.2f} unit**")
            st.write(f"💰 Total keuntungan maksimal: Rp {max_profit:,.0f}")

            fig, ax = plt.subplots(figsize=(7, 5))
            x_vals = np.linspace(0, total_time / time_A + 5, 400)
            y_vals = (total_time - time_A * x_vals) / time_B
            y_vals = np.maximum(0, y_vals)

            ax.plot(x_vals, y_vals, label="Batas Waktu Mesin", color="blue")
            ax.fill_between(x_vals, 0, y_vals, alpha=0.2, color="blue", label="Daerah Feasible")
            ax.scatter(x, y, color="red", zorder=5, label="Solusi Optimal")
            ax.set_xlim(left=0)
            ax.set_ylim(bottom=0)
            ax.set_xlabel("Unit Blender (Produk A)")
            ax.set_ylabel("Unit Pemanggang Roti (Produk B)")
            ax.set_title("Visualisasi Optimasi Produksi")
            ax.legend()
            ax.grid(True)
            st.pyplot(fig)
        else:
            st.error("❌ Gagal menemukan solusi optimal.")

with tab2:
    st.header("📦 Kalkulator EOQ")
    st.write("""
    Aplikasi ini menghitung Economic Order Quantity (EOQ) dan visualisasi biaya total
    menggunakan rumus:
    **EOQ** = √(2DS/H)  
    **Total Cost** = (D/Q)S + (Q/2)H
    """)

    col1, col2, col3 = st.columns(3)
    with col1:
        D = st.number_input("Permintaan Tahunan (unit)", value=10000, step=100, format="%d")
    with col2:
        S = st.number_input("Biaya Pemesanan (Rp./pesan)", value=40000.0, step=1000.0, format="%.2f")
    with col3:
        H = st.number_input("Biaya Penyimpanan (Rp./unit/tahun)", value=2500.0, step=100.0, format="%.2f")

    Q = sqrt((2*D*S)/H)
    TC = (D/Q)*S + (Q/2)*H

    q_values = np.linspace(Q*0.5, Q*1.5, 100)
    tc_values = (D/q_values)*S + (q_values/2)*H

    fig, ax = plt.subplots(figsize=(8,5))
    ax.plot(q_values, tc_values, label='Total Biaya', color='green', linewidth=2)
    ax.axvline(Q, color='red', linestyle='--', linewidth=2, label='EOQ')
    ax.set_xlabel("Jumlah Pesanan")
    ax.set_ylabel("Biaya Total (Rp.)")
    ax.set_title("Grafik Total Biaya terhadap Jumlah Pesanan")
    ax.legend()
    ax.grid(True)
    st.pyplot(fig)

    st.subheader("📊 Hasil Perhitungan")
    result_col1, result_col2 = st.columns(2)
    with result_col1:
        st.metric(label="EOQ Optimal", value=f"{Q:.2f} unit")
    with result_col2:
        st.metric(label="Biaya Total Minimum", value=f"Rp.{TC:,.2f}")

with tab3:
    st.header("📈 Studi Kasus Antrian – Layanan Pelanggan")

    st.markdown("""
    Model ini mengevaluasi sistem antrian satu loket di kantor layanan pelanggan.
    Distribusi kedatangan diasumsikan Poisson, dan waktu pelayanan mengikuti eksponensial (Model M/M/1).
    """)

    col1, col2 = st.columns(2)
    with col1:
        lambda_ = st.number_input("Tingkat Kedatangan (λ pelanggan/jam)", value=8.0, step=0.1)
    with col2:
        mu = st.number_input("Tingkat Pelayanan (μ pelanggan/jam)", value=11.0, step=0.1)

    rho = lambda_ / mu
    L = lambda_ / (mu - lambda_) if mu > lambda_ else float('inf')
    W = 1 / (mu - lambda_) if mu > lambda_ else float('inf')
    Wq = lambda_ / (mu * (mu - lambda_)) if mu > lambda_ else float('inf')

    st.subheader("📊 Hasil Perhitungan")
    st.write(f"**Tingkat Utilisasi (ρ)**: {rho:.2f}")
    st.write(f"**Rata-rata Pelanggan dalam Sistem (L)**: {L:.2f}")
    st.write(f"**Waktu Rata-rata di Sistem (W)**: {W:.2f} jam")
    st.write(f"**Waktu Rata-rata Tunggu (Wq)**: {Wq:.2f} jam")

    st.subheader("📉 Visualisasi Panjang Antrian (Simulasi 100 Pelanggan)")
    np.random.seed(42)
    num_customers = 100
    inter_arrivals = np.random.exponential(1/lambda_, num_customers)
    service_times = np.random.exponential(1/mu, num_customers)

    arrival_times = np.cumsum(inter_arrivals)
    start_times = np.zeros(num_customers)
    end_times = np.zeros(num_customers)

    for i in range(num_customers):
        if i == 0:
            start_times[i] = arrival_times[i]
        else:
            start_times[i] = max(arrival_times[i], end_times[i-1])
        end_times[i] = start_times[i] + service_times[i]

    queue_lengths = [np.sum((arrival_times <= t) & (end_times > t)) for t in arrival_times]

    fig, ax = plt.subplots(figsize=(10,4))
    ax.step(arrival_times, queue_lengths, where='post', color='darkorange')
    ax.set_xlabel("Waktu (jam)")
    ax.set_ylabel("Jumlah Pelanggan di Sistem")
    ax.set_title("Simulasi Panjang Antrian dari Waktu ke Waktu")
    ax.grid(True)
    st.pyplot(fig)

with tab4:
    st.header("📉 Break-even Point Analysis")

    fixed_cost = st.number_input("Biaya Tetap (Rp)", value=200_000_000)
    variable_cost = st.number_input("Biaya Variabel per Unit (Rp)", value=40000)
    price = st.number_input("Harga Jual per Unit (Rp)", value=60000)

    break_even = fixed_cost / (price - variable_cost) if price > variable_cost else float('inf')

    x = np.linspace(0, break_even * 2, 100)
    revenue = price * x
    total_cost = fixed_cost + variable_cost * x

    fig, ax = plt.subplots()
    ax.plot(x, revenue, label='Pendapatan')
    ax.plot(x, total_cost, label='Biaya Total')
    ax.axvline(break_even, color='r', linestyle='--', label='Break-even')
    ax.set_xlabel("Jumlah Unit")
    ax.set_ylabel("Rupiah (Rp)")
    ax.legend()
    ax.grid(True)

    st.subheader("📊 Hasil Analisis")
    st.write(f"Break-even Point: {break_even:.2f} unit")
    st.pyplot(fig)

if __name__ == "__main__":
    st.write("Aplikasi Model Matematika Industri Siap Digunakan ✅")
