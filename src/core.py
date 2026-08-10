import sys

ADECUADO = "ADECUADO"
TOXICO = "TOXICO"
GRITO = "GRITO"
SPAM = "SPAM"
REVISION_HUMANA = "REVISION_HUMANA"

LABELS = {
    ADECUADO: "Mensaje Adecuado",
    TOXICO: "Mensaje Tóxico / Ofensivo",
    GRITO: "Advertencia: Gritar",
    SPAM: "Silenciado por Spam",
    REVISION_HUMANA: "Revisión Humana (Human-in-the-Loop)",
}


def ensure_utf8():
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8", errors="replace")


class Decision:
    def __init__(self, code, detail=""):
        self.code = code
        self.detail = detail

    @property
    def label(self):
        return LABELS[self.code]

    @property
    def blocked(self):
        return self.code in (TOXICO, SPAM)

    def __str__(self):
        return f"[{self.label}]{' (' + self.detail + ')' if self.detail else ''}"
