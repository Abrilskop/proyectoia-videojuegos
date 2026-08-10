import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.core import ADECUADO, GRITO, SPAM, TOXICO, ensure_utf8
from src.traditional.detector import TraditionalModerator
from src.traditional.rules import (
    clean_noise,
    contains_blacklist,
    load_blacklist,
    normalize,
    normalize_leetspeak,
)


def check(name, condition):
    status = "OK " if condition else "FAIL"
    print(f"  [{status}] {name}")
    return condition


def test_regla1():
    mod = TraditionalModerator()
    d = mod.classify("Eres un idiota", user_id="u1")
    assert d.code == TOXICO, d
    d = mod.classify("buena partida, gracias", user_id="u1")
    assert d.code == ADECUADO, d


def test_regla1_sin_acentos():
    blacklist = load_blacklist()
    assert contains_blacklist(normalize("esto es una imbecil"), blacklist) == "imbecil"
    assert contains_blacklist(normalize("eres un estúpido"), blacklist) == "estupido"


def test_regla2_leetspeak():
    mod = TraditionalModerator()
    for msg in ("1d10t4", "t0nt@", "eres un p3ndej0", "c4br0n de mierda", "h1j0 d3 puta"):
        d = mod.classify(msg, user_id="u2")
        assert d.code == TOXICO, (msg, d)


def test_normalizacion_leetspeak():
    assert normalize_leetspeak("1d10t4", {"1": "i", "0": "o", "4": "a"}) == "idiota"
    assert clean_noise("i-d-i-o-t-a") == "idiota"


def test_regla3_grito():
    mod = TraditionalModerator()
    d = mod.classify("VAMOS EQUIPO A GANAR ESTA PARTIDA AHORA MISMO YA!", user_id="u3")
    assert d.code == GRITO, d
    d = mod.classify("VAMOS", user_id="u3")
    assert d.code == ADECUADO, d


def test_regla4_spam():
    mod = TraditionalModerator()
    t0 = time.time()
    codes = [mod.classify("jajaja", user_id="u4", timestamp=t0 + i * 1.5).code for i in range(7)]
    assert codes[5] == SPAM or codes[6] == SPAM, codes


def test_falso_positivo_tradicional():
    mod = TraditionalModerator()
    d = mod.classify("este nivel es un infierno de difícil", user_id="u5")
    assert d.code == TOXICO, d


def run_all():
    ensure_utf8()
    results = []
    for fn in (
        test_regla1,
        test_regla1_sin_acentos,
        test_regla2_leetspeak,
        test_normalizacion_leetspeak,
        test_regla3_grito,
        test_regla4_spam,
        test_falso_positivo_tradicional,
    ):
        try:
            fn()
            results.append((fn.__name__, True))
        except AssertionError as e:
            results.append((fn.__name__, False))
            print(f"  Detalle: {e}")
        except Exception as e:
            results.append((fn.__name__, False))
            print(f"  Excepción: {e!r}")

    print("\nResultados:")
    ok = all(r[1] for r in results)
    for name, passed in results:
        print(f"  {'PASS' if passed else 'FAIL'}  {name}")
    print(f"\n{'TODOS LOS TESTS PASARON' if ok else 'HUBO FALLOS'}")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(run_all())
