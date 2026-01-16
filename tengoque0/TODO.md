# V3 Migración de Remind-Station sin Telegram ni Trello

Objetivo:
- Crear un archivo `adapter.py` que contenga mocks de Telegram y Trello.
- Reemplazar en todo el repo los imports de `telegram` y `trello` por `adapter`.
- Redirigir todas las llamadas a:
  - `context.bot.send_message(...)` → `adapter.send_message(...)`
  - `update.message.text` → `adapter.receive_message(...)`
  - `trello.add_card(...)` → `adapter.add_card(...)`
  - `trello.update_card(...)` → `adapter.update_card(...)`
  - `trello.delete_card(...)` → `adapter.delete_card(...)`

Especificaciones de `adapter.py`:
```python
class FakeBot:
    def send_message(self, chat_id, text):
        print(f"[BOT to {chat_id}] {text}")

class FakeUpdate:
    def __init__(self, text, chat_id=1):
        self.message = type("msg", (), {"text": text})
        self.effective_chat = type("chat", (), {"id": chat_id})

class FakeTrello:
    def add_card(self, text):
        print(f"[TRELLO] Card creada: {text}")
        return {"id": 1, "text": text}

    def update_card(self, card_id, new_text):
        print(f"[TRELLO] Card {card_id} actualizada a: {new_text}")

    def delete_card(self, card_id):
        print(f"[TRELLO] Card {card_id} eliminada")

bot = FakeBot()
trello = FakeTrello()

def send_message(text):
    bot.send_message(chat_id=1, text=text)

def receive_message(text):
    print(f"[USER] {text}")

def add_card(text):
    return trello.add_card(text)

def update_card(card_id, new_text):
    return trello.update_card(card_id, new_text)

def delete_card(card_id):
    return trello.delete_card(card_id)
