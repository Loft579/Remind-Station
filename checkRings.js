function checkRings() {
  const now = Date.now();
  document.querySelectorAll(".card").forEach(card => {
    let start = parseInt(card.dataset.startAt);
    const delay = parseInt(card.dataset.delay || 0);
    const countdownEl = card.querySelector(".countdown");

    if (delay > 0) {
      // avanzar start hasta el ciclo actual
      const start_old = start;
      while (start + delay <= now) {
        start += delay;
      }
      const nextRing = start + delay;
      const remaining = nextRing - now;

      if (start !== start_old) {
        // suena
        cardsContainer.prepend(card);
        card.dataset.startAt = start; // ojo: se acumula, no se reinicia
        if (Notification.permission === "granted") {
          new Notification(`pedido_${card.dataset.id} está sonando!`);
          const audio = new Audio("ding.mp3"); // poné tu archivo de sonido
          audio.play(); }
        }
      
      // mostrar contador
      const seconds = Math.floor(remaining / 1000) % 60;
      const minutes = Math.floor(remaining / 60000) % 60;
      const hours = Math.floor(remaining / 3600000);
      countdownEl.textContent = `${hours}h ${minutes}m ${seconds}s`;

      // aplicar transparencia según cuánto pasó desde el último ring
      const elapsed = now - start; // tiempo desde el último ciclo
      if (elapsed <= 60000) {
        const opacity = 1 - (elapsed / 60000) * 0.8;
        countdownEl.style.opacity = opacity;
      } else {
        countdownEl.style.opacity = 0.2;
      }
    }
  });
}