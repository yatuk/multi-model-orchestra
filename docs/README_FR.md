<p align="center">
  <img src="assets/logo.png" width="160" height="160" alt="logo de multi-model-orchestra : un chef d'orchestre de dessin animé avec un nœud papillon rouge levant sa baguette">
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
  <sub>Fournisseurs dont les modèles ont tourné via une lane et ont été notés dans le <a href="benchmark.md">benchmark</a>. Les noms et logos appartiennent à leurs propriétaires ; aucune approbation n'est sous-entendue.</sub>
</p>

<p align="center"><sub><a href="../README.md">English</a> · <a href="README_TR.md">Türkçe</a> · <a href="README_UK.md">Українська</a> · <a href="README_ZH.md">简体中文</a> · <a href="README_ZH-TW.md">繁體中文</a> · <a href="README_DE.md">Deutsch</a> · Français · <a href="README_ES.md">Español</a> · <a href="README_JA.md">日本語</a> · <a href="README_KO.md">한국어</a> · <a href="README_AZ.md">Azərbaycanca</a> · <a href="README_UZ.md">Oʻzbekcha</a> · <a href="README_KK.md">Қазақша</a> · <a href="README_KY.md">Кыргызча</a> · <a href="README_TK.md">Türkmençe</a> · <a href="README_CRH.md">Qırımtatarca</a> · <a href="README_UG.md">ئۇيغۇرچە</a> · <a href="README_PT.md">Português</a> · <a href="README_VI.md">Tiếng Việt</a></sub></p>

<p align="center"><b>Un modèle coûteux dirige, des modèles moins chers jouent, et chaque réponse est vérifiée avant d'être utilisée.</b><br>
Des skills pour Claude Code (ou tout outil qui lit des fichiers <code>SKILL.md</code>) qui confient le travail à Claude Opus, Sonnet et Haiku, à OpenAI GPT, à Kimi, à DeepSeek et à toute CLI d'agent ou API dont vous disposez : OpenCode, Grok, Gemini, Qwen, Cursor, Copilot, OpenRouter, des modèles locaux et plus encore.<br>
L'agent principal planifie, rédige les briefs et relit ; les autres modèles font le travail, et rien de ce qu'ils renvoient n'est considéré comme fiable tant qu'il n'a pas passé une vérification.</p>

<p align="center">
  <a href="../LICENSE"><img src="https://img.shields.io/badge/license-MIT-555" alt="Licence MIT"></a>
  <img src="https://img.shields.io/badge/lanes-32%20CLIs%20and%20APIs-2563EB" alt="32 lanes : CLI d'agents et API">
  <img src="https://img.shields.io/badge/runs%20on-bash%20·%20Git%20Bash%20on%20Windows-4EAA25" alt="Fonctionne avec bash, Git Bash sous Windows">
  <a href="https://github.com/yatuk/multi-model-orchestra"><img src="https://img.shields.io/github/stars/yatuk/multi-model-orchestra?style=social" alt="Étoiles GitHub"></a>
</p>

<p align="center"><b><a href="#démarrage-rapide">Installer</a></b> · <a href="lanes/README.md">Lanes</a> · <a href="otomode.md">otomode</a> · <a href="how-it-works.md#council">Council</a> · <a href="benchmark.md">Benchmark</a> · <a href="faq.md">FAQ</a></p>

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
      <code>mmo-run</code> est le runner unique pour toutes les lanes, avec des codes de statut stricts et un timeout sur chaque appel. Les lanes qui écrivent ne tournent que dans un worktree git qui contient votre branche, jamais dans votre checkout principal.
    </td>
    <td width="25%" valign="top">
      <b>Vérifier</b><br>
      Le chef d'orchestre lance lui-même la vérification avec <code>mmo-check</code> et lit le diff en entier : tests modifiés, fichiers hors du brief et vérification qui passerait sans le changement sont tous signalés. Le "terminé" d'une lane est une affirmation, pas un résultat.
    </td>
  </tr>
</table>

## Chiffres réels

| Quoi | Résultat | Détails |
|---|---|---|
| <!-- AB-RESULTS --> A/B : skill orchestra contre un simple "use subagents" (`claude-fable-5-2`, 2 exécutions par bras) | Même qualité : les quatre exécutions à 36/36 tests cachés, tests visibles intacts (le jeu de tâches est trop facile pour départager la qualité) | [benchmark.md](benchmark.md#ab-test-orchestra-skill-vs-use-subagents-2026-11-21) |
| <!-- AB-RESULTS --> A/B coût par exécution | Skill $1.88 contre $3.21 en moyenne, environ 40 % de moins, les intervalles ne se chevauchent pas. L'économie vient du fait que les sub-agents tournent sur Sonnet au lieu d'hériter de Fable. Pas de gain de vitesse (3.2 contre 3.5 min) | [RESULTS.md](../bench/ab/results/2026-11-21/RESULTS.md) |
| <!-- AB-RESULTS --> A/B limites | Un prompt d'une ligne "use Sonnet subagents" (2026-11-28, 2 exécutions, 36/36, moyenne $1.49, sub-agents sur Sonnet) a capté toute l'économie sans le skill ; A et B ont tourné un autre jour, ce n'est donc pas une comparaison contrôlée. `total_cost_usd` est un indicateur au tarif public, pas la consommation du forfait | [faq.md](faq.md#why-not-just-tell-the-model-to-use-subagents) |
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
- "Do this migration yourself; use the advisor skill with GPT before you start and before you say done."
- "otomode 6h: these four tasks, each checked with `go test ./...`."

## Compatible avec

| Outil | Utilisé pour | Nécessite |
|---|---|---|
| Claude Code | Les skills, et les paliers Claude Opus / Sonnet / Haiku comme sub-agents | Skills installés dans `~/.claude/skills` (ou dans le `.claude/skills` d'un projet) ; rien d'autre |
| Codex CLI | Lanes GPT | `codex` dans le PATH, connecté avec ChatGPT |
| Kimi Code CLI | Lanes Kimi et DeepSeek | `kimi` dans le PATH, connecté ; pour DeepSeek, un modèle `deepseek/*` dans le `config.toml` de Kimi Code |
| OpenCode | Tout fournisseur auquel il est connecté (DeepSeek, OpenRouter, Ollama, ses modèles gratuits) | `opencode` dans le PATH |
| Grok CLI | Lanes Grok | `grok` dans le PATH, connecté |
| Cursor CLI | Lanes Cursor | `cursor-agent` dans le PATH, connecté |
| Antigravity CLI | Lanes Antigravity | `agy` dans le PATH, connecté |
| Copilot CLI | Lanes Copilot | `copilot` dans le PATH, connecté |
| 19 autres CLI d'agents | Gemini CLI, Qwen Code, Amp, Droid, Auggie, Kiro, Cline, Kilo, Vibe, Crush, Goose, Aider, Pi, Devin, CodeBuddy, Letta Code, Qoder, gptme, llm | La CLI dans le PATH, connectée. Écrites d'après la documentation de chaque CLI et pas encore exécutées par le mainteneur : [ce que cela signifie](lanes/README.md#what-checked-means) |
| Aucune CLI | La lane `api` : tout point d'accès compatible OpenAI (OpenRouter, DeepSeek, Groq, un Ollama local, ...) pour des avis et du travail en masse | Python 3 et une clé dans une variable d'environnement |
| Agents cloud (expérimental) | Devin, agents cloud Cursor, tâches d'agent Copilot via `mmo-cloud` | Une clé du fournisseur, et le code poussé là où l'agent peut l'atteindre |

`mmo-run --list` affiche chaque lane et indique si elle est prête sur votre machine. Détails par lane : [docs/lanes](lanes/README.md).

Identifiants de modèles GPT : sur certains forfaits ChatGPT, la Codex CLI sert désormais d'autres identifiants (par exemple gpt-5.6-terra ou gpt-6-luna)
et en rejette d'autres. Les fichiers de skills nomment les valeurs par défaut ; testez les identifiants que votre forfait accepte avant d'y router du travail
(`mmo-preflight` pour voir les CLI, puis un brief `mmo-run` d'une ligne par identifiant). Voir [Model ids](how-it-works.md#model-ids).

## Première PR en 10 minutes

Pas de configuration nécessaire pour la plupart :

- **Lisez le README dans votre langue** et corrigez ce qui sonne comme une traduction automatique. Les 19 traductions ont été faites par un modèle ([tatar de Crimée](https://github.com/yatuk/multi-model-orchestra/issues/1), [ouïghour](https://github.com/yatuk/multi-model-orchestra/issues/2), [turkmène](https://github.com/yatuk/multi-model-orchestra/issues/3), [kazakh](https://github.com/yatuk/multi-model-orchestra/issues/4), [les autres](https://github.com/yatuk/multi-model-orchestra/issues/5)).
- **Collez une ligne d'erreur** donnée par une CLI (limite de débit, connexion expirée, modèle inconnu) pour que le runner sache la distinguer ([#10](https://github.com/yatuk/multi-model-orchestra/issues/10)).
- **Lancez les tests sous macOS ou Linux** et dites ce qui a cassé ([#8](https://github.com/yatuk/multi-model-orchestra/issues/8)).
- **Ajoutez une lane** pour la CLI que vous utilisez ([Gemini CLI](https://github.com/yatuk/multi-model-orchestra/issues/6), [Aider](https://github.com/yatuk/multi-model-orchestra/issues/7)), ou [votez pour la prochaine](https://github.com/yatuk/multi-model-orchestra/discussions/12).

Toutes : [good first issues](https://github.com/yatuk/multi-model-orchestra/issues?q=is%3Aissue+is%3Aopen+label%3A%22good+first+issue%22). Votre façon de router votre propre travail est la bienvenue dans [Show your routing setup](https://github.com/yatuk/multi-model-orchestra/discussions/11). Voir [CONTRIBUTING](../CONTRIBUTING.md).

## Pour aller plus loin

Les documents ci-dessous sont en anglais.

- [How it works](how-it-works.md) : table de routage, runner, codes de statut, vérification d'une lane, modèle de sécurité, council.
- [Lanes](lanes/README.md) : chaque lane, jusqu'où elle a été vérifiée, et comment en ajouter une.
- [otomode](otomode.md) : exécutions autonomes pendant votre absence.
- [Benchmark](benchmark.md) : benchmark des lanes et test A/B, avec la façon de lancer les deux.
- [Cost](cost.md) : les huit leviers de coût, et les commandes qui appliquent ou mesurent chacun.
- [FAQ](faq.md) : y compris la comparaison avec des projets similaires.
- [Failures seen](failures.md) : à quoi ressemble chaque échec et ce qui l'a corrigé.
- Article (en turc) : [Fable 5.2 ile orkestra ve otomode](fable-orkestra-ve-otomode.md), sur l'usage d'un modèle de boucle principale coûteux comme chef d'orchestre et sur le fait de le laisser travailler sans surveillance.

## Arborescence

```
skills/
  orchestra/   SKILL.md, lanes.md, templates/, scripts/ (mmo-run, mmo-check, mmo-council, mmo-score,
               mmo-cloud, mmo-preflight, providers/ with one file per lane)
  council/     chatgpt-lane/  kimi-lane/  deepseek-lane/  cloud-lane/
  otomode/     SKILL.md, scripts/ (otomode.py: switch, hook, usage gate; statusline.py)
bench/         run.sh, grade.py, tasks/, results/; ab/ for the A/B test
docs/          how-it-works, lanes/, otomode, benchmark, faq, translations
```

## Licence

MIT, voir [LICENSE](../LICENSE). L'illustration du README a été générée avec gpt-image-2 via la Codex CLI.
