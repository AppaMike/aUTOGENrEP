from flask import Flask, request, jsonify, send_from_directory
import json
import openai
import datetime
import os
from dotenv import load_dotenv

# Cargar variables de entorno desde .env
load_dotenv()

app = Flask(__name__, static_folder="static")

TEAM_FILE = "team-config.json"

# ===============================
# Cargar configuración de agentes
# ===============================
with open(TEAM_FILE, "r", encoding="utf-8") as f:
    team_data = json.load(f)["config"]["participants"]

# Obtener API key desde variable de entorno
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if not OPENAI_API_KEY:
    raise ValueError("❌ OPENAI_API_KEY no está configurada en las variables de entorno")

# ===============================
# Página principal (Frontend)
# ===============================
@app.route("/")
def home():
    return jsonify({
        "status": "ok",
        "message": "☀️ API de AutoGen Solar Operaciones está activa.",
        "usage": "Envía un POST a /deploy con {'prompt': 'tu mensaje'}"
    })

@app.route("/chat")
def chat():
    return send_from_directory(app.static_folder, "index.html")

# ===============================
# Endpoint de despliegue
# ===============================
@app.route("/deploy", methods=["POST"])
def deploy():
    try:
        data = request.get_json()
        user_prompt = data.get("prompt", "Describe tu rol dentro del equipo solar y confirma que estás listo para iniciar el despliegue.")
        responses = []
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

        for agent in team_data:
            cfg = agent["config"]
            model = cfg["model_client"]["config"]["model"]
            system_msg = cfg["system_message"]
            name = cfg["name"]

            print(f"🚀 Ejecutando {name}...")

            try:
                # Usar el cliente moderno de OpenAI
                client = openai.OpenAI(api_key=OPENAI_API_KEY)
                response = client.chat.completions.create(
                    model=model,
                    messages=[
                        {"role": "system", "content": system_msg},
                        {"role": "user", "content": user_prompt}
                    ]
                )
                msg = response.choices[0].message.content
                responses.append({"agent": name, "response": msg})
                print(f"💬 {name}: {msg[:120]}...")

            except Exception as e:
                responses.append({"agent": name, "error": str(e)})
                print(f"❌ Error en {name}: {e}")

        # Guardar log de respuestas
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

@app.route("/static/<path:filename>")
def static_files(filename):
    return send_from_directory(app.static_folder, filename)

if __name__ == "__main__":
    # Puerto para Render o local
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
