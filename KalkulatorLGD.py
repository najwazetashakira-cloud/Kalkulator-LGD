import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

st.set_page_config(page_title="Kalkulator Workout LGD", page_icon="📊", layout="wide")

# ============================================================
# CSS
# ============================================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
.block-container { padding-top: 2rem; padding-bottom: 3rem; max-width: 1160px; }
h1  { font-size: 2rem !important; font-weight: 700 !important; color: #1a1a2e !important;
      letter-spacing: -0.5px !important; margin-bottom: 0.3rem !important; }
h2  { font-size: 1.25rem !important; font-weight: 600 !important; color: #1a1a2e !important;
      margin-top: 2rem !important; margin-bottom: 0.8rem !important;
      padding-bottom: 0.4rem !important; border-bottom: 2px solid #e8eaf0 !important; }
h3  { font-size: 1.05rem !important; font-weight: 600 !important; color: #2c2c54 !important;
      margin-top: 1.2rem !important; margin-bottom: 0.5rem !important; }
p, li { font-size: 0.97rem !important; line-height: 1.7 !important; color: #3d3d5c; }
.card { background: #ffffff; border: 1px solid #e8eaf0; border-radius: 12px;
        padding: 1.1rem 1.4rem; margin-bottom: 1rem; box-shadow: 0 1px 4px rgba(0,0,0,0.05); }
.card-blue   { border-left: 4px solid #4361ee; background: #f5f7ff; }
.card-green  { border-left: 4px solid #2ec4b6; background: #f3fbfa; }
.card-amber  { border-left: 4px solid #f4a261; background: #fff8f0; }
.card-red    { border-left: 4px solid #e63946; background: #fff4f5; }
.card-gray   { border-left: 4px solid #adb5bd; background: #f8f9fa; }
.card-purple { border-left: 4px solid #7b2d8b; background: #faf5ff; }
.badge { display: inline-block; padding: 0.2rem 0.65rem; border-radius: 999px;
         font-size: 0.78rem; font-weight: 600; letter-spacing: 0.3px; margin-bottom: 0.4rem; }
.badge-blue   { background: #e0e7ff; color: #3730a3; }
.badge-green  { background: #d1fae5; color: #065f46; }
.badge-amber  { background: #fef3c7; color: #92400e; }
.badge-red    { background: #fee2e2; color: #991b1b; }
.badge-purple { background: #ede9fe; color: #5b21b6; }
.divider { border: none; border-top: 1px solid #e8eaf0; margin: 1.4rem 0; }
.note { font-size: 0.85rem !important; color: #6b7280; font-style: italic; }
[data-testid="stDataFrame"] { margin-top: 0.8rem; margin-bottom: 1rem;
                               border-radius: 8px; overflow: hidden; }
[data-testid="stMetricValue"] { font-size: 1.5rem !important; font-weight: 700 !important; }
</style>
""", unsafe_allow_html=True)

# ============================================================
# JUDUL
# ============================================================
st.title("📊 Kalkulator Workout LGD — NPV Recovery Kredit Bermasalah")

st.markdown("""
<div class="card card-blue">
<span class="badge badge-blue">Tentang kalkulator ini</span>
<p style="margin:0">
Membandingkan dua jalur penyelesaian kredit bermasalah berdasarkan <strong>nilai ekonomi recovery</strong>,
bukan nominal tagihan.
<br><br>
<strong>Opsi B</strong> — Terima pembayaran pokok sekarang. Pasti, langsung cair, dana bisa diputar kembali.<br>
<strong>Opsi A</strong> — Tunggu pembayaran penuh (pokok + bunga + denda). Ada <strong>tiga kemungkinan hasil</strong>:
debitur bayar penuh <em>(p₁)</em>, debitur akhirnya cuma mau bayar pokok juga tapi terlambat <em>(p₂)</em>,
atau tidak bayar sama sekali <em>(1−p₁−p₂)</em>.
</p>
</div>
""", unsafe_allow_html=True)

# ============================================================
# SATUAN WAKTU — dipilih lebih awal agar mempengaruhi semua input
# ============================================================
st.header("0. Satuan Waktu")

col_unit1, col_unit2 = st.columns([1, 3])
with col_unit1:
    time_unit = st.radio(
        "Pilih satuan waktu analisis",
        options=["Tahun", "Bulan"],
        index=0,
        help=(
            "Tahun: cocok untuk workout jangka panjang, litigasi, restrukturisasi besar. "
            "Rate yang diinput adalah rate tahunan.\n\n"
            "Bulan: cocok untuk penyelesaian cepat 3–24 bulan. "
            "Rate yang diinput adalah rate bulanan (bukan rate tahunan dibagi 12 — "
            "ini adalah effective monthly rate)."
        )
    )
with col_unit2:
    if time_unit == "Bulan":
        st.markdown("""
        <div class="card card-amber" style="margin-top:0.3rem">
        <span class="badge badge-amber">Mode Bulanan</span>
        <p style="margin:0">
        Discount rate dan lending rate yang diinput adalah <strong>rate per bulan</strong>
        (effective monthly rate). Rumus diskonto: <code>(1 + r_m)^t_bulan</code>.
        <br>
        Contoh: lending rate 12% per tahun ≈ 0,95% per bulan
        <em>(bukan 1% — karena compounding)</em>.
        </p>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="card card-gray" style="margin-top:0.3rem">
        <span class="badge badge-blue">Mode Tahunan</span>
        <p style="margin:0">
        Discount rate dan lending rate yang diinput adalah <strong>rate per tahun</strong>.
        Rumus diskonto: <code>(1 + r)^t</code>. Sesuai konvensi LGD Basel II / IFRS 9.
        </p>
        </div>
        """, unsafe_allow_html=True)

# Helper label
satuan     = "bulan" if time_unit == "Bulan" else "tahun"
satuan_cap = time_unit  # "Bulan" / "Tahun"

# ============================================================
# INPUT — PARAMETER KASUS
# ============================================================
st.header("1. Parameter Kasus")

col1, col2 = st.columns(2)
with col1:
    ead = st.number_input(
        "EAD — pokok kredit saat default (juta Rp)",
        min_value=0.01, value=10.0, step=1.0,
        help="Exposure at Default. Pokok outstanding saat default."
    )
    full_claim = st.number_input(
        "Total tagihan penuh: pokok + bunga + denda (juta Rp)",
        min_value=0.01, value=14.0, step=1.0,
        help="Nominal yang ditagihkan jika bank menunggu pembayaran penuh (Opsi A, skenario terbaik)."
    )
    recovery_now = st.number_input(
        "Recovery sekarang — Opsi B / nilai pokok (juta Rp)",
        min_value=0.0, value=10.0, step=1.0,
        help="Jumlah yang diterima jika Opsi B dipilih. Juga dipakai sebagai nilai recovery "
             "skenario p₂ (debitur akhirnya cuma mau bayar pokok setelah menunggu)."
    )

with col2:
    if time_unit == "Tahun":
        t = st.slider(
            "Estimasi waktu tunggu — t (tahun)",
            min_value=0.0, max_value=10.0, value=2.0, step=0.5,
            help="Perkiraan waktu hingga pembayaran Opsi A diterima."
        )
        r = st.slider(
            "Discount rate — r (per tahun)",
            min_value=0.0, max_value=0.50, value=0.12, step=0.01,
            help="Tingkat diskonto tahunan. Lending rate, EIR kontraktual, atau cost of fund."
        )
        lending_rate = st.slider(
            "Lending rate — untuk reinvestment analysis (per tahun)",
            min_value=0.0, max_value=0.30, value=0.12, step=0.01,
            help="Suku bunga tahunan yang diperoleh jika dana Opsi B langsung dipinjamkan kembali."
        )
    else:
        t = st.slider(
            "Estimasi waktu tunggu — t (bulan)",
            min_value=0, max_value=60, value=12, step=1,
            help="Perkiraan jumlah bulan hingga pembayaran Opsi A diterima."
        )
        t = float(t)

        # Metode konversi rate — dipilih sekali, berlaku untuk r dan lending_rate
        conv_method = st.radio(
            "Metode konversi rate tahunan → bulanan",
            options=["Nominal (÷ 12)", "Efektif (^1/12 − 1)"],
            index=0,
            horizontal=True,
            help=(
                "Nominal (÷12): umum di kredit konsumer Indonesia — bunga dihitung flat tiap bulan "
                "tanpa compounding antar bulan. Sesuai akad yang menyebut '12% p.a. nominal'. "
                "\n\nEfektif (^1/12−1): bunga di-compound setiap bulan. "
                "Sesuai akad yang menyebut '12% p.a. efektif' atau EIR/XIRR kontraktual."
            )
        )

        r_annual = st.slider(
            "Discount rate — r (% per tahun)",
            min_value=0.0, max_value=50.0, value=12.0, step=0.5,
            help="Masukkan rate tahunan. Konversi ke bulanan otomatis sesuai metode yang dipilih."
        )
        lending_annual = st.slider(
            "Lending rate — untuk reinvestment analysis (% per tahun)",
            min_value=0.0, max_value=30.0, value=12.0, step=0.5,
            help="Masukkan rate tahunan. Konversi ke bulanan otomatis sesuai metode yang dipilih."
        )

        # Konversi ke bulanan
        if conv_method == "Nominal (÷ 12)":
            r            = (r_annual / 100) / 12
            lending_rate = (lending_annual / 100) / 12
        else:
            r            = (1 + r_annual / 100) ** (1 / 12) - 1
            lending_rate = (1 + lending_annual / 100) ** (1 / 12) - 1

        # Tampilkan hasil konversi
        st.markdown(f"""
        <div class="card card-gray" style="margin-top:0.4rem">
        <span class="badge badge-blue">Rate bulanan yang digunakan</span>
        <p style="margin:0.3rem 0 0 0">
        Discount rate: {r_annual:.1f}%/thn
        {'÷ 12' if conv_method == 'Nominal (÷ 12)' else '^(1/12)−1'}
        = <strong>{r*100:.4f}%/bulan</strong>
        &nbsp;&nbsp;|&nbsp;&nbsp;
        Lending rate: {lending_annual:.1f}%/thn
        {'÷ 12' if conv_method == 'Nominal (÷ 12)' else '^(1/12)−1'}
        = <strong>{lending_rate*100:.4f}%/bulan</strong>
        </p>
        </div>
        """, unsafe_allow_html=True)

# ============================================================
# INPUT — MODEL TIGA SKENARIO
# ============================================================
st.header("2. Model Tiga Skenario Opsi A")

st.markdown("""
<div class="card card-blue">
<span class="badge badge-blue">Cara membaca model ini</span>
<p style="margin:0">
Jika bank memilih <strong>Opsi A (menunggu)</strong>, ada tiga kemungkinan yang bisa terjadi.
<br><br>
Kunci dari model ini: <strong>skenario p₂ bukan opsi ketiga bagi bank</strong> — ini adalah
risiko yang ditanggung jika bank memilih menunggu. Debitur akhirnya cuma mau bayar pokok,
nominalnya sama dengan Opsi B, tapi diterima lebih lambat sehingga nilainya lebih kecil.
Inilah "biaya tersembunyi" dari menunggu.
</p>
</div>
""", unsafe_allow_html=True)

col_p1, col_p2 = st.columns(2)
with col_p1:
    p1 = st.slider(
        "p₁ — Probabilitas bayar penuh (pokok + bunga + denda)",
        min_value=0.0, max_value=1.0, value=0.30, step=0.01,
        help="Probabilitas debitur akhirnya membayar semua tagihan sesuai Opsi A."
    )
with col_p2:
    p2_max = round(1.0 - p1, 2)
    if p2_max <= 0.0:
        p2 = 0.0
        st.markdown("""
        <div class="card card-gray" style="margin-top:0.5rem">
        <p style="margin:0"><strong>p₂ = 0%</strong> — otomatis karena p₁ = 100%.</p>
        </div>
        """, unsafe_allow_html=True)
    else:
        p2 = st.slider(
            "p₂ — Probabilitas akhirnya cuma mau bayar pokok (setelah menunggu)",
            min_value=0.0, max_value=p2_max,
            value=min(0.40, p2_max), step=0.01,
            help="Probabilitas debitur kooperatif tapi hanya mau bayar pokok — nominalnya sama "
                 "dengan Opsi B tapi diterima lebih lambat sehingga nilainya lebih kecil."
        )

p_nothing = max(round(1.0 - p1 - p2, 2), 0.0)

col_m1, col_m2, col_m3 = st.columns(3)
with col_m1:
    st.metric("p₁ — Bayar penuh", f"{p1:.0%}")
with col_m2:
    st.metric("p₂ — Bayar pokok saja (terlambat)", f"{p2:.0%}")
with col_m3:
    st.metric("Tidak bayar sama sekali", f"{p_nothing:.0%}",
              delta="⚠️ Tinggi" if p_nothing > 0.5 else None,
              delta_color="inverse")

if p1 + p2 >= 0.999:
    st.markdown("""
    <div class="card card-amber">
    <span class="badge badge-amber">Perhatian</span>
    <p style="margin:0">p₁ + p₂ = 100%, artinya probabilitas tidak bayar sama sekali = 0%.
    Pastikan ini mencerminkan kondisi aktual debitur.</p>
    </div>
    """, unsafe_allow_html=True)

# ============================================================
# INPUT — BIAYA COLLECTION
# ============================================================
st.header("3. Asumsi Biaya Collection")

col3, col4 = st.columns(2)
with col3:
    collection_cost = st.number_input(
        "Biaya collection / legal / administrasi (juta Rp)",
        min_value=0.0, value=0.0, step=0.5,
        help="Estimasi seluruh biaya yang timbul dalam proses penagihan."
    )
with col4:
    cost_timing = st.radio(
        "Kapan biaya collection terjadi?",
        options=["Akhir periode recovery", "Sekarang"],
        index=0,
        help="Jika akhir periode: biaya ikut didiskontokan. Jika sekarang: langsung mengurangi nilai ekonomi hari ini."
    )

# Validasi
if full_claim < recovery_now:
    st.markdown("""
    <div class="card card-amber"><span class="badge badge-amber">Perhatian</span>
    <p style="margin:0">Total tagihan penuh lebih kecil dari recovery sekarang. Periksa kembali parameter.</p>
    </div>""", unsafe_allow_html=True)

if recovery_now > ead:
    st.markdown("""
    <div class="card card-amber"><span class="badge badge-amber">Perhatian</span>
    <p style="margin:0">Recovery sekarang melebihi EAD — LGD raw Opsi B akan negatif.
    Gunakan LGD floor 0% untuk keperluan konservatif.</p>
    </div>""", unsafe_allow_html=True)

# ============================================================
# FUNGSI PERHITUNGAN
# ============================================================
def calculate_values(ead, full_claim, recovery_now, p1, p2, t, r, collection_cost, cost_timing):
    """
    Tiga skenario Opsi A:
      p1   → debitur bayar full_claim (pada waktu t)
      p2   → debitur bayar recovery_now / pokok saja (pada waktu t, lebih lambat)
      rest → tidak bayar sama sekali

    t dan r harus dalam satuan yang sama (keduanya tahunan atau keduanya bulanan).
    Rumus: df = (1 + r)^t — berlaku untuk kedua mode karena satuannya konsisten.
    """
    df       = (1 + r) ** t
    p_nothing = max(1.0 - p1 - p2, 0.0)

    expected_nominal = p1 * full_claim + p2 * recovery_now

    if cost_timing == "Akhir periode recovery":
        pv_a        = (expected_nominal - collection_cost) / df
        breakeven_p1 = (recovery_now * df + collection_cost - p2 * recovery_now) / full_claim
    else:
        pv_a        = (expected_nominal / df) - collection_cost
        breakeven_p1 = ((recovery_now + collection_cost) * df - p2 * recovery_now) / full_claim

    pv_b  = recovery_now
    pv_s1 = p1 * full_claim / df
    pv_s2 = p2 * recovery_now / df

    lgd_a_raw     = 1 - (pv_a / ead)
    lgd_b_raw     = 1 - (pv_b / ead)
    lgd_a_floored = max(lgd_a_raw, 0)
    lgd_b_floored = max(lgd_b_raw, 0)

    return {
        "df": df,
        "expected_nominal": expected_nominal,
        "p_nothing": p_nothing,
        "pv_a": pv_a, "pv_b": pv_b,
        "pv_s1": pv_s1, "pv_s2": pv_s2,
        "lgd_a_raw": lgd_a_raw, "lgd_b_raw": lgd_b_raw,
        "lgd_a_floored": lgd_a_floored, "lgd_b_floored": lgd_b_floored,
        "breakeven_p1": breakeven_p1,
        "diff": pv_a - pv_b,
    }

# ============================================================
# HITUNG
# ============================================================
res = calculate_values(ead, full_claim, recovery_now, p1, p2, t, r, collection_cost, cost_timing)

df_factor        = res["df"]
expected_nominal = res["expected_nominal"]
pv_a             = res["pv_a"]
pv_b             = res["pv_b"]
pv_s1            = res["pv_s1"]
pv_s2            = res["pv_s2"]
lgd_a_raw        = res["lgd_a_raw"]
lgd_b_raw        = res["lgd_b_raw"]
lgd_a_floored    = res["lgd_a_floored"]
lgd_b_floored    = res["lgd_b_floored"]
breakeven_p1     = res["breakeven_p1"]
diff             = res["diff"]

fv_reinvest   = recovery_now * (1 + lending_rate) ** t
interest_earned = fv_reinvest - recovery_now

# ============================================================
# TABS
# ============================================================
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📌 Hasil Utama",
    "💰 Reinvestment Analysis",
    "🧮 Langkah Perhitungan",
    "📈 Sensitivity Analysis",
    "📝 Catatan Metodologis",
])

# ─────────────────────────────────────────────────────────────
# TAB 1 — HASIL UTAMA
# ─────────────────────────────────────────────────────────────
with tab1:
    st.header("4. Hasil Utama")

    col_a, col_b, col_c = st.columns(3)
    with col_a:
        st.metric("PV Recovery — Opsi A", f"Rp {pv_a:,.2f} jt",
                  delta=f"LGD: {lgd_a_raw*100:.2f}%", delta_color="inverse")
    with col_b:
        st.metric("PV Recovery — Opsi B", f"Rp {pv_b:,.2f} jt",
                  delta=f"LGD: {lgd_b_raw*100:.2f}%", delta_color="inverse")
    with col_c:
        st.metric("Selisih PV (A − B)", f"Rp {diff:,.2f} jt")

    hidden_cost = p2 * recovery_now - pv_s2

    st.markdown(f"""
    <div class="card card-gray">
    <span class="badge badge-blue">Dekomposisi PV Opsi A per skenario</span>
    <p style="margin:0.4rem 0 0 0">
    Kontribusi p₁ (bayar penuh, terdiskon):
    <strong>Rp {pv_s1:,.2f} jt</strong> &nbsp;|&nbsp;
    Kontribusi p₂ (bayar pokok terlambat, terdiskon):
    <strong>Rp {pv_s2:,.2f} jt</strong> &nbsp;|&nbsp;
    Tidak bayar: <strong>Rp 0</strong>
    <br>
    <span style="font-size:0.85rem;color:#e63946;">
    ⚠ Biaya tersembunyi p₂: nominal Rp {p2*recovery_now:,.2f} jt — setelah diskonto hanya
    Rp {pv_s2:,.2f} jt — kehilangan nilai Rp {hidden_cost:,.2f} jt karena terlambat {t:.0f} {satuan}.
    </span>
    </p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<hr class='divider'>", unsafe_allow_html=True)

    if pv_a > pv_b:
        st.markdown(f"""
        <div class="card card-green">
        <span class="badge badge-green">Rekomendasi: Opsi A</span>
        <p style="margin:0">
        Dengan parameter saat ini, <strong>menunggu menghasilkan nilai ekonomi lebih tinggi</strong>.
        PV Opsi A = <strong>Rp {pv_a:,.2f} jt</strong> vs Opsi B = Rp {pv_b:,.2f} jt.
        Keunggulan: <strong>Rp {diff:,.2f} jt</strong>.
        </p>
        </div>""", unsafe_allow_html=True)
    elif pv_b > pv_a:
        st.markdown(f"""
        <div class="card card-green">
        <span class="badge badge-green">Rekomendasi: Opsi B</span>
        <p style="margin:0">
        <strong>Menerima pembayaran sekarang lebih menguntungkan secara ekonomi.</strong>
        Opsi B = <strong>Rp {pv_b:,.2f} jt</strong> vs PV Opsi A = Rp {pv_a:,.2f} jt.
        Nilai yang terkorbankan jika tetap menunggu: <strong>Rp {abs(diff):,.2f} jt</strong>.
        </p>
        </div>""", unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="card card-amber"><span class="badge badge-amber">Setara</span>
        <p style="margin:0">Kedua opsi hampir setara. Pertimbangkan faktor non-kuantitatif.</p>
        </div>""", unsafe_allow_html=True)

    if pv_b >= pv_a:
        st.markdown("""
        <div class="card card-purple">
        <span class="badge badge-purple">⚠️ Risiko Moral Hazard</span>
        <p style="margin:0">
        Opsi B direkomendasikan, tapi kebijakan settlement pokok saja membawa risiko moral hazard
        jika dipersepsikan luas. Pastikan keputusan ini bersifat <em>case-by-case</em>,
        didokumentasikan alasan spesifiknya, dan tidak menghapus catatan kredit buruk di SLIK.
        </p>
        </div>""", unsafe_allow_html=True)

    # ── Breakeven range ──
    # Batas atas: p₂ = 0 (tidak ada cushion, paling konservatif)
    bep_upper = calculate_values(ead, full_claim, recovery_now, p1, 0.0,
                                 t, r, collection_cost, cost_timing)["breakeven_p1"]
    # Batas bawah: p₂ = 1−p₁ (tidak ada yang tidak bayar sama sekali, paling optimis)
    # Diselesaikan analitik: p₁_bep*(full_claim − recovery_now) = recovery_now*(df−1) + C*(1 atau df)
    if full_claim > recovery_now:
        if cost_timing == "Akhir periode recovery":
            bep_lower = (recovery_now * (df_factor - 1) + collection_cost) / (full_claim - recovery_now)
        else:
            bep_lower = (recovery_now * (df_factor - 1) + collection_cost * df_factor) / (full_claim - recovery_now)
    else:
        bep_lower = bep_upper
    bep_lower = max(bep_lower, 0.0)

    bep_lo_pct = bep_lower * 100
    bep_hi_pct = bep_upper * 100
    p1_pct     = p1 * 100

    if bep_hi_pct > 100:
        st.markdown(f"""
        <div class="card card-red">
        <span class="badge badge-red">Breakeven tidak tercapai di semua skenario p₂</span>
        <p style="margin:0">
        Bahkan dengan asumsi p₂ paling optimis (p₂ = 1−p₁), p₁ minimum yang dibutuhkan
        = <strong>{bep_lo_pct:.1f}%</strong>. Pada kondisi p₂ = 0%, bisa mencapai
        <strong>{bep_hi_pct:.1f}%</strong>. Opsi A tidak bisa unggul pada kombinasi t dan r saat ini.
        </p>
        </div>""", unsafe_allow_html=True)
    elif p1_pct >= bep_hi_pct:
        st.markdown(f"""
        <div class="card card-green">
        <span class="badge badge-green">Opsi A layak di semua skenario p₂</span>
        <p style="margin:0">
        p₁ aktual <strong>{p1_pct:.1f}%</strong> melampaui breakeven bahkan pada kondisi
        paling konservatif (p₂ = 0%): breakeven = <strong>{bep_hi_pct:.1f}%</strong>.
        Opsi A unggul tanpa peduli seberapa besar p₂.
        </p>
        </div>""", unsafe_allow_html=True)
    elif p1_pct >= bep_lo_pct:
        st.markdown(f"""
        <div class="card card-amber">
        <span class="badge badge-amber">Breakeven p₁: {bep_lo_pct:.1f}% – {bep_hi_pct:.1f}%</span>
        <p style="margin:0">
        p₁ aktual <strong>{p1_pct:.1f}%</strong> berada di dalam range breakeven.<br>
        • Kalau p₂ besar (debitur kemungkinan bayar pokok meski terlambat)
        → breakeven serendah <strong>{bep_lo_pct:.1f}%</strong>
        → <span style="color:#065f46;font-weight:600">Opsi A layak</span><br>
        • Kalau p₂ kecil atau nol
        → breakeven bisa sampai <strong>{bep_hi_pct:.1f}%</strong>
        → <span style="color:#92400e;font-weight:600">Opsi A berisiko</span><br>
        Keputusan bergantung pada keyakinan seberapa besar p₂.
        </p>
        </div>""", unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div class="card card-red">
        <span class="badge badge-red">Breakeven p₁: {bep_lo_pct:.1f}% – {bep_hi_pct:.1f}%</span>
        <p style="margin:0">
        p₁ aktual <strong>{p1_pct:.1f}%</strong> belum mencapai breakeven di semua skenario p₂.
        Opsi B lebih rasional pada kombinasi t dan r saat ini.
        </p>
        </div>""", unsafe_allow_html=True)

    st.subheader("Ringkasan Perbandingan")
    summary_df = pd.DataFrame({
        "Komponen": [
            "Nilai nominal (skenario terbaik)",
            "Expected recovery nominal",
            "Present value recovery",
            "LGD raw",
            "LGD (floor 0%)",
        ],
        "Opsi A — Tunggu (3 skenario)": [
            f"Rp {full_claim:,.2f} jt  (jika p₁ terjadi)",
            f"Rp {expected_nominal:,.2f} jt",
            f"Rp {pv_a:,.2f} jt",
            f"{lgd_a_raw*100:.2f}%",
            f"{lgd_a_floored*100:.2f}%",
        ],
        "Opsi B — Terima sekarang (pasti)": [
            f"Rp {recovery_now:,.2f} jt",
            f"Rp {recovery_now:,.2f} jt",
            f"Rp {pv_b:,.2f} jt",
            f"{lgd_b_raw*100:.2f}%",
            f"{lgd_b_floored*100:.2f}%",
        ],
    })
    st.dataframe(summary_df, use_container_width=True, hide_index=True)

    st.subheader("Visualisasi — Dekomposisi PV Opsi A per Skenario")
    fig, ax = plt.subplots(figsize=(8, 3.2))
    fig.patch.set_facecolor('#fafafa')
    ax.set_facecolor('#fafafa')
    bw = 0.38
    ax.bar(0, pv_s1, bw, label=f'p₁: bayar penuh ({p1:.0%})', color='#4361ee', alpha=0.85)
    ax.bar(0, pv_s2, bw, bottom=pv_s1,
           label=f'p₂: bayar pokok terlambat ({p2:.0%})', color='#f4a261', alpha=0.85)
    if collection_cost > 0:
        cp = collection_cost / df_factor if cost_timing == "Akhir periode recovery" else collection_cost
        ax.bar(0, -cp, bw, bottom=pv_s1 + pv_s2, label='Biaya collection', color='#e63946', alpha=0.7)
    ax.bar(1, pv_b, bw, label='Opsi B — pasti', color='#2ec4b6', alpha=0.85)
    ax.axhline(pv_b, color='#2ec4b6', linewidth=1.3, linestyle='--', alpha=0.55)
    if p2 > 0:
        nominal_p2 = p2 * recovery_now
        ax.annotate(
            f'Nominal p₂: Rp {nominal_p2:,.2f} jt\n(PV hanya Rp {pv_s2:,.2f} jt)',
            xy=(0, pv_s1 + pv_s2 / 2),
            xytext=(0.55, pv_s1 + pv_s2 / 2),
            fontsize=7.5, color='#c05c00',
            arrowprops=dict(arrowstyle='->', color='#c05c00', lw=1.2),
            va='center'
        )
    ax.set_xticks([0, 1])
    ax.set_xticklabels(['Opsi A\n(3 skenario, PV)', 'Opsi B\n(pasti, sekarang)'], fontsize=10)
    ax.set_ylabel('Present Value (juta Rp)', fontsize=9)
    ax.set_title('Dekomposisi PV Opsi A — bagian oranye adalah "biaya tersembunyi" menunggu',
                 fontsize=9.5, fontweight='600')
    ax.legend(fontsize=8, loc='upper right', framealpha=0.88)
    ax.spines[['top', 'right']].set_visible(False)
    ax.grid(True, axis='y', alpha=0.2, linestyle='--')
    plt.tight_layout()
    st.pyplot(fig)

    st.markdown(f"""
    <p class="note">
    Batang oranye (p₂) adalah inti dari model tiga skenario: nominalnya sama dengan Opsi B,
    tapi nilainya lebih kecil karena terdiskon. Semakin besar p₂ dan semakin panjang t,
    semakin besar kerugian nilai yang tersembunyi di balik strategi menunggu.
    </p>
    """, unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────
# TAB 2 — REINVESTMENT ANALYSIS
# ─────────────────────────────────────────────────────────────
with tab2:
    st.header("Reinvestment Analysis — Jika Dana Opsi B Diputar Kembali")

    st.markdown(f"""
    <div class="card card-blue">
    <span class="badge badge-blue">Tujuan analisis</span>
    <p style="margin:0">
    Bagian ini tidak digunakan untuk menghitung LGD utama — analisis itu sudah selesai di Tab 1.
    Tujuan bagian ini adalah menunjukkan skenario tambahan: jika dana Opsi B diterima sekarang
    dan langsung dipinjamkan kembali, berapa nilainya pada akhir periode {t:.0f} {satuan}
    yang sama dengan waktu tunggu Opsi A?
    <br><br>
    Perbandingan dilakukan pada basis <strong>future value</strong>, bukan mencampur future value
    dengan present value, agar tidak terjadi double counting.
    </p>
    </div>
    """, unsafe_allow_html=True)

    col_r1, col_r2, col_r3 = st.columns(3)
    with col_r1:
        st.metric("Dana recovery Opsi B sekarang", f"Rp {recovery_now:,.2f} jt")
    with col_r2:
        r_lend_display = f"{lending_rate*100:.2f}%/{satuan}"
        st.metric(f"Future value setelah {t:.0f} {satuan} @ {r_lend_display}",
                  f"Rp {fv_reinvest:,.2f} jt")
    with col_r3:
        st.metric("Bunga reinvestasi",
                  f"Rp {interest_earned:,.2f} jt",
                  delta=f"+{interest_earned/recovery_now*100:.1f}% dari dana awal" if recovery_now > 0 else None)

    st.markdown("<hr class='divider'>", unsafe_allow_html=True)

    st.subheader(f"Perbandingan Future Value pada Akhir Periode ({t:.0f} {satuan})")

    fv_a_expected = expected_nominal
    fv_a_full     = full_claim

    comparison_df = pd.DataFrame({
        "Komponen": [
            "Opsi A — expected nominal recovery",
            "Opsi A — jika debitur bayar penuh (skenario p₁)",
            "Opsi B — recovery sekarang + reinvestasi",
        ],
        f"Nilai pada akhir {satuan} ke-{t:.0f}": [
            f"Rp {fv_a_expected:,.2f} jt",
            f"Rp {fv_a_full:,.2f} jt",
            f"Rp {fv_reinvest:,.2f} jt",
        ],
        "Keterangan": [
            f"p₁×full_claim + p₂×pokok = {p1:.0%}×{full_claim:,.1f} + {p2:.0%}×{recovery_now:,.1f}",
            f"Skenario optimistis murni — hanya terjadi dengan probabilitas p₁ = {p1:.0%}",
            f"Dana Opsi B diputar pada {lending_rate*100:.2f}%/{satuan}",
        ],
    })
    st.dataframe(comparison_df, use_container_width=True, hide_index=True)

    diff_vs_expected = fv_reinvest - fv_a_expected
    diff_vs_full     = fv_reinvest - fv_a_full

    st.markdown(f"""
    <div class="card card-blue">
    <span class="badge badge-blue">Interpretasi</span>
    <p style="margin:0">
    Jika Opsi B diterima dan langsung dipinjamkan kembali pada {lending_rate*100:.2f}%/{satuan},
    dana Rp {recovery_now:,.2f} jt akan menjadi <strong>Rp {fv_reinvest:,.2f} jt</strong>
    setelah {t:.0f} {satuan}.
    <br><br>
    Sebagai pembanding, nilai nominal Opsi A pada akhir periode:<br>
    • Expected nominal (tiga skenario): <strong>Rp {fv_a_expected:,.2f} jt</strong>
    — selisih vs Opsi B reinvestasi: <strong>Rp {diff_vs_expected:,.2f} jt</strong><br>
    • Jika bayar penuh (prob. {p1:.0%}): <strong>Rp {fv_a_full:,.2f} jt</strong>
    — selisih vs Opsi B reinvestasi: <strong>Rp {diff_vs_full:,.2f} jt</strong>
    </p>
    </div>
    """, unsafe_allow_html=True)

    if fv_reinvest >= fv_a_expected:
        st.markdown("""
        <div class="card card-green"><span class="badge badge-green">Kesimpulan tambahan</span>
        <p style="margin:0">
        Dana Opsi B yang diputar kembali menghasilkan future value yang melampaui expected nominal
        recovery Opsi A. Ini memperkuat argumen Opsi B — bukan hanya lebih baik secara PV,
        tapi juga secara nominal akhir periode setelah reinvestasi.
        </p>
        </div>""", unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div class="card card-amber"><span class="badge badge-amber">Kesimpulan tambahan</span>
        <p style="margin:0">
        Hasil reinvestasi Opsi B (Rp {fv_reinvest:,.2f} jt) belum melampaui expected nominal Opsi A
        (Rp {fv_a_expected:,.2f} jt). Namun perlu diingat: expected nominal Opsi A adalah nilai
        rata-rata probabilistik — realisasinya bisa lebih rendah jika skenario p₂ atau tidak bayar yang terjadi.
        </p>
        </div>""", unsafe_allow_html=True)

    st.markdown("""
    <p class="note">
    Perbandingan ini sengaja dilakukan terhadap nilai nominal Opsi A (bukan PV-nya) untuk
    menghindari double counting — PV Opsi A sudah memasukkan efek diskonto di Tab 1.
    </p>
    """, unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────
# TAB 3 — LANGKAH PERHITUNGAN
# ─────────────────────────────────────────────────────────────
with tab3:
    st.header("5. Langkah Perhitungan")

    # Notasi sesuai satuan
    if time_unit == "Bulan":
        r_sym  = r"r_m"          # monthly rate symbol
        t_sym  = r"t_m"          # monthly t symbol
        r_disp = f"{r*100:.4f}\\%/\\text{{bln}}"
        t_disp = f"{t:.0f}\\text{{ bln}}"
        r_note = f"r_m = {r*100:.4f}\\% \\text{{ (effective monthly rate)}}"
        r_lend_sym = r"r_{m,\text{lending}}"
        r_lend_disp = f"{lending_rate*100:.4f}\\%"
    else:
        r_sym  = r"r"
        t_sym  = r"t"
        r_disp = f"{r:.4f}"
        t_disp = f"{t:.1f}\\text{{ thn}}"
        r_note = f"r = {r:.4f} \\text{{ (annual rate)}}"
        r_lend_sym = r"r_{\text{lending}}"
        r_lend_disp = f"{lending_rate:.4f}"

    st.markdown("### A. Faktor Diskonto")
    if time_unit == "Bulan":
        st.markdown("""
        <div class="card card-gray" style="margin-bottom:0.5rem">
        <p style="margin:0">Mode bulanan menggunakan <strong>effective monthly rate</strong>.
        Rumusnya tetap sama: <code>(1 + r_m)^t_m</code> — hanya satuannya yang berbeda dari mode tahunan.</p>
        </div>
        """, unsafe_allow_html=True)
    st.latex(
        f"(1+{r_sym})^{{{t_sym}}} = (1+{r*100:.4f}\\%)^{{{t:.0f}}} = {df_factor:.6f}"
    )

    st.markdown("### B. Expected Recovery Nominal Opsi A — Tiga Skenario")
    st.latex(
        r"E[R_A] = p_1 \cdot R_{\text{full}} + p_2 \cdot R_{\text{now}} + (1-p_1-p_2) \cdot 0"
    )
    st.latex(
        f"= {p1:.2f} \\times {full_claim:,.2f}"
        f" + {p2:.2f} \\times {recovery_now:,.2f}"
        f" = {expected_nominal:,.2f} \\text{{ jt}}"
    )

    if cost_timing == "Akhir periode recovery":
        st.markdown(f"### C. Present Value Recovery — Opsi A (biaya di akhir periode)")
        st.latex(
            r"PV(R_A) = \frac{E[R_A] - C}{(1+" + r_sym + r")^{" + t_sym + r"}}"
            f" = \\frac{{{expected_nominal:,.2f} - {collection_cost:,.2f}}}{{{df_factor:.6f}}}"
            f" = {pv_a:,.2f} \\text{{ jt}}"
        )
    else:
        st.markdown(f"### C. Present Value Recovery — Opsi A (biaya sekarang)")
        st.latex(
            r"PV(R_A) = \frac{E[R_A]}{(1+" + r_sym + r")^{" + t_sym + r"}} - C"
            f" = \\frac{{{expected_nominal:,.2f}}}{{{df_factor:.6f}}} - {collection_cost:,.2f}"
            f" = {pv_a:,.2f} \\text{{ jt}}"
        )

    st.markdown(f"### D. Breakeven p₁ (p₂ tetap = {p2:.0%})")
    if cost_timing == "Akhir periode recovery":
        st.latex(
            r"p_{1,\min} = \frac{R_{\text{now}} \cdot (1+" + r_sym + r")^{" + t_sym + r"} + C - p_2 \cdot R_{\text{now}}}{R_{\text{full}}}"
            f" = {breakeven_p1*100:.2f}\\%"
        )
    else:
        st.latex(
            r"p_{1,\min} = \frac{(R_{\text{now}} + C) \cdot (1+" + r_sym + r")^{" + t_sym + r"} - p_2 \cdot R_{\text{now}}}{R_{\text{full}}}"
            f" = {breakeven_p1*100:.2f}\\%"
        )

    st.markdown("### E. Present Value Recovery — Opsi B")
    st.latex(f"PV(R_B) = R_{{\\text{{now}}}} = {pv_b:,.2f} \\text{{ jt}}")

    st.markdown("### F. LGD")
    st.latex(
        rf"LGD_A = 1 - \frac{{{pv_a:,.2f}}}{{{ead:,.2f}}} = {lgd_a_raw*100:.2f}\%"
        r"\qquad"
        rf"LGD_B = 1 - \frac{{{pv_b:,.2f}}}{{{ead:,.2f}}} = {lgd_b_raw*100:.2f}\%"
    )

    st.markdown("### G. Biaya Tersembunyi Skenario p₂")
    st.latex(
        r"\text{Nilai hilang} = p_2 \cdot R_{\text{now}} - \frac{p_2 \cdot R_{\text{now}}}{(1+"
        + r_sym + r")^{" + t_sym + r"}}"
        f" = {p2*recovery_now:,.2f} - {pv_s2:,.2f}"
        f" = {p2*recovery_now - pv_s2:,.2f} \\text{{ jt}}"
    )

    st.markdown("### H. Future Value Opsi B — Reinvestasi")
    st.latex(
        r"FV_B = R_{\text{now}} \times (1+" + r_lend_sym + r")^{" + t_sym + r"}"
        f" = {recovery_now:,.2f} \\times (1 + {lending_rate*100:.4f}\\%)^{{{t:.0f}}}"
        f" = {fv_reinvest:,.2f} \\text{{ jt}}"
    )

# ─────────────────────────────────────────────────────────────
# TAB 4 — SENSITIVITY ANALYSIS
# ─────────────────────────────────────────────────────────────
with tab4:
    st.header("6. Sensitivity Analysis")

    # Rentang t disesuaikan satuan
    if time_unit == "Bulan":
        t_vals     = [3, 6, 9, 12, 18, 24, 36]
        t_cols     = [f"{x} bln" for x in t_vals]
        t_grid_bep = np.arange(0, 37, 1, dtype=float)
        t_lim_bep  = 36
        xlabel_bep = "Waktu tunggu recovery (bulan)"
        r_label    = f"r_m = {r*100:.2f}%/bln"
    else:
        t_vals     = [0.5, 1, 2, 3, 4, 5]
        t_cols     = [f"{x} thn" for x in t_vals]
        t_grid_bep = np.arange(0, 5.51, 0.25)
        t_lim_bep  = 5.5
        xlabel_bep = "Waktu tunggu recovery (tahun)"
        r_label    = f"r = {r:.0%}/thn"

    # Tabel A: p1 vs t
    st.subheader(f"A. p₁ vs Waktu Tunggu  (p₂ = {p2:.0%} tetap, {r_label})")
    st.markdown("""
    <div class="card card-blue"><p style="margin:0">
    Angka dalam kurung = selisih PV (A − B). Positif = A lebih baik. <strong>★ = parameter aktif.</strong>
    </p></div>
    """, unsafe_allow_html=True)

    p1_vals = [0.10, 0.20, 0.30, 0.40, 0.50, 0.65, 0.80, 0.90, 1.0]
    rows_a = []
    for p1_i in p1_vals:
        row = []
        for t_i in t_vals:
            ri = calculate_values(ead, full_claim, recovery_now, p1_i, p2, float(t_i), r, collection_cost, cost_timing)
            d  = ri["diff"]
            mk = " ★" if abs(p1_i - p1) < 0.06 and abs(float(t_i) - t) < (1.5 if time_unit == "Bulan" else 0.3) else ""
            if d > 0.1:    row.append(f"A (+{d:,.2f}){mk}")
            elif d < -0.1: row.append(f"B ({d:,.2f}){mk}")
            else:           row.append(f"≈ setara{mk}")
        rows_a.append(row)

    df_sa = pd.DataFrame(rows_a, index=[f"p₁ = {x:.0%}" for x in p1_vals], columns=t_cols)
    df_sa.index.name = "p₁ (bayar penuh)"
    st.dataframe(df_sa, use_container_width=True)

    # Tabel B: r vs t
    if time_unit == "Bulan":
        r_vals     = [0.003, 0.005, 0.007, 0.009, 0.010, 0.012, 0.015, 0.020]
        r_idx      = [f"r_m = {x*100:.2f}%/bln" for x in r_vals]
        r_tol      = 0.0015
    else:
        r_vals     = [0.06, 0.08, 0.10, 0.12, 0.15, 0.18, 0.20, 0.25]
        r_idx      = [f"r = {x:.0%}/thn" for x in r_vals]
        r_tol      = 0.015

    st.subheader(f"B. Discount Rate vs Waktu Tunggu  (p₁ = {p1:.0%}, p₂ = {p2:.0%})")
    st.markdown("""
    <div class="card card-blue"><p style="margin:0">
    Seberapa sensitif keputusan terhadap pilihan discount rate?
    Perbedaan rate kecil pun bisa membalik rekomendasi. <strong>★ = parameter aktif.</strong>
    </p></div>
    """, unsafe_allow_html=True)

    rows_b = []
    for r_i in r_vals:
        row = []
        for t_i in t_vals:
            ri = calculate_values(ead, full_claim, recovery_now, p1, p2, float(t_i), r_i, collection_cost, cost_timing)
            d  = ri["diff"]
            mk = " ★" if abs(r_i - r) < r_tol and abs(float(t_i) - t) < (1.5 if time_unit == "Bulan" else 0.3) else ""
            if d > 0.1:    row.append(f"A (+{d:,.2f}){mk}")
            elif d < -0.1: row.append(f"B ({d:,.2f}){mk}")
            else:           row.append(f"≈ setara{mk}")
        rows_b.append(row)

    df_sb = pd.DataFrame(rows_b, index=r_idx, columns=t_cols)
    df_sb.index.name = "Discount rate"
    st.dataframe(df_sb, use_container_width=True)

    # Breakeven chart — dengan range band (batas bawah dan atas)
    st.subheader("C. Breakeven Chart — Range p₁ Minimum vs Waktu Tunggu")
    st.markdown("""
    <div class="card card-blue"><p style="margin:0">
    <strong>Band abu-abu</strong> = range breakeven p₁ untuk semua kemungkinan p₂.<br>
    Batas bawah: p₂ = 1−p₁ (tidak ada yang tidak bayar sama sekali — paling optimis).<br>
    Batas atas: p₂ = 0% (semua yang tidak bayar penuh = tidak bayar sama sekali — paling konservatif).<br>
    Kalau p₁ aktual <strong>di atas band</strong>: Opsi A layak di semua skenario.
    Kalau <strong>di dalam band</strong>: tergantung asumsi p₂.
    Kalau <strong>di bawah band</strong>: Opsi B lebih rasional di semua skenario.
    </p></div>
    """, unsafe_allow_html=True)

    # Hitung dua kurva: batas atas (p2=0) dan batas bawah (p2=1-p1, analitik)
    bep_upper_arr = np.array([
        calculate_values(ead, full_claim, recovery_now, p1, 0.0, t_i, r, collection_cost, cost_timing)["breakeven_p1"]
        for t_i in t_grid_bep
    ])
    if full_claim > recovery_now:
        df_grid = (1 + r) ** t_grid_bep
        if cost_timing == "Akhir periode recovery":
            bep_lower_arr = (recovery_now * (df_grid - 1) + collection_cost) / (full_claim - recovery_now)
        else:
            bep_lower_arr = (recovery_now * (df_grid - 1) + collection_cost * df_grid) / (full_claim - recovery_now)
    else:
        bep_lower_arr = bep_upper_arr.copy()
    bep_lower_arr  = np.clip(bep_lower_arr,   0, 150)
    bep_upper_disp = np.clip(bep_upper_arr * 100, 0, 150)
    bep_lower_disp = np.clip(bep_lower_arr * 100, 0, 150)

    fig2, ax2 = plt.subplots(figsize=(10, 4.5))
    fig2.patch.set_facecolor('#fafafa')
    ax2.set_facecolor('#fafafa')

    # Zona A aman (di atas band)
    ax2.fill_between(t_grid_bep, bep_upper_disp, 130, alpha=0.10, color='#4361ee')
    # Band range breakeven
    ax2.fill_between(t_grid_bep, bep_lower_disp, bep_upper_disp,
                     alpha=0.25, color='#adb5bd', label='Range breakeven (semua p₂)')
    # Zona B aman (di bawah band)
    ax2.fill_between(t_grid_bep, 0, bep_lower_disp, alpha=0.10, color='#2ec4b6')

    ax2.plot(t_grid_bep, bep_upper_disp, color='#6b7280', linewidth=1.5,
             linestyle='--', label='Batas atas (p₂ = 0%)')
    ax2.plot(t_grid_bep, bep_lower_disp, color='#6b7280', linewidth=1.5,
             linestyle=':', label='Batas bawah (p₂ = 1−p₁)')
    ax2.axhline(p1 * 100, color='#e63946', linewidth=2.0,
                label=f'p₁ aktual ({p1:.0%})')
    ax2.axhline(100, color='#adb5bd', linewidth=1, linestyle=':', alpha=0.5)

    idx_t = np.argmin(np.abs(t_grid_bep - t))
    bep_at_t_upper = min(bep_upper_disp[idx_t], 150)
    bep_at_t_lower = min(bep_lower_disp[idx_t], 150)
    ax2.scatter([t], [(bep_at_t_upper + bep_at_t_lower) / 2], s=90, color='#6b7280',
                zorder=6, label=f'Parameter aktif (t={t:.0f} {satuan})')

    mid_t = t_lim_bep * 0.65
    ax2.text(mid_t, min(bep_upper_disp[-1] + 7, 124),
             'Opsi A aman (semua p₂)', color='#4361ee', fontsize=8.5, alpha=0.85)
    ax2.text(mid_t, max(bep_lower_disp[-1] - 9, 3),
             'Opsi B lebih baik (semua p₂)', color='#2ec4b6', fontsize=8.5, alpha=0.85)

    unit_r_title = f"r_m = {r*100:.2f}%/bln" if time_unit == "Bulan" else f"r = {r:.0%}/thn"
    ax2.set_xlabel(xlabel_bep, fontsize=10)
    ax2.set_ylabel('p₁ minimum (%)', fontsize=10)
    ax2.set_title(f'Range Breakeven p₁ vs Waktu Tunggu  ({unit_r_title})',
                  fontsize=11, fontweight='600')
    ax2.set_ylim(0, 130)
    ax2.set_xlim(0, t_lim_bep)
    ax2.grid(True, alpha=0.25, linestyle='--')
    ax2.spines[['top', 'right']].set_visible(False)
    ax2.legend(fontsize=8.5, loc='upper left', framealpha=0.88)
    plt.tight_layout()
    st.pyplot(fig2)

    st.markdown("""
    <p class="note">
    Band abu-abu adalah zona ketidakpastian — lebar band mencerminkan seberapa besar p₂
    mempengaruhi keputusan. Band sempit berarti keputusan robust terhadap asumsi p₂.
    Band lebar berarti keyakinan tentang p₂ sangat menentukan.
    Posisi garis merah (p₁ aktual) relatif terhadap band adalah anchor utama ke komite kredit.
    </p>
    """, unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────
# TAB 5 — CATATAN METODOLOGIS
# ─────────────────────────────────────────────────────────────
with tab5:
    st.header("7. Catatan Metodologis")

    notes = [
        ("badge-blue", "1. Model tiga skenario Opsi A",
         "Model ini memisahkan dua sumber ketidakpastian dalam Opsi A: "
         "<strong>p₁</strong> (debitur bayar penuh) dan <strong>p₂</strong> (debitur akhirnya "
         "cuma mau bayar pokok setelah menunggu). Skenario p₂ secara eksplisit menghitung "
         "'biaya tersembunyi' dari menunggu — nominal yang diterima sama dengan Opsi B, "
         "tapi nilainya lebih kecil karena terdiskon waktu."),

        ("badge-blue", "2. Satuan waktu dan konversi discount rate",
         "Kalkulator mendukung dua mode: <strong>tahunan</strong> (konvensi Basel II / IFRS 9) "
         "dan <strong>bulanan</strong> (cocok untuk penyelesaian cepat 3–24 bulan). "
         "Rumus diskonto tetap: <code>(1+r_m)^t_bulan</code> — satuannya harus konsisten. "
         "Mode bulanan menyediakan dua pilihan konversi dari rate tahunan: "
         "<strong>Nominal (÷12)</strong> — cocok untuk kredit konsumer Indonesia yang akadnya "
         "menyebut rate nominal, bunga antar bulan tidak di-compound; "
         "dan <strong>Efektif (^1/12−1)</strong> — cocok untuk akad EIR/XIRR atau bunga "
         "yang di-compound setiap bulan. "
         "Untuk r = 12%/thn: nominal → 1,0000%/bln, efektif → 0,9489%/bln."),

        ("badge-blue", "3. LGD dihitung terhadap EAD",
         "Konsisten dengan Basel II §460. LGD raw bisa negatif jika PV recovery > EAD — "
         "gunakan floor 0% untuk keperluan konservatif."),

        ("badge-blue", "4. Pemilihan discount rate",
         "<strong>Lending rate</strong>: tepat untuk opportunity cost dana. "
         "<strong>EIR kontraktual</strong>: relevan untuk valuasi recovery sesuai IFRS 9/PSAK 71. "
         "<strong>Cost of fund</strong>: sebagai batas bawah konservatif."),

        ("badge-blue", "5. Reinvestment analysis — basis future value",
         "Tab reinvestment menggunakan perbandingan future value untuk menghindari double counting. "
         "PV Opsi A sudah memasukkan efek diskonto di Tab 1 — membandingkan FV reinvestasi "
         "terhadap PV Opsi A akan melakukan double counting."),

        ("badge-purple", "6. Risiko moral hazard",
         "Jika Opsi B direkomendasikan, kalkulator otomatis menampilkan peringatan. "
         "Kebijakan settlement pokok saja harus bersifat case-by-case — dokumentasikan alasan "
         "spesifik dan pertimbangkan klausul yang mempertahankan catatan kredit buruk di SLIK."),

        ("badge-amber", "7. Batasan penggunaan",
         "Kalkulator ini tepat untuk analisis komparatif dua opsi penyelesaian. "
         "Belum cukup untuk: estimasi LGD regulatory capital (AIRB), kasus dengan jadwal cicilan "
         "bertahap berbeda waktu, dan analisis portfolio-level."),
    ]

    for badge_class, title, content in notes:
        st.markdown(f"""
        <div class="card">
        <span class="badge {badge_class}">{title}</span>
        <p style="margin:0.4rem 0 0 0">{content}</p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("""
    <div class="card card-gray">
    <p class="note" style="margin:0">
    Tagihan nominal lebih besar belum tentu menghasilkan nilai ekonomi recovery lebih tinggi —
    terutama saat p₁ rendah, p₂ signifikan, waktu tunggu panjang, dan opportunity cost besar.
    Gunakan breakeven p₁ sebagai anchor komunikasi ke komite kredit.
    </p>
    </div>
    """, unsafe_allow_html=True)
