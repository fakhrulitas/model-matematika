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

Masukkan parameter sesuai studi kasus, lalu tekan tombol *Hitung*. Hasil dan grafik akan ditampilkan.
""")

menu = st.tabs(["Optimasi Produksi", "Model Persediaan", "Model Antrian", "Model BEP"])

# 1. Optimasi Produksi
with menu[0]:
    st.header("🔧 Optimasi Produksi - Linear Programming")
    st.markdown("""
**Studi Kasus:** PT. Sinar Terang memproduksi blender (A) dan pemanggang roti (B). Kapasitas mesin 100 jam/minggu.
- Keuntungan per blender: Rp40.000  
- Keuntungan per pemanggang roti: Rp60.000  
- Waktu mesin: A = 2 jam, B = 3 jam
    """)
    
    if st.button("Hitung Optimasi Produksi"):
        c = [-40, -60]
        A = [[2, 3]]
        b = [100]
        x_bounds = (0, None)
        y_bounds = (0, None)

        res = linprog(c, A_ub=A, b_ub=b, bounds=[x_bounds, y_bounds])
        if res.success:
            a, b = res.x
            profit = -res.fun * 1000
            st.success(f"Blender: {a:.0f} unit, Pemanggang: {b:.0f} unit")
            st.info(f"Keuntungan Maksimum: Rp{profit:,.0f}")

            fig, ax = plt.subplots()
            ax.bar(["Blender", "Pemanggang"], [a, b], color=['green', 'orange'])
            ax.set_ylabel("Jumlah Produksi")
            st.pyplot(fig)
            
            st.caption("Interpretasi: Produksi tunggal pada salah satu jenis dapat menghasilkan keuntungan maksimum.")
        else:
            st.error("Solusi tidak ditemukan.")

# 2. EOQ Model
with menu[1]:
    st.header("📦 Model Persediaan - EOQ")
    st.markdown("""
**Studi Kasus:** Bengkel memerlukan 10.000 liter oli/tahun.
- Biaya pemesanan: Rp50.000  
- Biaya penyimpanan: Rp2.000/liter/tahun
    """)
    
    D = 10000
    S = 50000
    H = 2000

    eoq = np.sqrt((2 * D * S) / H)
    st.success(f"EOQ: {eoq:.2f} liter per pesanan")

    Q = np.linspace(100, 2 * eoq, 100)
    TC = D / Q * S + Q / 2 * H

    fig, ax = plt.subplots()
    ax.plot(Q, TC, label="Total Cost")
    ax.axvline(eoq, color='r', linestyle='--', label="EOQ")
    ax.set_xlabel("Jumlah Pesanan")
    ax.set_ylabel("Total Biaya")
    ax.legend()
    st.pyplot(fig)

    st.caption("Interpretasi: Pemesanan 707 liter setiap kali akan meminimalkan biaya total.")

# 3. Antrian M/M/1
with menu[2]:
    st.header("⏳ Model Antrian - M/M/1")
    st.markdown("""
**Studi Kasus:** Loket pelayanan menerima 10 pelanggan/jam dan dapat melayani 12 pelanggan/jam.
Distribusi kedatangan: Poisson, pelayanan: Eksponensial.
    """)

    lambd = 10
    mu = 12

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

        st.caption("Interpretasi: Antrean rata-rata 5 pelanggan, waktu tunggu sekitar 25 menit.")

# 4. BEP Model
with menu[3]:
    st.header("📈 Break Even Point (BEP)")
    st.markdown("""
**Studi Kasus:**
- Biaya tetap: Rp1.000.000  
- Biaya variabel: Rp10.000/unit  
- Harga jual: Rp20.000/unit
    """)

    FC = 1_000_000
    VC = 10_000
    P = 20_000

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
