<p align="center">
  <img src="assets/logo.png" width="160" height="160" alt="logo do multi-model-orchestra: um maestro de desenho animado com gravata-borboleta vermelha erguendo a batuta">
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
  <sub>Fornecedores cujos modelos foram executados por uma lane e pontuados no <a href="benchmark.md">benchmark</a>. Nomes e logotipos pertencem aos seus proprietários; nenhum endosso é implícito.</sub>
</p>

<p align="center"><sub><a href="../README.md">English</a> · <a href="README_TR.md">Türkçe</a> · <a href="README_UK.md">Українська</a> · <a href="README_ZH.md">简体中文</a> · <a href="README_ZH-TW.md">繁體中文</a> · <a href="README_DE.md">Deutsch</a> · <a href="README_FR.md">Français</a> · <a href="README_ES.md">Español</a> · <a href="README_JA.md">日本語</a> · <a href="README_KO.md">한국어</a> · <a href="README_AZ.md">Azərbaycanca</a> · <a href="README_UZ.md">Oʻzbekcha</a> · <a href="README_KK.md">Қазақша</a> · <a href="README_KY.md">Кыргызча</a> · <a href="README_TK.md">Türkmençe</a> · <a href="README_CRH.md">Qırımtatarca</a> · <a href="README_UG.md">ئۇيغۇرچە</a> · Português · <a href="README_VI.md">Tiếng Việt</a></sub></p>

<p align="center"><b>Deixe um modelo caro reger, modelos mais baratos tocarem, e cada resposta ser verificada antes de ser usada.</b><br>
Skills para o Claude Code (ou qualquer coisa que leia arquivos <code>SKILL.md</code>) que repassam trabalho ao Claude Opus, Sonnet e Haiku, ao OpenAI GPT, ao Kimi, ao DeepSeek e a qualquer CLI de agente ou API que você tenha: OpenCode, Grok, Gemini, Qwen, Cursor, Copilot, OpenRouter, modelos locais e mais.<br>
O agente principal planeja, escreve os briefs e revisa; os outros modelos fazem o trabalho, e nada do que devolvem é considerado confiável até passar por uma verificação.</p>

<p align="center">
  <a href="../LICENSE"><img src="https://img.shields.io/badge/license-MIT-555" alt="Licença MIT"></a>
  <img src="https://img.shields.io/badge/lanes-32%20CLIs%20and%20APIs-2563EB" alt="32 lanes: CLIs de agentes e APIs">
  <img src="https://img.shields.io/badge/runs%20on-bash%20·%20Git%20Bash%20on%20Windows-4EAA25" alt="Roda em bash, Git Bash no Windows">
  <a href="https://github.com/yatuk/multi-model-orchestra"><img src="https://img.shields.io/github/stars/yatuk/multi-model-orchestra?style=social" alt="Estrelas no GitHub"></a>
</p>

<p align="center"><b><a href="#início-rápido">Instalar</a></b> · <a href="lanes/README.md">Lanes</a> · <a href="otomode.md">otomode</a> · <a href="how-it-works.md#council">Council</a> · <a href="benchmark.md">Benchmark</a> · <a href="faq.md">FAQ</a></p>

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
      <code>mmo-run</code> é o runner único para todas as lanes, com códigos de status rígidos e um timeout em cada chamada. Lanes que escrevem rodam apenas em um worktree do git que contém a sua branch, nunca no seu checkout principal.
    </td>
    <td width="25%" valign="top">
      <b>Verificar</b><br>
      O maestro roda a verificação ele mesmo com o <code>mmo-check</code> e lê o diff inteiro: testes alterados, arquivos fora do brief e uma verificação que passaria sem a mudança são todos sinalizados. O "pronto" de uma lane é uma alegação, não um resultado.
    </td>
  </tr>
</table>

## Números reais

| O quê | Resultado | Detalhes |
|---|---|---|
| <!-- AB-RESULTS --> A/B: skill orchestra contra um simples "use subagents" (`claude-fable-5-2`, 2 execuções por braço) | Mesma qualidade: as quatro execuções com 36/36 testes ocultos, testes visíveis intactos (o conjunto de tarefas é fácil demais para separar a qualidade) | [benchmark.md](benchmark.md#ab-test-orchestra-skill-vs-use-subagents-2026-11-21) |
| <!-- AB-RESULTS --> A/B custo por execução | Skill $1.88 contra $3.21 em média, cerca de 40% a menos, as faixas não se sobrepõem. A economia vem de os sub-agents rodarem no Sonnet em vez de herdarem o Fable. Sem ganho de velocidade (3.2 contra 3.5 min) | [RESULTS.md](../bench/ab/results/2026-11-21/RESULTS.md) |
| <!-- AB-RESULTS --> A/B limites | Um prompt de uma linha "use Sonnet subagents" (2026-11-28, 2 execuções, 36/36, média $1.49, sub-agents no Sonnet) capturou toda a economia sem o skill; A e B rodaram em outro dia, então não é uma comparação controlada. `total_cost_usd` é um indicador a preço de tabela, não o uso do plano | [faq.md](faq.md#why-not-just-tell-the-model-to-use-subagents) |
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
- "Do this migration yourself; use the advisor skill with GPT before you start and before you say done."
- "otomode 6h: these four tasks, each checked with `go test ./...`."

## Funciona com

| Ferramenta | Usada para | Requer |
|---|---|---|
| Claude Code | Os skills e os níveis Claude Opus / Sonnet / Haiku como sub-agents | Skills instalados em `~/.claude/skills` (ou no `.claude/skills` de um projeto); nada além disso |
| Codex CLI | Lanes GPT | `codex` no PATH, com login no ChatGPT |
| Kimi Code CLI | Lanes Kimi e DeepSeek | `kimi` no PATH, com login; para o DeepSeek, um modelo `deepseek/*` no `config.toml` do Kimi Code |
| OpenCode | Qualquer provedor em que ele esteja logado (DeepSeek, OpenRouter, Ollama, seus modelos gratuitos) | `opencode` no PATH |
| Grok CLI | Lanes Grok | `grok` no PATH, com login |
| Cursor CLI | Lanes Cursor | `cursor-agent` no PATH, com login |
| Antigravity CLI | Lanes Antigravity | `agy` no PATH, com login |
| Copilot CLI | Lanes Copilot | `copilot` no PATH, com login |
| Mais 19 CLIs de agentes | Gemini CLI, Qwen Code, Amp, Droid, Auggie, Kiro, Cline, Kilo, Vibe, Crush, Goose, Aider, Pi, Devin, CodeBuddy, Letta Code, Qoder, gptme, llm | A CLI no PATH, com login. Escritas a partir da documentação de cada CLI e ainda não executadas pelo mantenedor: [o que isso significa](lanes/README.md#what-checked-means) |
| Nenhuma CLI | A lane `api`: qualquer endpoint compatível com a OpenAI (OpenRouter, DeepSeek, Groq, um Ollama local, ...) para opiniões e trabalho em massa | Python 3 e uma chave em uma variável de ambiente |
| Agentes na nuvem (experimental) | Devin, agentes na nuvem do Cursor, tarefas de agente do Copilot por meio do `mmo-cloud` | Uma chave do fornecedor, e o código enviado para onde o agente consiga acessá-lo |

O `mmo-run --list` mostra cada lane e se ela está pronta na sua máquina. Detalhes por lane: [docs/lanes](lanes/README.md).

IDs de modelos GPT: em alguns planos do ChatGPT, a Codex CLI agora serve ids diferentes (por exemplo gpt-5.6-terra ou gpt-6-luna)
e rejeita outros. Os arquivos de skills indicam os padrões; teste os ids que o seu plano aceita antes de rotear trabalho para lá
(`mmo-preflight` para ver as CLIs e depois um brief de uma linha com `mmo-run` por id). Veja [Model ids](how-it-works.md#model-ids).

## Primeiro PR em 10 minutos

Para a maioria não é preciso configurar nada:

- **Leia o README no seu idioma** e corrija o que soar como tradução de máquina. Todas as 19 traduções foram feitas por um modelo ([tártaro da Crimeia](https://github.com/yatuk/multi-model-orchestra/issues/1), [uigur](https://github.com/yatuk/multi-model-orchestra/issues/2), [turcomeno](https://github.com/yatuk/multi-model-orchestra/issues/3), [cazaque](https://github.com/yatuk/multi-model-orchestra/issues/4), [as demais](https://github.com/yatuk/multi-model-orchestra/issues/5)).
- **Cole uma linha de erro** que uma CLI lhe deu (limite de uso, login expirado, modelo desconhecido) para que o runner consiga distingui-la ([#10](https://github.com/yatuk/multi-model-orchestra/issues/10)).
- **Rode os testes no macOS ou no Linux** e diga o que quebrou ([#8](https://github.com/yatuk/multi-model-orchestra/issues/8)).
- **Adicione uma lane** para a CLI que você usa ([Gemini CLI](https://github.com/yatuk/multi-model-orchestra/issues/6), [Aider](https://github.com/yatuk/multi-model-orchestra/issues/7)), ou [vote na próxima](https://github.com/yatuk/multi-model-orchestra/discussions/12).

Todas elas: [good first issues](https://github.com/yatuk/multi-model-orchestra/issues?q=is%3Aissue+is%3Aopen+label%3A%22good+first+issue%22). A forma como você roteia o seu próprio trabalho é bem-vinda em [Show your routing setup](https://github.com/yatuk/multi-model-orchestra/discussions/11). Veja [CONTRIBUTING](../CONTRIBUTING.md).

## Mais

Os documentos abaixo estão em inglês.

- [How it works](how-it-works.md): tabela de roteamento, runner, códigos de status, verificação de uma lane, modelo de segurança, council.
- [Lanes](lanes/README.md): cada lane, até onde ela foi verificada e como adicionar uma.
- [otomode](otomode.md): execuções autônomas enquanto você está fora.
- [Benchmark](benchmark.md): benchmark de lanes e o teste A/B, com instruções de como rodar ambos.
- [Cost](cost.md): as oito alavancas de custo e os comandos que aplicam ou medem cada uma.
- [FAQ](faq.md): inclusive como isto se compara a projetos semelhantes.
- [Failures seen](failures.md): como cada falha se apresenta e o que a corrigiu.
- Artigo (em turco): [Fable 5.2 ile orkestra ve otomode](fable-orkestra-ve-otomode.md), sobre usar um modelo caro de loop principal como maestro e deixá-lo trabalhando sem supervisão.

## Estrutura

```
skills/
  orchestra/   SKILL.md, lanes.md, templates/, scripts/ (mmo-run, mmo-check, mmo-council, mmo-score,
               mmo-cloud, mmo-preflight, providers/ with one file per lane)
  council/     chatgpt-lane/  kimi-lane/  deepseek-lane/  cloud-lane/
  otomode/     SKILL.md, scripts/ (otomode.py: switch, hook, usage gate; statusline.py)
bench/         run.sh, grade.py, tasks/, results/; ab/ for the A/B test
docs/          how-it-works, lanes/, otomode, benchmark, faq, translations
```

## Licença

MIT, veja [LICENSE](../LICENSE). A ilustração do README foi gerada com o gpt-image-2 por meio da Codex CLI.
