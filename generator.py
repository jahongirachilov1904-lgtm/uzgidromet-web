# -*- coding: utf-8 -*-
import os
import re
import numpy as np
import pandas as pd
import geopandas as gpd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patheffects as pe
from PIL import Image

from matplotlib.patches import FancyBboxPatch, Circle, Polygon, Rectangle, PathPatch
from matplotlib.lines import Line2D
from matplotlib.path import Path
from matplotlib.colors import ListedColormap, BoundaryNorm
# =====================================================
# 1) YO'LLAR
# =====================================================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

SHP = os.path.join(BASE_DIR, "shapefile", "uzb_admbnda_adm1_2018b.shp")
TEMPLATE_BG = os.path.join(BASE_DIR, "assets", "blank_a4_template.png")
FLOOD_BG = os.path.join(BASE_DIR, "assets", "flood_mountain.png")
UZGIDRO_LOGO = os.path.join(BASE_DIR, "assets", "O'zgidromet.png")
OUT_DIR = os.path.join(BASE_DIR, "output")

os.makedirs(OUT_DIR, exist_ok=True)
# =====================================================
# 2) FONT
# =====================================================
plt.rcParams["font.family"] = "Cambria"
plt.rcParams["axes.unicode_minus"] = False
# =====================================================
# 3) XARITA NOMLARI VA SILJITISHLAR
# =====================================================
# Xaritada viloyat nomlari qisqa va qora yozuvda chiqishi uchun
region_label_names = {
    "Qoraqalpog'iston Respublikasi": "Qoraqalpog'iston",
    "Toshkent ш.": "Toshkent sh.",
    "Surxandaryo": "Surxondaryo",}
# Ayrim kichik viloyatlar bir-biriga kirishib ketmasligi uchun yozuv siljitishlari
# qiymatlar metrda berilgan, chunki xarita EPSG:3857 proyeksiyasida chiziladi
label_offsets_temp = {
    "Andijon": (45000, -15000),
    "Namangan": (25000, 27000),
    "Farg'ona": (50000, -45000),
    "Sirdaryo": (35000, -20000),
    "Toshkent ш.": (50000, 25000),
    "Toshkent": (35000, 35000),
    "Xorazm": (-20000, -45000),}
label_offsets_wind = {
    "Andijon": (45000, -12000),
    "Namangan": (25000, 25000),
    "Farg'ona": (50000, -42000),
    "Sirdaryo": (35000, -16000),
    "Toshkent ш.": (50000, 23000),
    "Toshkent": (35000, 33000),
    "Xorazm": (-20000, -42000),}
# =====================================================
# 4) HARORATNI TO'G'RI O'RTACHALASH
# =====================================================
def temp_mid(temp_text):
    text = str(temp_text)
    text = text.replace("–", "-").replace("—", "-").replace("−", "-")
    nums = re.findall(r"\d+(?:\.\d+)?", text)
    if len(nums) >= 2:
        return (float(nums[0]) + float(nums[1])) / 2.0
    elif len(nums) == 1:
        return float(nums[0])
    return np.nan
# =====================================================
# 5) HARORAT RANGLARI
# Weather map uslubi:
# -16°C dan +50°C gacha, har 2°C interval
# Legendaning uchlari uchburchak bo'lib qoladi: extend="both"
# =====================================================
# Shkala qiymatlari: -16, -14, -12, ..., +50
# Eslatma: np.arange(-16, 52, 2) oxirgi 50 ni ham oladi
temp_levels = np.arange(-16, 52, 2)
# Weather-map uslubidagi ranglar:
# sovuq = to'q ko'k/ko'k, iliq = yashil/sariq,
# issiq = to'q sariq/qizil/to'q qizil
# Ranglar soni interval soniga teng bo'lishi kerak:
# temp_levels 34 ta chegara beradi, demak 33 ta rang kerak
temp_colors = [
    "#0015BC",  # -16
    "#0038FF",  # -14
    "#0066FF",  # -12
    "#0095FF",  # -10
    "#00BFFF",  # -8
    "#4DD2FF",  # -6
    "#80E5FF",  # -4
    "#B3F0FF",  # -2

    "#C8FFC8",  # 0
    "#9EFF66",  # 2
    "#6EDB3F",  # 4
    "#33CC33",  # 6
    "#00B050",  # 8

    "#B7E000",  # 10
    "#D4E500",  # 12
    "#FFFF00",  # 14
    "#FFE000",  # 16
    "#FFC000",  # 18

    "#FFA000",  # 20
    "#FF8C00",  # 22
    "#FF7800",  # 24
    "#FF6400",  # 26
    "#FF5000",  # 28

    "#FF3C00",  # 30
    "#FF2800",  # 32
    "#FF1400",  # 34
    "#FF0000",  # 36
    "#E60000",  # 38

    "#CC0000",  # 40
    "#B30000",  # 42
    "#990000",  # 44
    "#800000",  # 46
    "#660000",  # 48
]
cmap = ListedColormap(temp_colors)
norm = BoundaryNorm(temp_levels, ncolors=cmap.N, clip=True)


def temp_to_color(value):
    if pd.isna(value):
        return "#EEEEEE"

    rgba = cmap(norm(value))
    return rgba

# =====================================================
# 6) ICONLAR
# =====================================================
def draw_sun(ax, x, y, s=1, transform=None, z=100):
    tr = transform if transform is not None else ax.transData
    r = 23000 * s if transform is None else 0.035 * s

    for a in np.linspace(0, 2 * np.pi, 18, endpoint=False):
        ax.add_line(Line2D(
            [x + np.cos(a) * r * 1.25, x + np.cos(a) * r * 1.9],
            [y + np.sin(a) * r * 1.25, y + np.sin(a) * r * 1.9],
            color="#FFC400",
            linewidth=1.7,
            transform=tr,
            zorder=z
        ))

    ax.add_patch(Circle(
        (x, y), r,
        facecolor="#FFD21A",
        edgecolor="#FF9900",
        linewidth=1.0,
        transform=tr,
        zorder=z + 1))
def draw_cloud(ax, x, y, s=1, transform=None, z=100):
    tr = transform if transform is not None else ax.transData
    r = 23000 * s if transform is None else 0.035 * s

    ax.add_patch(Circle((x - r, y), r * 0.82, facecolor="#6F8390",
                        edgecolor="none", transform=tr, zorder=z))
    ax.add_patch(Circle((x, y + r * 0.35), r, facecolor="#B7C6D0",
                        edgecolor="#6D7D86", linewidth=0.5,
                        transform=tr, zorder=z + 1))
    ax.add_patch(Circle((x + r, y), r * 0.82, facecolor="#6F8390",
                        edgecolor="none", transform=tr, zorder=z))
    ax.add_patch(Rectangle(
        (x - r * 1.75, y - r * 0.55),
        r * 3.5,
        r * 0.95,
        facecolor="#B7C6D0",
        edgecolor="none",
        transform=tr,
        zorder=z + 2))
def draw_rain(ax, x, y, s=1, transform=None, z=100):
    draw_cloud(ax, x, y, s=s, transform=transform, z=z)
    tr = transform if transform is not None else ax.transData
    r = 23000 * s if transform is None else 0.035 * s

    for dx in [-r * 0.8, 0, r * 0.8]:
        ax.add_line(Line2D(
            [x + dx, x + dx - r * 0.25],
            [y - r, y - r * 1.75],
            color="#009CFF",
            linewidth=1.7,
            transform=tr,
            zorder=z + 5))
def draw_storm(ax, x, y, s=1, transform=None, z=100):
    draw_rain(ax, x, y, s=s, transform=transform, z=z)
    tr = transform if transform is not None else ax.transData
    r = 23000 * s if transform is None else 0.035 * s

    bolt = np.array([
        [x + r * 0.10, y - r * 0.65],
        [x - r * 0.42, y - r * 1.95],
        [x + r * 0.02, y - r * 1.70],
        [x - r * 0.18, y - r * 2.70],
        [x + r * 0.75, y - r * 1.35],
        [x + r * 0.20, y - r * 1.50],
    ])

    ax.add_patch(Polygon(
        bolt,
        closed=True,
        facecolor="#FFC400",
        edgecolor="#E09800",
        linewidth=0.6,
        transform=tr,
        zorder=z + 8
    ))


def draw_wind(ax, x, y, s=1, transform=None, z=100):
    """
    Haqiqiy shamol belgisi: egri chiziqli wind-icon.
    Bu PNG emas, Pythonning o'zida chiziladi.
    """
    tr = transform if transform is not None else ax.transData
    r = 23000 * s if transform is None else 0.035 * s

    main_color = "#0B4EA2"
    light_color = "#00AEEF"

    def add_curve(points, lw=2.2, color=main_color, zadd=0):
        verts = [(x + px * r, y + py * r) for px, py in points]
        codes = [Path.MOVETO] + [Path.CURVE4] * (len(verts) - 1)
        path = Path(verts, codes)
        patch = PathPatch(
            path,
            facecolor="none",
            edgecolor=color,
            linewidth=lw,
            capstyle="round",
            joinstyle="round",
            transform=tr,
            zorder=z + zadd
        )
        ax.add_patch(patch)

    # Ustki egri shamol chizig'i
    add_curve([
        (-1.70,  0.45),
        (-0.95,  0.72),
        (-0.10,  0.70),
        ( 0.55,  0.45),
        ( 1.05,  0.25),
        ( 0.95, -0.10),
        ( 0.50,  0.02),
    ], lw=2.2, color=main_color, zadd=2)

    # O'rta asosiy shamol chizig'i
    add_curve([
        (-1.85,  0.05),
        (-0.90,  0.18),
        ( 0.05,  0.18),
        ( 0.95,  0.05),
        ( 1.45, -0.03),
        ( 1.45, -0.38),
        ( 0.95, -0.28),
    ], lw=2.6, color=main_color, zadd=3)

    # Pastki egri shamol chizig'i
    add_curve([
        (-1.45, -0.38),
        (-0.75, -0.55),
        ( 0.05, -0.55),
        ( 0.70, -0.38),
        ( 1.05, -0.25),
        ( 0.95,  0.02),
        ( 0.62, -0.05),
    ], lw=2.0, color=main_color, zadd=2)

    # Ikonka ichiga engil havorang urg'u chiziqlari
    add_curve([
        (-1.55, -0.10),
        (-0.80, -0.02),
        (-0.05, -0.02),
        ( 0.65, -0.10),
    ], lw=1.5, color=light_color, zadd=4)



def draw_wind_arrow(ax, x, y, s=1, direction="E", transform=None, z=100):
    """
    Shamol yo'nalishini strelka bilan ko'rsatadi.
    direction: N, NE, E, SE, S, SW, W, NW
    """
    tr = transform if transform is not None else ax.transData
    r = 23000 * s if transform is None else 0.035 * s

    angles = {
        "E": 0, "NE": 45, "N": 90, "NW": 135,
        "W": 180, "SW": 225, "S": 270, "SE": 315
    }

    angle = np.deg2rad(angles.get(str(direction).upper(), 0))
    dx = np.cos(angle) * r * 1.8
    dy = np.sin(angle) * r * 1.8

    ax.annotate(
        "",
        xy=(x + dx, y + dy),
        xytext=(x - dx, y - dy),
        arrowprops=dict(
            arrowstyle="-|>",
            lw=2.0,
            color="#0B4EA2",
            mutation_scale=10
        ),
        transform=tr,
        zorder=z
    )


def put_icon(ax, kind, x, y, s=1, transform=None, z=100):
    if kind == "sun":
        draw_sun(ax, x, y, s=s, transform=transform, z=z)
    elif kind == "rain":
        draw_rain(ax, x, y, s=s, transform=transform, z=z)
    elif kind == "storm":
        draw_storm(ax, x, y, s=s, transform=transform, z=z)
    elif kind == "wind":
        draw_wind(ax, x, y, s=s, transform=transform, z=z)
    else:
        draw_cloud(ax, x, y, s=s, transform=transform, z=z)

def create_infographic(
    weather,
    side_rows,
    forecast_days,
    warning_days,
    subtitle,
    warning_title="SEL-SUV TOSHQIN",
    warning_text="HODISALARI YUZAGA\nKELISHI MUMKIN!",
    dpi=500
):
    """
    Streamlit app.py dan kelgan ma'lumotlar asosida Uzgidromet infografika PNG yaratadi.
    """
    # =====================================================
    # 7) SHP O'QISH
    # =====================================================
    if not os.path.exists(SHP):
        raise FileNotFoundError(f"SHP topilmadi: {SHP}")

    gdf = gpd.read_file(SHP)
    gdf["info"] = gdf["ADM1_UZ"].map(weather)

    gdf["map_temp"] = gdf["info"].apply(
        lambda d: temp_mid(d["temp"]) if isinstance(d, dict) else np.nan
    )

    gdf["fill_color"] = gdf["map_temp"].apply(temp_to_color)

    print("Mos tushmagan hududlar:")
    print(gdf.loc[gdf["info"].isna(), ["ADM1_UZ", "ADM1_EN", "ADM1_RU"]])

    print("\nXaritaga rang berishda ishlatilgan qiymatlar:")
    for _, r in gdf.dropna(subset=["map_temp"]).iterrows():
        print(r["ADM1_UZ"], r["info"]["temp"], "=>", r["map_temp"], r["fill_color"])

    gdf = gdf.to_crs(epsg=3857)
    gdf["point"] = gdf.geometry.representative_point()

    minx, miny, maxx, maxy = gdf.total_bounds

    # =====================================================
    # 8) TEMPLATE
    # =====================================================
    if not os.path.exists(TEMPLATE_BG):
        raise FileNotFoundError(f"Template topilmadi: {TEMPLATE_BG}")

    template = Image.open(TEMPLATE_BG).convert("RGB")
    tw, th = template.size

    fig_w = 11.69
    fig_h = fig_w / (tw / th)

    fig = plt.figure(figsize=(fig_w, fig_h), dpi=dpi)
    fig.patch.set_facecolor("white")

    bg_ax = fig.add_axes([0, 0, 1, 1], zorder=0)
    bg_ax.imshow(template, extent=[0, 1, 0, 1], aspect="auto")
    bg_ax.axis("off")

    # =====================================================
    # 9) HEADER
    # =====================================================
    if os.path.exists(UZGIDRO_LOGO):
        uzg_ax = fig.add_axes([0.030, 0.890, 0.085, 0.085], zorder=25)
        uzg_ax.imshow(Image.open(UZGIDRO_LOGO).convert("RGBA"))
        uzg_ax.axis("off")

    fig.text(
        0.50,
        0.950,
        f"{forecast_days} OB-HAVO PROGNOZI",
        ha="center",
        fontsize=24,
        fontweight="bold",
        color="white",
        zorder=30
    )

    fig.text(
        0.50,
        0.920,
        subtitle,
        ha="center",
        fontsize=11,
        color="white",
        zorder=30)
    # =====================================================
    # 10) BLOKLAR JOYLASHUVI
    # =====================================================
    ax1_pos = [0.030, 0.535, 0.465, 0.345]
    ax2_pos = [0.505, 0.535, 0.465, 0.345]
    ax3_pos = [0.040, 0.165, 0.455, 0.320]
    ax4_pos = [0.515, 0.180, 0.450, 0.305]

    ax1 = fig.add_axes(ax1_pos, zorder=10)
    ax2 = fig.add_axes(ax2_pos, zorder=10)
    ax3 = fig.add_axes(ax3_pos, zorder=10)
    ax4 = fig.add_axes(ax4_pos, zorder=10)

    for ax in [ax1, ax2, ax3, ax4]:
        ax.axis("off")


    def block_title(ax, title, x=0.50, y=0.920, fontsize=14):
        ax.text(
            x,
            y,
            title,
            transform=ax.transAxes,
            ha="center",
            va="center",
            fontsize=fontsize,
            color="#073B8E",
            fontweight="bold",
            zorder=31
        )



    def get_region_label(row):
        name = str(row["ADM1_UZ"])
        return region_label_names.get(name, name)


    def draw_region_names(ax, offsets=None, fontsize=4.9):
        """Viloyat nomlarini xaritada qora, kichik yozuvda chiqaradi."""
        offsets = offsets or {}

        for _, row in gdf.iterrows():
            info = row["info"]
            if not isinstance(info, dict):
                continue

            name = str(row["ADM1_UZ"])
            x, y = row["point"].x, row["point"].y
            dx, dy = offsets.get(name, (0, 0))

            ax.text(
                x + dx,
                y + dy+50000,
                get_region_label(row),
                ha="center",
                va="center",
                fontsize=fontsize,
                fontweight="bold",
                color="black",
                zorder=160)
    # =====================================================
    # 11) 1-BLOK: HARORAT XARITASI
    # =====================================================
    block_title(ax1, "HARORAT XARITASI", x=0.52, y=0.915)
    gdf.plot(
        ax=ax1,
        color=gdf["fill_color"],
        edgecolor="white",
        linewidth=0.8)
    gdf.boundary.plot(
        ax=ax1,
        color="#0B4EA2",
        linewidth=0.5)
    for _, row in gdf.iterrows():
        info = row["info"]
        if not isinstance(info, dict):
            continue
        x, y = row["point"].x, row["point"].y
        scale = 0.42
        if row["ADM1_UZ"] in ["Andijon", "Namangan", "Farg'ona", "Sirdaryo", "Toshkent ш."]:
            scale = 0.32
        put_icon(ax1, info["kind"], x, y + 17000, s=scale)
        ax1.text(
            x,
            y - 35000,
            info["temp"],
            ha="center",
            va="center",
            fontsize=7.0,
            fontweight="normal",
            color="#0B3D91",
            zorder=130
        )
    # Viloyat nomlari: qora va kichik yozuvda
    draw_region_names(ax1, offsets=label_offsets_temp, fontsize=4.2)

    ax1.set_xlim(minx - 40000, maxx + 40000)
    ax1.set_ylim(miny - 50000, maxy + 50000)

    # COLORBAR
    sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
    sm.set_array([])

    # Legendani xarita tagida uzunroq qilish
    cbar_x = ax1_pos[0] + 0.055
    cbar_y = ax1_pos[1] - 0.002
    cbar_w = ax1_pos[2] * 0.86
    cbar_h = 0.012

    cax = fig.add_axes([cbar_x, cbar_y, cbar_w, cbar_h], zorder=50)

    cbar = fig.colorbar(
        sm,
        cax=cax,
        orientation="horizontal",
        extend="both",              # uchlari uchburchak bo'lib turadi
        boundaries=temp_levels,
        ticks=temp_levels,           # -16 dan +50 gacha har 2°C
        spacing="proportional"
    )

    cbar.outline.set_linewidth(0.8)
    cbar.ax.tick_params(labelsize=3.5, pad=1)
    cbar.set_label("Kunduzgi harorat, °C", fontsize=6, labelpad=1)

    # =====================================================
    # 12) 2-BLOK: SHAMOL VA YOG'INGARCHILIK
    # =====================================================
    block_title(ax2, "SHAMOL VA YOG'INGARCHILIK", x=0.60, y=0.915)

    # Asosiy xarita foni
    gdf.plot(
        ax=ax2,
        color="#EEF7E9",
        edgecolor="#9AB7A7",
        linewidth=0.7
    )

    # Yog'ingarchilik bo'ladigan hududlar
    rain_regions = [
        region for region, info in weather.items()
        if isinstance(info, dict) and info.get("kind") in ["rain", "storm"]
    ]

    rain_gdf = gdf[gdf["ADM1_UZ"].isin(rain_regions)]

    rain_gdf.plot(
        ax=ax2,
        color="#9BD8FF",
        alpha=0.75,
        edgecolor="#4A9BC7",
        linewidth=0.7
    )

    # Har bir viloyat uchun shamol yo'nalishi va shamol tezligi
    for _, row in gdf.iterrows():
        info = row["info"]
        if not isinstance(info, dict):
            continue

        name = str(row["ADM1_UZ"])
        x, y = row["point"].x, row["point"].y

        wind_speed = info.get("wind", "7-12 m/s")
        wind_dir = info.get("wind_dir", "E")

        dx, dy = label_offsets_wind.get(name, (0, 0))

        # Shamol ikonkasi
        draw_wind(
            ax2,
            x + dx,
            y + dy + 15000,
            s=0.42,
            z=120
        )

        # Shamol tezligi yozuvi
        ax2.text(
            x + dx,
            y + dy - 18000,
            wind_speed,
            ha="center",
            va="center",
            fontsize=5.5,
            fontweight="normal",
            color="#0B3D91",
            path_effects=[pe.withStroke(linewidth=0.7, foreground="white")],
            zorder=130
        )

    # Yog'ingarchilik ikonkalari
    for _, row in rain_gdf.iterrows():
        x, y = row["point"].x, row["point"].y

        info = row["info"]
        kind = info.get("kind", "rain") if isinstance(info, dict) else "rain"

        put_icon(ax2, kind, x, y - 42000, s=0.25)

    # Viloyat nomlari
    draw_region_names(ax2, offsets=label_offsets_wind, fontsize=4.2)


    ax2.set_xlim(minx - 40000, maxx + 40000)
    ax2.set_ylim(miny - 50000, maxy + 50000)

    # =====================================================
    # 13) 3-BLOK
    # =====================================================
    block_title(ax3, "MUHIM OGOHLANTIRISH", y=0.935)

    ax3.add_patch(FancyBboxPatch(
        (0.00, 0.02), 1.00, 0.84,
        transform=ax3.transAxes,
        boxstyle="round,pad=0.00,rounding_size=0.012",
        facecolor="white",
        edgecolor="#D7E3F0",
        linewidth=1.0,
        zorder=1
    ))

    left_x0 = 0.00
    left_x1 = 0.50
    right_x0 = 0.50
    right_x1 = 1.00

    ax3.add_patch(Rectangle(
        (left_x0, 0.18),
        left_x1 - left_x0,
        0.68,
        transform=ax3.transAxes,
        facecolor="white",
        edgecolor="none",
        zorder=2
    ))

    if os.path.exists(FLOOD_BG):
        img = Image.open(FLOOD_BG).convert("RGB")
        ax3.imshow(
            img,
            extent=[right_x0, right_x1, 0.18, 0.86],
            transform=ax3.transAxes,
            aspect="auto",
            zorder=1
        )
    else:
        ax3.add_patch(Rectangle(
            (right_x0, 0.18),
            right_x1 - right_x0,
            0.68,
            transform=ax3.transAxes,
            facecolor="#DDEEFF",
            edgecolor="none",
            zorder=1
        ))

    ax3.add_patch(Rectangle(
        (0, 0.02),
        1,
        0.16,
        transform=ax3.transAxes,
        facecolor="#D40000",
        edgecolor="none",
        zorder=5
    ))
    tri = Polygon(
        [[0.015, 0.58], [0.095, 0.58], [0.055, 0.75]],
        closed=True,
        transform=ax3.transAxes,
        facecolor="white",
        edgecolor="#D40000",
        linewidth=2.7,
        zorder=10
    )

    ax3.add_patch(tri)

    ax3.text(
        0.055,
        0.645,
        "!",
        transform=ax3.transAxes,
        ha="center",
        va="center",
        fontsize=21,
        color="#D40000",
        fontweight="bold",
        zorder=11
    )
    ax3.text(
        0.190,
        0.705,
        f"{warning_days} KUNLARI",
        transform=ax3.transAxes,
        fontsize=7.2,
        color="white",
        fontweight="bold",
        ha="center",
        va="center",
        bbox=dict(
            boxstyle="round,pad=0.22",
            facecolor="#D40000",
            edgecolor="none"
        ),
        zorder=12
    )

    ax3.text(
        0.105,
        0.590,
        warning_title,
        transform=ax3.transAxes,
        fontsize=14.0,
        color="#C40000",
        fontweight="bold",
        ha="left",
        va="center",
        zorder=12
    )

    ax3.text(
        0.105,
        0.495,
        warning_text,
        transform=ax3.transAxes,
        fontsize=8.3,
        color="#111111",
        fontweight="bold",
        ha="left",
        va="center",
        linespacing=1.05,
        zorder=12
    )

    warning_lines = [
        ("Tog' oldi va tog'li hududlar", "cloud"),
        ("Kuchli yomg'irlar", "rain"),
        ("Sel-suv toshqin xavfi", "storm"),
    ]

    start_y = 0.350
    row_gap = 0.070
    icon_x = 0.075
    text_x = 0.135

    for i, (text, kind) in enumerate(warning_lines):
        yy = start_y - i * row_gap

        put_icon(ax3, kind, icon_x, yy, s=0.18,
                 transform=ax3.transAxes, z=90)

        ax3.text(
            text_x,
            yy,
            text,
            transform=ax3.transAxes,
            fontsize=7.6,
            color="#173B6D",
            fontweight="bold",
            ha="left",
            va="center",
            zorder=12
        )

    ax3.text(
        0.5,
        0.10,
        "EHTIYOT BO'LING, XAVFSIZLIK CHORALARIGA RIOYA QILING!",
        transform=ax3.transAxes,
        ha="center",
        va="center",
        fontsize=9.5,
        color="white",
        fontweight="bold",
        zorder=12
    )

    # =====================================================
    # 14) 4-BLOK
    # =====================================================
    block_title(ax4, "VILOYATLAR BO'YICHA PROGNOZ")

    ax4.add_patch(FancyBboxPatch(
        (0.02, 0.05), 0.96, 0.80,
        transform=ax4.transAxes,
        boxstyle="round,pad=0.01,rounding_size=0.02",
        facecolor="white",
        edgecolor="#CFE0EE",
        linewidth=1.1,
        zorder=1
    ))

    cols = [0.05, 0.52, 0.70, 0.86]

    ax4.text(cols[0], 0.80, "Hudud",
             transform=ax4.transAxes,
             fontsize=8,
             fontweight="bold",
             color="#173B6D")
    ax4.text(cols[1], 0.80, "Kechasi",
             transform=ax4.transAxes,
             fontsize=8,
             fontweight="bold",
             color="#173B6D")

    ax4.text(cols[2], 0.80, "Kunduzi",
             transform=ax4.transAxes,
             fontsize=8,
             fontweight="bold",
             color="#173B6D")
    ax4.text(cols[3], 0.80, "Holat",
             transform=ax4.transAxes,
             fontsize=8,
             fontweight="bold",
             color="#173B6D")
    y0 = 0.72
    row_h = 0.105
    for i, (region, night, day, kind) in enumerate(side_rows):
        y = y0 - i * row_h

        if i % 2 == 0:
            ax4.add_patch(Rectangle(
                (0.035, y - 0.035),
                0.93,
                row_h,
                transform=ax4.transAxes,
                facecolor="#F6FBFF",
                edgecolor="none",
                zorder=2
            ))

        ax4.text(cols[0], y, region,
                 transform=ax4.transAxes,
                 fontsize=7.2,
                 color="#173B6D",
                 fontweight="bold",
                 va="center",
                 zorder=3)
        ax4.text(cols[1], y, night,
                 transform=ax4.transAxes,
                 fontsize=8,
                 color="#173B6D",
                 va="center",
                 zorder=3)
        ax4.text(cols[2], y, day,
                 transform=ax4.transAxes,
                 fontsize=8,
                 color="#C22A00",
                 fontweight="bold",
                 va="center",
                 zorder=3)
        put_icon(ax4, kind, cols[3] + 0.045, y,
                 s=0.25, transform=ax4.transAxes, z=90)
    # =====================================================
    # 15) SAQLASH
    # =====================================================
    safe_days = re.sub(r"[^A-Za-z0-9А-Яа-яЁёЎўҚқҒғҲҳ_\-]+", "_", str(forecast_days))
    out_path = os.path.join(OUT_DIR, f"uzgidromet_4_blok_infografika_{safe_days}.png")

    plt.savefig(
        out_path,
        dpi=dpi,
        bbox_inches="tight",
        pad_inches=0,
        facecolor=fig.get_facecolor())
    plt.close(fig)
    return out_path
