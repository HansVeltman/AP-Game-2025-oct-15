(() => {
  // ====== helpers / DOM ======
  const $ = (sel) => document.querySelector(sel);
  const statusEl = $("#status");
  const logEl = $("#log");
  const canvas = document.getElementById("TheMainArea");
  const ctx = canvas.getContext("2d");

  const log = (t) => { if (logEl) logEl.textContent += t + "\n"; };

  // ====== WebSocket URL (prod = WSS) ======
  // Zet voor definitieve productie de host op 'api.thealignmentgame.com'
  const PROD_WS_HOST = 'api.thealignmentgame.com';      // ← definitief subdomein
  // Voor directe Render-test kun je tijdelijk deze gebruiken:
  // const PROD_WS_HOST = 'ap-game-2025-oct-15.onrender.com';

  const WS_URL =
    (location.hostname === 'localhost' || location.hostname === '127.0.0.1')
      ? 'ws://localhost:8765/'
      : `wss://${PROD_WS_HOST}/`; // trailing slash zodat upgrade op "/" plaatsvindt

  const ws = new WebSocket(WS_URL);
  ws.binaryType = "arraybuffer";

  ws.addEventListener("open",  () => { if (statusEl) statusEl.textContent = "WS open";     log("🎉 Verbonden met backend"); });
  ws.addEventListener("close", (e) => { if (statusEl) statusEl.textContent = "WS gesloten"; log(`🔌 Verbinding gesloten (${e.code})`);   });
  ws.addEventListener("error", (e) => { if (statusEl) statusEl.textContent = "WS fout";     log("⚠️ WebSocket fout"); console.log(e);   });

  // ====== kleine util om op 1 passend antwoord te wachten ======
  function waitForOnce(filterFn, timeoutMs = 7000) {
    return new Promise((resolve, reject) => {
      const timer = setTimeout(() => {
        ws.removeEventListener('message', onMsg);
        reject(new Error('timeout waiting for WS response'));
      }, timeoutMs);

      function onMsg(e) {
        try {
          if (typeof e.data !== "string") return;
          const data = JSON.parse(e.data);
          if (filterFn(data)) {
            clearTimeout(timer);
            ws.removeEventListener('message', onMsg);
            resolve(data);
          }
        } catch (_) {}
      }

      ws.addEventListener('message', onMsg);
    });
  }

  // ====== WS: asset via JSON ophalen → Blob URL → tekenen op canvas ======
  async function fetchAssetAsObjectURL(name) {
    const req = { type: 'asset', name };
    ws.send(JSON.stringify(req));
    const res = await waitForOnce(d => d.type === 'asset' && d.name === name);
    const b64 = res.data_b64;
    const mime = res.mime || 'application/octet-stream';

    // base64 → bytes → Blob
    const bin = atob(b64);
    const len = bin.length;
    const bytes = new Uint8Array(len);
    for (let i = 0; i < len; i++) bytes[i] = bin.charCodeAt(i);
    const blob = new Blob([bytes], { type: mime });
    return URL.createObjectURL(blob); // vergeet evt. later niet te revoken
  }

  async function drawAssetOnCanvas(name) {
    try {
      const url = await fetchAssetAsObjectURL(name);
      await new Promise((resolve, reject) => {
        const img = new Image();
        img.onload = () => {
          // canvas vullen (desnoods schaal je met aspect-ratio zoals gewenst)
          ctx.clearRect(0, 0, canvas.width, canvas.height);
          ctx.drawImage(img, 0, 0, canvas.width, canvas.height);
          resolve();
          // URL.revokeObjectURL(url); // optioneel na tekenen
        };
        img.onerror = reject;
        img.src = url;
      });
      log(`🖼️ getekend: ${name}`);
    } catch (e) {
      log(`❌ kon asset niet tekenen: ${name} (${e.message})`);
      console.error(e);
    }
  }

  // ====== init: toon Start.png via WS ======
  ws.addEventListener('open', () => {
    // pas tekenen ná open, anders kan je eerste request racen met de handshake
    drawAssetOnCanvas('Start.png');
  });

  // ====== UI: logo click → terug naar start + optioneel bericht naar backend ======
  const logoEl = document.querySelector(".logo");
  if (logoEl) {
    logoEl.addEventListener("click", (e) => {
      e.preventDefault();
      log("🖱️ Logo → Start");
      drawAssetOnCanvas('Start.png');
      // Je bestaande protocol aanroepen blijft mogelijk:
      send({ messagetype: "SHOWSTART", numbers: {}, texts: {} });
    });
  } else {
    log("⚠️ .logo niet gevonden");
  }

  // ====== send helper (voor jouw bestaande 'messagetype'-berichten) ======
  function send(obj) {
    if (ws.readyState === WebSocket.OPEN) {
      ws.send(JSON.stringify(obj));
    } else {
      log("❌ Kan niet versturen: WS niet open");
    }
  }

  // ====== optioneel: bestaande renderer (als je die gebruikt) ======
  // Zorg dat DrawCanvas en AddPuzzle via <script> geladen zijn vóór dit script.
  const renderer = (window.DrawCanvas && typeof window.DrawCanvas.createRenderer === 'function')
    ? window.DrawCanvas.createRenderer(canvas)
    : null;

  // Berichten van backend verwerken
  ws.addEventListener("message", async (ev) => {
    if (typeof ev.data !== "string") return;
    const msg = JSON.parse(ev.data);

    // demo: ping/pong laten zien
    if (msg.type === "pong") {
      log("🏓 pong");
      return;
    }

    // jouw eerdere RUNSIMULATION-logica behouden
    if (msg.messagetype === "RUNSIMULATION") {
      const simDayNumber = Array.isArray(msg.numbers) ? (msg.numbers[0] ?? 0) : 0;
      const now = new Date();
      const simDate = new Date(now.getFullYear(), now.getMonth(), now.getDate() + simDayNumber);
      const h3 = document.querySelector('h3');
      if (h3) {
        const formatted = simDate.toLocaleDateString(undefined, { year: '2-digit', month: 'short', day: '2-digit' });
        h3.textContent = `Date: ${formatted} (days simulated: ${simDayNumber})`;
      }
      log(`▶️ Simulation → day counter = ${simDayNumber}`);
      return;
    }

    // renderers (als aanwezig) voor je eigen tekenprotocol
    if (renderer) {
      await renderer.render(msg);
    } else {
      // fallback: log alles
      log(`📩 WS message: ${JSON.stringify(msg).slice(0, 300)}`);
    }
  });

  // ====== demo: ping bij open ======
  ws.addEventListener('open', () => {
    ws.send(JSON.stringify({ type: 'ping' }));
    console.log('WS open, nu Start.png via WS ophalen…');
    drawAssetOnCanvas('Start.png');  // <- dit doet de WS-aanvraag
  });

  ws.addEventListener('message', (e) => {
  if (typeof e.data === 'string') {
    try {
      const msg = JSON.parse(e.data);
      if (msg.type === 'asset') {
        console.log('WS asset ontvangen:', msg.name, msg.mime, (msg.data_b64 || '').length, 'bytes(b64)');
      }
    } catch {}
  }});


  async function setLogoFromWS() {
    try {
      const url = await fetchAssetAsObjectURL('logo.png'); // moet bestaan in backend/assets/logo.png
      const logoEl = document.querySelector('.logo');
      if (logoEl) {
        logoEl.src = url;
        console.log('Logo via WS gezet');
      } else {
        console.warn('Geen .logo element gevonden');
      }
    } catch (e) {
      console.error('Logo via WS laden faalde:', e);
    }
  }

  // start ‘m zodra WS open is (of na Start.png tekenen):
  ws.addEventListener('open', () => {
    setLogoFromWS();
  });


  // ====== Admin knoppen (indien aanwezig in DOM) ======
  function bindClick(id, days, label) {
    const el = document.getElementById(id);
    if (!el) return;
    el.addEventListener("click", (e) => {
      e.preventDefault();
      log(`🕒 RUNSIMULATION → ${label}`);
      send({ messagetype: "RUNSIMULATION", numbers: [days], texts: [label] });
    });
  }
  bindClick("run-day",   1,   "Run one day");
  bindClick("run-week",  7,   "Run one week");
  bindClick("run-month", 30,  "Run one month");
  bindClick("run-year",  365, "Run one year");

  // Reset knop (als aanwezig)
  const resetEl = document.getElementById("Resetsim");
  if (resetEl) {
    resetEl.addEventListener("click", (e) => {
      e.preventDefault();
      log("🔁 Reset simulation");
      send({ messagetype: "RUNSIMULATION", numbers: [-1], texts: ["Reset the simulation"] });
      drawAssetOnCanvas('Start.png');
    });
  }
})();
