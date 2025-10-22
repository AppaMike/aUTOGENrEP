const form = document.getElementById("chat-form");
const input = document.getElementById("user-input");
const chatBox = document.getElementById("chat-box");

form.addEventListener("submit", async (e) => {
  e.preventDefault();
  const text = input.value.trim();
  if (!text) return;

  appendMessage("user", text);
  input.value = "";

  appendMessage("agent", "⏳ Procesando solicitud...");

  try {
    const res = await fetch("/deploy", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ prompt: text }),
    });

    const data = await res.json();
    chatBox.lastChild.remove(); // elimina el mensaje de espera

    if (data.status === "success") {
      data.responses.forEach((r) => {
        const msg = r.response
          ? `🤖 <strong>${r.agent}</strong>: ${r.response}`
          : `⚠️ <strong>${r.agent}</strong> Error: ${r.error}`;
        appendMessage("agent", msg, true);
      });
    } else {
      appendMessage("error", "❌ Error en el servidor: " + data.message);
    }
  } catch (err) {
    chatBox.lastChild.remove();
    appendMessage("error", "⚠️ Error de conexión: " + err.message);
  }
});

function appendMessage(role, text, isHTML = false) {
  const div = document.createElement("div");
  div.classList.add("message", role);
  if (isHTML) div.innerHTML = text;
  else div.textContent = text;
  chatBox.appendChild(div);
  chatBox.scrollTop = chatBox.scrollHeight;
}
