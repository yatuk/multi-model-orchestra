<p align="center">
  <img src="assets/logo.png" width="160" height="160" alt="multi-model-orchestra 로고: 빨간 보타이를 매고 지휘봉을 든 만화 속 지휘자">
</p>

<h1 align="center">multi-model-orchestra</h1>

<p align="center"><sub><a href="../README.md">English</a> · <a href="README_TR.md">Türkçe</a> · <a href="README_UK.md">Українська</a> · <a href="README_ZH.md">简体中文</a> · <a href="README_ZH-TW.md">繁體中文</a> · <a href="README_DE.md">Deutsch</a> · <a href="README_FR.md">Français</a> · <a href="README_ES.md">Español</a> · <a href="README_JA.md">日本語</a> · 한국어 · <a href="README_AZ.md">Azərbaycanca</a> · <a href="README_UZ.md">Oʻzbekcha</a> · <a href="README_KK.md">Қазақша</a> · <a href="README_KY.md">Кыргызча</a> · <a href="README_TK.md">Türkmençe</a> · <a href="README_CRH.md">Qırımtatarca</a> · <a href="README_UG.md">ئۇيغۇرچە</a> · <a href="README_PT.md">Português</a> · <a href="README_VI.md">Tiếng Việt</a></sub></p>

<p align="center"><b>비싼 모델 하나가 지휘하고, 더 저렴한 모델들이 연주하며, 모든 답은 사용하기 전에 검증합니다.</b><br>
Claude Code(또는 <code>SKILL.md</code> 파일을 읽는 모든 도구)용 skill로, 작업을 Claude Opus, Sonnet, Haiku, OpenAI GPT, Kimi, DeepSeek에 넘겨 줍니다.<br>
메인 agent는 계획을 세우고 brief를 작성하고 검토하며, 실제 작업은 다른 모델이 하고, 그들이 돌려주는 것은 어떤 것도 검사를 통과하기 전까지는 신뢰하지 않습니다.</p>

<p align="center">
  <a href="../LICENSE"><img src="https://img.shields.io/badge/license-MIT-555" alt="MIT 라이선스"></a>
  <img src="https://img.shields.io/badge/models-Claude%20·%20GPT%20·%20Kimi%20·%20DeepSeek-2563EB" alt="Claude, GPT, Kimi, DeepSeek lane">
  <img src="https://img.shields.io/badge/runs%20on-bash%20·%20Git%20Bash%20on%20Windows-4EAA25" alt="bash에서 실행, Windows에서는 Git Bash">
  <a href="https://github.com/yatuk/multi-model-orchestra"><img src="https://img.shields.io/github/stars/yatuk/multi-model-orchestra?style=social" alt="GitHub stars"></a>
</p>

<p align="center"><b><a href="#빠른-시작">설치</a></b> · <a href="otomode.md">otomode</a> · <a href="how-it-works.md#council">Council</a> · <a href="benchmark.md">Benchmark</a> · <a href="faq.md">FAQ</a></p>

<p align="center">
  <img src="../assets/orchestra-comic.png" alt="지휘자가 버그를 모델에 넘기고, diff를 요청하고, 블라인드 council을 연다" width="860">
  <br>
  <sub>지휘자는 파트를 나눠 주고, diff를 요청하고, 답이 판단의 문제일 때는 블라인드 council을 엽니다.</sub>
</p>

<table>
  <tr>
    <td width="25%" valign="top">
      <b>라우팅</b><br>
      각 작업은 난이도에 따라 검사를 통과할 수 있는 가장 저렴한 티어로 갑니다. lane은 감이 아니라 검사에 실패한 뒤에만 한 단계 올라갑니다.
    </td>
    <td width="25%" valign="top">
      <b>Brief</b><br>
      각 티어는 가장 잘 작동하는 brief를 받습니다. Opus에는 목표와 제약을, 더 저렴한 lane에는 번호가 매겨진 단계와 정확한 파일을 줍니다. lane은 brief만 볼 수 있으므로 brief는 처음 보는 사람을 위해 씁니다.
    </td>
    <td width="25%" valign="top">
      <b>실행</b><br>
      <code>mmo-run</code>은 모든 제공자를 위한 단 하나의 runner로, 엄격한 상태 코드와 호출마다 적용되는 타임아웃을 갖고 있습니다. 쓰기를 하는 lane은 git worktree 안에서만 실행되며, 메인 checkout에서는 절대 실행되지 않습니다.
    </td>
    <td width="25%" valign="top">
      <b>검사</b><br>
      지휘자가 직접 검사를 실행하고 diff 전체를 읽습니다. lane의 "완료"는 주장일 뿐, 결과가 아닙니다.
    </td>
  </tr>
</table>

## 실제 수치

| 항목 | 결과 | 세부 정보 |
|---|---|---|
| <!-- AB-RESULTS --> A/B: orchestra skill 대 일반 "use subagents" (`claude-fable-5-2`, 군당 2회 실행) | 품질 동일: 네 번 모두 숨겨진 테스트 36/36, 보이는 테스트도 그대로 유지 (과제 세트가 너무 쉬워 품질을 구분하지 못함) | [benchmark.md](benchmark.md#ab-test-orchestra-skill-vs-use-subagents-2026-11-21) |
| <!-- AB-RESULTS --> A/B 실행당 비용 | skill 평균 $1.88, 대조군 $3.21로 약 40% 저렴하며 범위가 겹치지 않습니다. 절감은 sub-agent가 Fable을 상속하지 않고 Sonnet에서 실행되기 때문입니다. 속도 이득은 없습니다 (3.2분 대 3.5분) | [RESULTS.md](../bench/ab/results/2026-11-21/RESULTS.md) |
| <!-- AB-RESULTS --> A/B의 한계 | 한 줄짜리 "use Sonnet subagents" 프롬프트는 테스트하지 않았으며 절감의 대부분을 얻을 수도 있습니다. `total_cost_usd`는 정가 기준의 대용 지표이지 플랜 사용량이 아닙니다 | [faq.md](faq.md#why-not-just-tell-the-model-to-use-subagents) |
| lane benchmark, 2026-11-21 (숨겨진 테스트가 있는 버그 수정, 정확한 답이 있는 추론, 60줄 일괄 라벨링) | Kimi k3.1-pro, DeepSeek v4-pro, DeepSeek flash, gpt-5.6-terra: 6/6, 3/3, 60/60. gpt-6-luna: 6/6, 0/3, 58/60. gpt-6.1-sol과 gpt-6-astra: 약 6/6, 약 3/3, 약 60/60 (추정치: 해당 플랜에서 제공되지 않아 점수는 2026-11-11 실행 결과 사용) | [benchmark.md](benchmark.md) |
| otomode, 5시간 무인 실행 1회 | 작업 13개, 작업마다 commit 1개. 주간 한도는 25%에서 31%로 증가. 프롬프트 6건을 거부하고 기록. 한 번의 실행이며 benchmark가 아닙니다 | [otomode.md](otomode.md#one-real-run) |

> [!WARNING]
> brief는 여러분의 컴퓨터 밖으로 나갑니다. 모든 lane은 자신의 brief를 해당 모델의 벤더에 전송합니다. brief에는 비밀 값, token,
> 개인 데이터를 절대 넣지 마세요. otomode의 hook은 프롬프트를 거부하고 삭제, 배포, push, 전송 명령을 거부하지만,
> 패턴을 매칭하는 방식입니다. 가드레일일 뿐 샌드박스가 아닙니다.

## 빠른 시작

아래 내용을 agent에 붙여 넣어 skill을 설치하게 하세요.

```text
Install multi-model-orchestra: clone https://github.com/yatuk/multi-model-orchestra,
run ./install.sh --link in it, then run ~/.claude/skills/orchestra/scripts/mmo-preflight
and tell me which lanes are ready.
```

직접 설치할 수도 있습니다. bash, git, `timeout`, Python 3이 필요하며, Windows에서는 Git Bash를 사용하세요.

```bash
git clone https://github.com/yatuk/multi-model-orchestra
cd multi-model-orchestra
./install.sh --link          # into ~/.claude/skills; --dir PATH for a project
~/.claude/skills/orchestra/scripts/mmo-preflight
```

`mmo-preflight`는 어떤 모델도 호출하지 않습니다. 이 컴퓨터에 어떤 lane이 있는지 알려 주므로, 지휘자는 없는 lane을 피해서 라우팅합니다.
otomode의 경우 hook을 등록하려면 `python ~/.claude/skills/otomode/scripts/otomode.py install`을 한 번 실행하세요.

그런 다음 예를 들어 이렇게 요청하세요.

- "`internal/auth`에서 실패하는 테스트를 고쳐 줘. orchestra skill을 따라서."
- "이 마이그레이션 계획을 머지하기 전에 GPT에게 세컨드 오피니언을 받아 줘."
- "council에 물어봐: 이 서비스를 쪼갤까, 아니면 하나의 프로세스로 둘까?"
- "otomode 6h: 이 네 가지 작업, 각각 `go test ./...`로 검사해 줘."

## 함께 쓰는 도구

| 도구 | 용도 | 필요한 것 |
|---|---|---|
| Claude Code | skill, 그리고 sub-agent로서의 Claude Opus / Sonnet / Haiku 티어 | skill이 `~/.claude/skills`(또는 프로젝트의 `.claude/skills`)에 설치되어 있을 것. 그 외에는 필요 없음 |
| Codex CLI | GPT lane | PATH에 `codex`가 있고 ChatGPT로 로그인되어 있을 것 |
| Kimi Code CLI | Kimi와 DeepSeek lane | PATH에 `kimi`가 있고 로그인되어 있을 것. DeepSeek은 Kimi Code의 `config.toml`에 `deepseek/*` 모델이 있어야 함 |

GPT 모델 id: 일부 ChatGPT 플랜에서는 Codex CLI가 이제 다른 id(예: gpt-5.6-terra 또는 gpt-6-luna)를 제공하고
다른 id는 거부합니다. skill 파일에는 기본값이 적혀 있습니다. 작업을 그쪽으로 라우팅하기 전에 자신의 플랜이 받아들이는 id를
스모크 테스트하세요(`mmo-preflight`로 CLI를 확인한 다음, id마다 한 줄짜리 `mmo-run` brief를 실행). [Model ids](how-it-works.md#model-ids)를 참고하세요.

## 더 보기

아래 문서는 영어입니다.

- [How it works](how-it-works.md): 라우팅 표, runner, 상태 코드, 안전 모델, council.
- [otomode](otomode.md): 자리를 비운 동안의 무인 실행.
- [Benchmark](benchmark.md): lane benchmark와 A/B 테스트, 그리고 둘을 실행하는 방법.
- [FAQ](faq.md): 유사한 프로젝트와의 비교 포함.
- 글(터키어): [Fable 5.2 ile orkestra ve otomode](fable-orkestra-ve-otomode.md), 비싼 메인 루프 모델을 지휘자로 쓰고 무인으로 일하게 두는 방법에 대해.

## 디렉터리 구조

```
skills/
  orchestra/   SKILL.md, scripts/ (mmo-run, mmo-council, mmo-preflight, mmo_extract.py), templates/
  council/     chatgpt-lane/  kimi-lane/  deepseek-lane/
  otomode/     SKILL.md, scripts/ (otomode.py: switch, hook, usage gate; statusline.py)
bench/         run.sh, grade.py, tasks/, results/; ab/ for the A/B test
docs/          how-it-works, otomode, benchmark, faq, translations
```

## 라이선스

MIT, [LICENSE](../LICENSE)를 참고하세요. README 일러스트는 Codex CLI를 통해 gpt-image-2로 생성했습니다.
