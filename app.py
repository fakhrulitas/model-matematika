# app.py
import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import linprog

st.set_page_config(page_title="Model Matematika Industri", layout="wide")

# Sidebar instructions
st.sidebar.title("📘 Petunjuk Penggunaan")
st.sidebar.markdown("""
Aplikasi ini memiliki 4 model matematika industri:
1. **Optimasi Produksi (LP)**
2. **Model Persediaan (EOQ)**
3. **Model Antrian (M/M/1)**
4. **Break Even Point (BEP)**

Secara default, aplikasi menampilkan parameter dari studi kasus. Namun, Anda dapat mengubah parameter sesuai kebutuhan.
""")

menu = st.tabs(["Optimasi Produksi", "Model Persediaan", "Model Antrian", "Model BEP"])

# 1. Optimasi Produksi
with menu[0]:
    st.header("🔧 Optimasi Produksi - Linear Programming")

    c1 = st.number_input("Keuntungan per unit Produk A (x)", value=40.0)
    c2 = st.number_input("Keuntungan per unit Produk B (y)", value=60.0)
    a1 = st.number_input("Jam mesin untuk Produk A (x)", value=2.0)
    a2 = st.number_input("Jam mesin untuk Produk B (y)", value=3.0)
    kapasitas = st.number_input("Total kapasitas jam mesin", value=100.0)

    st.markdown(f"""
**Model Matematis:**  
Maksimalkan Z = {c1:.0f}x + {c2:.0f}y  
Kendala: {a1:.0f}x + {a2:.0f}y ≤ {kapasitas:.0f}, x ≥ 0, y ≥ 0
    """)

    if st.button("Hitung Optimasi Produksi"):
        c = [-c1, -c2]
        A = [[a1, a2]]
        b = [kapasitas]
        bounds = [(0, None), (0, None)]

        res = linprog(c, A_ub=A, b_ub=b, bounds=bounds)
        if res.success:
            a, b_ = res.x
            profit = -res.fun * 1000
            st.success(f"Produk A: {a:.0f} unit, Produk B: {b_:.0f} unit")
            st.info(f"Keuntungan Maksimum: Rp{profit:,.0f}")

            fig, ax = plt.subplots()
            ax.bar(["Produk A", "Produk B"], [a, b_], color=['green', 'orange'])
            ax.set_ylabel("Jumlah Produksi")
            st.pyplot(fig)
            
            st.caption("Interpretasi: Solusi optimal untuk memaksimalkan keuntungan sesuai batasan produksi.")
        else:
            st.error("Solusi tidak ditemukan.")

# 2. EOQ Model
with menu[1]:
    st.header("📦 Model Persediaan - EOQ")

    D = st.number_input("Permintaan Tahunan (D)", value=10000.0)
    S = st.number_input("Biaya Pemesanan per Pesanan (S)", value=50000.0)
    H = st.number_input("Biaya Penyimpanan per unit per tahun (H)", value=2000.0)

    st.markdown(f"""
**Rumus EOQ:**  
\[
EOQ = \sqrt{{\frac{{2 \times {D:.0f} \times {S:.0f}}}{{{H:.0f}}}}} = \sqrt{{\frac{{{2*D*S:.0f}}}{{{H:.0f}}}}}
\]
    """, unsafe_allow_html=True)

    if st.button("Hitung EOQ"):
        eoq = np.sqrt((2 * D * S) / H)
        st.success(f"EOQ: {eoq:.2f} unit per pesanan")

        Q = np.linspace(100, 2 * eoq, 100)
        TC = D / Q * S + Q / 2 * H

        fig, ax = plt.subplots()
        ax.plot(Q, TC, label="Total Cost")
        ax.axvline(eoq, color='r', linestyle='--', label="EOQ")
        ax.set_xlabel("Jumlah Pesanan")
        ax.set_ylabel("Total Biaya")
        ax.legend()
        st.pyplot(fig)

        st.caption("Interpretasi: EOQ adalah jumlah optimal pemesanan agar biaya total minimum.")

# 3. Antrian M/M/1
with menu[2]:
    st.header("⏳ Model Antrian - M/M/1")

    lambd = st.number_input("Laju Kedatangan (λ)", value=10.0)
    mu = st.number_input("Laju Pelayanan (μ)", value=12.0)

    st.markdown(f"""
**Model Matematis:**
\[
L = \frac{{{lambd}}}{{{mu} - {lambd}}}, \quad L_q = \frac{{{lambd}^2}}{{{mu}({mu} - {lambd})}} \\
W = \frac{{1}}{{{mu} - {lambd}}}, \quad W_q = \frac{{{lambd}}}{{{mu}({mu} - {lambd})}}
\]
    """, unsafe_allow_html=True)

    if lambd >= mu:
        st.error("Sistem tidak stabil (λ ≥ μ). Harus λ < μ.")
    else:
        L = lambd / (mu - lambd)
        Lq = lambd**2 / (mu * (mu - lambd))
        W = 1 / (mu - lambd)
        Wq = lambd / (mu * (mu - lambd))

        st.write(f"Utilisasi: {lambd / mu:.2%}")
        st.write(f"Rata-rata pelanggan dalam sistem (L): {L:.2f}")
        st.write(f"Waktu dalam sistem (W): {W:.2f} jam atau {W*60:.0f} menit")
        st.write(f"Waktu tunggu antrean (Wq): {Wq:.2f} jam atau {Wq*60:.0f} menit")

        fig, ax = plt.subplots()
        ax.bar(["Dalam Sistem", "Dalam Antrean"], [L, Lq], color=['blue', 'orange'])
        ax.set_ylabel("Rata-rata Pelanggan")
        st.pyplot(fig)

        st.caption("Interpretasi: Rata-rata pelanggan dan waktu tunggu dihitung dari parameter λ dan μ.")

# 4. BEP Model
with menu[3]:
    st.header("📈 Break Even Point (BEP)")

    FC = st.number_input("Biaya Tetap (Fixed Cost)", value=1_000_000.0)
    VC = st.number_input("Biaya Variabel per unit", value=10_000.0)
    P = st.number_input("Harga Jual per unit", value=20_000.0)

    st.markdown(f"""
**Rumus BEP:**  
\[
\text{{BEP}} = \frac{{{FC:.0f}}}{{{P:.0f} - {VC:.0f}}} = \frac{{\text{{FC}}}}{{P - VC}}
\]  
    """, unsafe_allow_html=True)

    if P <= VC:
        st.error("Harga jual harus lebih besar dari biaya variabel.")
    else:
        bep = FC / (P - VC)
        st.success(f"BEP: {bep:.0f} unit untuk balik modal")

        Q = np.linspace(0, 2 * bep, 100)
        TR = P * Q
        TC = FC + VC * Q

        fig, ax = plt.subplots()
        ax.plot(Q, TR, label="Total Revenue")
        ax.plot(Q, TC, label="Total Cost")
        ax.axvline(bep, color='red', linestyle='--', label="BEP")
        ax.set_xlabel("Jumlah Unit")
        ax.set_ylabel("Rupiah")
        ax.legend()
        st.pyplot(fig)

        st.caption(f"Interpretasi: Minimal produksi dan penjualan {bep:.0f} unit untuk menutup semua biaya.")
