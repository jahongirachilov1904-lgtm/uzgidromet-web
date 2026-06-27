# -*- coding: utf-8 -*-
import os
import streamlit as st
import pandas as pd

from generator import create_infographic

st.set_page_config(
    page_title="Uzgidromet Web",
    page_icon="🌦",
    layout="wide"
)

st.title("🌦 Uzgidromet ob-havo infografika web dasturi")
st.info("Harorat, hodisa, shamol va prognoz kunlarini qo‘lda kiritasiz. Keyin PNG infografika yaratiladi.")

# ===============================
# 1. UMUMIY MA'LUMOTLAR
# ===============================
st.subheader("📅 Prognoz ma'lumotlari")

col1, col2 = st.columns(2)

with col1:
    forecast_days = st.text_input("Prognoz kunlari", "22-27 IYUN")

with col2:
    warning_days = st.text_input("Ogohlantirish kunlari", "16-19 IYUN")

subtitle = st.text_input(
    "Sarlavha ostidagi matn",
    "O'zbekiston hududlari bo'yicha 5 kunlik prognoz"
)

warning_title = st.text_input(
    "Ogohlantirish nomi",
    "SEL-SUV TOSHQIN"
)

warning_text = st.text_area(
    "Ogohlantirish matni",
    "HODISALARI YUZAGA\nKELISHI MUMKIN!"
)

# ===============================
# 2. VILOYATLAR
# ===============================
regions = [
    "Andijon",
    "Buxoro",
    "Jizzax",
    "Farg'ona",
    "Qashqadaryo",
    "Xorazm",
    "Namangan",
    "Navoiy",
    "Qoraqalpog'iston Respublikasi",
    "Samarqand",
    "Surxandaryo",
    "Sirdaryo",
    "Toshkent",
    "Toshkent ш."
]

default_values = {
    "Andijon": {"temp": "31-36°", "night": "18-23°", "kind": "Momaqaldiroq", "wind": "13-18 m/s", "wind_dir": "NE"},
    "Buxoro": {"temp": "35-40°", "night": "20-25°", "kind": "Quyoshli", "wind": "7-12 m/s", "wind_dir": "E"},
    "Jizzax": {"temp": "31-36°", "night": "20-25°", "kind": "Yomg'ir", "wind": "7-12 m/s", "wind_dir": "E"},
    "Farg'ona": {"temp": "31-36°", "night": "18-23°", "kind": "Momaqaldiroq", "wind": "13-18 m/s", "wind_dir": "NE"},
    "Qashqadaryo": {"temp": "35-40°", "night": "22-27°", "kind": "Quyoshli", "wind": "7-12 m/s", "wind_dir": "SE"},
    "Xorazm": {"temp": "37-42°", "night": "20-25°", "kind": "Quyoshli", "wind": "7-12 m/s", "wind_dir": "E"},
    "Namangan": {"temp": "31-36°", "night": "18-23°", "kind": "Momaqaldiroq", "wind": "13-18 m/s", "wind_dir": "NE"},
    "Navoiy": {"temp": "35-40°", "night": "20-25°", "kind": "Quyoshli", "wind": "7-12 m/s", "wind_dir": "E"},
    "Qoraqalpog'iston Respublikasi": {"temp": "37-42°", "night": "20-25°", "kind": "Quyoshli", "wind": "7-12 m/s", "wind_dir": "E"},
    "Samarqand": {"temp": "31-36°", "night": "20-25°", "kind": "Yomg'ir", "wind": "7-12 m/s", "wind_dir": "E"},
    "Surxandaryo": {"temp": "35-40°", "night": "22-27°", "kind": "Quyoshli", "wind": "7-12 m/s", "wind_dir": "SE"},
    "Sirdaryo": {"temp": "31-36°", "night": "20-25°", "kind": "Yomg'ir", "wind": "13-18 m/s", "wind_dir": "E"},
    "Toshkent": {"temp": "31-36°", "night": "20-25°", "kind": "Yomg'ir", "wind": "13-18 m/s", "wind_dir": "NE"},
    "Toshkent ш.": {"temp": "31-36°", "night": "20-25°", "kind": "Momaqaldiroq", "wind": "13-18 m/s", "wind_dir": "NE"},
}

kind_options = {
    "Quyoshli": "sun",
    "Yomg'ir": "rain",
    "Momaqaldiroq": "storm",
    "Bulutli": "cloud"
}

wind_dirs = ["E", "NE", "N", "NW", "W", "SW", "S", "SE"]

st.subheader("🌡 Viloyatlar bo‘yicha ob-havo ma'lumotlari")

weather = {}

for region in regions:
    d = default_values[region]

    with st.expander(f"📍 {region}", expanded=False):
        c1, c2, c3, c4, c5 = st.columns(5)

        with c1:
            night = st.text_input(
                "Kechasi",
                d["night"],
                key=f"{region}_night"
            )

        with c2:
            temp = st.text_input(
                "Kunduzi",
                d["temp"],
                key=f"{region}_temp"
            )

        with c3:
            kind_label = st.selectbox(
                "Hodisa",
                list(kind_options.keys()),
                index=list(kind_options.keys()).index(d["kind"]),
                key=f"{region}_kind"
            )

        with c4:
            wind = st.text_input(
                "Shamol",
                d["wind"],
                key=f"{region}_wind"
            )

        with c5:
            wind_dir = st.selectbox(
                "Yo‘nalish",
                wind_dirs,
                index=wind_dirs.index(d["wind_dir"]),
                key=f"{region}_wind_dir"
            )

        weather[region] = {
            "temp": temp,
            "night": night,
            "kind": kind_options[kind_label],
            "wind": wind,
            "wind_dir": wind_dir
        }

# ===============================
# 3. JADVAL KO'RINISHIDA TEKSHIRISH
# ===============================
st.subheader("📋 Kiritilgan ma'lumotlar")

df = pd.DataFrame([
    {
        "Viloyat": region,
        "Kechasi": data["night"],
        "Kunduzi": data["temp"],
        "Hodisa": data["kind"],
        "Shamol": data["wind"],
        "Yo'nalish": data["wind_dir"]
    }
    for region, data in weather.items()
])

st.dataframe(df, width="stretch")

# ===============================
# 4. 4-BLOK UCHUN SIDE_ROWS
# ===============================
side_rows = [
    [
        "Toshkent shahri",
        weather["Toshkent ш."]["night"],
        weather["Toshkent ш."]["temp"],
        weather["Toshkent ш."]["kind"]
    ],
    [
        "Qoraqalpog'iston R., Xorazm",
        weather["Qoraqalpog'iston Respublikasi"]["night"],
        weather["Qoraqalpog'iston Respublikasi"]["temp"],
        weather["Qoraqalpog'iston Respublikasi"]["kind"]
    ],
    [
        "Buxoro, Navoiy",
        weather["Buxoro"]["night"],
        weather["Buxoro"]["temp"],
        weather["Buxoro"]["kind"]
    ],
    [
        "Toshkent, Samarqand,\nJizzax, Sirdaryo",
        weather["Toshkent"]["night"],
        weather["Toshkent"]["temp"],
        weather["Toshkent"]["kind"]
    ],
    [
        "Qashqadaryo,\nSurxondaryo",
        weather["Qashqadaryo"]["night"],
        weather["Qashqadaryo"]["temp"],
        weather["Qashqadaryo"]["kind"]
    ],
    [
        "Andijon, Namangan,\nFarg'ona",
        weather["Andijon"]["night"],
        weather["Andijon"]["temp"],
        weather["Andijon"]["kind"]
    ],
]

# ===============================
# 5. INFOGRAFIKA YARATISH
# ===============================
st.subheader("🖼 Infografika yaratish")

if st.button("✅ Infografika yaratish", type="primary"):
    try:
        out_path = create_infographic(
            weather=weather,
            side_rows=side_rows,
            forecast_days=forecast_days,
            warning_days=warning_days,
            subtitle=subtitle,
            warning_title=warning_title,
            warning_text=warning_text,
            dpi=500
        )

        st.success("Infografika tayyor!")

        st.image(out_path, width="stretch")

        with open(out_path, "rb") as f:
            st.download_button(
                label="📥 PNG faylni yuklab olish",
                data=f,
                file_name=os.path.basename(out_path),
                mime="image/png"
            )

    except Exception as e:
        st.error("Xatolik yuz berdi.")
        st.exception(e)