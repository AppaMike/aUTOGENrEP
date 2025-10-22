from flask import Flask, request, jsonify
from openai import OpenAI
import json
import datetime
import os

# ================================================
# CONFIGURACIÓN BASE
# ================================================
app = Flask(__name__)

TEAM_FILE = "team-config.json"

# Cargar configuración de agentes
with open(TEAM_FILE, "r", encoding="utf-8") as f:
    team_data = json.load(f)["config"]["participants"]

# ================================================
# ENDPOINT PRINCIPAL
# ================================================
@app.route("/", methods=["GET"])
def home():
    return jsonify({
        "status": "ok",
        "message": "☀️ API de AutoGen Solar Operaciones está activa.",
        "usage": "Envía un POST a /deploy con {'prompt': 'tu mensaje'}"
    })


# ================================================
# ENDPOINT DE DEPLOY
# ================================================
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

            print(f"\n🚀 Ejecutando {name}...")

            try:
                # Crear cliente OpenAI con la nueva sintaxis
                client = OpenAI(api_key=api_key)

                response = client.chat.completions.create(
                    model=model,
                    messages=[
                        {"role": "system", "content": system_msg},
                        {"role": "user", "content": user_prompt}
                    ]
                )

                msg = response.choices[0].message.content
                responses.append({"agent": name, "response": msg})
                print(f"💬 {name}: {msg[:120]}...")  # muestra primer fragmento

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


# ================================================
# SERVIR INTERFAZ WEB (opcional)
# ================================================
@app.route("/chat", methods=["GET"])
def chat_ui():
    return app.send_static_file("index.html")


# ================================================
# EJECUCIÓN LOCAL / RENDER
# ================================================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
