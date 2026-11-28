"""The one table that says which tier a lane and model belong to (mmo-roster and mmo-score import it).

    from mmo_tiers import tier_of, note_of
    tier_of("codex", "gpt-6-astra")   -> "strong"
    tier_of("grok", "grok-4.9")       -> "middle"   (no row for the id: the lane default)
    tier_of("grok", "x", default=False) -> "unknown"  (mmo-score: no guess for an id the table lacks)

Order of decision: the first matching MODEL row (provider regex + model-name regex), then, when
default=True, the lane default, then "unknown". Tiers: strong, middle, cheap, bulk. Edit this file
and nothing else to place a new model. Run `python mmo_tiers.py` to print a few probes.
"""
import re

TIERS = ["bulk", "cheap", "middle", "strong"]  # lowest first; mmo-score escalates along this list

ANY = r"."
CHEAP_FAMILIES = r"^(deepseek|kimi|qwen|claude-deepseek|claude-kimi|claude-minimax)$"

# (provider regex, model regex on the lower-cased id, tier). First match wins.
MODEL_TIER = [
    # strong: top models of each family
    (ANY, r"opus|fable|astra|-pro-max|ultra|gemini-4-(neon|carbon)", "strong"),
    # opencode's own free models carry ids like opencode/big-pickle that say nothing about size
    (r"^opencode$", r"^opencode/", "bulk"),
    # bulk: small, fast or free. "mini" must not match inside "gemini".
    (ANY, r"haiku|luna|flash|hydrogen|(?<![a-z])mini\b|-nano|(?<![a-z])lite|-free\b|:free\b", "bulk"),
    # cheap: a fast variant of a middle model, and the cheap vendors' own models
    (ANY, r"grok.*build-fast", "cheap"),
    (ANY, r"deepseek|kimi|qwen|minimax|glm", "cheap"),
    (CHEAP_FAMILIES, ANY, "cheap"),
    # middle: everyday workhorses
    (ANY, r"sonnet|-sol\b|grok-4\.\d|composer|gemini-4-argon|abliterated-model-large", "middle"),
]

# What a lane is usually good for (skills/orchestra/lanes.md); used only when no model row matched.
LANE_TIER = {
    "codex": "middle", "claude": "middle", "claude-agent": "middle", "grok": "middle", "gemini": "middle",
    "agy": "middle", "cursor": "middle", "copilot": "middle", "amp": "middle", "droid": "middle",
    "auggie": "middle", "kiro": "middle",
    "deepseek": "cheap", "kimi": "cheap", "qwen": "cheap", "opencode": "cheap", "cline": "cheap",
    "kilo": "cheap", "vibe": "cheap", "crush": "cheap", "goose": "cheap", "aider": "cheap",
    "pi": "cheap", "claude-deepseek": "cheap", "claude-kimi": "cheap", "claude-minimax": "cheap",
}

LANE_NOTE = {"api": "opinion or bulk only: no tools, the brief must carry everything",
             "llm": "opinion or bulk only: no tools, the brief must carry everything"}


def tier_of(provider, model, default=True):
    """strong, middle, cheap or bulk; "unknown" when nothing says."""
    provider, model = provider or "", (model or "").lower()
    if model:
        for prov_re, model_re, tier in MODEL_TIER:
            if re.search(prov_re, provider) and re.search(model_re, model):
                return tier
    if default and provider in LANE_TIER:
        return LANE_TIER[provider]
    return "unknown"


def note_of(provider):
    """A short caveat for lanes that cannot touch files, else an empty string."""
    return LANE_NOTE.get(provider or "", "")


if __name__ == "__main__":
    for p, m in (("grok", "grok-4.7"), ("agy", "gemini-4-hydrogen-high"), ("api", "ablit:abliterated-model-large-flash")):
        print(p, m, tier_of(p, m))
