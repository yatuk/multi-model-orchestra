# The api lane, and Claude Code on other vendors

## The api lane

`api` talks to any OpenAI-compatible chat endpoint with one HTTP request. No agent CLI is involved.
Use it for a second opinion or for bulk work on text you hand over in the brief.

The model is written `endpoint:model`. Only the first colon splits, so model ids may hold slashes
and colons. There is no default model.

```bash
# OpenRouter (key in OPENROUTER_API_KEY)
mmo-run api --brief brief.md --out out.md -m openrouter:deepseek/deepseek-v4-pro

# DeepSeek direct (key in DEEPSEEK_API_KEY)
mmo-run api --brief brief.md --out out.md -m deepseek:deepseek-v4-pro

# A local Ollama (no key; the model must already be pulled)
mmo-run api --brief brief.md --out out.md -m ollama:qwen3:8b
```

What it cannot do:

- It has no tools. It cannot read your repo, run commands or edit files, so the brief must carry
  every file excerpt and fact it needs. `--mode rw` is refused (exit 2).
- One request, no streaming. A long answer from a slow model can take minutes: raise `-t` and
  `MMO_API_TIMEOUT` (default 600 seconds) together.

Failures classify as usual: HTTP 401 or a missing key is `auth` (exit 7), 402 and 429 are `limit`
(exit 6), an unknown model is `model` (exit 8). A missing key prints `no API key: set <VARIABLE>`.
Moonshot reports an empty balance as 429, so it reads as `limit` too.

### Endpoint table

| Name | Base URL | Key variable |
|---|---|---|
| openrouter | https://openrouter.ai/api/v1 | OPENROUTER_API_KEY |
| deepseek | https://api.deepseek.com | DEEPSEEK_API_KEY |
| moonshot | https://api.moonshot.ai/v1 | MOONSHOT_API_KEY |
| zai | https://api.z.ai/api/paas/v4 | ZAI_API_KEY |
| minimax | https://api.minimax.io/v1 | MINIMAX_API_KEY |
| xai | https://api.x.ai/v1 | XAI_API_KEY |
| mistral | https://api.mistral.ai/v1 | MISTRAL_API_KEY |
| groq | https://api.groq.com/openai/v1 | GROQ_API_KEY |
| cerebras | https://api.cerebras.ai/v1 | CEREBRAS_API_KEY |
| together | https://api.together.ai/v1 | TOGETHER_API_KEY |
| fireworks | https://api.fireworks.ai/inference/v1 | FIREWORKS_API_KEY |
| gemini | https://generativelanguage.googleapis.com/v1beta/openai | GEMINI_API_KEY |
| ollama | http://localhost:11434/v1 | none |
| lmstudio | http://localhost:1234/v1 | none |

The base URLs come from each vendor's documentation. Where the vendor names no key variable
(zai, minimax, fireworks, gemini), the variable name is this lane's own choice. Model ids change
often: check the vendor's list. Left out on purpose: Alibaba DashScope (its URL holds your workspace
id: use the override below) and llama.cpp (its default port is not certain: use the override).

### Other endpoints and overrides

Any name works through two variables (the name is upper-cased):

```bash
export MMO_API_MYHOST_URL=https://llm.example.com/v1
export MMO_API_MYHOST_KEY=...          # set it to an empty string for no Authorization header
mmo-run api --brief brief.md --out out.md -m myhost:some-model
```

The same variables override a table entry, for example `MMO_API_OLLAMA_URL` to reach Ollama on
another machine. Optional: `MMO_API_MAX_TOKENS` (sent as `max_tokens`), `MMO_API_TIMEOUT`.
`mmo-run` also sets `MMO_API_USAGE_FILE`: the response's `usage` numbers (and `cost` when the endpoint
returns one, as OpenRouter can) and its `model` are written there, never the key or the prompt, so
stdout stays the pure answer. A 429 with a `Retry-After` header puts it in the error line.
The key is read from the environment, sent only as a Bearer header, and never printed or written to
the out file.

## Where the keys live

Either export the key variables in your shell, or put them in one file outside every repository:
`~/.config/mmo/keys.env` (or the file `MMO_KEYS_FILE` names), one `NAME=value` per line. `mmo-run` reads it
for every lane, in the lane's own child process only (and in a throwaway subshell for `--list`), so the
`claude-deepseek`, `claude-kimi` and `claude-minimax` lanes find their keys there too, and a key never
reaches the conductor, the brief or the output file. Keep it
readable by you alone (`chmod 600`). A custom endpoint is two lines there:

```
MMO_API_MYHOST_URL=https://api.example.com/v1
MMO_API_MYHOST_KEY=...
```

and is used as `mmo-run api -m myhost:<model>`.

## Claude Code on another vendor

Anthropic does not support running Claude Code on other vendors' models. The vendors document it,
so these lanes exist, but expect rough edges. They reuse the `claude` lane (so the same read-only
tool limits apply) and only set the environment: `ANTHROPIC_BASE_URL`, `ANTHROPIC_AUTH_TOKEN`
copied from the vendor's key, an empty `ANTHROPIC_API_KEY` (so a saved claude.ai login is not
used) and the model variables. `-m` sets all the model variables.

| Lane | Endpoint | Key variable | Default model |
|---|---|---|---|
| claude-deepseek | https://api.deepseek.com/anthropic | DEEPSEEK_API_KEY | deepseek-v4-pro |
| claude-kimi | https://api.moonshot.ai/anthropic | MOONSHOT_API_KEY | kimi-k3 |
| claude-minimax | https://api.minimax.io/anthropic | MINIMAX_API_KEY | MiniMax-M3.1-Flash |

With the key missing, the lane fails with `no API key: set <VARIABLE>` (status `auth`) and
`mmo-run --list` shows it as `setup`. There is no `claude-glm` lane: the Z.ai page gives
inconsistent model ids (glm-5.4 in the Claude Code guide, glm-5.3 elsewhere), so none was guessed.
Remove stale `ANTHROPIC_*` entries from your Claude Code `settings.json`: they override the shell.

## Pointing the Codex CLI at another provider (note only, no adapter)

Codex reads provider tables from `~/.codex/config.toml` (a project `.codex/config.toml` cannot define
them):

```toml
[model_providers.mistral]
name = "Mistral"
base_url = "https://api.mistral.ai/v1"
env_key = "MISTRAL_API_KEY"   # the NAME of the variable, not the key
```

Then `codex exec -c model_provider=mistral -c model=devstral-latest "..."`, or keep a separate setup
in `~/.codex/<name>.config.toml` and run `codex --profile <name>`. The ids openai, ollama, lmstudio,
amazon-bedrock, amazon-bedrock-runtime and gcp are reserved, so a local Ollama entry needs another
id. Vendors that offer only Chat Completions may not work with `wire_api = "responses"`; which
values Codex still accepts was not confirmed.
