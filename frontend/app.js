(() => {
  // ====== helpers / DOM ======
  const $ = (sel) => document.querySelector(sel);
  const statusEl = $("#status");
  const logEl = $("#log");
  const canvas = document.getElementById("TheMainArea");
  const ctx = canvas.getContext("2d");

  // Renderer beschikbaar maken voor de hele module
  let renderer = null;
  if (window.DrawCanvas && typeof window.DrawCanvas.createRenderer === 'function') {
    renderer = window.DrawCanvas.createRenderer(canvas);
  }

  const log = (t) => { if (logEl) logEl.textContent += t + "\n"; };

  // ====== WebSocket URL (prod = WSS) ======
  const PROD_WS_HOST = 'api.thealignmentgame.com';      // ← definitief subdomein // Zet voor definitieve productie de host op 'api.thealignmentgame.com'
  // const PROD_WS_HOST = 'ap-game-2025-oct-15.onrender.com'; // Voor directe Render-test kun je tijdelijk deze gebruiken:

  const WS_URL = // NEW
    (location.hostname === 'localhost' || location.hostname === '127.0.0.1')
      ? 'ws://localhost:8765/'
      : `wss://${PROD_WS_HOST}/`; // trailing slash zodat upgrade op "/" plaatsvindt

  // ====== WEBSOCKET AANMAKEN  met log-listeners
  const ws = new WebSocket(WS_URL);
  ws.binaryType = "arraybuffer";
  ws.addEventListener("open",  () =>  { if (statusEl) statusEl.textContent = "WS open";     log("🎉 Verbonden met backend"); });
  ws.addEventListener("close", (e) => { if (statusEl) statusEl.textContent = "WS gesloten"; log(`🔌 Verbinding gesloten (${e.code})`);   });
  ws.addEventListener("error", (e) => { if (statusEl) statusEl.textContent = "WS fout";     log("⚠️ WebSocket fout"); console.log(e);   });

  ws.addEventListener('open', () => {  // ====== init: toon Start.png via WS ======
    drawAssetOnCanvas('Start.png'); // pas tekenen ná open, anders kan je eerste request racen met de handshake
  });

  //========= diverse helperfuncties =====================

  const logoEl = document.querySelector(".logo"); // ====== UI: logo click → terug naar start + optioneel bericht naar backend ======
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


  //  TEKENFUNCTIES EN AFBEELDINGEN OPHALEN ============

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
    const bin = atob(b64);  // base64 → bytes → Blob
    const len = bin.length;
    const bytes = new Uint8Array(len);
    for (let i = 0; i < len; i++) bytes[i] = bin.charCodeAt(i);
    const blob = new Blob([bytes], { type: mime });
    return URL.createObjectURL(blob); // vergeet evt. later niet te revoken
  }

async function drawAssetOnCanvas(name) {
  try {
    const url = await fetchAssetAsObjectURL(name); // maak er een object van

    // 2) canvas tekenen
    const img = await new Promise((resolve, reject) => {
      const im = new Image();
      im.onload = () => resolve(im);
      im.onerror = reject;
      im.src = url;
    });

    // vul de canvas en teken strak op formaat
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    ctx.drawImage(img, 0, 0, canvas.width, canvas.height);
    console.log('🖼️ getekend op canvas:', name);
    } catch (e) {
    console.error(`❌ kon asset niet tekenen: ${name}`, e);
    } 
  }   


  //  ==== ACTIES: klik op logo of in menu ======

  async function setLogoFromWS() {
    try {
      const url = await fetchAssetAsObjectURL('logo.png'); // komt uit backend/assets/logo.png

      // Pak het echte IMG-element, niet de <a>
      const logoEl = document.querySelector('img.logo-img')    // als je variant 1 gebruikte
                    || document.getElementById('logo-img');    // of variant 2

      if (!logoEl) {
        console.warn('Geen logo <img> element gevonden');
        return;
      }

      logoEl.src = url;
      console.log('✅ Logo via WS gezet');
    } catch (e) {
      console.error('❌ Logo via WS laden faalde:', e);
    }
  }

  // Na ws.open aanroepen:
  ws.addEventListener('open', () => {
    console.log('WS open, nu Start.png via WS ophalen…');
    // drawAssetOnCanvas('Start.png');  // <- zorg dat deze functie bestaat (zie hieronder)
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
  bindClick("Resetsim",  -1,  "Reset simulation");

})();
