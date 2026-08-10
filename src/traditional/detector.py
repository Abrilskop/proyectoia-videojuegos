import time

from src.core import ADECUADO, GRITO, SPAM, TOXICO, Decision
from src.traditional.rules import (
    SpamTracker,
    load_blacklist,
    load_leet,
    rule1_blacklist,
    rule2_leetspeak,
    rule3_shouting,
)


class TraditionalModerator:
    """Sistema Tradicional (paradigma simbólico / reglas de negocio).

    Regla 1: lista negra de palabras exactas (lista_negra.txt)
    Regla 2: Regex/leetspeak (letras reemplazadas por caracteres especiales)
    Regla 3: Gritar (len > 40 y > 90% en MAYÚSCULAS)
    Regla 4: Spam (mismo string > 5 veces en 10 segundos)
    """

    def __init__(self):
        self.blacklist = load_blacklist()
        self.leet = load_leet()
        self.spam_tracker = SpamTracker()

    def classify(self, message, user_id="anonimo", timestamp=None):
        if timestamp is None:
            timestamp = time.time()

        word = rule1_blacklist(message, self.blacklist)
        if word:
            return Decision(TOXICO, f"Regla 1: palabra '{word}' en lista negra")

        word = rule2_leetspeak(message, self.blacklist, self.leet)
        if word:
            return Decision(TOXICO, f"Regla 2: leetspeak detectado ('{word}')")

        if self.spam_tracker.is_spam(user_id, message, timestamp):
            return Decision(
                SPAM, "Regla 4: mismo mensaje más de 5 veces en 10 segundos"
            )

        if rule3_shouting(message):
            return Decision(GRITO, "Regla 3: mensaje > 40 chars y > 90% en MAYÚSCULAS")

        return Decision(ADECUADO)
