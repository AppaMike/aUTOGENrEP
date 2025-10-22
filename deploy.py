import json
import openai
import datetime

# ============================
# CONFIGURACIÓN INICIAL
# ============================

TEAM_FILE = "team-config.json"
LOG_FILE = f"deploy_log_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"

# ============================
# FUNCIONES DE UTILIDAD
# ============================

def log_message(message):
    """Guarda mensajes en un archivo de log."""
    with open(LOG_FILE, "a", encoding="utf-8") as log:
        log.write(message + "\n")

def run_agent(agent, prompt):
    """Ejecuta un agente de OpenAI con su configuración local."""
    cfg = agent["config"]
    model = cfg["model_client"]["config"]["model"]
    api_key = cfg["model_client"]["config"]["api_key"]
    system_msg = cfg["system_message"]
    name = cfg["name"]

    openai.api_key = api_key
    print(f"\n🤖 {name} ({model}) responde...")

    try:
        response = openai.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_msg},
                {"role": "user", "content": prompt}
            ]
        )
        msg = response.choices[0].message.content
        print(f"💬 {name}: {msg}")
        log_message(f"{name}: {msg}\n")
    except Exception as e:
        print(f"❌ Error en {name}: {e}")
        log_message(f"Error en {name}: {e}\n")

# ============================
# PROCESO PRINCIPAL
# ============================

def main():
    print("💬 Iniciando despliegue del equipo AutoGen (modo independiente)...")

    try:
        with open(TEAM_FILE, "r", encoding="utf-8") as f:
            team_data = json.load(f)

        if "config" not in team_data or "participants" not in team_data["config"]:
            print("❌ Error: No se encontraron participantes en el archivo de configuración.")
            return

        participants = team_data["config"]["participants"]

        print("✅ Formato moderno detectado (config.participants).")
        print("⚙️ Equipo cargado correctamente.\n")

        # Mensaje de inicio grupal
        intro_prompt = (
            "Eres parte del equipo solar de Equity Solar. "
            "Cada agente debe describir su rol y confirmar que está listo para iniciar el despliegue automático del proyecto solar."
        )

        # Ejecutar cada agente
        for agent in participants:
            run_agent(agent, intro_prompt)

        print("\n✅ Despliegue completado.")
        print(f"📁 Log guardado en: {LOG_FILE}")

    except FileNotFoundError:
        print(f"❌ No se encontró el archivo: {TEAM_FILE}")
    except json.JSONDecodeError:
        print("❌ Error: El archivo JSON tiene formato inválido.")
    except Exception as e:
        print(f"❌ Error general: {e}")

# ============================
# EJECUCIÓN
# ============================

if __name__ == "__main__":
    main()
