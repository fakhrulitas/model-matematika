# app.py
import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import linprog

# Sidebar
st.sidebar.title("📘 Dokumentasi Aplikasi")
st.sidebar.markdown("""
Aplikasi ini memiliki 4 menu utama:

1. **Optimasi Produksi (Linear Programming)**: Menyelesaikan masalah optimasi produksi dengan metode Simpleks.
2. **Model Persediaan (EOQ)**: Menghitung Economic Order Quantity.
3. **Model Antrian (M/M/1)**: Analisis sistem antrian dengan distribusi eksponensial.
4. **Model Industri Lain**: Contoh: Break-Even Analysis (Analisis Titik Impas).
""")

# Tab
tab1, tab2, tab3, tab4 = st.tabs(["Optimasi Produksi", "Model Persediaan (EOQ)", "Model Antrian (M/M/1)", "Model Industri Lain"])

with tab1:
    st.header("Optimasi Produksi - Linear Programming")
    st.markdown("Masukkan data untuk memaksimalkan fungsi keuntungan.")
    
    profit = st.text_input("Koefisien Fungsi Objektif (pisahkan dengan koma, contoh: 40,30)", "40,30")
    constraint1 = st.text_input("Kendala 1 (contoh: 1,1,<=40)", "1,1,<=40")
    constraint2 = st.text_input("Kendala 2 (contoh: 2,1,<=60)", "2,1,<=60")

    if st.button("Hitung Optimasi"):
        c = -np.array([float(i) for i in profit.split(",")])
        A = []
        b = []

        for cons in [constraint1, constraint2]:
            parts = cons.split(',')
            A.append([float(parts[0]), float(parts[1])])
            b.append(float(parts[3]))

        res = linprog(c, A_ub=A, b_ub=b)

        if res.success:
            st.success(f"Hasil Optimal: {res.x}, Total Keuntungan: {-res.fun}")
            st.bar_chart(res.x)
        else:
            st.error("Optimasi gagal. Periksa input.")

with tab2:
    st.header("Model Persediaan - EOQ")
    D = st.number_input("Permintaan per tahun (D)", value=1000)
    S = st.number_input("Biaya Pemesanan (S)", value=50)
    H = st.number_input("Biaya Penyimpanan per unit (H)", value=2)

    if st.button("Hitung EOQ"):
        eoq = np.sqrt((2 * D * S) / H)
        st.success(f"EOQ: {eoq:.2f} unit")

        fig, ax = plt.subplots()
        Q = np.linspace(1, 2*eoq, 100)
        TC = D/Q*S + Q/2*H
        ax.plot(Q, TC, label="Total Cost")
        ax.axvline(eoq, color='r', linestyle='--', label=f'EOQ = {eoq:.2f}')
        ax.set_xlabel('Order Quantity (Q)')
        ax.set_ylabel('Total Cost')
        ax.legend()
        st.pyplot(fig)

with tab3:
    st.header("Model Antrian - M/M/1")
    lam = st.number_input("Laju kedatangan (λ)", value=5.0)
    mu = st.number_input("Laju pelayanan (μ)", value=8.0)

    if st.button("Hitung Model Antrian"):
        if lam >= mu:
            st.error("Sistem tidak stabil (λ >= μ)")
        else:
            rho = lam / mu
            Lq = rho**2 / (1 - rho)
            Wq = Lq / lam
            L = lam / (mu - lam)
            W = 1 / (mu - lam)
            st.write(f"Utilisasi: {rho:.2f}")
            st.write(f"Rata-rata pelanggan dalam antrian (Lq): {Lq:.2f}")
            st.write(f"Rata-rata waktu dalam antrian (Wq): {Wq:.2f}")
            st.write(f"Rata-rata pelanggan dalam sistem (L): {L:.2f}")
            st.write(f"Rata-rata waktu dalam sistem (W): {W:.2f}")

            labels = ['Dalam Antrian', 'Dalam Sistem']
            values = [Lq, L]
            fig, ax = plt.subplots()
            ax.bar(labels, values, color=['orange', 'green'])
            st.pyplot(fig)

with tab4:
    st.header("Model Industri Lain - Break Even Point")
    FC = st.number_input("Fixed Cost (FC)", value=10000)
    VC = st.number_input("Variable Cost per Unit (VC)", value=10)
    P = st.number_input("Harga Jual per Unit (P)", value=20)

    if st.button("Hitung Break Even"):
        if P <= VC:
            st.error("Harga jual harus lebih besar dari biaya variabel.")
        else:
            BEP = FC / (P - VC)
            st.success(f"Break-Even Point: {BEP:.2f} unit")
            x = np.linspace(0, BEP*2, 100)
            total_cost = FC + VC * x
            total_revenue = P * x

            fig, ax = plt.subplots()
            ax.plot(x, total_cost, label="Total Cost")
            ax.plot(x, total_revenue, label="Total Revenue")
            ax.axvline(BEP, color='r', linestyle='--', label=f'BEP = {BEP:.2f}')
            ax.legend()
            st.pyplot(fig)
