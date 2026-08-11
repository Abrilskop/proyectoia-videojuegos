import time
from pathlib import Path

import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.bot.moderator import ChatModerator
from src.bot.store import Store


class StubAI:
    def __init__(self, rules):
        self.rules = rules

    def predict_proba(self, text):
        for needle, prob in self.rules:
            if needle in text:
                return prob
        return 0.05

    def adjust_by_reputation(self, prob, reputation=0.5):
        return prob


def make_moderator(ai=None, umbral_bloqueo=0.80, umbral_revision=0.50):
    return ChatModerator(
        ai=ai,
        store=Store(":memory:"),
        umbral_bloqueo=umbral_bloqueo,
        umbral_revision=umbral_revision,
    )


def test_tradicional_bloquea_insulto():
    mod = make_moderator(ai=StubAI([]))
    r = mod.moderate("eres un idiota", guild_id="g", user_id="u")
    assert r.block, r
    assert r.source == "tradicional"


def test_tradicional_bloquea_leetspeak():
    mod = make_moderator(ai=StubAI([]))
    r = mod.moderate("1d10t4", guild_id="g", user_id="u")
    assert r.block, r


def test_tradicional_advierte_grito():
    mod = make_moderator(ai=StubAI([]))
    r = mod.moderate(
        "VAMOS EQUIPO A GANAR ESTA PARTIDA AHORA MISMO YA!",
        guild_id="g",
        user_id="u",
    )
    assert r.action == "advertencia", r


def test_tradicional_bloquea_spam():
    mod = make_moderator(ai=StubAI([]))
    t0 = time.time()
    r = None
    for i in range(6):
        r = mod.moderate("jajaja", guild_id="g", user_id="u", timestamp=t0 + i * 0.1)
    assert r.block, r
    assert r.source == "tradicional"


def test_ia_aprueba_probabilidad_baja():
    mod = make_moderator(ai=StubAI([("sospechoso", 0.9)]))
    r = mod.moderate("buena partida", guild_id="g", user_id="u")
    assert r.action == "ok", r
    assert r.source == "ia"


def test_ia_envia_revision_humana():
    mod = make_moderator(ai=StubAI([("sospechoso", 0.6)]))
    r = mod.moderate("mensaje sospechoso", guild_id="g", user_id="u")
    assert r.needs_review, r
    assert r.source == "ia"


def test_ia_bloquea_probabilidad_alta():
    mod = make_moderator(ai=StubAI([("sospechoso", 0.95)]))
    r = mod.moderate("mensaje sospechoso", guild_id="g", user_id="u")
    assert r.block, r
    assert r.source == "ia"


def test_reputacion_se_penaliza():
    mod = make_moderator(ai=StubAI([]))
    mod.moderate("eres un idiota", guild_id="g", user_id="u")
    assert mod.store.get_reputation("g", "u") < 0.5


def test_auditoria_guarda_decisiones():
    mod = make_moderator(ai=StubAI([]))
    mod.moderate("eres un idiota", guild_id="g", user_id="u")
    row = mod.store.conn.execute("SELECT COUNT(*) AS n FROM decisions").fetchone()
    assert row["n"] == 1
