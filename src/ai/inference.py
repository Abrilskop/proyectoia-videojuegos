import math
from pathlib import Path

import torch
from transformers import AutoModelForSequenceClassification, AutoTokenizer

from src.core import ADECUADO, REVISION_HUMANA, TOXICO, Decision

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_MODEL_DIR = ROOT / "models" / "toxic_transformer"

UMBRAL_AUTO_BLOQUEO = 0.80  # >= 0.80 -> bloqueo/sanción automática
UMBRAL_DETECCION = 0.50     # 0.50 - 0.80 -> cola de moderación humana


class ToxicClassifier:
    """Sistema IA (Red Neuronal tipo Transformer) + reputación histórica."""

    def __init__(self, model_dir=DEFAULT_MODEL_DIR):
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.model = AutoModelForSequenceClassification.from_pretrained(str(model_dir))
        self.model.to(self.device)
        self.model.eval()
        self.tokenizer = AutoTokenizer.from_pretrained(str(model_dir))

    def predict_proba(self, text):
        enc = self.tokenizer(
            text,
            return_tensors="pt",
            truncation=True,
            max_length=128,
            padding=True,
        )
        enc = {k: v.to(self.device) for k, v in enc.items()}
        with torch.no_grad():
            logits = self.model(**enc).logits
        probs = torch.softmax(logits, dim=-1)[0]
        return float(probs[1])

    def adjust_by_reputation(self, prob, reputation=0.5):
        logit = math.log(max(prob, 1e-9) / max(1 - prob, 1e-9))
        logit_adj = logit + (reputation - 0.5) * 2.0
        return 1 / (1 + math.exp(-logit_adj))

    def classify(self, text, reputation=0.5):
        prob = self.predict_proba(text)
        prob = self.adjust_by_reputation(prob, reputation)
        if prob >= UMBRAL_AUTO_BLOQUEO:
            return Decision(TOXICO, f"probabilidad de toxicidad {prob:.2f}"), prob
        if prob >= UMBRAL_DETECCION:
            return (
                Decision(REVISION_HUMANA, f"probabilidad de toxicidad {prob:.2f}"),
                prob,
            )
        return Decision(ADECUADO, f"probabilidad de toxicidad {prob:.2f}"), prob
