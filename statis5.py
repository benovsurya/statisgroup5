import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# =============================
# Language Dictionary
# =============================
LANG = {
    "English": {
        "title": "Survey Data Analysis Web App",
        "upload": "Upload Survey Data (CSV)",
        "desc": "Descriptive Analysis",
        "assoc": "Association Analysis",
        "select_col": "Select Column",
        "select_cols": "Select Two Columns",
        "freq": "Frequency Table",
        "chi": "Chi-Square Statistic",
        "cramer": "Cramer's V",
        "no_file": "Please upload a CSV file",
        "page": "Select Page",
        "cont": "Contingency Table"
    },
    "Indonesia": {
        "title": "Aplikasi Analisis Data Survei",
        "upload": "Unggah Data Survei (CSV)",
        "desc": "Analisis Deskriptif",
        "assoc": "Analisis Asosiasi",
        "select_col": "Pilih Kolom",
        "select_cols": "Pilih Dua Kolom",
        "freq": "Tabel Frekuensi",
        "chi": "Statistik Chi-Square",
        "cramer": "Cramer's V",
        "no_file": "Silakan unggah file CSV",
        "page": "Pilih Halaman",
        "cont": "Tabel Kontingensi"
    }
}

# =============================
# Sidebar
# =============================
st.sidebar.title("Settings")
language = st.sidebar.selectbox("Language / Bahasa", ["English", "Indonesia"])
text = LANG[language]

page = st.sidebar.selectbox(
    text["page"],
    ["Descriptive Analysis", "Association Analysis"]
)

uploaded_file = st.sidebar.file_uploader(
    text["upload"],
    type=["csv"]
)

# =============================
# Main Title
# =============================
st.title(text["title"])

# =============================
# Read CSV (SAFE & STABLE)
# =============================
if uploaded_file is not None:
    try:
        df = pd.read_csv(
            uploaded_file,
            sep=None,               # auto detect delimiter
            engine="python",
            encoding="utf-8",
            on_bad_lines="skip"
        )

        st.subheader("Preview Data")
        st.dataframe(df.head())

        # =============================
        # DESCRIPTIVE ANALYSIS
        # =============================
        if page == "Descriptive Analysis":
            st.header(text["desc"])

            column = st.selectbox(text["select_col"], df.columns)

            freq_table = (
                df[column]
                .astype(str)              # PENTING: hindari error encoding
                .value_counts()
                .reset_index()
            )
            freq_table.columns = [column, "Frequency"]

            st.subheader(text["freq"])
            st.dataframe(freq_table)

            # ===== SAFE BAR CHART (MATPLOTLIB) =====
            fig, ax = plt.subplots()
            ax.bar(freq_table[column], freq_table["Frequency"])
            ax.set_xlabel(column)
            ax.set_ylabel("Frequency")
            ax.set_title("Frequency Distribution")
            plt.xticks(rotation=45, ha="right")

            st.pyplot(fig)

        # =============================
        # ASSOCIATION ANALYSIS
        # =============================
        elif page == "Association Analysis":
            st.header(text["assoc"])

            col1, col2 = st.selectbox(
                text["select_cols"],
                [(c1, c2) for c1 in df.columns for c2 in df.columns if c1 != c2]
            )

            contingency = pd.crosstab(
                df[col1].astype(str),
                df[col2].astype(str)
            )

            st.subheader(text["cont"])
            st.dataframe(contingency)

            # =============================
            # Chi-Square (MANUAL, NO SCIPY)
            # =============================
            observed = contingency.values
            row_sum = observed.sum(axis=1)
            col_sum = observed.sum(axis=0)
            total = observed.sum()

            expected = np.outer(row_sum, col_sum) / total
            chi_square = ((observed - expected) ** 2 / expected).sum()

            # =============================
            # Cramer's V
            # =============================
            n = total
            r, c = observed.shape
            cramer_v = np.sqrt(chi_square / (n * (min(r, c) - 1)))

            st.metric(text["chi"], round(chi_square, 4))
            st.metric(text["cramer"], round(cramer_v, 4))

    except Exception as e:
        st.error("❌ Gagal membaca atau memproses file CSV")
        st.code(str(e))

else:
    st.warning(text["no_file"])
