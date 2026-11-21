<p align="center">
  <img src="assets/logo.png" width="160" height="160" alt="logo de multi-model-orchestra : un chef d'orchestre de dessin animé avec un nœud papillon rouge levant sa baguette">
</p>

<h1 align="center">multi-model-orchestra</h1>

<p align="center"><sub><a href="../README.md">English</a> · <a href="README_TR.md">Türkçe</a> · <a href="README_UK.md">Українська</a> · <a href="README_ZH.md">简体中文</a> · <a href="README_ZH-TW.md">繁體中文</a> · <a href="README_DE.md">Deutsch</a> · Français · <a href="README_ES.md">Español</a> · <a href="README_JA.md">日本語</a> · <a href="README_KO.md">한국어</a> · <a href="README_AZ.md">Azərbaycanca</a> · <a href="README_UZ.md">Oʻzbekcha</a> · <a href="README_KK.md">Қазақша</a> · <a href="README_KY.md">Кыргызча</a> · <a href="README_TK.md">Türkmençe</a> · <a href="README_CRH.md">Qırımtatarca</a> · <a href="README_UG.md">ئۇيغۇرچە</a> · <a href="README_PT.md">Português</a> · <a href="README_VI.md">Tiếng Việt</a></sub></p>

<p align="center"><b>Un modèle coûteux dirige, des modèles moins chers jouent, et chaque réponse est vérifiée avant d'être utilisée.</b><br>
Des skills pour Claude Code (ou tout outil qui lit des fichiers <code>SKILL.md</code>) qui confient le travail à Claude Opus, Sonnet et Haiku, à OpenAI GPT, à Kimi et à DeepSeek.<br>
L'agent principal planifie, rédige les briefs et relit ; les autres modèles font le travail, et rien de ce qu'ils renvoient n'est considéré comme fiable tant qu'il n'a pas passé une vérification.</p>

<p align="center">
  <a href="../LICENSE"><img src="https://img.shields.io/badge/license-MIT-555" alt="Licence MIT"></a>
  <img src="https://img.shields.io/badge/models-Claude%20·%20GPT%20·%20Kimi%20·%20DeepSeek-2563EB" alt="Lanes Claude, GPT, Kimi et DeepSeek">
  <img src="https://img.shields.io/badge/runs%20on-bash%20·%20Git%20Bash%20on%20Windows-4EAA25" alt="Fonctionne avec bash, Git Bash sous Windows">
  <a href="https://github.com/yatuk/multi-model-orchestra"><img src="https://img.shields.io/github/stars/yatuk/multi-model-orchestra?style=social" alt="Étoiles GitHub"></a>
</p>

<p align="center"><b><a href="#démarrage-rapide">Installer</a></b> · <a href="otomode.md">otomode</a> · <a href="how-it-works.md#council">Council</a> · <a href="benchmark.md">Benchmark</a> · <a href="faq.md">FAQ</a></p>

<p align="center">
  <img src="../assets/orchestra-comic.png" alt="Un chef d'orchestre confie un bug à un modèle, demande le diff et réunit un council à l'aveugle" width="860">
  <br>
  <sub>Le chef d'orchestre distribue les partitions, demande le diff et réunit un council à l'aveugle quand la réponse relève du jugement.</sub>
</p>

<table>
  <tr>
    <td width="25%" valign="top">
      <b>Router</b><br>
      Chaque tâche va, selon sa difficulté, au palier le moins cher capable de passer sa vérification. Une lane ne monte d'un palier qu'après avoir échoué à la vérification, pas au pif.
    </td>
    <td width="25%" valign="top">
      <b>Brief</b><br>
      Chaque palier reçoit le brief avec lequel il travaille le mieux : objectif et contraintes pour Opus, étapes numérotées et fichiers exacts pour les lanes moins chères. Une lane ne voit que le brief, il est donc écrit pour un inconnu.
    </td>
    <td width="25%" valign="top">
      <b>Exécuter</b><br>
      <code>mmo-run</code> est le runner unique pour tous les fournisseurs, avec des codes de statut stricts et un timeout sur chaque appel. Les lanes qui écrivent ne tournent que dans un worktree git, jamais dans votre checkout principal.
    </td>
    <td width="25%" valign="top">
      <b>Vérifier</b><br>
      Le chef d'orchestre lance lui-même la vérification et lit le diff en entier. Le "terminé" d'une lane est une affirmation, pas un résultat.
    </td>
  </tr>
</table>

## Chiffres réels

| Quoi | Résultat | Détails |
|---|---|---|
| <!-- AB-RESULTS --> A/B : skill orchestra contre un simple "use subagents" (`claude-fable-5-2`, 2 exécutions par bras) | Même qualité : les quatre exécutions à 36/36 tests cachés, tests visibles intacts (le jeu de tâches est trop facile pour départager la qualité) | [benchmark.md](benchmark.md#ab-test-orchestra-skill-vs-use-subagents-2026-11-21) |
| <!-- AB-RESULTS --> A/B coût par exécution | Skill $1.88 contre $3.21 en moyenne, environ 40 % de moins, les intervalles ne se chevauchent pas. L'économie vient du fait que les sub-agents tournent sur Sonnet au lieu d'hériter de Fable. Pas de gain de vitesse (3.2 contre 3.5 min) | [RESULTS.md](../bench/ab/results/2026-11-21/RESULTS.md) |
| <!-- AB-RESULTS --> A/B limites | Un prompt d'une ligne "use Sonnet subagents" n'a pas été testé et pourrait capter l'essentiel de l'économie. `total_cost_usd` est un indicateur au tarif public, pas la consommation du forfait | [faq.md](faq.md#why-not-just-tell-the-model-to-use-subagents) |
| Benchmark des lanes, 2026-11-21 (correction de bug avec tests cachés, raisonnement à réponse exacte, étiquetage en masse de 60 lignes) | Kimi k3.1-pro, DeepSeek v4-pro, DeepSeek flash et gpt-5.6-terra : 6/6, 3/3, 60/60. gpt-6-luna : 6/6, 0/3, 58/60. gpt-6.1-sol et gpt-6-astra : ~6/6, ~3/3, ~60/60 (estimé : non proposés sur ce forfait, scores de l'exécution du 2026-11-11) | [benchmark.md](benchmark.md) |
| otomode, une exécution autonome de 5 heures | 13 tâches, un commit chacune ; la limite hebdomadaire est passée de 25 % à 31 % ; 6 invites refusées et consignées. Une exécution, pas un benchmark | [otomode.md](otomode.md#one-real-run) |

> [!WARNING]
> Les briefs quittent votre machine : chaque lane envoie son brief au fournisseur de ce modèle. Ne mettez jamais de secrets,
> de tokens ni de données personnelles dans un brief. Le hook d'otomode refuse les invites et rejette les commandes de suppression,
> de déploiement, de push et d'envoi, mais il fonctionne par correspondance de motifs : c'est un garde-fou, pas un sandbox.

## Démarrage rapide

Collez ceci dans votre agent et laissez-le installer les skills :

```text
Install multi-model-orchestra: clone https://github.com/yatuk/multi-model-orchestra,
run ./install.sh --link in it, then run ~/.claude/skills/orchestra/scripts/mmo-preflight
and tell me which lanes are ready.
```

Ou faites-le vous-même. Nécessite bash, git, `timeout` et Python 3 ; sous Windows, utilisez Git Bash.

```bash
git clone https://github.com/yatuk/multi-model-orchestra
cd multi-model-orchestra
./install.sh --link          # into ~/.claude/skills; --dir PATH for a project
~/.claude/skills/orchestra/scripts/mmo-preflight
```

`mmo-preflight` n'appelle jamais de modèle. Il indique quelles lanes existent sur cette machine, afin que le chef d'orchestre contourne celles qui manquent.
Pour otomode, lancez une fois `python ~/.claude/skills/otomode/scripts/otomode.py install` pour enregistrer son hook.

Demandez ensuite, par exemple :

- "Fix the failing tests in `internal/auth`. Follow the orchestra skill."
- "Get a second opinion from GPT on this migration plan before I merge it."
- "Ask the council: should we split this service or keep one process?"
- "otomode 6h: these four tasks, each checked with `go test ./...`."

## Compatible avec

| Outil | Utilisé pour | Nécessite |
|---|---|---|
| Claude Code | Les skills, et les paliers Claude Opus / Sonnet / Haiku comme sub-agents | Skills installés dans `~/.claude/skills` (ou dans le `.claude/skills` d'un projet) ; rien d'autre |
| Codex CLI | Lanes GPT | `codex` dans le PATH, connecté avec ChatGPT |
| Kimi Code CLI | Lanes Kimi et DeepSeek | `kimi` dans le PATH, connecté ; pour DeepSeek, un modèle `deepseek/*` dans le `config.toml` de Kimi Code |

Identifiants de modèles GPT : sur certains forfaits ChatGPT, la Codex CLI sert désormais d'autres identifiants (par exemple gpt-5.6-terra ou gpt-6-luna)
et en rejette d'autres. Les fichiers de skills nomment les valeurs par défaut ; testez les identifiants que votre forfait accepte avant d'y router du travail
(`mmo-preflight` pour voir les CLI, puis un brief `mmo-run` d'une ligne par identifiant). Voir [Model ids](how-it-works.md#model-ids).

## Pour aller plus loin

Les documents ci-dessous sont en anglais.

- [How it works](how-it-works.md) : table de routage, runner, codes de statut, modèle de sécurité, council.
- [otomode](otomode.md) : exécutions autonomes pendant votre absence.
- [Benchmark](benchmark.md) : benchmark des lanes et test A/B, avec la façon de lancer les deux.
- [FAQ](faq.md) : y compris la comparaison avec des projets similaires.
- Article (en turc) : [Fable 5.2 ile orkestra ve otomode](fable-orkestra-ve-otomode.md), sur l'usage d'un modèle de boucle principale coûteux comme chef d'orchestre et sur le fait de le laisser travailler sans surveillance.

## Arborescence

```
skills/
  orchestra/   SKILL.md, scripts/ (mmo-run, mmo-council, mmo-preflight, mmo_extract.py), templates/
  council/     chatgpt-lane/  kimi-lane/  deepseek-lane/
  otomode/     SKILL.md, scripts/ (otomode.py: switch, hook, usage gate; statusline.py)
bench/         run.sh, grade.py, tasks/, results/; ab/ for the A/B test
docs/          how-it-works, otomode, benchmark, faq, translations
```

## Licence

MIT, voir [LICENSE](../LICENSE). L'illustration du README a été générée avec gpt-image-2 via la Codex CLI.
