import sqlite3
import webbrowser
import subprocess
import os
from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

def init_db():
    conn = sqlite3.connect("clinica_mn.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS historias (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            n_historia TEXT,
            -- Filiación Fila 1
            nombre_apellido TEXT,
            fecha_nacimiento TEXT,
            dni TEXT,
            sexo TEXT,
            edad INTEGER,
            -- Filiación Fila 2
            nombre_familiar TEXT,
            parentesco TEXT,
            dni_familiar TEXT,
            telefono TEXT,
            fecha_atencion TEXT,
            -- Motivo
            motivo_consulta TEXT,
            -- Antecedentes (SI/NO)
            ant_diabetes TEXT,
            ant_tuberculosis TEXT,
            ant_anemia TEXT,
            ant_fiebre_reumatica TEXT,
            ant_cardiovascular TEXT,
            ant_renal TEXT,
            ant_hepatica TEXT,
            ant_anestesia TEXT,
            ant_drogas TEXT,
            ant_hemorragias1 TEXT,
            ant_hemorragias2 TEXT,
            ant_otros TEXT,
            -- Funciones Vitales
            fv_peso TEXT,
            fv_fc TEXT,
            fv_fr TEXT,
            fv_talla TEXT,
            fv_pa TEXT,
            fv_temp TEXT
        )
    """)
    conn.commit()
    conn.close()

@app.route("/")
def index():
    return redirect(url_for("dashboard"))

@app.route("/dashboard")
def dashboard():
    busqueda = request.args.get("q", "")
    conn = sqlite3.connect("clinica_mn.db")
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
        conn = sqlite3.connect("clinica_mn.db")
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO historias (
                n_historia, nombre_apellido, fecha_nacimiento, dni, sexo, edad,
                nombre_familiar, parentesco, dni_familiar, telefono, fecha_atencion,
                motivo_consulta, ant_diabetes, ant_tuberculosis, ant_anemia, ant_fiebre_reumatica,
                ant_cardiovascular, ant_renal, ant_hepatica, ant_anestesia,
                ant_drogas, ant_hemorragias1, ant_hemorragias2, ant_otros,
                fv_peso, fv_fc, fv_fr, fv_talla, fv_pa, fv_temp
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            data.get("n_historia"), data.get("nombre_apellido"), data.get("fecha_nacimiento"),
            data.get("dni"), data.get("sexo"), data.get("edad"),
            data.get("nombre_familiar"), data.get("parentesco"), data.get("dni_familiar"),
            data.get("telefono"), data.get("fecha_atencion"), data.get("motivo_consulta"),
            data.get("ant_diabetes"), data.get("ant_tuberculosis"), data.get("ant_anemia"), data.get("ant_fiebre_reumatica"),
            data.get("ant_cardiovascular"), data.get("ant_renal"), data.get("ant_hepatica"), data.get("ant_anestesia"),
            data.get("ant_drogas"), data.get("ant_hemorragias1"), data.get("ant_hemorragias2"), data.get("ant_otros"),
            data.get("fv_peso"), data.get("fv_fc"), data.get("fv_fr"), data.get("fv_talla"), data.get("fv_pa"), data.get("fv_temp")
        ))
        conn.commit()
        conn.close()
        return redirect(url_for("dashboard"))
    
    conn = sqlite3.connect("clinica_mn.db")
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM historias")
    count = cursor.fetchone()[0]
    conn.close()
    siguiente_n = str(count + 1).zfill(2)

    return render_template("formulario.html", siguiente_n=siguiente_n)

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