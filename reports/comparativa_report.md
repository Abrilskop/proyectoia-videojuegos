# Informe de Evaluación Comparativa

## Descripción
Ambos sistemas (paradigma tradicional basado en reglas y paradigma de IA basado en un Transformer)
se evalúan con los **mismos casos de entrada**, incluyendo leetspeak, sarcasmo, contexto de juego
y falsos positivos típicos del filtro por palabras clave.

**Modelo IA:** distilbert-base-multilingual-cased (fine-tuning) · 6000 ejemplos sintéticos.

## Métricas sobre casos curados (n=21)

| Sistema | Precisión | Recall | F1 | Exactitud |
|---------|-----------|--------|----|-----------|
| Tradicional (reglas) | 0.800 | 0.727 | 0.762 | 0.762 |
| IA - bloqueo automático (>=80%) | 1.000 | 1.000 | 1.000 | 1.000 |
| IA - detección (incl. revisión humana) | 1.000 | 1.000 | 1.000 | 1.000 |

## Muestra sobre dataset de test (n=400)

| Sistema | Precisión | Recall | F1 | Exactitud |
|---------|-----------|--------|----|-----------|
| Tradicional (reglas) | 0.916 | 0.712 | 0.801 | 0.825 |
| IA - bloqueo automático (>=80%) | 1.000 | 1.000 | 1.000 | 1.000 |

## Detalle por caso curado

| Mensaje | Categoría | Etiqueta real | Tradicional | IA |
|---|---|---|---|---|
| `1d10t4` | leetspeak | 1 | Mensaje Tóxico / Ofensivo | Mensaje Tóxico / Ofensivo |
| `t0nt@` | leetspeak | 1 | Mensaje Tóxico / Ofensivo | Mensaje Tóxico / Ofensivo |
| `eres un p3ndej0` | leetspeak | 1 | Mensaje Tóxico / Ofensivo | Mensaje Tóxico / Ofensivo |
| `h1j0 d3 puta` | leetspeak | 1 | Mensaje Tóxico / Ofensivo | Mensaje Tóxico / Ofensivo |
| `eres un idiota` | insulto_directo | 1 | Mensaje Tóxico / Ofensivo | Mensaje Tóxico / Ofensivo |
| `tú eres una rata` | insulto_directo | 1 | Mensaje Tóxico / Ofensivo | Mensaje Tóxico / Ofensivo |
| `vete a la mierda` | insulto_directo | 1 | Mensaje Tóxico / Ofensivo | Mensaje Tóxico / Ofensivo |
| `te voy a reportar por tóxico, pendejo` | insulto_directo | 1 | Mensaje Tóxico / Ofensivo | Mensaje Tóxico / Ofensivo |
| `claro, excelente jugada genio` | sarcasmo | 1 | Mensaje Adecuado | Mensaje Tóxico / Ofensivo |
| `muy inteligente, campeón, mira cómo juegas` | sarcasmo | 1 | Mensaje Adecuado | Mensaje Tóxico / Ofensivo |
| `seguro que llegas a diamante jugando así, genio` | sarcasmo | 1 | Mensaje Adecuado | Mensaje Tóxico / Ofensivo |
| `este nivel es un infierno de difícil` | falso_positivo | 0 | Mensaje Tóxico / Ofensivo | Mensaje Adecuado |
| `la rata del jefe del nivel 3 es difícil de matar` | contexto_juego | 0 | Mensaje Tóxico / Ofensivo | Mensaje Adecuado |
| `mataste al jefe, gran trabajo` | contexto_juego | 0 | Mensaje Adecuado | Mensaje Adecuado |
| `ese personaje está roto en esta versión` | contexto_juego | 0 | Mensaje Adecuado | Mensaje Adecuado |
| `buena partida, gracias` | normal | 0 | Mensaje Adecuado | Mensaje Adecuado |
| `necesito munición para el boss` | normal | 0 | Mensaje Adecuado | Mensaje Adecuado |
| `gg` | normal | 0 | Mensaje Adecuado | Mensaje Adecuado |
| `vamos equipo, juntos ganamos` | normal | 0 | Mensaje Adecuado | Mensaje Adecuado |
| `VAMOS EQUIPO A GANAR ESTA PARTIDA AHORA MISMO` | grito | 0 | Advertencia: Gritar | Mensaje Adecuado |
| `jajaja` | spam | 0 | Mensaje Adecuado | Mensaje Adecuado |

![Gráfica comparativa](comparativa_grafica.png)

Tiempo de inferencia (casos curados): Tradicional 12.1 ms | IA 932.8 ms
