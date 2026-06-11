import os
import json
import psycopg2
import psycopg2.extras
from flask import Flask, request, jsonify
from datetime import datetime
from functools import wraps
from apscheduler.schedulers.background import BackgroundScheduler

app = Flask(__name__)

# URL de tu Base de Datos fija de Ohio
DATABASE_URL = "postgresql://flask_user:VX1dWJ4Om4rgDdRYCTIKNFSmkZzcL5fL@dpg-d8lfqha8qa3s73e66dhg-a.ohio-postgres.render.com/flask_db_36tl"
# API Key exigida por el PDF (puedes cambiarla si usas variables de entorno)
API_KEY = "clave-practica-07"

def get_db():
    return psycopg2.connect(DATABASE_URL)

def init_db():
    """Crea las tablas oficiales de la práctica e inserta los datos iniciales."""
    conn = get_db()
    cur = conn.cursor()
    
    # 1. Tabla de materias (Estructura oficial del PDF)
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
        );
    """)
    
    # 2. Tabla de reportes para el Cron Job
    cur.execute("""
        CREATE TABLE IF NOT EXISTS reportes (
            id SERIAL PRIMARY KEY,
            tipo VARCHAR(50),
            datos JSONB,
            fecha TIMESTAMP DEFAULT NOW()
        );
    """)
    
    # 3. Insertar materias iniciales de informática (si está vacía)
    cur.execute("SELECT COUNT(*) FROM materias")
    if cur.fetchone()[0] == 0:
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
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s);
            """, m)
    conn.commit()
    cur.close()
    conn.close()

def tarea_cron_interno_reporte():
    """Simula el Cron Job externo exigido por el PDF de forma interna y gratuita."""
    try:
        conn = get_db()
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        
        # Recopilar estadísticas oficiales
        cur.execute("SELECT COUNT(*) as total FROM materias WHERE activa = true")
        total = cur.fetchone()["total"]
        
        cur.execute("""
            SELECT semestre, COUNT(*) as materias, SUM(creditos) as creditos 
            FROM materias WHERE activa = true GROUP BY semestre ORDER BY semestre
        """)
        por_semestre = cur.fetchall()
        
        cur.execute("SELECT tipo, COUNT(*) as total FROM materias WHERE activa = true GROUP BY tipo")
        por_tipo = cur.fetchall()
        
        # Construir JSON del reporte
        reporte = {
            "total_materias_activas": total,
            "por_semestre": por_semestre,
            "por_tipo": por_tipo,
            "generado_por": "Cron Job Interno Gratuito (APScheduler)",
            "timestamp": datetime.now().isoformat()
        }
        
        # Guardar en la tabla reportes
        cur.execute("INSERT INTO reportes (tipo, datos) VALUES (%s, %s);", ("estadisticas_automaticas", json.dumps(reporte, default=str)))
        conn.commit()
        cur.close()
        conn.close()
        print(f"⏰ Cron Interno: Reporte de estadísticas guardado con éxito. Materias activas: {total}")
    except Exception as e:
        print(f"Error en Cron interno de reportes: {e}")

# Inicializar Base de datos al arrancar
init_db()

# Configurar el reloj/cron para generar reportes gratis cada 5 minutos
scheduler = BackgroundScheduler()
scheduler.add_job(func=tarea_cron_interno_reporte, trigger="interval", minutes=5)
scheduler.start()

# Middleware de seguridad (API Key) obligatorio del PDF
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

# Documentación interactiva visual (Copiada idéntica de tu PDF)
@app.route("/")
def index():
    base_url = request.url_root.rstrip("/")
    return f"""
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8"><title>API Materias - Practica 07</title>
        <style>
            body {{ font-family: 'Courier New', monospace; background: #0d1117; color: #c9d1d9; padding: 20px; }}
            .container {{ max-width: 800px; margin: 0 auto; }}
            h1 {{ color: #58a6ff; }} .info {{ background: #1f2937; padding: 12px; margin: 15px 0; border-radius: 6px; }}
            button {{ background: #238636; color: white; border: none; padding: 10px; margin: 5px; cursor: pointer; border-radius: 4px; }}
            pre {{ background: #161b22; padding: 15px; border-radius: 6px; white-space: pre-wrap; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>API REST: Catalogo de Materias</h1>
            <p>Práctica 07 - PaaS Render | Servicios en la Nube</p>
            <div class="info">
                <strong>Base URL:</strong> <code>{base_url}</code> | <strong>Cron Job:</strong> Activado Interno (Cada 5 min Gratis)
            </div>
            <h2>Pruebas Rápidas</h2>
            <button onclick="probar('/api/materias')">GET /api/materias</button>
            <button onclick="probar('/api/estadisticas')">GET /api/estadisticas</button>
            <button onclick="probar('/api/reportes')">GET /api/reportes (Cron Job)</button>
            <button onclick="probar('/api/status')">GET /api/status</button>
            <pre id="resultado">Haz clic en un botón para cargar los datos del catálogo oficial...</pre>
        </div>
        <script>
            async function probar(endpoint) {{
                const res = await fetch(endpoint);
                const data = await res.json();
                document.getElementById('resultado').textContent = JSON.stringify(data, null, 2);
            }}
        </script>
    </body>
    </html>
    """

# 1. GET: Listar materias con filtros opcionales (PDF)
@app.route("/api/materias", methods=["GET"])
def listar_materias():
    conn = get_db()
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
    
    for m in materias:
        if m.get("fecha_registro"):
            m["fecha_registro"] = m["fecha_registro"].isoformat()
            
    cur.close()
    conn.close()
    return jsonify({"total": len(materias), "materias": materias})

# 2. POST: Crear materia (Protegido por API Key)
@app.route("/api/materias", methods=["POST"])
@requiere_api_key
def crear_materia():
    conn = get_db()
    data = request.get_json()
    if not data or not all(k in data for k in ["clave", "nombre", "semestre"]):
        return jsonify({"error": "Faltan campos obligatorios (clave, nombre, semestre)"}), 400
        
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    try:
        cur.execute("""
            INSERT INTO materias (clave, nombre, semestre, creditos, tipo, horas_teoria, horas_practica, competencia)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s) RETURNING *;
        """, (data["clave"], data["nombre"], data["semestre"], data.get("creditos", 5), data.get("tipo", "Obligatoria"), data.get("horas_teoria", 3), data.get("horas_practica", 2), data.get("competencia", "")))
        nueva = cur.fetchone()
        conn.commit()
        if nueva.get("fecha_registro"):
            nueva["fecha_registro"] = nueva["fecha_registro"].isoformat()
        return jsonify({"mensaje": "Materia creada exitosamente", "materia": nueva}), 201
    except psycopg2.errors.UniqueViolation:
        return jsonify({"error": f"La clave {data['clave']} ya existe"}), 409
    finally:
        cur.close()
        conn.close()

# 3. GET: Estadísticas en vivo
@app.route("/api/estadisticas", methods=["GET"])
def estadisticas():
    conn = get_db()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute("SELECT COUNT(*) as total_materias, SUM(creditos) as total_creditos FROM materias WHERE activa = true")
    totales = cur.fetchone()
    cur.close()
    conn.close()
    return jsonify({"resumen": totales, "generado": datetime.now().isoformat()})

# 4. GET: Ver reportes guardados por el Cron Job
@app.route("/api/reportes", methods=["GET"])
def listar_reportes():
    conn = get_db()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute("SELECT * FROM reportes ORDER BY fecha DESC LIMIT 10")
    reportes = cur.fetchall()
    for r in reportes:
        if r.get("fecha"):
            r["fecha"] = r["fecha"].isoformat()
    cur.close()
    conn.close()
    return jsonify({"total": len(reportes), "reportes": reportes})

# 5. GET: Status general
@app.route("/api/status")
def status():
    return jsonify({
        "status": "ok",
        "plataforma": "Render.com",
        "modelo": "PaaS Moderno",
        "cron_job": "Configurado Interno APScheduler (Gratis)",
        "timestamp": datetime.now().isoformat()
    })

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
