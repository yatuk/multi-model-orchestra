<p align="center">
  <img src="assets/logo.png" width="160" height="160" alt="logo do multi-model-orchestra: um maestro de desenho animado com gravata-borboleta vermelha erguendo a batuta">
</p>

<h1 align="center">multi-model-orchestra</h1>

<p align="center"><sub><a href="../README.md">English</a> · <a href="README_TR.md">Türkçe</a> · <a href="README_UK.md">Українська</a> · <a href="README_ZH.md">简体中文</a> · <a href="README_ZH-TW.md">繁體中文</a> · <a href="README_DE.md">Deutsch</a> · <a href="README_FR.md">Français</a> · <a href="README_ES.md">Español</a> · <a href="README_JA.md">日本語</a> · <a href="README_KO.md">한국어</a> · <a href="README_AZ.md">Azərbaycanca</a> · <a href="README_UZ.md">Oʻzbekcha</a> · <a href="README_KK.md">Қазақша</a> · <a href="README_KY.md">Кыргызча</a> · <a href="README_TK.md">Türkmençe</a> · <a href="README_CRH.md">Qırımtatarca</a> · <a href="README_UG.md">ئۇيغۇرچە</a> · Português · <a href="README_VI.md">Tiếng Việt</a></sub></p>

<p align="center"><b>Deixe um modelo caro reger, modelos mais baratos tocarem, e cada resposta ser verificada antes de ser usada.</b><br>
Skills para o Claude Code (ou qualquer coisa que leia arquivos <code>SKILL.md</code>) que repassam trabalho ao Claude Opus, Sonnet e Haiku, ao OpenAI GPT, ao Kimi e ao DeepSeek.<br>
O agente principal planeja, escreve os briefs e revisa; os outros modelos fazem o trabalho, e nada do que devolvem é considerado confiável até passar por uma verificação.</p>

<p align="center">
  <a href="../LICENSE"><img src="https://img.shields.io/badge/license-MIT-555" alt="Licença MIT"></a>
  <img src="https://img.shields.io/badge/models-Claude%20·%20GPT%20·%20Kimi%20·%20DeepSeek-2563EB" alt="Lanes de Claude, GPT, Kimi e DeepSeek">
  <img src="https://img.shields.io/badge/runs%20on-bash%20·%20Git%20Bash%20on%20Windows-4EAA25" alt="Roda em bash, Git Bash no Windows">
  <a href="https://github.com/yatuk/multi-model-orchestra"><img src="https://img.shields.io/github/stars/yatuk/multi-model-orchestra?style=social" alt="Estrelas no GitHub"></a>
</p>

<p align="center"><b><a href="#início-rápido">Instalar</a></b> · <a href="otomode.md">otomode</a> · <a href="how-it-works.md#council">Council</a> · <a href="benchmark.md">Benchmark</a> · <a href="faq.md">FAQ</a></p>

<p align="center">
  <img src="../assets/orchestra-comic.png" alt="Um maestro entrega um bug a um modelo, pede o diff e convoca um council às cegas" width="860">
  <br>
  <sub>O maestro distribui as partes, pede o diff e convoca um council às cegas quando a resposta é uma questão de julgamento.</sub>
</p>

<table>
  <tr>
    <td width="25%" valign="top">
      <b>Rotear</b><br>
      Cada tarefa vai, conforme a dificuldade, para o nível mais barato que consiga passar na sua verificação. Uma lane só sobe de nível depois de falhar na verificação, não por palpite.
    </td>
    <td width="25%" valign="top">
      <b>Brief</b><br>
      Cada nível recebe o brief com o qual trabalha melhor: objetivo e restrições para o Opus, passos numerados e arquivos exatos para as lanes mais baratas. Uma lane vê só o brief, então ele é escrito para um estranho.
    </td>
    <td width="25%" valign="top">
      <b>Executar</b><br>
      <code>mmo-run</code> é o runner único para todos os provedores, com códigos de status rígidos e um timeout em cada chamada. Lanes que escrevem rodam apenas em um worktree do git, nunca no seu checkout principal.
    </td>
    <td width="25%" valign="top">
      <b>Verificar</b><br>
      O maestro roda a verificação ele mesmo e lê o diff inteiro. O "pronto" de uma lane é uma alegação, não um resultado.
    </td>
  </tr>
</table>

## Números reais

| O quê | Resultado | Detalhes |
|---|---|---|
| <!-- AB-RESULTS --> A/B: skill orchestra contra um simples "use subagents" (`claude-fable-5-2`, 2 execuções por braço) | Mesma qualidade: as quatro execuções com 36/36 testes ocultos, testes visíveis intactos (o conjunto de tarefas é fácil demais para separar a qualidade) | [benchmark.md](benchmark.md#ab-test-orchestra-skill-vs-use-subagents-2026-11-21) |
| <!-- AB-RESULTS --> A/B custo por execução | Skill $1.88 contra $3.21 em média, cerca de 40% a menos, as faixas não se sobrepõem. A economia vem de os sub-agents rodarem no Sonnet em vez de herdarem o Fable. Sem ganho de velocidade (3.2 contra 3.5 min) | [RESULTS.md](../bench/ab/results/2026-11-21/RESULTS.md) |
| <!-- AB-RESULTS --> A/B limites | Um prompt de uma linha "use Sonnet subagents" não foi testado e pode capturar a maior parte da economia. `total_cost_usd` é um indicador a preço de tabela, não o uso do plano | [faq.md](faq.md#why-not-just-tell-the-model-to-use-subagents) |
| Benchmark de lanes, 2026-11-21 (correção de bug com testes ocultos, raciocínio de resposta exata, rotulagem em massa de 60 linhas) | Kimi k3.1-pro, DeepSeek v4-pro, DeepSeek flash e gpt-5.6-terra: 6/6, 3/3, 60/60. gpt-6-luna: 6/6, 0/3, 58/60. gpt-6.1-sol e gpt-6-astra: ~6/6, ~3/3, ~60/60 (estimado: não oferecidos nesse plano, pontuações da execução de 2026-11-11) | [benchmark.md](benchmark.md) |
| otomode, uma execução autônoma de 5 horas | 13 tarefas, um commit cada; o limite semanal foi de 25% para 31%; 6 prompts negados e registrados. Uma execução, não um benchmark | [otomode.md](otomode.md#one-real-run) |

> [!WARNING]
> Os briefs saem da sua máquina: cada lane envia o seu brief ao fornecedor daquele modelo. Nunca coloque segredos, tokens
> ou dados pessoais em um brief. O hook do otomode nega prompts e recusa comandos de exclusão, deploy, push e envio,
> mas ele funciona por correspondência de padrões: é um guarda-corpo, não um sandbox.

## Início rápido

Cole isto no seu agente e deixe que ele instale os skills:

```text
Install multi-model-orchestra: clone https://github.com/yatuk/multi-model-orchestra,
run ./install.sh --link in it, then run ~/.claude/skills/orchestra/scripts/mmo-preflight
and tell me which lanes are ready.
```

Ou faça você mesmo. Requer bash, git, `timeout` e Python 3; no Windows, use o Git Bash.

```bash
git clone https://github.com/yatuk/multi-model-orchestra
cd multi-model-orchestra
./install.sh --link          # into ~/.claude/skills; --dir PATH for a project
~/.claude/skills/orchestra/scripts/mmo-preflight
```

O `mmo-preflight` nunca chama um modelo. Ele diz quais lanes existem nesta máquina, para que o maestro roteie contornando as que faltam.
Para o otomode, rode uma vez `python ~/.claude/skills/otomode/scripts/otomode.py install` para registrar o hook dele.

Depois peça, por exemplo:

- "Fix the failing tests in `internal/auth`. Follow the orchestra skill."
- "Get a second opinion from GPT on this migration plan before I merge it."
- "Ask the council: should we split this service or keep one process?"
- "otomode 6h: these four tasks, each checked with `go test ./...`."

## Funciona com

| Ferramenta | Usada para | Requer |
|---|---|---|
| Claude Code | Os skills e os níveis Claude Opus / Sonnet / Haiku como sub-agents | Skills instalados em `~/.claude/skills` (ou no `.claude/skills` de um projeto); nada além disso |
| Codex CLI | Lanes GPT | `codex` no PATH, com login no ChatGPT |
| Kimi Code CLI | Lanes Kimi e DeepSeek | `kimi` no PATH, com login; para o DeepSeek, um modelo `deepseek/*` no `config.toml` do Kimi Code |

IDs de modelos GPT: em alguns planos do ChatGPT, a Codex CLI agora serve ids diferentes (por exemplo gpt-5.6-terra ou gpt-6-luna)
e rejeita outros. Os arquivos de skills indicam os padrões; teste os ids que o seu plano aceita antes de rotear trabalho para lá
(`mmo-preflight` para ver as CLIs e depois um brief de uma linha com `mmo-run` por id). Veja [Model ids](how-it-works.md#model-ids).

## Mais

Os documentos abaixo estão em inglês.

- [How it works](how-it-works.md): tabela de roteamento, runner, códigos de status, modelo de segurança, council.
- [otomode](otomode.md): execuções autônomas enquanto você está fora.
- [Benchmark](benchmark.md): benchmark de lanes e o teste A/B, com instruções de como rodar ambos.
- [FAQ](faq.md): inclusive como isto se compara a projetos semelhantes.
- Artigo (em turco): [Fable 5.2 ile orkestra ve otomode](fable-orkestra-ve-otomode.md), sobre usar um modelo caro de loop principal como maestro e deixá-lo trabalhando sem supervisão.

## Estrutura

```
skills/
  orchestra/   SKILL.md, scripts/ (mmo-run, mmo-council, mmo-preflight, mmo_extract.py), templates/
  council/     chatgpt-lane/  kimi-lane/  deepseek-lane/
  otomode/     SKILL.md, scripts/ (otomode.py: switch, hook, usage gate; statusline.py)
bench/         run.sh, grade.py, tasks/, results/; ab/ for the A/B test
docs/          how-it-works, otomode, benchmark, faq, translations
```

## Licença

MIT, veja [LICENSE](../LICENSE). A ilustração do README foi gerada com o gpt-image-2 por meio da Codex CLI.
