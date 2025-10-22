# ============================================
# main.py — API + Interfaz para AutoGen Solar
# ============================================
from flask import Flask, request, jsonify, send_from_directory
import json
import openai
import datetime
import os

app = Flask(__name__, static_folder="static")

# ===============================
# Cargar configuración del equipo
# ===============================
TEAM_FILE = "team-config.json"

try:
    with open(TEAM_FILE, "r", encoding="utf-8") as f:
        team_data = json.load(f)["config"]["participants"]
except Exception as e:
    print(f"❌ Error al cargar {TEAM_FILE}: {e}")
    team_data = []

# ===============================
# Página de estado (raíz)
# ===============================
@app.route("/", methods=["GET"])
def home():
    return jsonify({
        "status": "ok",
        "message": "☀️ API de AutoGen Solar Operaciones está activa.",
        "usage": "Visita /chat para usar la interfaz o haz POST a /deploy."
    })

# ===============================
# Servir la interfaz de chat (frontend)
# ===============================
@app.route("/chat", methods=["GET"])
def chat_ui():
    return send_from_directory(app.static_folder, "index.html")

# ===============================
# Endpoint del chat interactivo
# ===============================
@app.route("/chat", methods=["POST"])
def chat_api():
    try:
        data = request.get_json()
        user_message = data.get("message", "").strip()

        if not user_message:
            return jsonify({"error": "No se recibió ningún mensaje."}), 400

        responses = []
        print(f"\n💬 Usuario: {user_message}")

        for agent in team_data:
            cfg = agent["config"]
            api_key = cfg["model_client"]["config"]["api_key"]
            model = cfg["model_client"]["config"]["model"]
            system_msg = cfg["system_message"]
            name = cfg["name"]

            openai.api_key = api_key
            print(f"🤖 Ejecutando {name}...")

            try:
                response = openai.chat.completions.create(
                    model=model,
                    messages=[
                        {"role": "system", "content": system_msg},
                        {"role": "user", "content": user_message}
                    ]
                )
                msg = response.choices[0].message.content
                responses.append(f"{name}: {msg}")
                print(f"✅ {name}: {msg[:120]}...")

            except Exception as e:
                error_msg = f"❌ Error en {name}: {e}"
                responses.append(error_msg)
                print(error_msg)

        if not responses:
            return jsonify({"response": "⚙️ El equipo no devolvió ninguna respuesta."})

        final_response = "\n\n".join(responses)
        return jsonify({"response": final_response})

    except Exception as e:
        print(f"❌ Error general en /chat: {e}")
        return jsonify({"error": str(e)}), 500

# ===============================
# Endpoint de despliegue grupal
# ===============================
@app.route("/deploy", methods=["POST"])
def deploy():
    try:
        data = request.get_json()
        user_prompt = data.get(
            "prompt",
            "Describe tu rol dentro del equipo solar y confirma que estás listo para iniciar el despliegue."
        )

        responses = []
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

        for agent in team_data:
            cfg = agent["config"]
            api_key = cfg["model_client"]["config"]["api_key"]
            model = cfg["model_client"]["config"]["model"]
            system_msg = cfg["system_message"]
            name = cfg["name"]

            openai.api_key = api_key
            print(f"🚀 Ejecutando {name}...")

            try:
                response = openai.chat.completions.create(
                    model=model,
                    messages=[
                        {"role": "system", "content": system_msg},
                        {"role": "user", "content": user_prompt}
                    ]
                )
                msg = response.choices[0].message.content
                responses.append({"agent": name, "response": msg})
                print(f"💬 {name}: {msg[:100]}...")

            except Exception as e:
                responses.append({"agent": name, "error": str(e)})
                print(f"❌ Error en {name}: {e}")

        # Guardar log
        log_file = f"deploy_log_{timestamp}.json"
        with open(log_file, "w", encoding="utf-8") as f:
            json.dump(responses, f, indent=2, ensure_ascii=False)

        return jsonify({
            "status": "success",
            "timestamp": timestamp,
            "responses": responses
        })

    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        })

# ===============================
# Servir archivos estáticos (CSS / JS)
# ===============================
@app.route("/static/<path:filename>")
def static_files(filename):
    return send_from_directory(app.static_folder, filename)

# ===============================
# Ejecutar servidor local
# ===============================
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
