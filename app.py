import sqlite3
import webbrowser
import subprocess
import os
import sys
from flask import Flask, render_template, request, redirect, url_for

if getattr(sys, 'frozen', False):
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(sys.executable))
else:
    base_path = os.path.dirname(os.path.abspath(__file__))

template_path = os.path.join(base_path, 'templates')
db_path = os.path.join(base_path, 'clinica_mn.db')

app = Flask(__name__, template_folder=template_path)

def _columnas_odontograma():
    """Nombres de columna de los campos del odontograma (sistema FDI)."""
    cols = []
    for n in [18, 17, 16, 15, 14, 13, 12, 11, 21, 22, 23, 24, 25, 26, 27, 28]:
        cols.append(f"rec_sup2_{n}")
    for n in [55, 54, 53, 52, 51, 61, 62, 63, 64, 65]:
        cols.append(f"rec_temp_sup_{n}")
    for n in [85, 84, 83, 82, 81, 71, 72, 73, 74, 75]:
        cols.append(f"rec_temp_inf_{n}")
    for n in [48, 47, 46, 45, 44, 43, 42, 41, 31, 32, 33, 34, 35, 36, 37, 38]:
        cols.append(f"rec_inf2_{n}")
    return cols


def _columnas_presupuesto():
    cols = []
    for i in range(1, 12):
        cols += [
            f"pres_item_{i}",
            f"pres_desc_{i}",
            f"pres_cant_{i}",
            f"pres_unit_{i}",
            f"pres_total_{i}",
            f"pres_obs_{i}",
        ]
    cols.append("pres_total_general")
    return cols


def _columnas_evolucion():
    cols = []
    for i in range(1, 12):
        cols += [
            f"evo_fecha_{i}",
            f"evo_tratamiento_{i}",
            f"evo_cuenta_{i}",
            f"evo_adelanto_{i}",
            f"evo_saldo_{i}",
        ]
    return cols


def _columnas_examen_clinico():
    """Nombres de columna de los checkboxes del examen clinico odontologico (P/N)."""
    items = [
        "ex_extraoral",
        "ex_cara",
        "ex_cuello",
        "ex_piel",
        "ex_ganglios",
        "ex_atm",
        "ex_intraoral",
        "ex_labios",
        "ex_carrillo",
        "ex_fondo_surco",
        "ex_periodoncia",
        "ex_zona_retromolar",
        "ex_paladar_duro",
        "ex_paladar_blanco",
        "ex_vitalidad_pulpar",
        "ex_oclusion",
        "ex_contactos_prematuros",
    ]
    cols = []
    for nombre in items:
        cols.append(f"{nombre}_p")
        cols.append(f"{nombre}_n")
    return cols


def _definiciones_columnas():
    """Definiciones SQL (nombre TIPO) de todas las columnas de la tabla historias."""
    definiciones = [
        "n_historia TEXT",
        "nombre_apellido TEXT",
        "fecha_nacimiento TEXT",
        "dni TEXT",
        "sexo TEXT",
        "edad INTEGER",
        "nombre_familiar TEXT",
        "parentesco TEXT",
        "dni_familiar TEXT",
        "telefono TEXT",
        "fecha_atencion TEXT",
        "motivo_consulta TEXT",
        "ant_diabetes TEXT",
        "ant_tuberculosis TEXT",
        "ant_anemia TEXT",
        "ant_fiebre_reumatica TEXT",
        "ant_cardiovascular TEXT",
        "ant_renal TEXT",
        "ant_hepatica TEXT",
        "ant_anestesia TEXT",
        "ant_drogas TEXT",
        "ant_hemorragias1 TEXT",
        "ant_hemorragias2 TEXT",
        "ant_otros TEXT",
        "fv_peso TEXT",
        "fv_fc TEXT",
        "fv_fr TEXT",
        "fv_talla TEXT",
        "fv_pa TEXT",
        "fv_temp TEXT",
        "ex_otros TEXT",
        "especificaciones_odontograma TEXT",
    ]
    definiciones += [f"{nombre} TEXT" for nombre in _columnas_examen_clinico()]
    definiciones += [f"{nombre} TEXT" for nombre in _columnas_odontograma()]
    definiciones += [f"{nombre} TEXT" for nombre in _columnas_presupuesto()]
    definiciones += [f"{nombre} TEXT" for nombre in _columnas_evolucion()]
    return definiciones


def _nombres_columnas():
    """Solo los nombres de columna (sin tipo), en el orden del INSERT."""
    nombres = [
        "n_historia",
        "nombre_apellido",
        "fecha_nacimiento",
        "dni",
        "sexo",
        "edad",
        "nombre_familiar",
        "parentesco",
        "dni_familiar",
        "telefono",
        "fecha_atencion",
        "motivo_consulta",
        "ant_diabetes",
        "ant_tuberculosis",
        "ant_anemia",
        "ant_fiebre_reumatica",
        "ant_cardiovascular",
        "ant_renal",
        "ant_hepatica",
        "ant_anestesia",
        "ant_drogas",
        "ant_hemorragias1",
        "ant_hemorragias2",
        "ant_otros",
        "fv_peso",
        "fv_fc",
        "fv_fr",
        "fv_talla",
        "fv_pa",
        "fv_temp",
        "ex_otros",
        "especificaciones_odontograma",
    ]
    nombres += _columnas_examen_clinico()
    nombres += _columnas_odontograma()
    nombres += _columnas_presupuesto()
    nombres += _columnas_evolucion()
    return nombres


def init_db():
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    definiciones = _definiciones_columnas()
    columnas_sql = ", ".join(definiciones)
    cursor.execute(
        f"""
        CREATE TABLE IF NOT EXISTS historias (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            {columnas_sql}
        )
    """
    )
    # Migracion para bases de datos ya existentes:
    # CREATE TABLE IF NOT EXISTS no modifica tablas creadas con un esquema viejo,
    # por eso agregamos las columnas que falten para evitar el error 500 al guardar.
    cursor.execute("PRAGMA table_info(historias)")
    existentes = {fila[1] for fila in cursor.fetchall()}
    for definicion in definiciones:
        nombre = definicion.split()[0]
        if nombre not in existentes:
            cursor.execute(f"ALTER TABLE historias ADD COLUMN {definicion}")
    conn.commit()
    conn.close()

@app.route("/")
def index():
    return redirect(url_for("dashboard"))

@app.route("/dashboard")
def dashboard():
    busqueda = request.args.get("q", "")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    if busqueda:
        cursor.execute("SELECT id, n_historia, dni, nombre_apellido, telefono, fecha_atencion FROM historias WHERE nombre_apellido LIKE ? OR dni LIKE ? ORDER BY id DESC", (f"%{busqueda}%", f"%{busqueda}%"))
    else:
        cursor.execute("SELECT id, n_historia, dni, nombre_apellido, telefono, fecha_atencion FROM historias ORDER BY id DESC")
    rows = cursor.fetchall()
    conn.close()
    return render_template("dashboard.html", historias=rows, busqueda=busqueda)

@app.route("/nueva", methods=["GET", "POST"])
def nueva_historia():
    if request.method == "POST":
        data = request.form
        nombres = _nombres_columnas()
        placeholders = ", ".join(["?"] * len(nombres))
        columnas_sql = ", ".join(nombres)
        valores = tuple(data.get(nombre) for nombre in nombres)

        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute(
            f"""
            INSERT INTO historias ({columnas_sql})
            VALUES ({placeholders})
        """,
            valores,
        )
        conn.commit()
        conn.close()
        return redirect(url_for("dashboard"))
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM historias")
    count = cursor.fetchone()[0]
    conn.close()
    siguiente_n = str(count + 1).zfill(2)

    return render_template("formulario.html", siguiente_n=siguiente_n)


@app.route("/ver/<int:id>")
def ver_historia(id):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM historias WHERE id = ?", (id,))
    row = cursor.fetchone()
    conn.close()
    if not row:
        return redirect(url_for("dashboard"))
    nombres = _nombres_columnas()
    historia = dict(zip(nombres, row))
    siguiente_n = historia.get("n_historia") or str(1).zfill(2)
    return render_template("formulario.html", siguiente_n=siguiente_n, historia=historia)


def abrir_como_programa():
    chrome_path = "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe"
    if not os.path.exists(chrome_path):
        chrome_path = os.path.expanduser("~") + "\\AppData\\Local\\Google\\Chrome\\Application\\chrome.exe"
    url = "http://127.0.0.1:5000/"
    try:
        subprocess.Popen([chrome_path, "--app=" + url, "--start-maximized", "--kiosk"])
    except Exception:
        pass

if __name__ == "__main__":
    init_db()
    from threading import Timer
    Timer(1.2, abrir_como_programa).start()
    app.run(port=5000)