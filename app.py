import os
import json
from flask import Flask, request, jsonify
from datetime import datetime
from functools import wraps

# Intentar importar psycopg2
try:
    import psycopg2
    import psycopg2.extras
    USAR_DB = True
except ImportError:
    USAR_DB = False

app = Flask(__name__)

# Configuracion desde variables de entorno
DATABASE_URL = os.environ.get("DATABASE_URL", "")
API_KEY = os.environ.get("API_KEY", "clave-practica-07")
APP_ENV = os.environ.get("APP_ENV", "development")

def get_db():
    if not USAR_DB or not DATABASE_URL:
        return None
    return psycopg2.connect(DATABASE_URL)

def init_db():
    conn = get_db()
    if not conn:
        return
    cur = conn.cursor()
    
    # Tabla de materias
    cur.execute("""
    CREATE TABLE IF NOT EXISTS materias (
        id SERIAL PRIMARY KEY,
        clave VARCHAR(15) NOT NULL UNIQUE,
        nombre VARCHAR(150) NOT NULL,
        semestre INTEGER NOT NULL CHECK (semestre BETWEEN 1 AND 9),
        creditos INTEGER DEFAULT 5,
        tipo VARCHAR(30) DEFAULT 'Obligatoria',
        horas_teoria INTEGER DEFAULT 3,
        horas_practica INTEGER DEFAULT 2,
        competencia VARCHAR(200),
        activa BOOLEAN DEFAULT true,
        fecha_registro TIMESTAMP DEFAULT NOW()
    )
    """)
    
    # Tabla de reportes
    cur.execute("""
    CREATE TABLE IF NOT EXISTS reportes (
        id SERIAL PRIMARY KEY,
        tipo VARCHAR(50),
        datos JSONB,
        fecha TIMESTAMP DEFAULT NOW()
    )
    """)
    
    # Insertar datos iniciales
    cur.execute("SELECT COUNT(*) FROM materias")
    count = cur.fetchone()[0]
    if count == 0:
        materias_iniciales = [
            ('INF-101', 'Fundamentos de Programacion', 1, 6, 'Obligatoria', 3, 3, 'Desarrollo de software'),
            ('INF-102', 'Matematicas Discretas', 1, 5, 'Obligatoria', 4, 1, 'Logica computacional'),
            ('INF-201', 'Estructura de Datos', 2, 6, 'Obligatoria', 3, 3, 'Desarrollo de software'),
            ('INF-202', 'Arquitectura de Computadoras', 2, 5, 'Obligatoria', 4, 1, 'Hardware y redes'),
            ('INF-301', 'Bases de Datos', 3, 6, 'Obligatoria', 3, 3, 'Gestion de datos'),
            ('INF-302', 'Redes de Computadoras', 3, 5, 'Obligatoria', 3, 2, 'Hardware y redes'),
            ('INF-401', 'Ingenieria de Software', 4, 6, 'Obligatoria', 3, 3, 'Desarrollo de software'),
            ('INF-402', 'Sistemas Operativos', 4, 5, 'Obligatoria', 3, 2, 'Infraestructura'),
            ('INF-501', 'Servicios en la Nube', 5, 5, 'Obligatoria', 2, 3, 'Infraestructura'),
            ('INF-502', 'Administracion de Datos', 5, 5, 'Obligatoria', 3, 2, 'Gestion de datos'),
            ('INF-601', 'Inteligencia Artificial', 6, 5, 'Obligatoria', 3, 2, 'IA y datos'),
            ('INF-602', 'Seguridad Informatica', 6, 5, 'Obligatoria', 3, 2, 'Infraestructura'),
            ('INF-701', 'Desarrollo de Apps Moviles', 7, 5, 'Optativa', 2, 3, 'Desarrollo de software'),
            ('INF-702', 'Big Data y Analitica', 7, 5, 'Optativa', 3, 2, 'IA y datos')
        ]
        for m in materias_iniciales:
            cur.execute("""
            INSERT INTO materias (clave, nombre, semestre, creditos, tipo, horas_teoria, horas_practica, competencia)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, m)
        conn.commit()
    cur.close()
    conn.close()

def requiere_api_key(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        key = request.headers.get("X-API-Key", "")
        if key != API_KEY:
            return jsonify({
                "error": "API Key invalida o no proporcionada",
                "instruccion": "Incluye el header X-API-Key con tu clave"
            }), 401
        return f(*args, **kwargs)
    return decorated

@app.route("/")
def index():
    base_url = request.url_root.rstrip("/")
    return f"""
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <title>API Materias - Practica 07</title>
        <style>
            body {{ font-family: sans-serif; background: #0d1117; color: #c9d1d9; padding: 20px; }}
            h1 {{ color: #58a6ff; }}
            pre {{ background: #1f2937; padding: 12px; border-radius: 6px; }}
        </style>
    </head>
    <body>
        <h1>API REST: Catalogo de Materias</h1>
        <p>Ambiente: {APP_ENV} | DB: {'Conectada' if (USAR_DB and DATABASE_URL) else 'No configurada'}</p>
        <p>Base URL: {base_url}</p>
    </body>
    </html>
    """

@app.route("/api/materias", methods=["GET"])
def listar_materias():
    conn = get_db()
    if not conn:
        return jsonify({"error": "Base de datos no disponible"}), 503
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    
    semestre = request.args.get("semestre")
    tipo = request.args.get("tipo")
    competencia = request.args.get("competencia")
    
    query = "SELECT * FROM materias WHERE activa = true"
    params = []
    if semestre:
        query += " AND semestre = %s"
        params.append(int(semestre))
    if tipo:
        query += " AND LOWER(tipo) = LOWER(%s)"
        params.append(tipo)
    if competencia:
        query += " AND LOWER(competencia) LIKE LOWER(%s)"
        params.append(f"%{competencia}%")
        
    query += " ORDER BY semestre, clave"
    cur.execute(query, params)
    materias = cur.fetchall()
    cur.close()
    conn.close()
    
    for m in materias:
        if m.get("fecha_registro"):
            m["fecha_registro"] = m["fecha_registro"].isoformat()
            
    return jsonify({
        "total": len(materias),
        "filtros": {"semestre": semestre, "tipo": tipo, "competencia": competencia},
        "materias": materias
    })

@app.route("/api/materias/<int:id>", methods=["GET"])
def obtener_materia(id):
    conn = get_db()
    if not conn:
        return jsonify({"error": "Base de datos no disponible"}), 503
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute("SELECT * FROM materias WHERE id = %s", (id,))
    materia = cur.fetchone()
    cur.close()
    conn.close()
    if not materia:
        return jsonify({"error": f"Materia con id {id} no encontrada"}), 404
    if m.get("fecha_registro"):
        materia["fecha_registro"] = materia["fecha_registro"].isoformat()
    return jsonify(materia)

@app.route("/api/materias", methods=["POST"])
@requiere_api_key
def crear_materia():
    conn = get_db()
    if not conn:
        return jsonify({"error": "Base de datos no disponible"}), 503
    data = request.get_json()
    if not data:
        return jsonify({"error": "Body JSON requerido"}), 400
    campos_requeridos = ["clave", "nombre", "semestre"]
    for campo in campos_requeridos:
        if campo not in data:
            return jsonify({"error": f"Campo requerido: {campo}"}), 400
            
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    try:
        cur.execute("""
        INSERT INTO materias (clave, nombre, semestre, creditos, tipo, horas_teoria, horas_practica, competencia)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s) RETURNING *
        """, (data["clave"], data["nombre"], data["semestre"], data.get("creditos", 5),
              data.get("tipo", "Obligatoria"), data.get("horas_teoria", 3), data.get("horas_practica", 2), data.get("competencia", "")))
        nueva = cur.fetchone()
        conn.commit()
        if nueva.get("fecha_registro"):
            nueva["fecha_registro"] = nueva["fecha_registro"].isoformat()
        cur.close()
        conn.close()
        return jsonify({"mensaje": "Materia creada", "materia": nueva}), 201
    except psycopg2.errors.UniqueViolation:
        conn.rollback()
        cur.close()
        conn.close()
        return jsonify({"error": f"La clave {data['clave']} ya existe"}), 409

@app.route("/api/materias/<int:id>", methods=["PUT"])
@requiere_api_key
def actualizar_materia(id):
    conn = get_db()
    if not conn:
        return jsonify({"error": "Base de datos no disponible"}), 503
    data = request.get_json()
    campos_permitidos = ["nombre", "semestre", "creditos", "tipo", "horas_teoria", "horas_practica", "competencia"]
    updates = []
    values = []
    for campo in campos_permitidos:
        if campo in data:
            updates.append(f"{campo} = %s")
            values.append(data[campo])
    if not updates:
        return jsonify({"error": "No se proporcionaron campos para actualizar"}), 400
    values.append(id)
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute(f"UPDATE materias SET {', '.join(updates)} WHERE id = %s RETURNING *", values)
    actualizada = cur.fetchone()
    conn.commit()
    cur.close()
    conn.close()
    if not actualizada:
        return jsonify({"error": f"Materia {id} no encontrada"}), 404
    return jsonify({"mensaje": "Materia actualizada", "materia": actualizada})

@app.route("/api/materias/<int:id>", methods=["DELETE"])
@requiere_api_key
def eliminar_materia(id):
    conn = get_db()
    if not conn:
        return jsonify({"error": "Base de datos no disponible"}), 503
    cur = conn.cursor()
    cur.execute("UPDATE materias SET activa = false WHERE id = %s AND activa = true", (id,))
    afectadas = cur.rowcount
    conn.commit()
    cur.close()
    conn.close()
    if afectadas == 0:
        return jsonify({"error": f"Materia {id} no encontrada o ya inactiva"}), 404
    return jsonify({"mensaje": f"Materia {id} desactivada (soft delete)"})

@app.route("/api/estadisticas", methods=["GET"])
def estadisticas():
    conn = get_db()
    if not conn:
        return jsonify({"error": "Base de datos no disponible"}), 503
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute("SELECT semestre, COUNT(*) as total, SUM(creditos) as total_creditos FROM materias WHERE activa = true GROUP BY semestre ORDER BY semestre")
    por_semestre = cur.fetchall()
    cur.execute("SELECT tipo, COUNT(*) as total FROM materias WHERE activa = true GROUP BY tipo")
    por_tipo = cur.fetchall()
    cur.execute("SELECT COUNT(*) as total_materias, SUM(creditos) as total_creditos FROM materias WHERE activa = true")
    totales = cur.fetchone()
    cur.close()
    conn.close()
    return jsonify({"resumen": totales, "por_semestre": por_semestre, "por_tipo": por_tipo, "generado": datetime.now().isoformat()})

@app.route("/api/reportes", methods=["GET"])
def listar_reportes():
    conn = get_db()
    if not conn:
        return jsonify({"error": "Base de datos no disponible"}), 503
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute("SELECT * FROM reportes ORDER BY fecha DESC LIMIT 10")
    reportes = cur.fetchall()
    cur.close()
    conn.close()
    for r in reportes:
        if r.get("fecha"):
            r["fecha"] = r["fecha"].isoformat()
    return jsonify({"total": len(reportes), "reportes": reportes})

@app.route("/api/status")
def status():
    return jsonify({
        "status": "ok",
        "ambiente": APP_ENV,
        "plataforma": "Render.com",
        "servicios": {"api": "activa", "base_datos": "conectada" if (USAR_DB and DATABASE_URL) else "no configurada"}
    })

with app.app_context():
    init_db()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
