import argparse
import json
import time
from pathlib import Path

from src.core import ADECUADO, GRITO, REVISION_HUMANA, SPAM, TOXICO, ensure_utf8
from src.traditional.detector import TraditionalModerator

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_SCRIPT = ROOT / "data" / "scripted_chat.json"

COLORS = {
    TOXICO: "\033[91m",           # rojo
    SPAM: "\033[93m",             # amarillo
    GRITO: "\033[93m",
    REVISION_HUMANA: "\033[96m",  # cian
    ADECUADO: "\033[92m",         # verde
}
RESET = "\033[0m"

REPUTACIONES = {
    "jugador_01": 0.9, "jugador_02": 0.1, "jugador_03": 0.2,
    "jugador_04": 0.95, "jugador_05": 0.3, "jugador_06": 0.5,
    "jugador_07": 0.8, "jugador_08": 0.0, "jugador_09": 0.6,
    "jugador_10": 0.85,
}
DEFAULT_REP = 0.5


def run_message(mod_trad, mod_ai, user, message, reputation, show_reputation=False):
    d_trad = mod_trad.classify(message, user_id=user)
    d_ai, prob = mod_ai.classify(message, reputation=reputation)

    rep = f" (reputación {reputation:.2f})" if show_reputation else ""
    line_t = f"{COLORS[d_trad.code]}{d_trad.label}{RESET}"
    line_a = f"{COLORS[d_ai.code]}{d_ai.label}{RESET}"

    print(f"\n  {user}{rep}: {message}")
    print(f"    [TRADICIONAL] {line_t}" + (f"  ({d_trad.detail})" if d_trad.detail else ""))
    print(f"    [IA]          {line_a}  (prob. toxicidad {prob:.2f})")
    return d_trad, d_ai


def run_script(mod_trad, mod_ai, script_path):
    data = json.loads(Path(script_path).read_text(encoding="utf-8"))
    print(f"=== {data.get('scenario', 'Guion')} ===\n")
    t0 = time.time()
    for entry in data["messages"]:
        run_message(
            mod_trad,
            mod_ai,
            entry["user"],
            entry["message"],
            REPUTACIONES.get(entry["user"], DEFAULT_REP),
        )
        time.sleep(0.4)
    print(f"\n=== Fin del guion ({time.time() - t0:.1f}s) ===")


def run_interactive(mod_trad, mod_ai):
    print("Simulador de chat de videojuego (interactivo)")
    print("Escribe un mensaje y pulsa Enter. 'salir' termina. '/rep' muestra reputación.\n")
    user = "jugador_demo"
    rep = DEFAULT_REP
    while True:
        try:
            msg = input("> ").strip()
        except (EOFError, KeyboardInterrupt):
            break
        if not msg:
            continue
        if msg.lower() == "salir":
            break
        if msg.lower() == "/rep":
            rep = float(input("  nueva reputación (0.0 - 1.0): ") or rep)
            continue
        run_message(mod_trad, mod_ai, user, msg, rep, show_reputation=True)


def main():
    ensure_utf8()
    ap = argparse.ArgumentParser(description="Simulador de chat con ambos filtros")
    ap.add_argument("--guion", default=str(DEFAULT_SCRIPT), help="JSON con escenarios")
    ap.add_argument("--interactivo", action="store_true")
    args = ap.parse_args()

    from src.ai.inference import ToxicClassifier

    print("Cargando moderadores...")
    mod_trad = TraditionalModerator()
    mod_ai = ToxicClassifier()
    print("Listo.\n")

    if args.interactivo:
        run_interactive(mod_trad, mod_ai)
    else:
        run_script(mod_trad, mod_ai, args.guion)


if __name__ == "__main__":
    main()
