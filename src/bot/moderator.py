import time
from dataclasses import dataclass

from src.core import ADECUADO, GRITO, REVISION_HUMANA, SPAM, TOXICO, Decision
from src.traditional.detector import TraditionalModerator

from src.bot.store import Store

PENALIZA_BLOQUEO = -0.15
PENALIZA_REVISION = -0.05
PENALIZA_GRITO = -0.02
RECOMPENSA_OK = 0.01


@dataclass
class ModeratorResult:
    decision: Decision
    action: str
    source: str
    traditional: Decision | None = None
    prob: float | None = None
    reputation: float = 0.5

    @property
    def block(self):
        return self.action == "bloquear"

    @property
    def needs_review(self):
        return self.action == "revision_humana"


class ChatModerator:
    """Pipeline de moderación del bot: sistema tradicional primero, IA después.

    - R1/R2 (lista negra/leetspeak) o R4 (spam) -> bloquear
    - R3 (grito) -> advertencia
    - Si pasa, IA con umbrales: >= bloqueo -> bloquear, revision <= p < bloqueo -> cola humana
    """

    def __init__(self, trad=None, ai=None, store=None, umbral_bloqueo=0.80, umbral_revision=0.50):
        self.trad = trad or TraditionalModerator()
        self.ai = ai
        self.store = store or Store(":memory:")
        self.umbral_bloqueo = umbral_bloqueo
        self.umbral_revision = umbral_revision

    def analyze(self, message, guild_id="g", user_id="u", timestamp=None):
        if timestamp is None:
            timestamp = time.time()

        d_trad = self.trad.classify(message, user_id=user_id, timestamp=timestamp)

        if d_trad.code in (TOXICO, SPAM):
            return ModeratorResult(d_trad, "bloquear", "tradicional", traditional=d_trad)
        if d_trad.code == GRITO:
            return ModeratorResult(d_trad, "advertencia", "tradicional", traditional=d_trad)

        if self.ai is None:
            return ModeratorResult(d_trad, "ok", "tradicional", traditional=d_trad)

        prob_raw = self.ai.predict_proba(message)
        prob = self.ai.adjust_by_reputation(prob_raw, self.store.get_reputation(guild_id, user_id))

        if prob >= self.umbral_bloqueo:
            decision = Decision(TOXICO, f"probabilidad de toxicidad {prob:.2f}")
            return ModeratorResult(decision, "bloquear", "ia", traditional=d_trad, prob=prob)
        if prob >= self.umbral_revision:
            decision = Decision(REVISION_HUMANA, f"probabilidad de toxicidad {prob:.2f}")
            return ModeratorResult(decision, "revision_humana", "ia", traditional=d_trad, prob=prob)

        decision = Decision(ADECUADO, f"probabilidad de toxicidad {prob:.2f}")
        return ModeratorResult(decision, "ok", "ia", traditional=d_trad, prob=prob)

    def moderate(self, message, guild_id="g", user_id="u", channel_id="", timestamp=None):
        result = self.analyze(message, guild_id=guild_id, user_id=user_id, timestamp=timestamp)

        if result.action == "bloquear":
            result.reputation = self.store.adjust_reputation(guild_id, user_id, PENALIZA_BLOQUEO)
        elif result.action == "revision_humana":
            result.reputation = self.store.adjust_reputation(guild_id, user_id, PENALIZA_REVISION)
        elif result.action == "advertencia":
            result.reputation = self.store.adjust_reputation(guild_id, user_id, PENALIZA_GRITO)
        else:
            result.reputation = self.store.adjust_reputation(guild_id, user_id, RECOMPENSA_OK)

        self.store.add_decision(
            guild_id,
            user_id,
            channel_id,
            message,
            result.decision.label,
            result.prob,
            result.action,
        )
        return result
