// instruments data
const instruments = [
  { id: 'guitar', name: 'Guitare', icon: '🎸' },
  { id: 'piano',  name: 'Piano',  icon: '🎹' },
  { id: 'drums',  name: 'Batterie', icon: '🥁' },
  { id: 'bass',   name: 'Basse',  icon: '🎸' },
  { id: 'synth',  name: 'Synthé', icon: '🎛️' },
];

const listEl = document.getElementById('instrumentsList');
let selectedIndex = 0;

const playBtn = document.getElementById('playMusic');

// create DOM cards
instruments.forEach((ins, i) => {
  const el = document.createElement('div');
  el.className = 'instrument-card';
  el.dataset.index = i;
  el.innerHTML = `<div class="icon">${ins.icon}</div><div class="name">${ins.name}</div>`;
  //el.innerHTML = `<div class="name">${ins.name}</div>`;
  listEl.appendChild(el);
});

// render function: positions the cards around selectedIndex
function renderInstruments(selected) {
  const cards = Array.from(document.querySelectorAll('.instrument-card'));
  const centerY = listEl.clientHeight / 2;
  const gap = 78; // vertical gap between center positions (px) - tune it
  cards.forEach(card => {
    const i = Number(card.dataset.index);
    const d = i - selected;               // distance from center
    const y = centerY + d * gap;         // target center position
    const absd = Math.abs(d);

    // compute scale and opacity based on distance
    const scale = Math.max(0.5, 1 - 0.18 * absd);       // center=1, others shrink
    const opacity = Math.max(0.18, 1 - 0.28 * absd);    // center=1, far = faded
    const z = 100 - absd;

    // translate so that item is centered vertically at y
    card.style.transform = `translateX(-50%) translateY(${y - card.clientHeight/2}px) scale(${scale})`;
    card.style.opacity = opacity;
    card.style.zIndex = z;
    // add blur to far items
    card.style.filter = absd === 0 ? 'none' : `blur(${Math.min(3, absd * 0.6)}px)`;
  });
}

// initial render (wait for layout)
window.addEventListener('load', () => {
  renderInstruments(selectedIndex);
  window.addEventListener('resize', () => renderInstruments(selectedIndex));
});

// helper to change selection with bounds
function changeSelection(delta) {
  selectedIndex = Math.max(0, Math.min(instruments.length - 1, selectedIndex + delta));
  renderInstruments(selectedIndex);
  // TODO: trigger audio / update server about instrument change
  console.log('selection ->', selectedIndex, instruments[selectedIndex].name);
}

/* ===== joystick handling =====
   we expect messages like: {type:"joystick", code:"ABS_Y", state: <0..255>}
   We'll use thresholds and debouncing.
*/
const UP_THRESHOLD = 60;
const DOWN_THRESHOLD = 200;
let heldUp = false;
let heldDown = false;
let repeatTimer = null;
const REPEAT_DELAY = 400; // ms before auto-repeat starts
const REPEAT_INTERVAL = 150; // ms between repeats

function joystickMoveUpOnce() {
  changeSelection(-1);
}
function joystickMoveDownOnce() {
  changeSelection(1);
}
function startAutoRepeat(dir) {
  // dir: -1 up, +1 down
  if (repeatTimer) clearInterval(repeatTimer);
  repeatTimer = setInterval(() => changeSelection(dir), REPEAT_INTERVAL);
}
function stopAutoRepeat() {
  if (repeatTimer) {
    clearInterval(repeatTimer);
    repeatTimer = null;
  }
}

// Suppose you already have a WebSocket `ws` that receives events:
const ws = new WebSocket(`ws://${location.host}/ws`);
ws.onopen = () => console.log('WS connected');
ws.onmessage = (evt) => {
  let msg = {};
  try { msg = JSON.parse(evt.data); } catch(e){ return; }

  // sensor update (if any)
  if (msg.type === 'sensor') {
    // ...
  }

  // joystick events
  if (msg.type === 'joystick' && msg.code === 'ABS_Y') {
    const s = msg.state;
    // up pressed
    if (s <= UP_THRESHOLD) {
      if (!heldUp) {
        heldUp = true;
        joystickMoveUpOnce();
        // start repeating after a delay
        setTimeout(() => {
          if (heldUp) startAutoRepeat(-1);
        }, REPEAT_DELAY);
      }
    }
    // down pressed
    else if (s >= DOWN_THRESHOLD) {
      if (!heldDown) {
        heldDown = true;
        joystickMoveDownOnce();
        setTimeout(() => {
          if (heldDown) startAutoRepeat(1);
        }, REPEAT_DELAY);
      }
    }
    // neutral
    else {
      if (heldUp || heldDown) {
        heldUp = false;
        heldDown = false;
        stopAutoRepeat();
      }
    }
  }
};

// fallback keyboard for testing
window.addEventListener('keydown', (e) => {
  if (e.key === 'ArrowUp') changeSelection(-1);
  if (e.key === 'ArrowDown') changeSelection(1);
});

playBtn.addEventListener('click', () => {
  const instrument = instruments[selectedIndex].name;

  ws.send(JSON.stringify({
    type: "play",
    instrument: instrument
  }));

  console.log("Play request sent for", instrument);
});

ws.onmessage = (e) => {
  console.log("Message reçu :", e.data);
  const data = JSON.parse(e.data);

  console.log("Type de message :", data.type);

  if (data.type === "connection") {
    ws.send(JSON.stringify({
      type: "connection", 
      msg: "Pong"
    }));

  }
};
