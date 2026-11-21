<p align="center">
  <img src="assets/logo.png" width="160" height="160" alt="logo de multi-model-orchestra: un director de orquesta de dibujos animados con pajarita roja levantando la batuta">
</p>

<h1 align="center">multi-model-orchestra</h1>

<p align="center"><sub><a href="../README.md">English</a> · <a href="README_TR.md">Türkçe</a> · <a href="README_UK.md">Українська</a> · <a href="README_ZH.md">简体中文</a> · <a href="README_ZH-TW.md">繁體中文</a> · <a href="README_DE.md">Deutsch</a> · <a href="README_FR.md">Français</a> · Español · <a href="README_JA.md">日本語</a> · <a href="README_KO.md">한국어</a> · <a href="README_AZ.md">Azərbaycanca</a> · <a href="README_UZ.md">Oʻzbekcha</a> · <a href="README_KK.md">Қазақша</a> · <a href="README_KY.md">Кыргызча</a> · <a href="README_TK.md">Türkmençe</a> · <a href="README_CRH.md">Qırımtatarca</a> · <a href="README_UG.md">ئۇيغۇرچە</a> · <a href="README_PT.md">Português</a> · <a href="README_VI.md">Tiếng Việt</a></sub></p>

<p align="center"><b>Que un modelo caro dirija, que modelos más baratos toquen, y que cada respuesta se compruebe antes de usarla.</b><br>
Skills para Claude Code (o cualquier cosa que lea archivos <code>SKILL.md</code>) que reparten el trabajo entre Claude Opus, Sonnet y Haiku, OpenAI GPT, Kimi y DeepSeek.<br>
El agente principal planifica, escribe los briefs y revisa; los demás modelos hacen el trabajo, y nada de lo que devuelven se da por bueno hasta que pasa una comprobación.</p>

<p align="center">
  <a href="../LICENSE"><img src="https://img.shields.io/badge/license-MIT-555" alt="Licencia MIT"></a>
  <img src="https://img.shields.io/badge/models-Claude%20·%20GPT%20·%20Kimi%20·%20DeepSeek-2563EB" alt="Lanes de Claude, GPT, Kimi y DeepSeek">
  <img src="https://img.shields.io/badge/runs%20on-bash%20·%20Git%20Bash%20on%20Windows-4EAA25" alt="Funciona con bash, Git Bash en Windows">
  <a href="https://github.com/yatuk/multi-model-orchestra"><img src="https://img.shields.io/github/stars/yatuk/multi-model-orchestra?style=social" alt="Estrellas de GitHub"></a>
</p>

<p align="center"><b><a href="#inicio-rápido">Instalar</a></b> · <a href="otomode.md">otomode</a> · <a href="how-it-works.md#council">Council</a> · <a href="benchmark.md">Benchmark</a> · <a href="faq.md">FAQ</a></p>

<p align="center">
  <img src="../assets/orchestra-comic.png" alt="Un director entrega un bug a un modelo, pide el diff y convoca un council a ciegas" width="860">
  <br>
  <sub>El director reparte las partituras, pide el diff y convoca un council a ciegas cuando la respuesta es cuestión de criterio.</sub>
</p>

<table>
  <tr>
    <td width="25%" valign="top">
      <b>Enrutar</b><br>
      Cada tarea va, según su dificultad, al nivel más barato que pueda superar su comprobación. Una lane sube de nivel solo después de fallar la comprobación, no por corazonada.
    </td>
    <td width="25%" valign="top">
      <b>Brief</b><br>
      Cada nivel recibe el brief con el que mejor trabaja: objetivo y restricciones para Opus, pasos numerados y archivos exactos para las lanes más baratas. Una lane solo ve el brief, así que se escribe para un desconocido.
    </td>
    <td width="25%" valign="top">
      <b>Ejecutar</b><br>
      <code>mmo-run</code> es el único runner para todos los proveedores, con códigos de estado estrictos y un timeout en cada llamada. Las lanes que escriben solo corren en un worktree de git, nunca en tu checkout principal.
    </td>
    <td width="25%" valign="top">
      <b>Comprobar</b><br>
      El director ejecuta él mismo la comprobación y lee el diff completo. El "hecho" de una lane es una afirmación, no un resultado.
    </td>
  </tr>
</table>

## Cifras reales

| Qué | Resultado | Detalles |
|---|---|---|
| <!-- AB-RESULTS --> A/B: skill orchestra frente a un simple "use subagents" (`claude-fable-5-2`, 2 ejecuciones por brazo) | Misma calidad: las cuatro ejecuciones con 36/36 pruebas ocultas, pruebas visibles intactas (el conjunto de tareas es demasiado fácil para separar la calidad) | [benchmark.md](benchmark.md#ab-test-orchestra-skill-vs-use-subagents-2026-11-21) |
| <!-- AB-RESULTS --> A/B coste por ejecución | Skill $1.88 frente a $3.21 de media, cerca de un 40 % menos, los rangos no se solapan. El ahorro viene de que los sub-agents corren en Sonnet en lugar de heredar Fable. Sin mejora de velocidad (3.2 frente a 3.5 min) | [RESULTS.md](../bench/ab/results/2026-11-21/RESULTS.md) |
| <!-- AB-RESULTS --> A/B límites | Un prompt de una línea "use Sonnet subagents" no se probó y podría captar la mayor parte del ahorro. `total_cost_usd` es un indicador a precio de lista, no el uso del plan | [faq.md](faq.md#why-not-just-tell-the-model-to-use-subagents) |
| Benchmark de lanes, 2026-11-21 (corrección de un bug con pruebas ocultas, razonamiento de respuesta exacta, etiquetado masivo de 60 líneas) | Kimi k3.1-pro, DeepSeek v4-pro, DeepSeek flash y gpt-5.6-terra: 6/6, 3/3, 60/60. gpt-6-luna: 6/6, 0/3, 58/60. gpt-6.1-sol y gpt-6-astra: ~6/6, ~3/3, ~60/60 (estimado: no se ofrecen en ese plan, puntuaciones de la ejecución del 2026-11-11) | [benchmark.md](benchmark.md) |
| otomode, una ejecución desatendida de 5 horas | 13 tareas, un commit cada una; el límite semanal pasó del 25 % al 31 %; 6 avisos denegados y registrados. Una ejecución, no un benchmark | [otomode.md](otomode.md#one-real-run) |

> [!WARNING]
> Los briefs salen de tu máquina: cada lane envía su brief al proveedor de ese modelo. Nunca pongas secretos, tokens
> ni datos personales en un brief. El hook de otomode deniega avisos y rechaza los comandos de borrado, despliegue,
> push y envío, pero se basa en patrones: es una barandilla, no un sandbox.

## Inicio rápido

Pega esto en tu agente y deja que instale los skills:

```text
Install multi-model-orchestra: clone https://github.com/yatuk/multi-model-orchestra,
run ./install.sh --link in it, then run ~/.claude/skills/orchestra/scripts/mmo-preflight
and tell me which lanes are ready.
```

O hazlo tú mismo. Requiere bash, git, `timeout` y Python 3; en Windows, usa Git Bash.

```bash
git clone https://github.com/yatuk/multi-model-orchestra
cd multi-model-orchestra
./install.sh --link          # into ~/.claude/skills; --dir PATH for a project
~/.claude/skills/orchestra/scripts/mmo-preflight
```

`mmo-preflight` nunca llama a un modelo. Te dice qué lanes existen en esta máquina, para que el director enrute evitando las que faltan.
Para otomode, ejecuta una vez `python ~/.claude/skills/otomode/scripts/otomode.py install` para registrar su hook.

Después pide, por ejemplo:

- "Fix the failing tests in `internal/auth`. Follow the orchestra skill."
- "Get a second opinion from GPT on this migration plan before I merge it."
- "Ask the council: should we split this service or keep one process?"
- "otomode 6h: these four tasks, each checked with `go test ./...`."

## Funciona con

| Herramienta | Para qué se usa | Requiere |
|---|---|---|
| Claude Code | Los skills y los niveles Claude Opus / Sonnet / Haiku como sub-agents | Skills instalados en `~/.claude/skills` (o en el `.claude/skills` de un proyecto); nada más |
| Codex CLI | Lanes GPT | `codex` en el PATH, con sesión iniciada en ChatGPT |
| Kimi Code CLI | Lanes Kimi y DeepSeek | `kimi` en el PATH, con sesión iniciada; para DeepSeek, un modelo `deepseek/*` en el `config.toml` de Kimi Code |

IDs de modelos GPT: en algunos planes de ChatGPT, la Codex CLI ahora sirve otros ids (por ejemplo gpt-5.6-terra o gpt-6-luna)
y rechaza otros. Los archivos de skills indican los valores por defecto; prueba los ids que acepta tu plan antes de enrutar trabajo allí
(`mmo-preflight` para ver las CLI, y luego un brief de una línea con `mmo-run` por cada id). Consulta [Model ids](how-it-works.md#model-ids).

## Más

Los documentos siguientes están en inglés.

- [How it works](how-it-works.md): tabla de enrutamiento, runner, códigos de estado, modelo de seguridad, council.
- [otomode](otomode.md): ejecuciones desatendidas mientras no estás.
- [Benchmark](benchmark.md): benchmark de lanes y prueba A/B, con instrucciones para ejecutar ambos.
- [FAQ](faq.md): incluida la comparación con proyectos similares.
- Artículo (en turco): [Fable 5.2 ile orkestra ve otomode](fable-orkestra-ve-otomode.md), sobre usar un modelo caro de bucle principal como director y dejarlo trabajar sin supervisión.

## Estructura

```
skills/
  orchestra/   SKILL.md, scripts/ (mmo-run, mmo-council, mmo-preflight, mmo_extract.py), templates/
  council/     chatgpt-lane/  kimi-lane/  deepseek-lane/
  otomode/     SKILL.md, scripts/ (otomode.py: switch, hook, usage gate; statusline.py)
bench/         run.sh, grade.py, tasks/, results/; ab/ for the A/B test
docs/          how-it-works, otomode, benchmark, faq, translations
```

## Licencia

MIT, consulta [LICENSE](../LICENSE). La ilustración del README se generó con gpt-image-2 a través de la Codex CLI.
