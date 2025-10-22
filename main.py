from flask import Flask, request, jsonify
import json
import openai
import datetime

# ================================================
# CONFIGURACIÓN BASE
# ================================================
app = Flask(__name__)

TEAM_FILE = "team-config.json"

# Cargar agentes desde el archivo
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

            openai.api_key = api_key
            print(f"\n🚀 Ejecutando {name}...")

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
# EJECUCIÓN LOCAL
# ================================================
if __name__ == "__main__":
    # host=0.0.0.0 para que Render lo vea
    app.run(host="0.0.0.0", port=8080)
