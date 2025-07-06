import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import pulp
from math import sqrt
from scipy.optimize import linprog
import sympy as sp

st.set_page_config(page_title="Model Matematika Industri", layout="wide")

# Sidebar Dokumentasi
st.sidebar.header("📘 Panduan Penggunaan")
st.sidebar.markdown("""
**1. Optimasi Produksi - PT. Sinar Terang**:
- Input jam mesin & keuntungan
- Sistem akan menghitung kombinasi produk optimal

**2. Model Persediaan (EOQ)**:
- Masukkan permintaan tahunan, biaya simpan & pesan
- Hitung EOQ untuk biaya minimum

**3. Model Antrian Layanan**:
- Input laju kedatangan dan pelayanan
- Simulasi sistem antrian M/M/1 dan analisis performa

**4. Model Industri Lain - Titik Impas**:
- Hitung Break-even Point
- Visualisasi Pendapatan & Biaya
""")

tab1, tab2, tab3, tab4 = st.tabs(["Optimasi Produksi", "Model Persediaan", "Model Antrian", "Break-even Point"])

# ----------------------------- TAB 1: OPTIMASI PRODUKSI -----------------------------
with tab1:
    st.title("🏭 Optimasi Produksi – PT. Sinar Terang")
    st.markdown("""
    Hitung jumlah optimal produksi untuk:
    - Blender
    - Pemanggang Roti

    Berdasarkan batas jam mesin dan keuntungan tiap unit.
    """)

    with st.form("form1"):
        st.subheader("🔧 Parameter Produksi")
        col1, col2 = st.columns(2)

        with col1:
            profit_A = st.number_input("Keuntungan per unit Blender (Rp)", value=70000)
            time_A = st.number_input("Jam mesin per unit Blender", value=2.0)

        with col2:
            profit_B = st.number_input("Keuntungan per unit Pemanggang Roti (Rp)", value=80000)
            time_B = st.number_input("Jam mesin per unit Pemanggang Roti", value=3.0)

        total_time = st.number_input("Total jam mesin per minggu", value=100.0)
        submitted = st.form_submit_button("🔍 Hitung")

    if submitted:
        c = [-profit_A, -profit_B]
        A = [[time_A, time_B]]
        b = [total_time]
        bounds = [(0, None), (0, None)]

        result = linprog(c, A_ub=A, b_ub=b, bounds=bounds, method='highs')

        st.subheader("📊 Hasil Optimasi")
        if result.success:
            x, y = result.x
            z = -result.fun
            st.success("✅ Solusi Optimal Ditemukan")
            st.write(f"🔹 Blender: **{x:.2f} unit**")
            st.write(f"🔹 Pemanggang Roti: **{y:.2f} unit**")
            st.write(f"💰 Total Keuntungan Maksimal: Rp {z:,.0f}")

            # Visualisasi
            fig, ax = plt.subplots()
            x_vals = np.linspace(0, total_time/time_A, 400)
            y_vals = (total_time - time_A * x_vals) / time_B
            ax.plot(x_vals, y_vals, label='Kendala Waktu Mesin', color='blue')
            ax.fill_between(x_vals, 0, y_vals, alpha=0.2, label='Daerah Feasible')
            ax.scatter(x, y, color='red', label='Solusi Optimal')
            ax.set_xlabel("Unit Blender")
            ax.set_ylabel("Unit Pemanggang Roti")
            ax.set_title("Visualisasi Optimasi Produksi")
            ax.grid(True)
            ax.legend()
            st.pyplot(fig)
        else:
            st.error("❌ Gagal menemukan solusi optimal")

# ----------------------------- TAB 2: EOQ -----------------------------
with tab2:
    st.header("📦 EOQ - Economic Order Quantity")
    st.markdown("""
    Hitung kuantitas pemesanan optimal (EOQ) agar biaya persediaan minimum.
    Rumus EOQ:
    $$ EOQ = \sqrt{\frac{2DS}{H}} $$
    """)

    col1, col2, col3 = st.columns(3)
    with col1:
        D = st.number_input("Permintaan Tahunan (liter)", value=10000)
    with col2:
        S = st.number_input("Biaya Pemesanan per Pesanan (Rp)", value=60000.0)
    with col3:
        H = st.number_input("Biaya Simpan per Liter/Tahun (Rp)", value=2500.0)

    Q = sqrt((2 * D * S) / H)
    TC = (D / Q) * S + (Q / 2) * H

    st.subheader("📊 Hasil EOQ")
    st.metric("EOQ Optimal", f"{Q:.2f} liter")
    st.metric("Biaya Total Minimum", f"Rp {TC:,.0f}")

# ----------------------------- TAB 3: ANTRIAN -----------------------------
with tab3:
    st.header("🧍‍♂️ Model Antrian M/M/1")
    st.markdown("""
    Simulasi sistem antrian 1 server. 
    Asumsi: Distribusi Poisson (λ) dan Eksponensial (μ)
    """)

    lambda_ = st.number_input("Laju Kedatangan (λ)", value=8.0)
    mu = st.number_input("Laju Pelayanan (μ)", value=11.0)

    rho = lambda_ / mu
    L = lambda_ / (mu - lambda_) if mu > lambda_ else np.inf
    W = 1 / (mu - lambda_) if mu > lambda_ else np.inf
    Wq = lambda_ / (mu * (mu - lambda_)) if mu > lambda_ else np.inf

    st.subheader("📈 Statistik Antrian")
    st.write(f"Utilisasi Sistem (ρ): {rho:.2f}")
    st.write(f"Jumlah Rata-rata Pelanggan di Sistem (L): {L:.2f}")
    st.write(f"Waktu Rata-rata dalam Sistem (W): {W:.2f} jam")
    st.write(f"Waktu Rata-rata dalam Antrian (Wq): {Wq:.2f} jam")

# ----------------------------- TAB 4: BREAK EVEN -----------------------------
with tab4:
    st.header("📉 Analisis Titik Impas (Break-even Point)")

    fixed_cost = st.number_input("Biaya Tetap (Rp)", value=20000000)
    variable_cost = st.number_input("Biaya Variabel per Unit (Rp)", value=250000)
    price = st.number_input("Harga Jual per Unit (Rp)", value=400000)

    if price > variable_cost:
        break_even = fixed_cost / (price - variable_cost)

        x_vals = np.linspace(0, break_even * 2, 200)
        revenue = x_vals * price
        cost = fixed_cost + x_vals * variable_cost

        fig, ax = plt.subplots()
        ax.plot(x_vals, revenue, label='Pendapatan')
        ax.plot(x_vals, cost, label='Biaya Total')
        ax.axvline(break_even, color='red', linestyle='--', label='Break-even')
        ax.set_xlabel("Jumlah Unit")
        ax.set_ylabel("Rupiah (Rp)")
        ax.set_title("Grafik Titik Impas")
        ax.grid(True)
        ax.legend()
        st.pyplot(fig)

        st.subheader("📊 Hasil Perhitungan")
        st.metric("Titik Impas (Unit)", f"{break_even:.2f}")
    else:
        st.warning("Harga jual harus lebih besar dari biaya variabel!")
