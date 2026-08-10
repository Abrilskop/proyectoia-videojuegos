import argparse
import random
from pathlib import Path

import pandas as pd

INSULTOS = [
    "idiota", "estúpido", "estúpida", "tonto", "tonta", "imbécil", "basura",
    "inútil", "retrasado", "retrasada", "gilipollas", "cabrón", "cabrona",
    "pendejo", "pendeja", "mierda", "zorra", "perra", "tarado", "burro",
    "mongolo", "culero", "marica", "puto", "rata", "cerdo", "anormal",
    "pelotudo", "boludo", "feo", "gordo",
]

TOXIC_TEMPLATES = [
    "eres {i}",
    "tú eres {i}",
    "eres un {i}",
    "eres una {i}",
    "qué {i} eres",
    "cállate {i}",
    "{i} de mierda",
    "juegas como una mierda",
    "vete a la mierda",
    "no sirves para nada {i}",
    "te voy a reportar, {i}",
    "sabes perder porque eres {i}",
    "qué mal juegas {i}",
    "eres la peor persona de este equipo",
    "ojalá te baneen para siempre",
    "nadie quiere jugar contigo {i}",
    "tu madre es una {i}",
    "claro, genio, sigue así",
    "muy inteligente, campeón, mira cómo juegas",
    "excelente, sigue regalando la partida genio",
    "qué bien que jugaste, inútil",
    "seguro que llegas a diamante jugando así, genio",
    "tú eres una rata",
    "eres un {i} que no sabe nada del juego",
    "el equipo pierde por tu culpa {i}",
    "todos te odian en esta comunidad",
    "vete a jugar otro juego {i}",
    "borra el juego {i}",
    "ojalá pierdas todas las partidas {i}",
    "ya cállate, eres insoportable {i}",
]

SAFE_TEMPLATES = [
    "buena partida",
    "buena esa, gracias",
    "gracias por la ayuda",
    "vamos a ganar esta",
    "juguemos otra ronda",
    "necesito munición",
    "hay un enemigo a la derecha",
    "sígueme por aquí",
    "¿dónde está el boss?",
    "este nivel es un infierno de difícil",
    "la rata del jefe del nivel 3 es difícil de matar",
    "el escuadrón del jefe es complicado",
    "me encanta este juego",
    "buena jugada",
    "pásame el medkit porfa",
    "vamos equipo, juntos ganamos",
    "gg",
    "GG, bien jugado",
    "qué buena partida",
    "ese personaje está roto en esta versión",
    "el lag me mata a veces",
    "estoy esperando en la cola del nivel",
    "¿quién quiere jugar ranked?",
    "saludos desde latinoamérica",
    "aguante argentina",
    "no estés triste, la ganas la próxima",
    "nos vemos en la próxima partida",
    "buena estrategia la del equipo",
    "hay que rotar a la izquierda",
    "cubran la zona B",
    "estoy a un punto de subir de nivel",
    "el ping está alto hoy",
    "vamos a ganar el duelo de jefes",
    "¿alguien tiene micrófono?",
    "recojan las mejoras del mapa",
    "vamos a ganar esta partida",
    "necesito que alguien cubra la retaguardia",
    "genial, lo hicimos",
    "qué partida tan reñida",
    "el jefe final es muy bueno",
    "esa skin es muy bonita",
    "¿dónde consigo las pociones?",
    "bajen por el pasillo de la izquierda",
    "aguanten un poco más equipo",
    "voy a revivir a los caídos",
    "mejor cambiemos de estrategia",
    "tranquilos, todavía podemos ganar",
    "buen trabajo en la última ronda",
    "la rata del laboratorio es un jefe genial",
    "el dragón del nivel 4 da miedo",
    "cómo se llama esta zona del mapa",
    "recuerden recoger las llaves",
]

LEET_CHARS = {"a": "4", "e": "3", "i": "1", "o": "0", "s": "5", "t": "7", "g": "9"}


def leet_word(word):
    out = []
    for ch in word.lower():
        if ch in LEET_CHARS and random.random() < 0.7:
            out.append(LEET_CHARS[ch])
        else:
            out.append(ch)
    return "".join(out)


def jitter(text):
    t = text
    if random.random() < 0.2:
        t += random.choice(["...", "!!!", " :)", " ?", " jaja"])
    if random.random() < 0.15:
        t = t.upper()
    return t


def build_dataset(total, seed):
    rng = random.Random(seed)
    random.seed(seed)
    rows = []
    n_toxic = int(total * 0.45)
    n_safe = total - n_toxic

    for _ in range(n_toxic):
        templ = rng.choice(TOXIC_TEMPLATES)
        if "{i}" in templ:
            insult = rng.choice(INSULTOS)
            if rng.random() < 0.3:
                insult = leet_word(insult)
            msg = templ.format(i=insult)
        else:
            msg = templ
        rows.append({"message": jitter(msg), "label": 1})

    for _ in range(n_safe):
        msg = rng.choice(SAFE_TEMPLATES)
        rows.append({"message": jitter(msg), "label": 0})

    rng.shuffle(rows)
    return pd.DataFrame(rows)


def main():
    ap = argparse.ArgumentParser(description="Genera dataset sintético de toxicidad")
    ap.add_argument("--total", type=int, default=6000)
    ap.add_argument("--seed", type=int, default=42)
    args = ap.parse_args()

    root = Path(__file__).resolve().parents[2]
    raw_dir = root / "data" / "raw"
    proc_dir = root / "data" / "processed"
    raw_dir.mkdir(parents=True, exist_ok=True)
    proc_dir.mkdir(parents=True, exist_ok=True)

    df = build_dataset(args.total, args.seed)
    df = df.sample(frac=1, random_state=args.seed).reset_index(drop=True)

    n = len(df)
    train = df.iloc[: int(n * 0.7)]
    val = df.iloc[int(n * 0.7): int(n * 0.85)]
    test = df.iloc[int(n * 0.85):]

    df.to_csv(raw_dir / "chat_toxicidad.csv", index=False, encoding="utf-8")
    train.to_csv(proc_dir / "train.csv", index=False, encoding="utf-8")
    val.to_csv(proc_dir / "val.csv", index=False, encoding="utf-8")
    test.to_csv(proc_dir / "test.csv", index=False, encoding="utf-8")

    print(f"Total: {n}  (tóxicos={int(df['label'].sum())}, seguros={int((df['label']==0).sum())})")
    print(f"train={len(train)}  val={len(val)}  test={len(test)}")
    print("Guardado en data/raw/chat_toxicidad.csv y data/processed/")


if __name__ == "__main__":
    main()
