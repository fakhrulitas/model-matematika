import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from math import sqrt
from scipy.optimize import linprog

st.set_page_config(page_title="Model Matematika Industri", layout="wide")

# Sidebar
st.sidebar.header("📘 Panduan Aplikasi")
st.sidebar.markdown("""
**Studi Kasus Tersedia:**

1. **Optimasi Produksi - PT. Sinar Terang**
2. **Model Persediaan - EOQ**
3. **Model Antrian - M/M/1**
4. **Model Industri - Break Even Point**
""")

tab1, tab2, tab3, tab4 = st.tabs([
    "Optimasi Produksi",
    "Model Persediaan",
    "Model Antrian",
    "Break-Even Point"
])

with tab1:
    st.title("🏭 Studi Kasus 1: Optimasi Produksi – PT. Sinar Terang")
    st.markdown("""
    PT Sinar Terang memproduksi Blender dan Pemanggang Roti.
    Tentukan kombinasi produksi yang memaksimalkan keuntungan tanpa melebihi batas jam mesin.
    """)

    with st.form("opt_form"):
        st.subheader("🔧 Masukkan Parameter Produksi")
        col1, col2 = st.columns(2)
        with col1:
            profit_A = st.number_input("Keuntungan per unit Blender (Rp)", value=70000, step=1000)
            time_A = st.number_input("Jam mesin per unit Blender", value=2.0, step=0.1)
        with col2:
            profit_B = st.number_input("Keuntungan per unit Pemanggang Roti (Rp)", value=80000, step=1000)
            time_B = st.number_input("Jam mesin per unit Pemanggang Roti", value=3.0, step=0.1)

        total_time = st.number_input("Total jam mesin tersedia per minggu", value=100.0)
        submitted = st.form_submit_button("Hitung Solusi Optimal")

    if submitted:
        c = [-profit_A, -profit_B]
        A = [[time_A, time_B]]
        b = [total_time]
        bounds = [(0, None), (0, None)]
        result = linprog(c, A_ub=A, b_ub=b, bounds=bounds, method='highs')

        if result.success:
            x, y = result.x
            max_profit = -result.fun
            st.success("Solusi Optimal Ditemukan")
            st.write(f"Jumlah Blender: {x:.2f} unit")
            st.write(f"Jumlah Pemanggang Roti: {y:.2f} unit")
            st.write(f"Total Keuntungan Maksimal: Rp{max_profit:,.0f}")

            fig, ax = plt.subplots()
            x_vals = np.linspace(0, total_time / time_A + 5, 400)
            y_vals = (total_time - time_A * x_vals) / time_B
            y_vals = np.maximum(0, y_vals)

            ax.plot(x_vals, y_vals, label="Kendala Waktu Mesin", color="blue")
            ax.fill_between(x_vals, 0, y_vals, alpha=0.2, label="Daerah Feasible")
            ax.scatter(x, y, color="red", label="Solusi Optimal")
            ax.set_xlabel("Unit Blender")
            ax.set_ylabel("Unit Pemanggang Roti")
            ax.set_title("Grafik Optimasi Produksi")
            ax.legend()
            st.pyplot(fig)
        else:
            st.error("Gagal menemukan solusi optimal.")

with tab2:
    st.title("📦 Studi Kasus 2: Model Persediaan – EOQ")
    st.markdown("""
    Hitung jumlah pemesanan optimal agar biaya total minimum.
    Model: Economic Order Quantity (EOQ)
    """)

    D = st.number_input("Permintaan Tahunan (liter)", value=10000, step=100)
    S = st.number_input("Biaya Pemesanan per Pesanan (Rp)", value=40000.0, step=1000.0)
    H = st.number_input("Biaya Penyimpanan per Unit per Tahun (Rp)", value=2500.0, step=100.0)

    EOQ = sqrt((2 * D * S) / H)
    TC = (D / EOQ) * S + (EOQ / 2) * H

    q_vals = np.linspace(EOQ * 0.5, EOQ * 1.5, 100)
    tc_vals = (D / q_vals) * S + (q_vals / 2) * H

    fig2, ax2 = plt.subplots()
    ax2.plot(q_vals, tc_vals, label='Total Biaya', color='green')
    ax2.axvline(EOQ, color='red', linestyle='--', label='EOQ')
    ax2.set_xlabel("Jumlah Pemesanan")
    ax2.set_ylabel("Biaya Total (Rp)")
    ax2.set_title("Grafik Biaya Total vs Jumlah Pemesanan")
    ax2.legend()
    st.pyplot(fig2)

    st.metric("EOQ Optimal", f"{EOQ:.2f} liter")
    st.metric("Biaya Total Minimum", f"Rp{TC:,.0f}")

with tab3:
    st.title("👥 Studi Kasus 3: Model Antrian – Layanan Pelanggan")
    st.markdown("""
    Model Antrian M/M/1 untuk menghitung waktu tunggu dan panjang antrian.
    """)

    λ = st.number_input("Laju Kedatangan (λ)", value=8.0, step=0.1)
    μ = st.number_input("Laju Pelayanan (μ)", value=11.0, step=0.1)

    if μ <= λ:
        st.warning("⚠️ Sistem tidak stabil: μ harus lebih besar dari λ")
    else:
        ρ = λ / μ
        L = λ / (μ - λ)
        W = 1 / (μ - λ)
        Wq = λ / (μ * (μ - λ))

        st.metric("Tingkat Utilisasi (ρ)", f"{ρ:.2f}")
        st.metric("Rata-rata Pelanggan dalam Sistem (L)", f"{L:.2f}")
        st.metric("Rata-rata Waktu dalam Sistem (W)", f"{W*60:.2f} menit")
        st.metric("Rata-rata Waktu Tunggu (Wq)", f"{Wq*60:.2f} menit")

with tab4:
    st.title("🏭 Studi Kasus 4: Break-Even Point (BEP)")
    st.markdown("""
    Hitung jumlah minimum produk yang harus dijual agar perusahaan tidak merugi.
    """)

    F = st.number_input("Biaya Tetap (Rp)", value=200_000_000)
    V = st.number_input("Biaya Variabel per Unit (Rp)", value=40000)
    P = st.number_input("Harga Jual per Unit (Rp)", value=60000)

    if P <= V:
        st.error("Harga jual harus lebih besar dari biaya variabel.")
    else:
        BEP = F / (P - V)
        st.metric("Break-Even Point (unit)", f"{BEP:.2f} unit")

        x_vals = np.linspace(0, BEP * 2, 100)
        revenue = P * x_vals
        total_cost = F + V * x_vals

        fig4, ax4 = plt.subplots()
        ax4.plot(x_vals, revenue, label="Pendapatan")
        ax4.plot(x_vals, total_cost, label="Biaya Total")
        ax4.axvline(BEP, color='red', linestyle='--', label='BEP')
        ax4.set_xlabel("Jumlah Unit")
        ax4.set_ylabel("Rupiah (Rp)")
        ax4.legend()
        st.pyplot(fig4)
