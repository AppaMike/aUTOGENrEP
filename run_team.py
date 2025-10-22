import os
import json
from flask import Flask, request, jsonify
from autogen_agentchat.teams import TeamManager
from autogen_agentchat.models.openai import OpenAIChatCompletionClient

app = Flask(__name__)

# === Cargar la configuración del equipo ===
with open("team-config.json", "r", encoding="utf-8") as f:
    team_config = json.load(f)

# === Función para crear el cliente OpenAI ===
def create_model_client(model_cfg):
    return OpenAIChatCompletionClient(
        model=model_cfg["model"],
        api_key=os.getenv("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", model_cfg.get("api_key"))
    )

# === Inicializar el equipo ===
team = TeamManager.from_config_dict(team_config)

# === Endpoint principal ===
@app.route("/chat", methods=["POST"])
def chat():
    try:
        data = request.get_json()
        user_message = data.get("message", "")

        if not user_message:
            return jsonify({"error": "No se recibió mensaje"}), 400

        response = team.step(input=user_message)
        return jsonify({"response": response})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# === Endpoint de prueba ===
@app.route("/")
def home():
    return "✅ Servidor Flask con AutoGen activo y listo."

# === Ejecutar localmente o en Render ===
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    app.run(host="0.0.0.0", port=port)


