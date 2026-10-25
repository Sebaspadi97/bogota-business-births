"""
Radiografía del emprendimiento en Bogotá · SP Lab
Fuente: Dinámica Empresarial Bogotá (Datos Abiertos Bogotá), corte marzo 2026, licencia CC BY-SA 4.0.
Uso: python analisis.py <archivo_dbf_o_xlsx> <carpeta_salida>
El archivo publicado con extensión .xlsx es en realidad una tabla dBase (DBF); se lee con read_dbf.
"""
import sys, os
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager as fm

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from read_dbf import read_dbf

SRC, OUT = sys.argv[1], sys.argv[2]
os.makedirs(os.path.join(OUT, "tablas"), exist_ok=True)
os.makedirs(os.path.join(OUT, "graficos"), exist_ok=True)

# ---------- 1. Lectura y limpieza ----------
df, fields, n, _ = read_dbf(SRC, "utf-8")
num = {"Periodo": "anio", "Mes": "mes", "empresasvi": "vigentes", "empresasCr": "creadas", "EmpresasCa": "canceladas"}
for c in num:
    df[c] = pd.to_numeric(df[c], errors="coerce").fillna(0).astype(int)
df = df.rename(columns={**num, "LOCNOMBRE": "localidad", "TamanioEmp": "tamano", "RamaActivi": "rama",
                        "CodigoCIIU": "ciiu", "Organizaci": "organizacion", "SexoRL": "sexo_rl"})
df["ciiu"] = df["ciiu"].str.zfill(4)  # el archivo pierde los ceros a la izquierda (0010 -> 10)
df["localidad"] = df["localidad"].replace({"Usaquen": "Usaquén", "Engativa": "Engativá", "Fontibon": "Fontibón",
                                           "Ciudad Bolivar": "Ciudad Bolívar", "San Cristobal": "San Cristóbal",
                                           "Los Martires": "Los Mártires", "Candelaria": "La Candelaria",
                                           "Sin Localidad": "Sin localidad"})
df = df[["anio", "mes", "localidad", "tamano", "rama", "ciiu", "organizacion", "sexo_rl", "vigentes", "creadas", "canceladas"]]

CIIU = {  # Descripciones oficiales, Resolución DIAN 0139 de 2012 (CIIU Rev. 4 A.C.)
    "5630": "Expendio de bebidas alcohólicas para consumo en el establecimiento (bares)",
    "9602": "Peluquería y otros tratamientos de belleza",
    "5611": "Expendio a la mesa de comidas preparadas (restaurantes)",
    "4711": "Comercio al por menor no especializado, principalmente alimentos (tiendas)",
    "0010": "Asalariados (clasificación DIAN, no CIIU)",
    "8299": "Otras actividades de apoyo a las empresas n.c.p.",
    "7020": "Consultoría de gestión",
    "4771": "Comercio al por menor de prendas de vestir",
    "1410": "Confección de prendas de vestir",
    "4773": "Comercio al por menor de farmacéuticos y cosméticos",
    "6810": "Actividades inmobiliarias con bienes propios o arrendados",
    "6201": "Desarrollo de sistemas informáticos",
    "4791": "Comercio al por menor por internet",
    "7310": "Publicidad",
    "4723": "Comercio al por menor de carnes y pescados",
    "4520": "Mantenimiento y reparación de vehículos",
    "5619": "Otros tipos de expendio de comidas preparadas",
    "1081": "Elaboración de productos de panadería",
    "4774": "Comercio al por menor de otros productos nuevos",
    "6910": "Actividades jurídicas",
    "4721": "Comercio al por menor de productos agrícolas",
    "4923": "Transporte de carga por carretera",
    "5613": "Expendio de comidas preparadas en cafeterías",
}
df["ciiu_desc"] = df["ciiu"].map(CIIU)
df.to_csv(os.path.join(OUT, "tablas", "00_datos_limpios.csv"), index=False, encoding="utf-8-sig")

# ---------- 2. Calidad de datos ----------
calidad = pd.DataFrame([
    ("Registros", len(df)),
    ("Cortes (año-mes) distintos", df.groupby(["anio", "mes"]).ngroups),
    ("Corte", f"{df.anio.iat[0]}-{df.mes.iat[0]:02d}"),
    ("Empresas vigentes", int(df.vigentes.sum())),
    ("Empresas creadas año corrido", int(df.creadas.sum())),
    ("Empresas canceladas año corrido", int(df.canceladas.sum())),
    ("Localidades con nombre (sin 'Sin localidad')", df.loc[df.localidad != "Sin localidad", "localidad"].nunique()),
    ("Vigentes sin localidad", int(df.loc[df.localidad == "Sin localidad", "vigentes"].sum())),
    ("Códigos CIIU distintos", df.ciiu.nunique()),
    ("Registros con sexo del RL indeterminado", int((df.sexo_rl == "Indeterminado").sum())),
], columns=["indicador", "valor"])

# ---------- 3. Tablas ----------
def resumen(by):
    t = df.groupby(by)[["vigentes", "creadas"]].sum()
    t["tasa_creacion_pct"] = t.creadas / t.vigentes * 100
    t["participacion_creadas_pct"] = t.creadas / t.creadas.sum() * 100
    return t.sort_values("creadas", ascending=False).round(2)

def mujeres(by):
    d = df[df.sexo_rl.isin(["Femenino", "Masculino"])]
    p = d.pivot_table(index=by, columns="sexo_rl", values=["vigentes", "creadas"], aggfunc="sum")
    r = pd.DataFrame({
        "pct_mujeres_vigentes": p[("vigentes", "Femenino")] / (p[("vigentes", "Femenino")] + p[("vigentes", "Masculino")]) * 100,
        "pct_mujeres_creadas": p[("creadas", "Femenino")] / (p[("creadas", "Femenino")] + p[("creadas", "Masculino")]) * 100,
        "creadas_con_sexo": p[("creadas", "Femenino")] + p[("creadas", "Masculino")],
    })
    r["diferencia_pp"] = r.pct_mujeres_creadas - r.pct_mujeres_vigentes
    return r.sort_values("pct_mujeres_creadas", ascending=False).round(1)

T = {
    "01_localidad": resumen("localidad").sort_values("tasa_creacion_pct", ascending=False),
    "02_rama": resumen("rama"),
    "03_tamano": resumen("tamano"),
    "04_organizacion": resumen("organizacion"),
    "05_actividad_top25": resumen(["ciiu"]).head(25).join(pd.Series(CIIU, name="descripcion")),
    "06_mujeres_localidad": mujeres("localidad"),
    "07_mujeres_rama": mujeres("rama"),
    "08_bares_localidad": df[df.ciiu == "5630"].groupby("localidad")[["vigentes", "creadas"]].sum().sort_values("creadas", ascending=False),
    "09_cafeterias_localidad": df[df.ciiu == "5613"].groupby("localidad")[["vigentes", "creadas"]].sum().sort_values("vigentes", ascending=False),
    "10_localidad_x_rama_tasa": (lambda p: (p["creadas"] / p["vigentes"] * 100).round(2))(
        df.groupby(["localidad", "rama"])[["vigentes", "creadas"]].sum().unstack()),
}
tot = df[["vigentes", "creadas"]].sum()
dias = 90  # 1 ene - 31 mar 2026
claves = pd.DataFrame([
    ("Empresas vigentes (mar 2026)", tot.vigentes),
    ("Empresas creadas ene-mar 2026", tot.creadas),
    ("Tasa de creación trimestral Bogotá (%)", round(tot.creadas / tot.vigentes * 100, 2)),
    ("Empresas creadas por día", round(tot.creadas / dias, 1)),
    ("Bares creados ene-mar 2026 (CIIU 5630)", int(df.loc[df.ciiu == "5630", "creadas"].sum())),
    ("Bares creados por día", round(df.loc[df.ciiu == "5630", "creadas"].sum() / dias, 1)),
    ("% mujeres RL en empresas creadas (sexo conocido)", round(T["07_mujeres_rama"].eval("pct_mujeres_creadas*creadas_con_sexo").sum() / T["07_mujeres_rama"].creadas_con_sexo.sum(), 1)),
], columns=["indicador", "valor"])
d = df[df.sexo_rl.isin(["Femenino", "Masculino"])]
claves.loc[len(claves)] = ("% mujeres RL en empresas vigentes (sexo conocido)",
                           round(d.loc[d.sexo_rl == "Femenino", "vigentes"].sum() / d.vigentes.sum() * 100, 1))

with pd.ExcelWriter(os.path.join(OUT, "tablas", "resultados_dinamica_empresarial_bogota.xlsx")) as xw:
    claves.to_excel(xw, "00_claves", index=False)
    calidad.to_excel(xw, "00_calidad", index=False)
    for k, v in T.items():
        v.to_excel(xw, k[:31])

# ---------- 4. Gráficos (paleta SP Lab) ----------
for f in fm.findSystemFonts():
    if "Inter" in f:
        fm.fontManager.addfont(f)
plt.rcParams.update({"font.family": "Inter", "font.size": 10.5, "axes.spines.top": False, "axes.spines.right": False,
                     "axes.spines.left": False, "axes.spines.bottom": False, "figure.facecolor": "#F8FAF7", "axes.facecolor": "#F8FAF7"})
VERDE, PROF, GRIS, CLARO, CARBON, DORADO, MENTA = "#245B45", "#183D32", "#66736C", "#E7EBE7", "#202824", "#D6A64F", "#8CCFAD"
fmt = lambda v, d=1: f"{v:,.{d}f}".replace(",", "X").replace(".", ",").replace("X", ".")

def titulo(fig, t, s):
    fig.text(0.02, 0.965, t, fontsize=15, fontweight="bold", color=CARBON, va="top")
    fig.text(0.02, 0.905, s, fontsize=10.5, color=GRIS, va="top")

def pie(fig):
    fig.text(0.02, 0.02, "Fuente: Datos Abiertos Bogotá, Dinámica Empresarial (corte mar 2026), CC BY-SA 4.0 · Análisis: Sebas Padilla Lab",
             fontsize=8, color=GRIS)

# 4.1 Tasa de creación por localidad
t = T["01_localidad"].drop("Sin localidad").sort_values("tasa_creacion_pct")
media = tot.creadas / tot.vigentes * 100
fig, ax = plt.subplots(figsize=(9, 7.2)); fig.subplots_adjust(left=0.2, right=0.93, top=0.84, bottom=0.07)
top3 = t.tasa_creacion_pct.nlargest(3).index
ax.barh(t.index, t.tasa_creacion_pct, color=[VERDE if i in top3 else "#B9C2BC" for i in t.index], height=0.68)
for i, (loc, v) in enumerate(t.tasa_creacion_pct.items()):
    ax.text(v + 0.08, i, fmt(v), va="center", fontsize=9.5, color=CARBON, fontweight="bold" if loc in top3 else "normal",
            bbox=dict(facecolor="#F8FAF7", edgecolor="none", pad=1), zorder=5)
ax.axvline(media, color=DORADO, lw=1.6, ls="--", zorder=1)
ax.text(media + 0.08, len(t) - 0.4, f"Bogotá: {fmt(media)} %", color="#9A7425", fontsize=9.5, fontweight="bold")
ax.set_xticks([]); ax.tick_params(axis="y", length=0, colors=CARBON)
titulo(fig, "En el sur de Bogotá nacen más empresas por cada cien que ya existen",
       "Empresas creadas entre enero y marzo de 2026 por cada 100 vigentes, según localidad")
pie(fig); fig.savefig(os.path.join(OUT, "graficos", "01_tasa_creacion_localidad.png"), dpi=200); plt.close(fig)

# 4.2 Mujeres: vigentes vs creadas por localidad (dumbbell)
m = T["06_mujeres_localidad"].drop("Sin localidad").sort_values("pct_mujeres_creadas")
fig, ax = plt.subplots(figsize=(9, 7.2)); fig.subplots_adjust(left=0.2, right=0.93, top=0.8, bottom=0.1)
y = range(len(m))
ax.hlines(y, m.pct_mujeres_vigentes, m.pct_mujeres_creadas, color=CLARO, lw=4)
ax.scatter(m.pct_mujeres_vigentes, y, s=55, color="#B9C2BC", zorder=3, label="Empresas vigentes")
ax.scatter(m.pct_mujeres_creadas, y, s=70, color=VERDE, zorder=4, label="Empresas creadas ene–mar 2026")
for i, v in enumerate(m.pct_mujeres_creadas):
    ax.text(max(v, m.pct_mujeres_vigentes.iat[i]) + 0.6, i, f"{fmt(v)} %", va="center", fontsize=9, color=CARBON,
            bbox=dict(facecolor="#F8FAF7", edgecolor="none", pad=1), zorder=5)
ax.axvline(50, color=DORADO, lw=1.4, ls="--", zorder=1); ax.text(50.3, len(m) - 0.4, "Paridad", color="#9A7425", fontsize=9.5, fontweight="bold")
ax.set_yticks(list(y)); ax.set_yticklabels(m.index); ax.tick_params(axis="y", length=0, colors=CARBON)
ax.set_xlim(30, 57); ax.xaxis.set_major_formatter(lambda v, p: f"{v:.0f} %"); ax.tick_params(axis="x", colors=GRIS)
ax.legend(loc="lower left", bbox_to_anchor=(-0.02, 1.0), ncol=2, frameon=False, fontsize=9.5)
titulo(fig, "Las empresas nuevas tienen más mujeres al frente que las existentes",
       "% de empresas con representante legal mujer (sexo conocido), vigentes frente a creadas ene–mar 2026")
pie(fig); fig.savefig(os.path.join(OUT, "graficos", "02_mujeres_localidad.png"), dpi=200); plt.close(fig)

# 4.3 Top 10 actividades de las empresas nuevas
a = T["05_actividad_top25"].head(10).iloc[::-1]
CORTO = {"5630": "Bares (expendio de bebidas alcohólicas)", "9602": "Peluquerías y belleza", "5611": "Restaurantes (comida a la mesa)",
         "4711": "Tiendas de alimentos (minorista no especializado)", "0010": "Asalariados (código DIAN 0010)",
         "8299": "Otros servicios de apoyo a empresas", "7020": "Consultoría de gestión", "4771": "Venta de ropa al por menor",
         "1410": "Confección de ropa", "4773": "Droguerías y cosméticos"}
lab = [CORTO.get(c, CIIU.get(c, c)) for c in a.index]
fig, ax = plt.subplots(figsize=(9, 6.2)); fig.subplots_adjust(left=0.37, right=0.95, top=0.82, bottom=0.08)
ax.barh(lab, a.creadas, color=[VERDE if c == "5630" else "#B9C2BC" for c in a.index], height=0.68)
for i, v in enumerate(a.creadas):
    ax.text(v + 15, i, fmt(v, 0), va="center", fontsize=9.5, color=CARBON, fontweight="bold" if a.index[i] == "5630" else "normal")
ax.set_xticks([]); ax.tick_params(axis="y", length=0, colors=CARBON, labelsize=9.2)
titulo(fig, f"Los bares lideran: unos {fmt(a.loc['5630','creadas']/dias, 0)} nuevos cada día en el primer trimestre",
       "Empresas creadas entre enero y marzo de 2026 por actividad económica (CIIU), 10 principales")
pie(fig); fig.savefig(os.path.join(OUT, "graficos", "03_top_actividades.png"), dpi=200); plt.close(fig)

print(claves.to_string(index=False)); print(calidad.to_string(index=False))
