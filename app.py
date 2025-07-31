import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import pulp
from math import sqrt
from scipy.optimize import linprog
import sympy as sp
import pandas as pd
import json
import base64

st.set_page_config(page_title="Model Matematika", layout="centered")

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
- Simulasikan sistem antrian dan tampilkan metrik serta grafik ringkas

**4. Break-even Point**:
- Analisis titik impas produksi
- Visualisasi pendapatan dan biaya
""")

tab1, tab2, tab3, tab4 = st.tabs([
    "Optimasi Produksi", "Model Persediaan", "Model Antrian", "Break-even Point"
])

with tab1:
    st.title("🏭 OPTIMASI PRODUKSI - PT SINAR TERANG MANDIRI")
    
    # Custom CSS styling
    st.markdown("""
    <style>
        body {
            font-family: 'Segoe UI', sans-serif;
        }
        .main {
            background-color: #fffdf7;
        }
        h1 {
            color: #d2691e;
            text-align: center;
            font-size: 40px;
            margin-bottom: 20px;
        }
        .stButton > button {
            background-color: #ffb347;
            color: white;
            font-weight: bold;
        }
        .stDownloadButton > button {
            background-color: #20c997;
            color: white;
            font-weight: bold;
        }
        .logo {
            display: block;
            margin-left: auto;
            margin-right: auto;
            width: 300px;
            margin-bottom: 1rem;
        }
    </style>
    """, unsafe_allow_html=True)
    
    # Tambahkan logo
    st.markdown("<img src='https://mihzzrbqlgf1.cdn.shift8web.ca/wp-content/uploads/2021/01/Sinar-Terang-Logo.jpg' class='logo'>", unsafe_allow_html=True)
    
    st.markdown("""
    <p style='font-size: 18px;'>
    Aplikasi ini membantu PT. Sinar Terang Mandiri menentukan jumlah produksi optimal untuk dua produk:<br>
    - Produk A: Blender<br>
    - Produk B: Pemanggang Roti<br><br>
    Tujuannya adalah untuk memaksimalkan keuntungan, dengan batasan waktu mesin yang tersedia per minggu.
    </p>
    """, unsafe_allow_html=True)
    
    # INPUT
    st.header("📥 Input Data Produksi")
    
    col1, col2 = st.columns(2)
    with col1:
        profit_X = st.number_input("Keuntungan Per unit Blender (Rp)", value=7000)
        labor_X = st.number_input("Jam kerja Blender", value=2)
    
    with col2:
        profit_Y = st.number_input("Keuntungan Per unit Pemanggang Roti (Rp)", value=8000)
        labor_Y = st.number_input("Jam kerja Pemanggang Roti", value=3)
        
    # batasan
    st.subheader("⛔ Batasan Waktu Mesin Per Minggu")
    total_labor = st.slider("Total Jam Mesin Per Minggu (jam)", min_value=1, max_value=100, value=100, step=1)
    
    # Tampilkan Fungsi Objektif
    st.subheader("📈 Fungsi Objektif")
    
    st.latex(r'''
    \text Z = {%.0f}x + {%.0f}y
    ''' % (profit_X, profit_Y))
    
    st.markdown("""
    di mana:
    - \\(x\\) = jumlah Blender
    - \\(y\\) = jumlah Pemanggang Roti
    """)
    
    # Fungsi untuk download data sebagai JSON
    def download_json(data, filename="hasil.json"):
        json_str = json.dumps(data, indent=4)
        b64 = base64.b64encode(json_str.encode()).decode()
        href = f'<a href="data:file/json;base64,{b64}" download="{filename}">📥 Download Hasil sebagai JSON</a>'
        return href
    
    # Solve using linprog
    c = [-profit_X, -profit_Y]  # Max profit -> Minimize negative
    A = [[labor_X, labor_Y]]
    b = [total_labor]
    
    res = linprog(c, A_ub=A, b_ub=b, method='highs')
    
    if res.success:
        x_blender, x_pemanggang_roti = res.x
        total_profit = -res.fun
    
        st.success("✅ Solusi Optimal Ditemukan!")
        st.write(f"Jumlah **Blender**: `{x_blender:.2f}` unit")
        st.write(f"Jumlah **Pemanggang Roti**: `{x_pemanggang_roti:.2f}` unit")
        st.write(f"💰 **Total Keuntungan Maksimal**: `Rp {total_profit:,.0f}`")
    
        # Tabel ringkasan
        hasil = pd.DataFrame({
            "Produk": ["Blender", "Pemanggang Roti"],
            "Jumlah Optimal": [x_blender, x_pemanggang_roti],
            "Keuntungan per Unit": [profit_X, profit_Y],
            "Total Keuntungan": [x_blender * profit_X, x_pemanggang_roti * profit_Y]
        })
        st.subheader("📋 Ringkasan Perhitungan")
        st.dataframe(hasil, use_container_width=True)
    
        # Download hasil
        st.markdown(download_json({
            "Blender": round(x_blender, 2),
            "Pemanggang Roti": round(x_pemanggang_roti, 2),
            "Total Keuntungan": round(total_profit, 2)
        }), unsafe_allow_html=True)
    
        # Visualisasi
        st.subheader("📊 Visualisasi Area Feasible dan Solusi Optimal")
        x_vals = np.linspace(0, 50, 400)
        y_vals = (total_labor - labor_X * x_vals) / labor_Y
    
        fig, ax = plt.subplots()
        ax.plot(x_vals, y_vals, label='Batas Waktu Mesin', color='orange')
        ax.fill_between(x_vals, y_vals, 0, where=(y_vals >= 0), color='peachpuff', alpha=0.3)
    
        ax.plot(x_blender, x_pemanggang_roti, 'ro', label='Solusi Optimal')
        ax.set_xlim(left=0)
        ax.set_ylim(bottom=0)
        ax.set_xlabel("Blender")
        ax.set_ylabel("Pemanggang Roti")
        ax.legend()
        st.pyplot(fig)
    
    else:
        st.error("❌ Tidak ditemukan solusi feasible. Coba ubah batasan atau input.")

with tab2:
    st.header("\U0001F4E6 MODEL PERSEDIAAN – EOQ (ECONOMIC ORDER QUANTITY)")
    st.write("""
    Aplikasi ini menghitung Economic Order Quantity (EOQ) dan visualisasi biaya total
    menggunakan rumus:
    **EOQ** = √(2DS/H)  
    **Total Cost** = (D/Q)S + (Q/2)H
    """)

    st.markdown("Simulasi sistem persediaan barang untuk menentukan jumlah pemesanan optimal (EOQ).")
    
    tab1, tab2 = st.tabs(["🔢 Input Manual", "📘 Studi Kasus Budi Jaya"])
    
    # ---------------------------- TAB 1: Input Manual ----------------------------
    with tab1:
        st.header("Masukkan Data Persediaan Anda")
    
        D = st.number_input("Permintaan Tahunan (unit)", min_value=1, value=5000)
        S = st.number_input("Biaya Pemesanan per Pesanan (Rp)", min_value=1.0, value=75000.0)
        H = st.number_input("Biaya Penyimpanan per Unit per Tahun (Rp)", min_value=1.0, value=1500.0)
        P = st.number_input("Harga Jual per Unit (Rp)", min_value=1.0, value=100000.0)
    
        if D > 0 and S > 0 and H > 0:
            EOQ = np.sqrt((2 * D * S) / H)
            num_orders = D / EOQ
            total_cost = (D / EOQ) * S + (EOQ / 2) * H
            unit_cost = total_cost / D
            profit_total = D * (P - unit_cost)
    
            st.subheader("📈 Hasil Perhitungan")
            col1, col2, col3 = st.columns(3)
            col1.metric("EOQ (unit)", f"{EOQ:.2f}")
            col2.metric("Jumlah Pesanan/Tahun", f"{num_orders:.2f}")
            col3.metric("Total Biaya Persediaan", f"Rp {total_cost:,.2f}")
            st.metric("Laba Total", f"Rp {profit_total:,.2f}")
    
            # Grafik Biaya
            st.subheader("📉 Grafik Komponen Biaya vs Jumlah Pemesanan")
            Q_range = np.linspace(1, EOQ * 2, 100)
            ordering_cost = (D / Q_range) * S
            holding_cost = (Q_range / 2) * H
            total_costs = ordering_cost + holding_cost
    
            fig1, ax1 = plt.subplots()
            ax1.plot(Q_range, ordering_cost, label='Biaya Pemesanan', color='orange', linestyle='--')
            ax1.plot(Q_range, holding_cost, label='Biaya Penyimpanan', color='green', linestyle='--')
            ax1.plot(Q_range, total_costs, label='Total Biaya', color='blue')
            ax1.axvline(EOQ, color='red', linestyle=':', label=f'EOQ = {EOQ:.2f}')
            ax1.set_xlabel('Jumlah Pemesanan (Q)')
            ax1.set_ylabel('Biaya (Rp)')
            ax1.set_title('Grafik Komponen Biaya vs Jumlah Pemesanan')
            ax1.legend()
            ax1.grid(True)
            st.pyplot(fig1)
    
            # Grafik Laba
            st.subheader("📈 Grafik Laba Total vs Jumlah Pemesanan")
            unit_costs = total_costs / D
            profit_range = D * (P - unit_costs)
    
            fig2, ax2 = plt.subplots()
            ax2.plot(Q_range, profit_range, label='Laba Total', color='purple')
            ax2.axhline(0, color='gray', linestyle='--')
            ax2.axvline(EOQ, color='red', linestyle=':', label=f'EOQ = {EOQ:.2f}')
            ax2.fill_between(Q_range, profit_range, 0, where=(profit_range > 0), color='lightgreen', alpha=0.3, label='Untung')
            ax2.fill_between(Q_range, profit_range, 0, where=(profit_range < 0), color='salmon', alpha=0.3, label='Rugi')
            ax2.set_xlabel('Jumlah Pemesanan (Q)')
            ax2.set_ylabel('Laba Total (Rp)')
            ax2.set_title('Grafik Laba vs Jumlah Pemesanan')
            ax2.legend()
            ax2.grid(True)
            st.pyplot(fig2)
    
            # Grafik Khusus Zona Untung/Rugi
            st.subheader("💰 Zona Untung dan Rugi terhadap Jumlah Pemesanan")
            fig3, ax3 = plt.subplots()
            ax3.plot(Q_range, profit_range, label="Laba Total", color="blue")
            ax3.axvline(EOQ, color="red", linestyle=":", label=f'EOQ = {EOQ:.2f} unit')
            ax3.axhline(0, color="black", linestyle="--")
            ax3.fill_between(Q_range, profit_range, 0, where=profit_range > 0, interpolate=True, color='lightgreen', alpha=0.4, label="Zona Untung")
            ax3.fill_between(Q_range, profit_range, 0, where=profit_range < 0, interpolate=True, color='salmon', alpha=0.4, label="Zona Rugi")
            ax3.set_xlabel("Jumlah Pemesanan (Q)")
            ax3.set_ylabel("Laba Total (Rp)")
            ax3.set_title("Visualisasi Zona Untung dan Rugi")
            ax3.legend()
            ax3.grid(True)
            st.pyplot(fig3)
    
        else:
            st.error("Semua input harus lebih besar dari nol!")
    
    # ---------------------------- TAB 2: Studi Kasus ----------------------------
    with tab2:
        st.header("📘 Studi Kasus: Toko Elektronik Budi Jaya")
        st.write("""
        Toko Budi Jaya menjual lampu pintar. Berikut data tahunannya:
        - Permintaan tahunan (D): 2.400 unit
        - Biaya pemesanan per pesanan (S): Rp 100.000
        - Biaya penyimpanan per unit per tahun (H): Rp 2.000
        - Harga Jual per unit (P): Rp 150.000
        """)
    
        D2 = 2400
        S2 = 100000
        H2 = 2000
        P2 = 150000
    
        EOQ2 = np.sqrt((2 * D2 * S2) / H2)
        num_orders2 = D2 / EOQ2
        total_cost2 = (D2 / EOQ2) * S2 + (EOQ2 / 2) * H2
        unit_cost2 = total_cost2 / D2
        profit_total2 = D2 * (P2 - unit_cost2)
    
        st.subheader("📊 Hasil Perhitungan Studi Kasus")
        st.write(f"**EOQ:** {EOQ2:.2f} unit")
        st.write(f"**Jumlah Pemesanan/Tahun:** {num_orders2:.2f}")
        st.write(f"**Total Biaya Persediaan:** Rp {total_cost2:,.2f}")
        st.write(f"**Laba Total:** Rp {profit_total2:,.2f}")
    
        # Grafik Biaya
        Q_range2 = np.linspace(1, EOQ2 * 2, 100)
        ordering_cost2 = (D2 / Q_range2) * S2
        holding_cost2 = (Q_range2 / 2) * H2
        total_costs2 = ordering_cost2 + holding_cost2
    
        st.subheader("📉 Grafik Komponen Biaya vs Jumlah Pemesanan")
        fig4, ax4 = plt.subplots()
        ax4.plot(Q_range2, ordering_cost2, label='Biaya Pemesanan', color='orange', linestyle='--')
        ax4.plot(Q_range2, holding_cost2, label='Biaya Penyimpanan', color='green', linestyle='--')
        ax4.plot(Q_range2, total_costs2, label='Total Biaya', color='blue')
        ax4.axvline(EOQ2, color='red', linestyle=':', label=f'EOQ = {EOQ2:.2f}')
        ax4.set_xlabel('Jumlah Pemesanan (Q)')
        ax4.set_ylabel('Biaya (Rp)')
        ax4.set_title('Grafik Komponen Biaya vs Jumlah Pemesanan')
        ax4.legend()
        ax4.grid(True)
        st.pyplot(fig4)
    
        # Grafik Laba
        unit_costs2 = total_costs2 / D2
        profit_range2 = D2 * (P2 - unit_costs2)
    
        st.subheader("📈 Grafik Laba Total vs Jumlah Pemesanan")
        fig5, ax5 = plt.subplots()
        ax5.plot(Q_range2, profit_range2, label='Laba Total', color='purple')
        ax5.axhline(0, color='gray', linestyle='--')
        ax5.axvline(EOQ2, color='red', linestyle=':', label=f'EOQ = {EOQ2:.2f}')
        ax5.fill_between(Q_range2, profit_range2, 0, where=(profit_range2 > 0), color='lightgreen', alpha=0.3, label='Untung')
        ax5.fill_between(Q_range2, profit_range2, 0, where=(profit_range2 < 0), color='salmon', alpha=0.3, label='Rugi')
        ax5.set_xlabel('Jumlah Pemesanan (Q)')
        ax5.set_ylabel('Laba Total (Rp)')
        ax5.set_title('Grafik Laba vs Jumlah Pemesanan')
        ax5.legend()
        ax5.grid(True)
        st.pyplot(fig5)
    
        # Grafik Khusus Zona Untung/Rugi
        st.subheader("💰 Zona Untung dan Rugi terhadap Jumlah Pemesanan")
        fig6, ax6 = plt.subplots()
        ax6.plot(Q_range2, profit_range2, label="Laba Total", color="blue")
        ax6.axvline(EOQ2, color="red", linestyle=":", label=f'EOQ = {EOQ2:.2f} unit')
        ax6.axhline(0, color="black", linestyle="--")
        ax6.fill_between(Q_range2, profit_range2, 0, where=profit_range2 > 0, interpolate=True, color='lightgreen', alpha=0.4, label="Zona Untung")
        ax6.fill_between(Q_range2, profit_range2, 0, where=profit_range2 < 0, interpolate=True, color='salmon', alpha=0.4, label="Zona Rugi")
        ax6.set_xlabel("Jumlah Pemesanan (Q)")
        ax6.set_ylabel("Laba Total (Rp)")
        ax6.set_title("Visualisasi Zona Untung dan Rugi")
        ax6.legend()
        ax6.grid(True)
        st.pyplot(fig6)
    
    # ---------------------------- Penjelasan Rumus ----------------------------
    with st.expander("ℹ️ Penjelasan Rumus EOQ"):
        st.latex(r'''EOQ = \sqrt{\frac{2DS}{H}}''')
        st.markdown("""
        - **D** = Permintaan tahunan (unit)  
        - **S** = Biaya pemesanan per pesanan  
        - **H** = Biaya penyimpanan per unit per tahun  
    
        **Total Biaya Persediaan (TC):**
        """)
        st.latex(r'''TC = \left( \frac{D}{Q} \times S \right) + \left( \frac{Q}{2} \times H \right)''')
        st.markdown("""**Laba Total = D × (Harga Jual - Biaya per Unit)**""")

with tab3:
    st.header("\U0001F4C8 MODEL  ANTRIAN – LAYANAN PELANGGAN")

    col1, col2 = st.columns(2)
    with col1:
        lambda_ = st.number_input("Tingkat Kedatangan (λ pelanggan/jam)", value=8.0, step=0.1)
    with col2:
        mu = st.number_input("Tingkat Pelayanan (μ pelanggan/jam)", value=11.0, step=0.1)

    rho = lambda_ / mu
    W = 1 / (mu - lambda_) if mu > lambda_ else float('inf')
    Wq = lambda_ / (mu * (mu - lambda_)) if mu > lambda_ else float('inf')

    st.subheader("\U0001F4CA Ringkasan Waktu Rata-rata")

    fig, ax = plt.subplots()
    ax.bar(["Dalam Sistem", "Dalam Antrean"], [W, Wq], color=["blue", "orange"])
    ax.set_ylabel("Waktu (jam)")
    st.pyplot(fig)

    st.write(f"**Utilisasi Sistem (ρ):** {rho:.2f}")
    st.write(f"**Rata-rata waktu di sistem (W):** {W:.2f} jam")
    st.write(f"**Rata-rata waktu tunggu dalam antrean (Wq):** {Wq:.2f} jam")

with tab4:
    st.header("\U0001F4C9 MODEL PRODUKSI INDUSTRI – BREAK-EVEN POINT (BEP)")

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
    ax.ticklabel_format(style='plain', axis='y')  # Tambahan untuk hilangkan 1e9
    ax.set_xlabel("Jumlah Unit")
    ax.set_ylabel("Rupiah (Rp)")
    ax.legend()
    ax.grid(True)

    st.subheader("\U0001F4CA Hasil Analisis")
    st.write(f"Break-even Point: {break_even:.2f} unit")
    st.pyplot(fig)

# Perlu dihapus atau dikondisikan secara aman
# if __name__ == "__main__":
#     st.write("Aplikasi Model Matematika Industri Siap Digunakan ✅")
