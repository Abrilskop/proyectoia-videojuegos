CASES = [
    ("1d10t4", 1, "leetspeak"),
    ("t0nt@", 1, "leetspeak"),
    ("eres un p3ndej0", 1, "leetspeak"),
    ("h1j0 d3 puta", 1, "leetspeak"),
    ("eres un idiota", 1, "insulto_directo"),
    ("tú eres una rata", 1, "insulto_directo"),
    ("vete a la mierda", 1, "insulto_directo"),
    ("te voy a reportar por tóxico, pendejo", 1, "insulto_directo"),
    ("claro, excelente jugada genio", 1, "sarcasmo"),
    ("muy inteligente, campeón, mira cómo juegas", 1, "sarcasmo"),
    ("seguro que llegas a diamante jugando así, genio", 1, "sarcasmo"),
    ("este nivel es un infierno de difícil", 0, "falso_positivo"),
    ("la rata del jefe del nivel 3 es difícil de matar", 0, "contexto_juego"),
    ("mataste al jefe, gran trabajo", 0, "contexto_juego"),
    ("ese personaje está roto en esta versión", 0, "contexto_juego"),
    ("buena partida, gracias", 0, "normal"),
    ("necesito munición para el boss", 0, "normal"),
    ("gg", 0, "normal"),
    ("vamos equipo, juntos ganamos", 0, "normal"),
    ("VAMOS EQUIPO A GANAR ESTA PARTIDA AHORA MISMO", 0, "grito"),
    ("jajaja", 0, "spam"),
]

SPAM_REPEATS = 6
SPAM_WINDOW = 1.0
