# app.py
import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import linprog

# Sidebar instructions
st.sidebar.title("📘 Petunjuk Penggunaan")
st.sidebar.markdown("""
Pilih salah satu model di tab berikut:
1. **Optimasi Produksi (Linear Programming)**
2. **Model Persediaan (EOQ)**
3. **Model Antrian (M/M/1)**
4. **Model Break Even Point (BEP)**

Masukkan parameter yang dibutuhkan, hasil dan grafik akan ditampilkan.
""")

# Tab menu utama
menu = st.tabs(["Optimasi Produksi", "Model Persediaan", "Model Antrian", "Model BEP"])

# 1. Optimasi Produksi (Linear Programming)
with menu[0]:
    st.header("🔧 Optimasi Produksi - Linear Programming")
    st.markdown("Gunakan metode LP untuk memaksimalkan profit atau meminimalkan biaya.")

    c1 = st.number_input("Profit per unit Produk A", value=20.0)
    c2 = st.number_input("Profit per unit Produk B", value=30.0)
    a11 = st.number_input("Waktu kerja per unit A (jam)", value=2.0)
    a12 = st.number_input("Waktu kerja per unit B (jam)", value=1.0)
    b1 = st.number_input("Total jam kerja tersedia", value=100.0)

    if st.button("Hitung Optimasi"):
        res = linprog(c=[-c1, -c2], A_ub=[[a11, a12]], b_ub=[b1], bounds=[(0, None), (0, None)])
        if res.success:
            st.success("Solusi ditemukan!")
            st.write(f"Produksi A: {res.x[0]:.2f} unit")
            st.write(f"Produksi B: {res.x[1]:.2f} unit")
            st.write(f"Total Profit: {-res.fun:.2f}")

            fig, ax = plt.subplots()
            ax.bar(["Produk A", "Produk B"], res.x)
            ax.set_ylabel("Jumlah Produksi")
            st.pyplot(fig)
        else:
            st.error("Gagal menemukan solusi.")

# 2. Model Persediaan EOQ
with menu[1]:
    st.header("📦 Model Persediaan - EOQ")
    D = st.number_input("Permintaan Tahunan (D)", value=1000.0)
    S = st.number_input("Biaya Pemesanan (S)", value=50.0)
    H = st.number_input("Biaya Penyimpanan per unit (H)", value=2.0)

    if st.button("Hitung EOQ"):
        eoq = np.sqrt((2 * D * S) / H)
        st.success(f"EOQ: {eoq:.2f} unit")

        Q = np.linspace(1, 2 * eoq, 100)
        TC = D/Q * S + Q/2 * H

        fig, ax = plt.subplots()
        ax.plot(Q, TC, label="Total Cost")
        ax.axvline(eoq, color='r', linestyle='--', label="EOQ")
        ax.set_xlabel("Order Quantity")
        ax.set_ylabel("Total Cost")
        ax.legend()
        st.pyplot(fig)

# 3. Model Antrian M/M/1
with menu[2]:
    st.header("⏳ Model Antrian - M/M/1")
    lambd = st.number_input("Laju Kedatangan (λ)", value=2.0)
    mu = st.number_input("Laju Pelayanan (μ)", value=3.0)

    if lambd >= mu:
        st.error("Sistem tidak stabil. Pastikan λ < μ")
    else:
        L = lambd / (mu - lambd)
        Lq = lambd**2 / (mu * (mu - lambd))
        W = 1 / (mu - lambd)
        Wq = lambd / (mu * (mu - lambd))

        st.write(f"Rata-rata jumlah dalam sistem (L): {L:.2f}")
        st.write(f"Rata-rata waktu dalam sistem (W): {W:.2f} jam")
        st.write(f"Rata-rata jumlah dalam antrian (Lq): {Lq:.2f}")
        st.write(f"Rata-rata waktu tunggu (Wq): {Wq:.2f} jam")

        fig, ax = plt.subplots()
        ax.bar(["L", "Lq"], [L, Lq], color=['blue', 'orange'])
        ax.set_ylabel("Jumlah rata-rata")
        st.pyplot(fig)

# 4. Model Matematika Tambahan: Break Even Point
with menu[3]:
    st.header("📈 Model Break Even Point (BEP)")
    fc = st.number_input("Biaya Tetap (Fixed Cost)", value=1000.0)
    vc = st.number_input("Biaya Variabel per Unit", value=10.0)
    p = st.number_input("Harga Jual per Unit", value=20.0)

    if p <= vc:
        st.error("Harga jual harus lebih besar dari biaya variabel.")
    else:
        bep = fc / (p - vc)
        st.success(f"Break Even Point: {bep:.2f} unit")

        Q = np.linspace(0, 2 * bep, 100)
        TR = p * Q
        TC = fc + vc * Q

        fig, ax = plt.subplots()
        ax.plot(Q, TR, label="Total Revenue")
        ax.plot(Q, TC, label="Total Cost")
        ax.axvline(bep, color='red', linestyle='--', label="BEP")
        ax.set_xlabel("Jumlah Produksi")
        ax.set_ylabel("Biaya / Pendapatan")
        ax.legend()
        st.pyplot(fig)
