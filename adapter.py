"""
Adapter module to mock Telegram and Trello APIs for local development.
Provides FakeBot, FakeUpdate, and FakeTrello classes for testing without external dependencies.
"""

class FakeBot:
    """Mock Telegram Bot that simulates sending messages."""
    
    def send_message(self, chat_id, text, parse_mode="", reply_markup=None):
        """Simulate sending a message."""
        print(f"[BOT to {chat_id}] {text}")
        # Return a fake message object with message_id
        return type("Message", (), {"message_id": 1})()
    
    def delete_message(self, chat_id, message_id):
        """Simulate deleting a message."""
        print(f"[BOT] Deleted message {message_id} from chat {chat_id}")
        return True
    
    def getFile(self, file_id):
        """Simulate getting a file."""
        return type("File", (), {"file_id": file_id, "download": lambda filename: None})()


class FakeUpdate:
    """Mock Telegram Update with message and chat information."""
    
    def __init__(self, text, chat_id=1):
        self.message = type("msg", (), {
            "text": text,
            "photo": [],
            "caption": None,
            "voice": None,
            "chat": type("chat", (), {"id": chat_id})()
        })()
        self.effective_chat = type("chat", (), {"id": chat_id})()
        self.message.from_user = type("user", (), {"id": chat_id})()


class FakeTrello:
    """Mock Trello API for card operations."""
    
    def __init__(self):
        self.cards = {}
        self.next_id = len(self.cards) + 1


    def add_card(self, text):
        """Create a new card."""
        card_id = self.next_id
        self.cards[card_id] = {"id": card_id, "text": text}
        self.next_id += 1
        print(f"[TRELLO] Card creada: {text}")
        return {"id": card_id, "text": text}
    
    def update_card(self, card_id, new_text):
        """Update an existing card."""
        if card_id in self.cards:
            self.cards[card_id]["text"] = new_text
            print(f"[TRELLO] Card {card_id} actualizada a: {new_text}")
            return {"id": card_id, "text": new_text}
        return None
    
    def delete_card(self, card_id):
        """Delete a card."""
        if card_id in self.cards:
            del self.cards[card_id]
            print(f"[TRELLO] Card {card_id} eliminada")
            return True
        return False


# Global instances
bot = FakeBot()
trello = FakeTrello()


# Helper functions
def send_message(chat_id, text, parse_mode="", reply_markup=None):
    """Send a message through the fake bot."""
    return bot.send_message(chat_id, text, parse_mode, reply_markup)


def receive_message(text, chat_id=1):
    """Simulate receiving a message from user."""
    print(f"[USER {chat_id}] {text}")
    return FakeUpdate(text, chat_id)


def add_card(text):
    """Add a card to fake Trello."""
    return trello.add_card(text)


def update_card(card_id, new_text):
    """Update a Trello card."""
    return trello.update_card(card_id, new_text)


def delete_card(card_id):
    """Delete a Trello card."""
    return trello.delete_card(card_id)

def download_audio(filepath: str):
    # En Telegram se descargaba el archivo desde la nube.
    # En V2 podés simular que ya lo tenés en tu front-end o subirlo manualmente.
    print(f"[AUDIO] Archivo simulado guardado en {filepath}")



# Re-export for convenience
__all__ = [
    'FakeBot',
    'FakeUpdate', 
    'FakeTrello',
    'bot',
    'trello',
    'send_message',
    'receive_message',
    'add_card',
    'update_card',
    'delete_card',
    'download_audio'
]
