// local_adapter.js
function send_message(text) {
  // reemplaza bot.send_message
  const chat = document.getElementById("chat");
  chat.innerHTML += `<div class="bot">${text}</div>`;
}

function receive_message(text) {
  // reemplaza update.message.text
  handleCommand(text);
}

function create_card(text) {
  // reemplaza trello.create_card
  const card = { id: Date.now(), text };
  cards.push(card);
  renderCards();
}

function list_cards() {
  return cards;
}

function delete_card(id) {
  cards = cards.filter(c => c.id !== id);
  renderCards();
}
