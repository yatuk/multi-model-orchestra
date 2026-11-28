---
name: council
description: Ask the same question to three models from different families, read-only and in parallel, then judge the answers blind against a rubric written first. Use for design decisions, risky trade-offs, root-cause hypotheses and reviews where one model's view is not enough and at least part of the answer can be checked. Needs the orchestra skill's scripts.
---

# Council

One model can be confidently wrong. Three models from different families are wrong in different ways,
and the differences are where the useful information is.

## When it helps, and when it does not

- It helps when the answers are discrete (which option, yes or no, which root cause) or carry claims
  you can check. Then three independent answers are three leads.
- It is weak for open design taste, where you, the judge, are the bottleneck: you will pick the answer
  that sounds like your own plan. Say so instead of dressing a preference up as a panel result.
- One round only. A vote among independent answers gives most of what a debate gives; panelists who
  read each other mostly end up agreeing.
- Three families, not three sizes of one family: models from one family share their mistakes.

## Run it

1. Write the question to a file. Include the evidence (code excerpts, logs, constraints) and say what a good
   answer looks like: a recommendation, the main risk, and what would change the recommendation.
   If you already have a plan, state it as one option among others, not as "our plan".
2. **Before you run it**, write the rubric into `council/rubric.md`: the three to five things a good
   answer must get right, and which of them you can check. A rubric written after reading the answers
   only describes the answer you liked.
3. Run it. The default panel is GPT, Kimi and DeepSeek; pass `--lane` for the lanes that are ready on
   this machine (`mmo-run --list`), one per family:

```bash
../orchestra/scripts/mmo-council --question q.md --outdir council/ -C <repo>
../orchestra/scripts/mmo-council --question q.md --outdir council/ \
  --lane codex:gpt-6-astra --lane deepseek:deepseek/deepseek-v4-pro --lane api:openrouter:<model>
```

4. Check `status.txt`. A lane marked FAILED (including `model`, a rejected model id) is not an answer and
   not a vote. If fewer than two lanes answered, say so and do not call it a council.
5. Read `answer-A.md`, `answer-B.md`, ... **before** opening `key.txt`. The letters are shuffled, so you
   judge the reasoning and not the brand.

## Judge it

- Score each answer against the rubric, claim by claim, not "which one is best overall".
- Check the checkable claims yourself (run the code, read the file, look up the API). A claim you
  checked outranks any number of votes.
- Then read the answers once more in the order given in `order-reversed.txt` and see whether your
  ranking holds. The answer read first gets an unearned head start.
- Agreement is a hint, not proof: models share training data and blind spots.
- A single dissent with a concrete, checkable argument beats a majority with none.
- Your final answer is your own synthesis. Do not paste one panelist's answer as the result.
- Tell the user which models answered, which failed, and where the panel split.
- Note in one line whether the panel agreed or split. A panel that always agrees is costing you three
  calls for one answer: use it less. Log it with `mmo-score council-note --task ID --agreed|--split`.
