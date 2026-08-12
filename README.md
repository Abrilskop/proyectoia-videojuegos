# Moderación de Chats de Videojuegos: Paradigma Tradicional vs IA

Proyecto académico que implementa **dos sistemas de moderación de lenguaje tóxico** en chats de
videojuegos en línea, tal como describe el informe:

- **Sistema Tradicional** (paradigma simbólico / reglas de negocio con IF/ELSE).
- **Sistema de IA** (Red Neuronal tipo **Transformer**, `distilbert-base-multilingual-cased`,
  fine-tuning en dataset sintético de toxicidad en español).

## Estructura

```
src/
  traditional/          Sistema 1: reglas R1-R4 (lista negra, leetspeak, gritos, spam)
  ai/                   Sistema 2: generador de dataset, entrenamiento, inferencia
  evaluation/           Casos del reporte, métricas y comparativa (gráfica + reporte MD)
  demo/                 Simulador de chat en consola
data/
  raw/                  dataset sintético generado (chat_toxicidad.csv)
  processed/            train.csv / val.csv / test.csv
  scripted_chat.json    Escenarios del reporte para el modo guion
models/toxic_transformer/   Modelo IA entrenado
reports/                comparativa_report.md + comparativa_grafica.png
tests/                  Tests unitarios de las reglas tradicionales
```

## Requisitos

- Python 3.13, GPU NVIDIA con CUDA (recomendado; si no, todo funciona en CPU más lento).
- Instalar dependencias:

```powershell
.venv\Scripts\python.exe -m pip install -r requirements.txt
```

## Ejecución (en orden)

1. **Generar dataset sintético** (6000 ejemplos etiquetados):
```powershell
.venv\Scripts\python.exe -m src.ai.dataset_builder --total 6000
```

2. **Entrenar el Transformer** (≈3-5 min en RTX 2060):
```powershell
.venv\Scripts\python.exe -m src.ai.train --epochs 4 --batch 16
```

3. **Tests de las reglas tradicionales** (R1-R4):
```powershell
.venv\Scripts\python.exe tests\run_tests.py
```

4. **Evaluación comparativa** (métricas + gráfica + reporte):
```powershell
.venv\Scripts\python.exe -m src.evaluation.comparativa
```

5. **Demo en consola** — modo guion (escenarios del informe):
```powershell
.venv\Scripts\python.exe -m src.demo.chat_simulator
```
   Modo interactivo (escribes mensajes en vivo):
```powershell
.venv\Scripts\python.exe -m src.demo.chat_simulator --interactivo
```
## Diagramas de flujo

Diagramas de los dos paradigmas y el informe completo de la actividad (`reports/informe_completo.md`):

- `reports/diagrama_tradicional.png` — flujo del sistema tradicional (R1-R4).
- `reports/diagrama_ia.png` — flujo del sistema de IA (entrenamiento + inferencia).
- `reports/comparativa_grafica.png` — gráfica comparativa de métricas.

Para regenerarlos: `.venv\Scripts\python.exe -m src.evaluation.diagramas`

## Bot de Discord (moderación en vivo)

Bot que modera mensajes reales con el pipeline completo: el sistema tradicional primero
(~12 ms) y, si pasa, el Transformer en GPU. Bloquea (borra + timeout), advierte gritos y
reenvía mensajes ambiguos (0.50–0.80) a una cola de revisión humana. La reputación por
jugador y la auditoría de decisiones se persisten en `bot.db` (SQLite).

### Configuración (una vez)

1. Crea una app en <https://discord.com/developers> → *Applications* → *New Application*.
2. En *Bot* → *Reset Token* → copia el token.
3. Activa **Message Content Intent** (imprescindible) y, opcionalmente, **Server Members Intent**.
4. Invita el bot con *OAuth2 → URL Generator*: scopes `bot` + `applications.commands`,
   permisos *Read Messages*, *Send Messages*, *Manage Messages*, *Moderate Members* y *View Channel*.
5. Copia `.env.example` → `.env`, pega tu token y (opcional) los IDs de canal de revisión y de log.

### Ejecución

```powershell
.venv\Scripts\python.exe -m src.bot.run_bot
```

Comandos del bot:

- `/moderate <mensaje>` — prueba un mensaje con ambos sistemas.
- `/reputacion <@usuario>` — consulta la reputación acumulada.

## Reglas del sistema tradicional

| Regla | Descripción |
|---|---|
| R1 | Palabra exacta contenida en `lista_negra.txt` → bloqueo |
| R2 | Leetspeak (letras→símbolos, ej. `1d10t4`) → normalización + bloqueo |
| R3 | Mensaje > 40 chars con > 90% MAYÚSCULAS → advertencia (gritar) |
| R4 | Mismo mensaje > 5 veces en 10 segundos → silenciar por spam |

## Sistema de IA

- **Modelo:** Transformer preentrenado multilingüe con cabezal de clasificación binaria.
- **Umbrales (sección 4 del informe):** probabilidad ≥ 0.80 → bloqueo automático;
  0.50–0.80 → cola de moderación humana (Human-in-the-Loop); < 0.50 → adecuado.
- **Reputación histórica:** el perfil del jugador ajusta la probabilidad previa del mensaje.
- **Generalización:** no aprende palabras prohibidas, sino relaciones contextuales
  (ej. "la rata del jefe del nivel 3" es adecuado, pero "tú eres una rata" es tóxico).

## Resultados esperados (ver `reports/comparativa_report.md`)

- El sistema tradicional cae en **falsos positivos** ("este nivel es un infierno de difícil")
  y **no detecta sarcasmo**.
- El sistema de IA supera al tradicional en precisión, recall y F1 sobre los mismos casos.
