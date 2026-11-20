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
            f"evo_observaciones_{i}",
            f"evo_estado_{i}",
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
        "ant_fiebre_reumatica TEXT