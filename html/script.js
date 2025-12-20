const valueDiv = document.getElementById("value");
const button = document.getElementById("btn");

const ws = new WebSocket(`ws://${location.host}/ws`);

ws.onmessage = (event) => {
    const data = JSON.parse(event.data);

    if (data.type === "sensor") {
        valueDiv.textContent = data.value;
    }
};

button.onclick = () => {
    ws.send(JSON.stringify({
        type: "button"
    }));
};
