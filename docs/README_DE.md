<p align="center">
  <img src="assets/logo.png" width="160" height="160" alt="multi-model-orchestra Logo: ein Cartoon-Dirigent mit roter Fliege, der den Taktstock hebt">
</p>

<h1 align="center">multi-model-orchestra</h1>

<p align="center">
  <img src="https://img.shields.io/badge/Claude-D97757?style=flat-square&logo=claude&logoColor=white" alt="Claude" height="22">
  <img src="https://img.shields.io/badge/GPT%20(Codex)-10A37F?style=flat-square" alt="GPT (Codex)" height="22">
  <img src="https://img.shields.io/badge/DeepSeek-4D6BFE?style=flat-square&logo=deepseek&logoColor=white" alt="DeepSeek" height="22">
  <img src="https://img.shields.io/badge/Kimi-1B1B1B?style=flat-square&logo=kimi&logoColor=white" alt="Kimi" height="22">
  <img src="https://img.shields.io/badge/Grok-000000?style=flat-square" alt="Grok" height="22">
  <img src="https://img.shields.io/badge/OpenCode-211E1E?style=flat-square&logo=opencode&logoColor=white" alt="OpenCode" height="22">
  <img src="https://img.shields.io/badge/Gemini-8E75B2?style=flat-square&logo=googlegemini&logoColor=white" alt="Gemini" height="22">
  <img src="https://img.shields.io/badge/Cursor-000000?style=flat-square&logo=cursor&logoColor=white" alt="Cursor" height="22">
  <img src="https://img.shields.io/badge/OpenRouter-6467F2?style=flat-square&logo=openrouter&logoColor=white" alt="OpenRouter" height="22">
  <img src="https://img.shields.io/badge/NVIDIA-76B900?style=flat-square&logo=nvidia&logoColor=white" alt="NVIDIA" height="22">
  <img src="https://img.shields.io/badge/Baidu-2932E1?style=flat-square&logo=baidu&logoColor=white" alt="Baidu" height="22">
  <br>
  <sub>Anbieter, deren Modelle über eine Lane gelaufen sind und im <a href="benchmark.md">Benchmark</a> bewertet wurden. Namen und Logos gehören ihren Inhabern; eine Billigung ist damit nicht verbunden.</sub>
</p>

<p align="center"><sub><a href="../README.md">English</a> · <a href="README_TR.md">Türkçe</a> · <a href="README_UK.md">Українська</a> · <a href="README_ZH.md">简体中文</a> · <a href="README_ZH-TW.md">繁體中文</a> · Deutsch · <a href="README_FR.md">Français</a> · <a href="README_ES.md">Español</a> · <a href="README_JA.md">日本語</a> · <a href="README_KO.md">한국어</a> · <a href="README_AZ.md">Azərbaycanca</a> · <a href="README_UZ.md">Oʻzbekcha</a> · <a href="README_KK.md">Қазақша</a> · <a href="README_KY.md">Кыргызча</a> · <a href="README_TK.md">Türkmençe</a> · <a href="README_CRH.md">Qırımtatarca</a> · <a href="README_UG.md">ئۇيغۇرچە</a> · <a href="README_PT.md">Português</a> · <a href="README_VI.md">Tiếng Việt</a></sub></p>

<p align="center"><b>Ein teures Modell dirigiert, günstigere Modelle spielen, und jede Antwort wird geprüft, bevor sie verwendet wird.</b><br>
Skills für Claude Code (oder alles, was <code>SKILL.md</code>-Dateien liest), die Arbeit an Claude Opus, Sonnet und Haiku, OpenAI GPT, Kimi, DeepSeek und jede Agent-CLI oder API weitergeben, die du hast: OpenCode, Grok, Gemini, Qwen, Cursor, Copilot, OpenRouter, lokale Modelle und mehr.<br>
Der Haupt-Agent plant, schreibt die Briefs und prüft; die anderen Modelle erledigen die Arbeit, und nichts, was sie zurückgeben, gilt als vertrauenswürdig, bevor es eine Prüfung bestanden hat.</p>

<p align="center">
  <a href="../LICENSE"><img src="https://img.shields.io/badge/license-MIT-555" alt="MIT-Lizenz"></a>
  <img src="https://img.shields.io/badge/lanes-32%20CLIs%20and%20APIs-2563EB" alt="32 Lanes: Agent-CLIs und APIs">
  <img src="https://img.shields.io/badge/runs%20on-bash%20·%20Git%20Bash%20on%20Windows-4EAA25" alt="Läuft auf bash, unter Windows mit Git Bash">
  <a href="https://github.com/yatuk/multi-model-orchestra"><img src="https://img.shields.io/github/stars/yatuk/multi-model-orchestra?style=social" alt="GitHub-Sterne"></a>
</p>

<p align="center"><b><a href="#schnellstart">Installation</a></b> · <a href="lanes/README.md">Lanes</a> · <a href="otomode.md">otomode</a> · <a href="how-it-works.md#council">Council</a> · <a href="benchmark.md">Benchmark</a> · <a href="faq.md">FAQ</a></p>

<p align="center">
  <img src="../assets/orchestra-comic.png" alt="Ein Dirigent gibt einem Modell einen Bug, verlangt den Diff und beruft einen blinden Council ein" width="860">
  <br>
  <sub>Der Dirigent verteilt die Stimmen, verlangt den Diff und beruft einen blinden Council ein, wenn die Antwort eine Ermessensfrage ist.</sub>
</p>

<table>
  <tr>
    <td width="25%" valign="top">
      <b>Routen</b><br>
      Jede Aufgabe geht nach Schwierigkeit an die günstigste Stufe, die ihre Prüfung bestehen kann. Eine Lane steigt erst auf, nachdem sie die Prüfung nicht bestanden hat, nicht nach Bauchgefühl.
    </td>
    <td width="25%" valign="top">
      <b>Brief</b><br>
      Jede Stufe bekommt den Brief, mit dem sie am besten arbeitet: Ziel und Randbedingungen für Opus, nummerierte Schritte und exakte Dateien für die günstigeren Lanes. Eine Lane sieht nur den Brief, daher wird er für Fremde geschrieben.
    </td>
    <td width="25%" valign="top">
      <b>Ausführen</b><br>
      <code>mmo-run</code> ist der eine Runner für jede Lane, mit harten Statuscodes und einem Timeout bei jedem Aufruf. Schreibende Lanes laufen nur in einem Git-Worktree, der deinen Branch enthält, nie in deinem Haupt-Checkout.
    </td>
    <td width="25%" valign="top">
      <b>Prüfen</b><br>
      Der Dirigent führt die Prüfung selbst mit <code>mmo-check</code> aus und liest den gesamten Diff: berührte Tests, Dateien außerhalb des Briefs und eine Prüfung, die auch ohne die Änderung bestünde, werden alle markiert. Das "fertig" einer Lane ist eine Behauptung, kein Ergebnis.
    </td>
  </tr>
</table>

## Echte Zahlen

| Was | Ergebnis | Details |
|---|---|---|
| <!-- AB-RESULTS --> A/B: orchestra-Skill gegen schlichtes "use subagents" (`claude-fable-5-2`, 2 Läufe pro Arm) | Gleiche Qualität: alle vier Läufe 36/36 versteckte Tests, sichtbare Tests unverändert (das Aufgabenset ist zu leicht, um Qualität zu trennen) | [benchmark.md](benchmark.md#ab-test-orchestra-skill-vs-use-subagents-2026-11-21) |
| <!-- AB-RESULTS --> A/B Kosten pro Lauf | Skill im Mittel $1.88 gegen $3.21, rund 40 % weniger, die Bereiche überlappen nicht. Die Ersparnis kommt daher, dass Sub-Agents auf Sonnet laufen, statt Fable zu erben. Kein Geschwindigkeitsgewinn (3.2 gegen 3.5 Min.) | [RESULTS.md](../bench/ab/results/2026-11-21/RESULTS.md) |
| <!-- AB-RESULTS --> A/B Grenzen | Ein einzeiliger Prompt "use Sonnet subagents" (2026-11-28, 2 Läufe, 36/36, Mittel $1.49, Sub-Agents auf Sonnet) erreichte die gesamte Ersparnis ohne den Skill; A und B liefen an einem früheren Tag, daher ist es kein kontrollierter Vergleich. `total_cost_usd` ist ein Stellvertreter auf Listenpreis-Basis, keine Plan-Nutzung | [faq.md](faq.md#why-not-just-tell-the-model-to-use-subagents) |
| Lane-Benchmark, 2026-11-21 (Bugfix mit versteckten Tests, Schlussfolgern mit exakter Antwort, Massen-Labeling von 60 Zeilen) | Kimi k3.1-pro, DeepSeek v4-pro, DeepSeek flash und gpt-5.6-terra: 6/6, 3/3, 60/60. gpt-6-luna: 6/6, 0/3, 58/60. gpt-6.1-sol und gpt-6-astra: ~6/6, ~3/3, ~60/60 (geschätzt: in diesem Plan nicht verfügbar, Werte aus dem Lauf vom 2026-11-11) | [benchmark.md](benchmark.md) |
| otomode, ein unbeaufsichtigter Lauf über 5 Stunden | 13 Aufgaben, je ein Commit; das Wochenlimit stieg von 25 % auf 31 %; 6 Prompts abgelehnt und protokolliert. Ein Lauf, kein Benchmark | [otomode.md](otomode.md#one-real-run) |

> [!WARNING]
> Briefs verlassen deinen Rechner: Jede Lane sendet ihren Brief an den Anbieter des jeweiligen Modells. Schreibe nie Geheimnisse,
> Tokens oder personenbezogene Daten in einen Brief. Der Hook von otomode lehnt Prompts ab und verweigert Befehle zum Löschen,
> Deployen, Pushen und Senden, aber er arbeitet mit Mustern: Er ist eine Leitplanke, keine Sandbox.

## Schnellstart

Füge das in deinen Agenten ein und lass ihn die Skills installieren:

```text
Install multi-model-orchestra: clone https://github.com/yatuk/multi-model-orchestra,
run ./install.sh --link in it, then run ~/.claude/skills/orchestra/scripts/mmo-preflight
and tell me which lanes are ready.
```

Oder selbst. Benötigt bash, git, `timeout` und Python 3; unter Windows Git Bash verwenden.

```bash
git clone https://github.com/yatuk/multi-model-orchestra
cd multi-model-orchestra
./install.sh --link          # into ~/.claude/skills; --dir PATH for a project
~/.claude/skills/orchestra/scripts/mmo-preflight
```

`mmo-preflight` ruft nie ein Modell auf. Es zeigt dir, welche Lanes auf diesem Rechner vorhanden sind, damit der Dirigent um die fehlenden herumroutet.
Für otomode führe einmal `python ~/.claude/skills/otomode/scripts/otomode.py install` aus, um den Hook zu registrieren.

Frage dann zum Beispiel:

- "Fix the failing tests in `internal/auth`. Follow the orchestra skill."
- "Get a second opinion from GPT on this migration plan before I merge it."
- "Ask the council: should we split this service or keep one process?"
- "Do this migration yourself; use the advisor skill with GPT before you start and before you say done."
- "otomode 6h: these four tasks, each checked with `go test ./...`."

## Funktioniert mit

| Tool | Verwendet für | Benötigt |
|---|---|---|
| Claude Code | Die Skills und die Stufen Claude Opus / Sonnet / Haiku als Sub-Agents | Skills installiert in `~/.claude/skills` (oder im `.claude/skills` eines Projekts); sonst nichts |
| Codex CLI | GPT-Lanes | `codex` im PATH, mit ChatGPT angemeldet |
| Kimi Code CLI | Kimi- und DeepSeek-Lanes | `kimi` im PATH, angemeldet; für DeepSeek ein `deepseek/*`-Modell in der `config.toml` von Kimi Code |
| OpenCode | Jeder Anbieter, bei dem es angemeldet ist (DeepSeek, OpenRouter, Ollama, seine kostenlosen Modelle) | `opencode` im PATH |
| Grok CLI | Grok-Lanes | `grok` im PATH, angemeldet |
| Cursor CLI | Cursor-Lanes | `cursor-agent` im PATH, angemeldet |
| Antigravity CLI | Antigravity-Lanes | `agy` im PATH, angemeldet |
| Copilot CLI | Copilot-Lanes | `copilot` im PATH, angemeldet |
| 19 weitere Agent-CLIs | Gemini CLI, Qwen Code, Amp, Droid, Auggie, Kiro, Cline, Kilo, Vibe, Crush, Goose, Aider, Pi, Devin, CodeBuddy, Letta Code, Qoder, gptme, llm | Die CLI im PATH, angemeldet. Nach der Dokumentation der jeweiligen CLI geschrieben und vom Maintainer noch nicht ausgeführt: [was das bedeutet](lanes/README.md#what-checked-means) |
| Gar keine CLI | Die `api`-Lane: jeder OpenAI-kompatible Endpunkt (OpenRouter, DeepSeek, Groq, ein lokales Ollama, ...) für Zweitmeinungen und Massenarbeit | Python 3 und ein Schlüssel in einer Umgebungsvariable |
| Cloud-Agents (experimentell) | Devin, Cursor-Cloud-Agents, Copilot-Agent-Aufgaben über `mmo-cloud` | Ein Anbieter-Schlüssel, und der Code dorthin gepusht, wo der Agent ihn erreichen kann |

`mmo-run --list` zeigt jede Lane und ob sie auf deinem Rechner bereit ist. Details zu jeder Lane: [docs/lanes](lanes/README.md).

GPT-Modell-IDs: In manchen ChatGPT-Plänen liefert die Codex CLI inzwischen andere IDs (zum Beispiel gpt-5.6-terra oder gpt-6-luna)
und lehnt andere ab. Die Skill-Dateien nennen die Standardwerte; teste, welche IDs dein Plan akzeptiert, bevor du Arbeit dorthin routest
(`mmo-preflight`, um die CLIs zu sehen, dann pro ID ein einzeiliger `mmo-run`-Brief). Siehe [Model ids](how-it-works.md#model-ids).

## Erster PR in 10 Minuten

Für die meisten braucht es keine Einrichtung:

- **Lies das README in deiner Sprache** und korrigiere, was maschinell klingt. Alle 19 Übersetzungen hat ein Modell erstellt ([Krimtatarisch](https://github.com/yatuk/multi-model-orchestra/issues/1), [Uigurisch](https://github.com/yatuk/multi-model-orchestra/issues/2), [Turkmenisch](https://github.com/yatuk/multi-model-orchestra/issues/3), [Kasachisch](https://github.com/yatuk/multi-model-orchestra/issues/4), [die übrigen](https://github.com/yatuk/multi-model-orchestra/issues/5)).
- **Füge eine Fehlerzeile ein**, die dir eine CLI geliefert hat (Rate-Limit, abgelaufene Anmeldung, unbekanntes Modell), damit der Runner sie unterscheiden kann ([#10](https://github.com/yatuk/multi-model-orchestra/issues/10)).
- **Führe die Tests unter macOS oder Linux aus** und sag, was kaputtging ([#8](https://github.com/yatuk/multi-model-orchestra/issues/8)).
- **Füge eine Lane hinzu** für die CLI, die du nutzt ([Gemini CLI](https://github.com/yatuk/multi-model-orchestra/issues/6), [Aider](https://github.com/yatuk/multi-model-orchestra/issues/7)), oder [stimme für die nächste ab](https://github.com/yatuk/multi-model-orchestra/discussions/12).

Alle: [good first issues](https://github.com/yatuk/multi-model-orchestra/issues?q=is%3Aissue+is%3Aopen+label%3A%22good+first+issue%22). Wie du deine eigene Arbeit routest, ist in [Show your routing setup](https://github.com/yatuk/multi-model-orchestra/discussions/11) willkommen. Siehe [CONTRIBUTING](../CONTRIBUTING.md).

## Mehr

Die folgenden Dokumente sind auf Englisch.

- [How it works](how-it-works.md): Routing-Tabelle, Runner, Statuscodes, Prüfen einer Lane, Sicherheitsmodell, Council.
- [Lanes](lanes/README.md): jede Lane, wie weit sie geprüft wurde, und wie man eine hinzufügt.
- [otomode](otomode.md): unbeaufsichtigte Läufe, während du weg bist.
- [Benchmark](benchmark.md): Lane-Benchmark und der A/B-Test, samt Anleitung, wie man beide ausführt.
- [Cost](cost.md): die acht Kostenhebel und die Befehle, die jeden durchsetzen oder messen.
- [FAQ](faq.md): auch dazu, wie sich das Projekt zu ähnlichen Projekten verhält.
- [Failures seen](failures.md): wie jeder Fehler aussieht und was ihn behoben hat.
- Artikel (Türkisch): [Fable 5.2 ile orkestra ve otomode](fable-orkestra-ve-otomode.md), über den Einsatz eines teuren Haupt-Loop-Modells als Dirigent und darüber, es unbeaufsichtigt arbeiten zu lassen.

## Struktur

```
skills/
  orchestra/   SKILL.md, lanes.md, templates/, scripts/ (mmo-run, mmo-check, mmo-council, mmo-score,
               mmo-cloud, mmo-preflight, providers/ with one file per lane)
  council/     chatgpt-lane/  kimi-lane/  deepseek-lane/  cloud-lane/
  otomode/     SKILL.md, scripts/ (otomode.py: switch, hook, usage gate; statusline.py)
bench/         run.sh, grade.py, tasks/, results/; ab/ for the A/B test
docs/          how-it-works, lanes/, otomode, benchmark, faq, translations
```

## Lizenz

MIT, siehe [LICENSE](../LICENSE). Die Illustration im README wurde mit gpt-image-2 über die Codex CLI erzeugt.
