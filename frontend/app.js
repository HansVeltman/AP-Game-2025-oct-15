(() => { // arrow IIFE om scope te beperken, wordt direct uitgevoerd
  // Belangrijk: addpuzzle.js al is geladen via een <script> tag
  const $ = (sel) => document.querySelector(sel);
  const statusEl = $("#status");
  const logEl = $("#log");

  const canvas = document.getElementById("TheMainArea");
  const ctx = canvas.getContext("2d");

  const log = (t) => { logEl.textContent += t + "\n"; };


  function drawImageOnCanvas(url) {
    const img = new Image();
    img.onload = () => {
      ctx.clearRect(0, 0, canvas.width, canvas.height); //  eerst wissen
      ctx.drawImage(img, 0, 0, canvas.width, canvas.height);  // Vul het hele canvas (pas dit aan als je aspect-ratio wilt bewaren)
    };
    img.src = url;
  }

  drawImageOnCanvas("assets/Start.png"); // Toon startbeeld bij laden

  document.querySelector(".logo")?.addEventListener("click", (e) => { // Klik op logo => opnieuw Start.png tonen
    e.preventDefault();
    drawImageOnCanvas("assets/Start.png");
  });

  const logoEl = document.querySelector(".logo");
  if (logoEl) {
    logoEl.addEventListener("click", (e) => {
      e.preventDefault();
      log("🖱️ Logo clicked → terug naar start");
      drawImageOnCanvas("assets/Start.png");
      // optioneel: laat de backend ook weten dat we resetten
      // send(JSON.stringify({ type: "reset" }));
      }); } 
    else {log("⚠️ .logo niet gevonden"); }
  
  // 1 CReate WebSocket also for GitHUb
  const WS_URL = (location.hostname === "localhost" || location.hostname === "127.0.0.1")
  ? "ws://localhost:8765"
  : 'wss://' + PROD_WS_HOST;  // test even direct op render.com
  // : "wss://api.thealignmentgame.com";  // Productie
  const ws = new WebSocket(WS_URL);


  ws.binaryType = "arraybuffer";
  ws.addEventListener("open",  () => { statusEl.textContent = "WS open";     log("🎉 Verbonden met backend"); });
  ws.addEventListener("close", () => { statusEl.textContent = "WS gesloten"; log("🔌 Verbinding gesloten");   });
  ws.addEventListener("error", () => { statusEl.textContent = "WS fout";     log("⚠️ WebSocket fout");        });

  const send = (obj) => {
    if (ws.readyState === WebSocket.OPEN) {
      ws.send(JSON.stringify(obj));
    } else {
      log("❌ Kan niet versturen: WS niet open");
    }
  };

  const renderer = DrawCanvas.createRenderer(canvas); // 3) Renderer aanmaken vóórdat we WS-berichten verwerken
  ws.addEventListener("message", async (ev) => {
    if (typeof ev.data !== "string") return;
    const msg = JSON.parse(ev.data);
    if (msg.messagetype === "RUNSIMULATION") {
      const simDayNumber = Array.isArray(msg.numbers) ? (msg.numbers[0] ?? 0) : 0;
      const now = new Date();               // ← dit leest ‘nu’ van de computer (browser)
      const simDate = new Date(
        now.getFullYear(),
        now.getMonth(),
        now.getDate() + simDayNumber        // actuele dag + SimDayNumber
      );
      const h3 = document.querySelector('h3');
      if (h3) {
        const df = new Intl.DateTimeFormat(undefined, { year: '2-digit', month: 'short', day: '2-digit' });
        const parts = Object.fromEntries(df.formatToParts(simDate).map(p => [p.type, p.value]));
        const formatted = `${parts.year} ${parts.month} ${parts.day}`; // → bv. "25 Oct 14" / "25 okt 14"
        h3.textContent = `Date: ${formatted} (days simulated: ${simDayNumber})`;
      }

const formatted = simDate.toLocaleDateString(undefined, { year: '2-digit', month: 'short', day: '2-digit' });
h3.textContent = `Date: ${formatted} (days simulated: ${simDayNumber})`;

      log(`▶️ Simulation: ${msg.texts?.[0] || 'ok'} → day counter = ${simDayNumber}`);
      // No drawing needed; stop here.
      return;
    }
    await renderer.render(msg);
  });

    
  const logoLink = document.querySelector(".logo"); // 4) Logo click → SHOWSTART naar backend
  if (logoLink) {
    logoLink.addEventListener("click", (e) => {
      e.preventDefault();
      log("🖱️ Logo → SHOWSTART");
      send({ messagetype: "SHOWSTART", numbers: {}, texts: {} });
    });
  } else {
    log("⚠️ .logo niet gevonden");
  }

  // 5) Nu pas de puzzle initialiseren — send en ws bestaan nu
  AddPuzzle.init({ imgEl: canvas, send, ws, onClick: (key, msgType) => log(`🧩 Puzzle clicked → ${key} (${msgType})`) });

  // Administrators submenu → run: day
  const runDayLink = document.getElementById("run-day");
  if (runDayLink) {
    runDayLink.addEventListener("click", (e) => {
      e.preventDefault();
      log("🕒 RUNSIMULATION → one day");
      send({ messagetype: "RUNSIMULATION", numbers: [1], texts: ["Run one day"] });
    });
  }

  // Administrators submenu → run: week
  const runWeekLink = document.getElementById("run-week");
  if (runWeekLink) {
    runWeekLink.addEventListener("click", (e) => {
      e.preventDefault();
      log("🕒 RUNSIMULATION → one week");
      send({ messagetype: "RUNSIMULATION", numbers: [7], texts: ["Run one day"] });
    });
  }

    // Administrators submenu → run: month
  const runMonthLink = document.getElementById("run-month");
  if (runMonthLink) {
    runMonthLink.addEventListener("click", (e) => {
      e.preventDefault();
      log("🕒 RUNSIMULATION → one month");
      send({ messagetype: "RUNSIMULATION", numbers: [30], texts: ["Run one month"] });
    });
  }
    // Administrators submenu → run: year
  const runYearLink = document.getElementById("run-year");
  if (runYearLink) {
    runYearLink.addEventListener("click", (e) => {
      e.preventDefault();
      log("🕒 RUNSIMULATION → one year");
      send({ messagetype: "RUNSIMULATION", numbers: [365], texts: ["Run one year"] });
    });
  }

  Resetsim
  // Administrators submenu → Resetsim
  const ResetsimLink = document.getElementById("Resetsim");
  if (ResetsimLink) {
     ResetsimLink.addEventListener("click", (e) => {
      e.preventDefault();
      log("🕒 RUNSIMULATION → Reset simumaltion");
      send({ messagetype: "RUNSIMULATION", numbers: [-1], texts: ["Reset the simumaltion"] });
    });
  }


})();
