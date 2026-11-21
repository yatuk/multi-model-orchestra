<p align="center">
  <img src="assets/logo.png" width="160" height="160" alt="multi-model-orchestra Logo: ein Cartoon-Dirigent mit roter Fliege, der den Taktstock hebt">
</p>

<h1 align="center">multi-model-orchestra</h1>

<p align="center"><sub><a href="../README.md">English</a> · <a href="README_TR.md">Türkçe</a> · <a href="README_UK.md">Українська</a> · <a href="README_ZH.md">简体中文</a> · <a href="README_ZH-TW.md">繁體中文</a> · Deutsch · <a href="README_FR.md">Français</a> · <a href="README_ES.md">Español</a> · <a href="README_JA.md">日本語</a> · <a href="README_KO.md">한국어</a> · <a href="README_AZ.md">Azərbaycanca</a> · <a href="README_UZ.md">Oʻzbekcha</a> · <a href="README_KK.md">Қазақша</a> · <a href="README_KY.md">Кыргызча</a> · <a href="README_TK.md">Türkmençe</a> · <a href="README_CRH.md">Qırımtatarca</a> · <a href="README_UG.md">ئۇيغۇرچە</a> · <a href="README_PT.md">Português</a> · <a href="README_VI.md">Tiếng Việt</a></sub></p>

<p align="center"><b>Ein teures Modell dirigiert, günstigere Modelle spielen, und jede Antwort wird geprüft, bevor sie verwendet wird.</b><br>
Skills für Claude Code (oder alles, was <code>SKILL.md</code>-Dateien liest), die Arbeit an Claude Opus, Sonnet und Haiku, OpenAI GPT, Kimi und DeepSeek weitergeben.<br>
Der Haupt-Agent plant, schreibt die Briefs und prüft; die anderen Modelle erledigen die Arbeit, und nichts, was sie zurückgeben, gilt als vertrauenswürdig, bevor es eine Prüfung bestanden hat.</p>

<p align="center">
  <a href="../LICENSE"><img src="https://img.shields.io/badge/license-MIT-555" alt="MIT-Lizenz"></a>
  <img src="https://img.shields.io/badge/models-Claude%20·%20GPT%20·%20Kimi%20·%20DeepSeek-2563EB" alt="Claude-, GPT-, Kimi- und DeepSeek-Lanes">
  <img src="https://img.shields.io/badge/runs%20on-bash%20·%20Git%20Bash%20on%20Windows-4EAA25" alt="Läuft auf bash, unter Windows mit Git Bash">
  <a href="https://github.com/yatuk/multi-model-orchestra"><img src="https://img.shields.io/github/stars/yatuk/multi-model-orchestra?style=social" alt="GitHub-Sterne"></a>
</p>

<p align="center"><b><a href="#schnellstart">Installation</a></b> · <a href="otomode.md">otomode</a> · <a href="how-it-works.md#council">Council</a> · <a href="benchmark.md">Benchmark</a> · <a href="faq.md">FAQ</a></p>

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
      <code>mmo-run</code> ist der eine Runner für jeden Anbieter, mit harten Statuscodes und einem Timeout bei jedem Aufruf. Schreibende Lanes laufen nur in einem Git-Worktree, nie in deinem Haupt-Checkout.
    </td>
    <td width="25%" valign="top">
      <b>Prüfen</b><br>
      Der Dirigent führt die Prüfung selbst aus und liest den gesamten Diff. Das "fertig" einer Lane ist eine Behauptung, kein Ergebnis.
    </td>
  </tr>
</table>

## Echte Zahlen

| Was | Ergebnis | Details |
|---|---|---|
| <!-- AB-RESULTS --> A/B: orchestra-Skill gegen schlichtes "use subagents" (`claude-fable-5-2`, 2 Läufe pro Arm) | Gleiche Qualität: alle vier Läufe 36/36 versteckte Tests, sichtbare Tests unverändert (das Aufgabenset ist zu leicht, um Qualität zu trennen) | [benchmark.md](benchmark.md#ab-test-orchestra-skill-vs-use-subagents-2026-11-21) |
| <!-- AB-RESULTS --> A/B Kosten pro Lauf | Skill im Mittel $1.88 gegen $3.21, rund 40 % weniger, die Bereiche überlappen nicht. Die Ersparnis kommt daher, dass Sub-Agents auf Sonnet laufen, statt Fable zu erben. Kein Geschwindigkeitsgewinn (3.2 gegen 3.5 Min.) | [RESULTS.md](../bench/ab/results/2026-11-21/RESULTS.md) |
| <!-- AB-RESULTS --> A/B Grenzen | Ein einzeiliger Prompt "use Sonnet subagents" wurde nicht getestet und könnte den Großteil der Ersparnis erreichen. `total_cost_usd` ist ein Stellvertreter auf Listenpreis-Basis, keine Plan-Nutzung | [faq.md](faq.md#why-not-just-tell-the-model-to-use-subagents) |
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
- "otomode 6h: these four tasks, each checked with `go test ./...`."

## Funktioniert mit

| Tool | Verwendet für | Benötigt |
|---|---|---|
| Claude Code | Die Skills und die Stufen Claude Opus / Sonnet / Haiku als Sub-Agents | Skills installiert in `~/.claude/skills` (oder im `.claude/skills` eines Projekts); sonst nichts |
| Codex CLI | GPT-Lanes | `codex` im PATH, mit ChatGPT angemeldet |
| Kimi Code CLI | Kimi- und DeepSeek-Lanes | `kimi` im PATH, angemeldet; für DeepSeek ein `deepseek/*`-Modell in der `config.toml` von Kimi Code |

GPT-Modell-IDs: In manchen ChatGPT-Plänen liefert die Codex CLI inzwischen andere IDs (zum Beispiel gpt-5.6-terra oder gpt-6-luna)
und lehnt andere ab. Die Skill-Dateien nennen die Standardwerte; teste, welche IDs dein Plan akzeptiert, bevor du Arbeit dorthin routest
(`mmo-preflight`, um die CLIs zu sehen, dann pro ID ein einzeiliger `mmo-run`-Brief). Siehe [Model ids](how-it-works.md#model-ids).

## Mehr

Die folgenden Dokumente sind auf Englisch.

- [How it works](how-it-works.md): Routing-Tabelle, Runner, Statuscodes, Sicherheitsmodell, Council.
- [otomode](otomode.md): unbeaufsichtigte Läufe, während du weg bist.
- [Benchmark](benchmark.md): Lane-Benchmark und der A/B-Test, samt Anleitung, wie man beide ausführt.
- [FAQ](faq.md): auch dazu, wie sich das Projekt zu ähnlichen Projekten verhält.
- Artikel (Türkisch): [Fable 5.2 ile orkestra ve otomode](fable-orkestra-ve-otomode.md), über den Einsatz eines teuren Haupt-Loop-Modells als Dirigent und darüber, es unbeaufsichtigt arbeiten zu lassen.

## Struktur

```
skills/
  orchestra/   SKILL.md, scripts/ (mmo-run, mmo-council, mmo-preflight, mmo_extract.py), templates/
  council/     chatgpt-lane/  kimi-lane/  deepseek-lane/
  otomode/     SKILL.md, scripts/ (otomode.py: switch, hook, usage gate; statusline.py)
bench/         run.sh, grade.py, tasks/, results/; ab/ for the A/B test
docs/          how-it-works, otomode, benchmark, faq, translations
```

## Lizenz

MIT, siehe [LICENSE](../LICENSE). Die Illustration im README wurde mit gpt-image-2 über die Codex CLI erzeugt.
