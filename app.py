import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import pulp
from math import sqrt
from scipy.optimize import linprog
import sympy as sp
import json
import base64

st.set_page_config(page_title="Model Matematika", layout="wide")

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
    st.title("🏭 Optimasi Produksi - PT. Sinar Terang Mandiri")
    
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
    
    st.markdown("<h1>OPTIMASI PRODUKSI - PT SINAR TERANG MANDIRI</h1>", unsafe_allow_html=True)
    
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

    st.subheader("\U0001F4CA Hasil Perhitungan")
    result_col1, result_col2 = st.columns(2)
    with result_col1:
        st.metric(label="EOQ Optimal", value=f"{Q:.2f} unit")
    with result_col2:
        st.metric(label="Biaya Total Minimum", value=f"Rp.{TC:,.2f}")

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
