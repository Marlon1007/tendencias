import os

import psycopg
from flask import Flask, redirect, render_template_string, request, url_for

app = Flask(__name__)

def get_connection():
    return psycopg.connect(
        host=os.environ.get("DB_HOST", "db"),
        port=os.environ.get("DB_PORT", "5432"),
        dbname=os.environ["POSTGRES_DB"],
        user=os.environ["POSTGRES_USER"],
        password=os.environ["POSTGRES_PASSWORD"],
        connect_timeout=5,
    )


def init_db():
    with get_connection() as connection:
        connection.execute(
            "CREATE TABLE IF NOT EXISTS messages ("
            "id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY, "
            "content TEXT NOT NULL)"
        )


@app.errorhandler(psycopg.Error)
def database_error(error):
    app.logger.error("Database operation failed: %s", type(error).__name__)
    return "La base de datos no está disponible. Inténtalo de nuevo más tarde.", 503


@app.route("/", methods=["GET", "POST"])
def inicio():
    if request.method == "POST":
        content = request.form.get("content", "")
        if not content.strip():
            return "Escribe un texto antes de guardar.", 400
        with get_connection() as connection:
            connection.execute(
                "INSERT INTO messages (content) VALUES (%s)", (content,)
            )
        return redirect(url_for("inicio"), code=303)

    with get_connection() as connection:
        messages = connection.execute(
            "SELECT id, content FROM messages ORDER BY id DESC"
        ).fetchall()
    return render_template_string("""
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Marlon Silva - Taller Docker & Flask</title>
        <style>
            * {
                box-sizing: border-box;
                margin: 0;
                padding: 0;
            }
            body {
                font-family: system-ui, -apple-system, 'Segoe UI', Roboto, sans-serif;
                background-color: #090d16;
                background-image: radial-gradient(circle at top right, #132a2e 0%, #090d16 55%);
                color: #e2e8f0;
                display: flex;
                align-items: center;
                justify-content: center;
                min-height: 100vh;
                padding: 20px;
            }
            .container {
                background: #111827;
                border: 1px solid #1f2937;
                border-top: 4px solid #10b981;
                border-radius: 14px;
                padding: 36px;
                max-width: 560px;
                width: 100%;
                box-shadow: 0 20px 40px rgba(0, 0, 0, 0.55);
            }
            .header {
                display: flex;
                justify-content: space-between;
                align-items: center;
                flex-wrap: wrap;
                gap: 10px;
                margin-bottom: 20px;
            }
            .status-pill {
                display: inline-flex;
                align-items: center;
                gap: 8px;
                background: rgba(16, 185, 129, 0.12);
                border: 1px solid rgba(16, 185, 129, 0.35);
                color: #34d399;
                padding: 6px 14px;
                border-radius: 999px;
                font-size: 0.85rem;
                font-weight: 600;
            }
            .dot {
                width: 8px;
                height: 8px;
                background-color: #10b981;
                border-radius: 50%;
                box-shadow: 0 0 8px #10b981;
            }
            .workshop-banner {
                background: rgba(245, 158, 11, 0.12);
                border: 1px dashed #f59e0b;
                color: #fbbf24;
                padding: 10px 14px;
                border-radius: 8px;
                font-weight: 600;
                font-size: 0.95rem;
                margin-bottom: 18px;
            }
            h1 {
                font-size: 1.85rem;
                color: #f8fafc;
                margin-bottom: 10px;
                letter-spacing: -0.02em;
            }
            p {
                color: #94a3b8;
                line-height: 1.6;
                font-size: 0.98rem;
                margin-bottom: 24px;
            }
            .specs-grid {
                display: grid;
                grid-template-columns: repeat(2, 1fr);
                gap: 12px;
                background: #0b1120;
                border: 1px solid #1e293b;
                border-radius: 10px;
                padding: 16px;
            }
            .spec-item {
                display: flex;
                flex-direction: column;
                gap: 4px;
            }
            .spec-item.full {
                grid-column: span 2;
                border-bottom: 1px solid #1e293b;
                padding-bottom: 10px;
                margin-bottom: 2px;
            }
            .spec-label {
                font-size: 0.75rem;
                text-transform: uppercase;
                letter-spacing: 0.06em;
                color: #64748b;
            }
            .spec-value {
                font-family: ui-monospace, SFMono-Regular, Menlo, monospace;
                font-size: 0.9rem;
                color: #e2e8f0;
            }
            form { display: grid; gap: 12px; margin: 24px 0; }
            input, button { font: inherit; padding: 12px; border-radius: 8px; }
            input { width: 100%; min-width: 0; color: #e2e8f0; background: #0b1120; border: 1px solid #64748b; }
            button { background: #10b981; color: #090d16; border: 0; cursor: pointer; font-weight: 600; }
            input:focus-visible, button:focus-visible { outline: 3px solid #fbbf24; outline-offset: 3px; }
            .messages { padding-left: 24px; margin-top: 12px; }
            .messages li { margin-bottom: 10px; overflow-wrap: anywhere; white-space: pre-wrap; }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <span class="status-pill"><span class="dot"></span>Activo y Conectado</span>
            </div>
            <div class="workshop-banner">
                📌 Yo estudio en el Yavirac.
            </div>
            <h1>Marlon Silva</h1>
            <p>
                Aplicación web desarrollada con <strong>Python y Flask</strong>, empaquetada y ejecutándose de forma aislada dentro de un contenedor Linux.
            </p>
            <form method="post" action="{{ url_for('inicio') }}">
                <label for="content">Texto para guardar</label>
                <input id="content" name="content" type="text" required>
                <button type="submit">Guardar</button>
            </form>
            <h2>Textos guardados</h2>
            <ul class="messages">
                {% for message in messages %}
                <li>{{ message[1] }}</li>
                {% else %}
                <li>Todavía no hay textos guardados.</li>
                {% endfor %}
            </ul>
            <div class="specs-grid">
                <div class="spec-item full">
                    <span class="spec-label">Asignatura</span>
                    <span class="spec-value">Tendencias Actuales de Programación</span>
                </div>
                <div class="spec-item">
                    <span class="spec-label">Entorno</span>
                    <span class="spec-value">Python 3.14-slim | Flask</span>
                </div>
                <div class="spec-item">
                    <span class="spec-label">Red del Contenedor</span>
                    <span class="spec-value">0.0.0.0 : 5000</span>
                </div>
            </div>
        </div>
    </body>
    </html>
    """, messages=messages)

if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=5000)
