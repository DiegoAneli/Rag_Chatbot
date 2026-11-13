// Recuperiamo gli elementi HTML
const form = document.querySelector("#chat-form");
const input = document.querySelector("#message");
const messages = document.querySelector("#messages");
const button = form.querySelector("button");

// Funzione per aggiungere un messaggio alla chat
function addMessage(text, role) {

    const div = document.createElement("div");

    div.className = `message ${role}`;

    // textContent evita di interpretare HTML
    div.textContent = text;

    messages.appendChild(div);

    messages.scrollTop = messages.scrollHeight;

    return div;
}

// Gestione dell'invio del messaggio
form.addEventListener("submit", async (event) => {

    event.preventDefault();

    const message = input.value.trim();

    if (!message) return;

    addMessage(message, "user");

    input.value = "";
    button.disabled = true;

    const placeholder = addMessage(
        "Sto elaborando la risposta...",
        "bot"
    );

    try {

        // Richiesta HTTP al backend Python
        const response = await fetch("/api/chat", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                message: message
            })
        });

        if (!response.ok) {
            throw new Error("Errore nella richiesta");
        }

        const data = await response.json();

        placeholder.textContent = data.answer;

    } catch (error) {

        placeholder.textContent =
            "Errore: impossibile ottenere la risposta.";

        console.error(error);

    } finally {

        button.disabled = false;
        input.focus();

    }
});
