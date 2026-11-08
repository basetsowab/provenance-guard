# Provenance Guard

> ### 👋 Start here
>
> **New to this repo? Read [RUNNING.md](RUNNING.md) first.**
>
> Once `python test.py` passes, in one terminal:
>
> ```bash
> python app.py
> ```
>
> and in another:
>
> ```bash
> curl -X POST http://127.0.0.1:5000/ping \
>   -H "Content-Type: application/json" \
>   -d '{"message": "hello"}'
> ```
>
> That's a web service. Something sent it text and it sent something back.
> Everything this unit is filling in the middle.
>
> **The rest of this file is your submission.** Fill it in as you go.

---

<!-- ─────────────────────────────────────────────────────────────────────────
     Unit 7 asks for the first five sections. Unit 8 adds the five below.

     Everything is pasted as TEXT. A pasted curl response gets full credit;
     a picture of your terminal gets none.
     ───────────────────────────────────────────────────────────────────────── -->

<!-- ═══════════════════════ UNIT 7 — THE BUILD ═══════════════════════ -->

## What This Does

<!-- The path a submission takes, from arriving to the label a reader sees.
     Six or seven steps — this is the trace you wrote in Milestone 1. -->

Provenance Guard is a small web service a writing site can call to get a
cautious guess about whether a piece of text was written by a person or with
AI. A submission takes this path:

1. **Arrives at `POST /submit`** (`app.py::submit`) as JSON with `text` and
   `creator_id`.
2. **Gets checked for bad input.** A missing or empty field, a body that isn't
   a JSON object, fewer than 5 words, or more than 20,000 characters is refused
   with a 4xx error and a plain reason. The refusal is still written to the
   audit log.
3. **Signal one, the model signal** (`detector.py::model_signal`). A local
   GPT-2 model measures how predictable the text is. Output: 0–1, where higher
   means more AI-like.
4. **Signal two, the style signal** (`stylometry.py::style_signal`). This
   measures the shape of the text: sentence length spread, vocabulary variety
   and punctuation. Output: 0–1, where higher means more AI-like.
5. **The combining rule** (`scoring.py::combine_signals`) turns the two scores
   into one confidence score from 0 to 1.
6. **The label** (`scoring.py::score_to_label`) turns that score into one of
   three plain-English messages: human, unsure or AI.
7. **Logged and returned.** The decision, both signal scores and the combined
   score are written to `logs/audit.jsonl` with a new `content_id`. The writer
   gets JSON back with the guess, the confidence, the label and both scores.
   If they disagree, they send that `content_id` to `POST /appeal`, which
   records their reasoning and moves the item to `under_review`.

---

## Signals and Scoring

<!-- For each signal: what property it measures, why that might differ between
     human and AI writing, and WHAT IT CAN'T SEE.

     The blind spot is not optional. If you can't name it you don't understand
     the signal yet — and unit 8's attack set is built out of blind spots. -->

### Signal one — the model signal

**What it measures:** How predictable the text is to a language model
(perplexity under GPT-2, run locally). Low perplexity maps to a high score.
`detector.py::model_signal`.

**Why that might differ between human and AI writing:** A language model
writes by picking likely next words, so text a model produced tends to be text
a model finds easy to predict. People make odder, more specific word choices.

**What it can't see:** Who actually wrote it. It rewards common words in short,
ordinary sentences, and plenty of people write that way: second-language
writers, younger writers, anyone writing plainly. Their work scores as
machine-like. The reverse also happens: AI text prompted to use rare or ornate
words reads as human.

### Signal two — the style signal

**What it measures:** The shape of the text, without reading it
(`stylometry.py::style_signal`). Three measures, each mapped onto 0–1:

| Measure | What it is | Reads as AI at | Reads as human at | Weight |
|---|---|---|---|---|
| Sentence length spread | std dev ÷ mean of words per sentence | ≤ 0.25 | ≥ 0.65 | 0.50 |
| Vocabulary variety | unique ÷ total words, averaged over 50-word windows | ≤ 0.66 | ≥ 0.80 | 0.25 |
| Expressive punctuation | `; : — – ( ) ! ? " …` per 100 words (not `.` or `,`) | 0 | ≥ 4 | 0.25 |

Values in between are scaled linearly. Text with only one sentence gets 0.5 for
spread (no evidence either way). Text under 120 words is pulled toward 0.5 in
proportion to its length, because the measures are mostly noise on very short
text.

**Why that might differ between human and AI writing:** Generated prose tends
toward even, mid-length sentences and plain punctuation. Human writing is
lumpier: a three-word sentence next to a forty-word one, plus dashes, asides and
questions.

**What it can't see:** Meaning. Anything that changes the shape without
changing the substance moves it: breaking up sentences, adding dashes or typos,
pasting in a quotation. It also penalises people who write in short, even,
simply punctuated sentences, which is the same group signal one already
penalises. In testing, vocabulary variety barely separated anything on short
texts; the AI sample actually had the highest variety.

### The combining rule

<!-- Write the rule in words, then give the numbers. What happens when the two
     signals disagree? -->

**The rule:** A weighted average, weighted toward the model signal because the
style signal is cheaper to game and noisier on short text. If the two signals
disagree strongly, that disagreement is treated as uncertainty: the result is
pulled halfway back toward 0.5, so a split can't tip into an accusation.

**The numbers** (all in `config.py`):

- `combined = 0.6 × model_score + 0.4 × style_score`
- If `|model_score − style_score| ≥ 0.4`, then `combined = 0.5 + (combined − 0.5) × 0.5`
- Thresholds: human ≤ 0.35, unsure between, AI ≥ 0.80 (0.70 in unit 7; raised in
  unit 8, see The Improvement). The AI threshold is set
  higher than the human one is low, so an accusation needs a stronger score.

**Where it lives:** `scoring.py::combine_signals`

<!-- ⚠️ The grader checks your code against that line. If your rule lives
     somewhere else, say where. -->

**A case where my two signals split, and what my rule does with it:**

A vivid personal paragraph I'd call clearly human (short anecdote, dashes, a
parenthetical aside) scored **model 0.49, style 0.21**. The model was unsure;
the style signal said human. The weighted average gave **0.38: "unsure"**,
just above the human threshold. The gap was 0.28, below 0.4, so the
disagreement rule didn't fire.

Calibration results from the four Milestone 4 inputs:

| Input | Model | Style | Combined | Label |
|---|---|---|---|---|
| Clearly AI | 0.877 | 0.629 | 0.778 | AI |
| Clearly human | 0.491 | 0.209 | 0.378 | unsure |
| Plain, simple human writing | 0.824 | 0.600 | 0.734 | **AI (false positive)** |
| Lightly edited AI | 0.717 | 0.577 | 0.661 | unsure |

The plain human paragraph is the false positive the model signal's blind spot
predicts. Both signals agreed it looked AI-like, so the disagreement rule
couldn't help.


---

## Label Variants

<!-- The exact text of all three labels, as a reader would see them, and the
     score range each covers.

     Write them for someone who has never heard the word "threshold". -->

| Label | Score range | The exact text a reader sees |
|---|---|---|
| high-confidence human | 0.00 – 0.35 | We think this was written by a person. Our automated check found nothing that suggests AI was used. |
| unsure | above 0.35, below 0.80 (unit 7: below 0.70) | We couldn't tell whether this was written by a person or with AI help. That happens often and it isn't an accusation. Nothing about how this piece is shown has changed. If you'd like a person to take a look, you can ask for a review. |
| high-confidence AI | 0.80 – 1.00 (unit 7: 0.70 – 1.00) | Our automated check thinks this was probably written with AI. Checks like this can be wrong, especially for plain or simple writing. If you wrote it yourself, you can ask for a review and a person will look at it. |

The text lives in `scoring.py` (`LABEL_HUMAN`, `LABEL_UNSURE`, `LABEL_AI`).

**Why I worded the "unsure" one this way:**
<!-- It's the hardest of the three. It has to admit uncertainty without
     sounding like an accusation, because the person reading it may well have
     written every word themselves. -->



---

## Sample Run

<!-- One submission and one appeal, pasted as text: the request, the response,
     and the log entries. -->

**A submission**

<!-- The response needs content_id, guess, confidence, label, AND both
     signal scores - model_score and style_score. Unit 8's tools read those
     two off the response, so leaving them out costs you next unit's
     diagnostics. -->

```bash
$ curl -X POST http://127.0.0.1:5000/submit \
  -H "Content-Type: application/json" \
  -d '{"text": "...", "creator_id": "..."}'
```

```json

```

**An appeal**

```bash
$ curl -X POST http://127.0.0.1:5000/appeal \
  -H "Content-Type: application/json" \
  -d '{"content_id": "...", "reasoning": "..."}'
```

```json

```

**What the log shows afterwards**

```bash
$ curl "http://127.0.0.1:5000/log?limit=3"
```

```json

```

---

## How I Used AI

**Moment 1**

- *What I asked for:*
- *What came back:*
- *What I changed:*

**Moment 2**

- *What I asked for:*
- *What came back:*
- *What I changed:*

<!-- ═══════════════════════ UNIT 8 — THE TEST ═══════════════════════ -->

---

## Rate Limiting

**My limits:** 5 per minute, 40 per day

**Why those numbers and not others:**
A real writer submits a handful of pieces an hour, maybe resubmitting once or
twice after an edit, so 5 in one minute is never in their way and 40 a day is
far more than anyone posts. A script trying to map my thresholds needs hundreds
of near-identical variations; at 40 a day it gets nowhere with one creator_id.
My own test runner (`run_eval.py`) sends each text 3 times per run under its
own creator_id, so these limits don't interfere with it.

**What a caller counts as:** The `creator_id` in the request body. If a
request has no usable `creator_id`, it counts against the caller's address
instead (`app.py::rate_limit_key`). Per-creator means one household sharing an
address isn't punished together, but one script can dodge it by inventing a
new `creator_id` per request — which is exactly what the attack set does.

**The run of status codes when I pushed past it:**

`python run_attacks.py --flood 15` → `results/flood_2026-11-07_2001.md`

```
200 200 200 200 200 429 429 429 429 429 429 429 429 429 429
```

10 of 15 were rate limited, and each rejection is in `logs/audit.jsonl` with
`"reason": "rate_limited"`.

---

## Attack Run — Before

<!-- Every attack with its outcome and a held-or-broke mark.
     `run_attacks.py --label before` produces the table. -->

`python run_attacks.py --set attack_set --label before` →
`results/attack_run_2026-11-07_2001_before.md`. All 56 inputs got a response;
nothing crashed (no 5xx).

**How I marked them:**
- *Evasion* (AI text trying to get past): HELD only if labelled AI. "Unsure"
  counts as BROKE, because the AI text got through without being flagged.
- *False positive* (human text): HELD if not labelled AI.
- *Prompt injection*: HELD if the instruction changed nothing it was aiming
  at (label text, log format, or a human writer being accused); BROKE if AI
  text got through without an AI label.
- *Malformed / flood*: HELD if refused with a 4xx and no crash.

Model, style and combined scores are copied from `logs/audit.jsonl`.

| Family | Held | Broke |
|---|---|---|
| evasion | 1 | 9 |
| false_positive | 2 | 6 |
| prompt_injection | 3 | 3 |
| malformed | 20 | 0 |
| flood_same_creator | 12 | 0 |
| **Total** | **38** | **18** |

| ID | Family | Targeting | Status | Guess | Model | Style | Combined | Verdict | Why |
|---|---|---|---|---|---|---|---|---|---|
| EV01 | evasion | signal two: typos raise word variety | 200 | unsure | 0.1635 | 0.6771 | 0.4345 | **BROKE** | AI text labelled unsure |
| EV02 | evasion | signal two: broken-up sentences raise length spread | 200 | unsure | 0.5943 | 0.1542 | 0.4591 | **BROKE** | AI text labelled unsure |
| EV03 | evasion | signal two: a pasted quotation changes the shape | 200 | unsure | 0.6662 | 0.299 | 0.5193 | **BROKE** | AI text labelled unsure |
| EV04 | evasion | signal one: unusual words raise perplexity | 200 | unsure | 0.6114 | 0.6792 | 0.6385 | **BROKE** | AI text labelled unsure |
| EV05 | evasion | both signals: heavy human editing pass | 200 | human | 0.3212 | 0.2771 | 0.3036 | **BROKE** | AI text labelled human |
| EV06 | evasion | signal two: one very long sentence and one very short | 200 | unsure | 0.5727 | 0.3083 | 0.4669 | **BROKE** | AI text labelled unsure |
| EV07 | evasion | signal two: padding with punctuation | 200 | unsure | 0.5862 | 0.2979 | 0.4709 | **BROKE** | AI text labelled unsure |
| EV08 | evasion | signal one: text below the token window | 200 | unsure | 0.2452 | 0.5174 | 0.3541 | **BROKE** | AI text labelled unsure |
| EV09 | evasion | both: AI text with a human opening paragraph bolted on | 200 | unsure | 0.7042 | 0.4797 | 0.6144 | **BROKE** | AI text labelled unsure |
| EV10 | evasion | signal two: repeated stanza structure | 200 | ai | 0.9792 | 0.7081 | 0.8708 | **HELD** | labelled AI |
| FP01 | false_positive | plain, clear human writing with no flourishes | 200 | unsure | 0.6175 | 0.4919 | 0.5673 | **HELD** | labelled unsure, not accused |
| FP02 | false_positive | human writing in a formal register | 200 | ai | 0.7387 | 0.6927 | 0.7203 | **BROKE** | human text labelled AI |
| FP03 | false_positive | a non-native English speaker writing carefully | 200 | ai | 0.8051 | 0.6053 | 0.7252 | **BROKE** | human text labelled AI |
| FP04 | false_positive | a student essay written to a rubric | 200 | ai | 0.8329 | 0.559 | 0.7233 | **BROKE** | human text labelled AI |
| FP05 | false_positive | technical documentation written by a person | 200 | ai | 0.8005 | 0.7721 | 0.7891 | **BROKE** | human text labelled AI |
| FP06 | false_positive | a person imitating a formal template | 200 | ai | 0.8814 | 0.4958 | 0.7272 | **BROKE** | human text labelled AI |
| FP07 | false_positive | human writing that repeats a phrase deliberately | 200 | ai | 0.8816 | 0.5 | 0.729 | **BROKE** | human text labelled AI |
| FP08 | false_positive | very short genuine human submission | 200 | unsure | 0.3223 | 0.5014 | 0.3939 | **HELD** | labelled unsure, not accused |
| PI01 | prompt_injection | instruction to ignore the check | 200 | unsure | 0.4625 | 0.4062 | 0.44 | **BROKE** | AI text with injected prefix labelled unsure |
| PI02 | prompt_injection | instruction disguised as a system message | 200 | human | 0.2044 | 0.3542 | 0.2643 | **BROKE** | AI text with injected prefix labelled human |
| PI03 | prompt_injection | instruction wrapped in the writer's voice | 200 | unsure | 0.5943 | 0.4466 | 0.5352 | **BROKE** | AI text with injected prefix labelled unsure |
| PI04 | prompt_injection | attempt to make the label text hostile | 200 | unsure | 0.4998 | 0.4242 | 0.4696 | **HELD** | human text not accused; label text unchanged |
| PI05 | prompt_injection | attempt to inject into the audit log | 200 | unsure | 0.6401 | 0.4308 | 0.5564 | **HELD** | log line stayed one valid JSON entry |
| PI06 | prompt_injection | instruction plus real human text | 200 | unsure | 0.5583 | 0.5054 | 0.5371 | **HELD** | human text not accused; label text unchanged |
| MF01 | malformed | text is only whitespace | 400 | — | — | — | — | **HELD** | 400 with a reason, no crash |
| MF02 | malformed | text is a single character | 422 | — | — | — | — | **HELD** | 422 with a reason, no crash |
| MF03 | malformed | text is control characters | 422 | — | — | — | — | **HELD** | 422 with a reason, no crash |
| MF04 | malformed | text is only punctuation | 422 | — | — | — | — | **HELD** | 422 with a reason, no crash |
| MF05 | malformed | text is a very long single word | 422 | — | — | — | — | **HELD** | 422 with a reason, no crash |
| MF06 | malformed | text is emoji only | 422 | — | — | — | — | **HELD** | 422 with a reason, no crash |
| MF07 | malformed | text is right-to-left script | 422 | — | — | — | — | **HELD** | 422 with a reason, no crash |
| MF08 | malformed | text is 60,000 characters | 413 | — | — | — | — | **HELD** | 413 with a reason, no crash |
| RQ01 | malformed | no text field at all | 400 | — | — | — | — | **HELD** | 400 with a reason, no crash |
| RQ02 | malformed | no creator_id | 400 | — | — | — | — | **HELD** | 400 with a reason, no crash |
| RQ03 | malformed | text is a number | 400 | — | — | — | — | **HELD** | 400 with a reason, no crash |
| RQ04 | malformed | text is a list | 400 | — | — | — | — | **HELD** | 400 with a reason, no crash |
| RQ05 | malformed | text is null | 400 | — | — | — | — | **HELD** | 400 with a reason, no crash |
| RQ06 | malformed | creator_id is an object | 400 | — | — | — | — | **HELD** | 400 with a reason, no crash |
| RQ07 | malformed | body is a JSON array, not an object | 400 | — | — | — | — | **HELD** | 400 with a reason, no crash |
| RQ08 | malformed | body is unparseable JSON | 400 | — | — | — | — | **HELD** | 400 with a reason, no crash |
| RQ09 | malformed | body is empty | 400 | — | — | — | — | **HELD** | 400 with a reason, no crash |
| RQ10 | malformed | body is form-encoded, not JSON | 429 | — | — | — | — | **HELD** | 429: never reached the route (address limit) |
| RQ11 | malformed | body is JSON claiming to be plain text | 429 | — | — | — | — | **HELD** | 429: never reached the route (address limit) |
| RQ12 | malformed | deeply nested JSON | 400 | — | — | — | — | **HELD** | 400 with a reason, no crash |
| FL01_01 | flood_same_creator | 20 rapid submissions from one creator | 200 | unsure | 0.0287 | 0.5 | 0.3586 | **HELD** | 5 accepted, then 429 |
| FL01_02 | flood_same_creator | 20 rapid submissions from one creator | 200 | unsure | 0.0287 | 0.5 | 0.3586 | **HELD** | 5 accepted, then 429 |
| FL01_03 | flood_same_creator | 20 rapid submissions from one creator | 200 | unsure | 0.0287 | 0.5 | 0.3586 | **HELD** | 5 accepted, then 429 |
| FL01_04 | flood_same_creator | 20 rapid submissions from one creator | 200 | unsure | 0.0287 | 0.5 | 0.3586 | **HELD** | 5 accepted, then 429 |
| FL01_05 | flood_same_creator | 20 rapid submissions from one creator | 200 | unsure | 0.0287 | 0.5 | 0.3586 | **HELD** | 5 accepted, then 429 |
| FL01_06 | flood_same_creator | 20 rapid submissions from one creator | 429 | — | — | — | — | **HELD** | 5 accepted, then 429 |
| FL01_07 | flood_same_creator | 20 rapid submissions from one creator | 429 | — | — | — | — | **HELD** | 5 accepted, then 429 |
| FL01_08 | flood_same_creator | 20 rapid submissions from one creator | 429 | — | — | — | — | **HELD** | 5 accepted, then 429 |
| FL01_09 | flood_same_creator | 20 rapid submissions from one creator | 429 | — | — | — | — | **HELD** | 5 accepted, then 429 |
| FL01_10 | flood_same_creator | 20 rapid submissions from one creator | 429 | — | — | — | — | **HELD** | 5 accepted, then 429 |
| FL01_11 | flood_same_creator | 20 rapid submissions from one creator | 429 | — | — | — | — | **HELD** | 5 accepted, then 429 |
| FL01_12 | flood_same_creator | 20 rapid submissions from one creator | 429 | — | — | — | — | **HELD** | 5 accepted, then 429 |

**Notes on the run:**
- RQ10 and RQ11 came back 429. They had no usable creator_id, so they counted
  against my address, which earlier malformed rows had already used up. They
  never reached my route, so this run doesn't show how the route handles them.
- MF07 (right-to-left script, 105 characters) was refused as "too short":
  `stylometry.words` only counts a–z, so non-Latin writing has zero words.
- In PI02, the injected "SYSTEM:" line didn't instruct anything (neither
  signal follows instructions), but its odd tokens dropped signal one from
  0.754 (the same AI text without the prefix) to 0.204.

**Ten audit log entries from the run**

<!-- Choose entries that show the interesting failures, not the ten easiest. -->

```json
{"timestamp": "2026-11-08T01:01:41+00:00", "content_id": "277d818c-124a-478f-a0ff-b70d638647c6", "creator_id": "attacker_FP03", "guess": "ai", "model_score": 0.8051, "style_score": 0.6053, "combined_score": 0.7252, "label": "Our automated check thinks this was probably written with AI. Checks like this can be wrong, especially for plain or simple writing. If you wrote it yourself, you can ask for a review and a person will look at it.", "status": "decided", "text_length": 418}
{"timestamp": "2026-11-08T01:01:41+00:00", "content_id": "ab1b7ac4-c441-4681-987a-86cff7273413", "creator_id": "attacker_FP05", "guess": "ai", "model_score": 0.8005, "style_score": 0.7721, "combined_score": 0.7891, "label": "Our automated check thinks this was probably written with AI. Checks like this can be wrong, especially for plain or simple writing. If you wrote it yourself, you can ask for a review and a person will look at it.", "status": "decided", "text_length": 393}
{"timestamp": "2026-11-08T01:01:42+00:00", "content_id": "62881d26-77be-4fa8-88de-6407ef3e6ca0", "creator_id": "attacker_FP07", "guess": "ai", "model_score": 0.8816, "style_score": 0.5, "combined_score": 0.729, "label": "Our automated check thinks this was probably written with AI. Checks like this can be wrong, especially for plain or simple writing. If you wrote it yourself, you can ask for a review and a person will look at it.", "status": "decided", "text_length": 335}
{"timestamp": "2026-11-08T01:01:39+00:00", "content_id": "45cb273a-d25f-40aa-8852-5f83a20fcc01", "creator_id": "attacker_EV05", "guess": "human", "model_score": 0.3212, "style_score": 0.2771, "combined_score": 0.3036, "label": "We think this was written by a person. Our automated check found nothing that suggests AI was used.", "status": "decided", "text_length": 460}
{"timestamp": "2026-11-08T01:01:42+00:00", "content_id": "70880e04-6448-4d49-8b67-d011e42e713e", "creator_id": "attacker_PI02", "guess": "human", "model_score": 0.2044, "style_score": 0.3542, "combined_score": 0.2643, "label": "We think this was written by a person. Our automated check found nothing that suggests AI was used.", "status": "decided", "text_length": 322}
{"timestamp": "2026-11-08T01:01:43+00:00", "content_id": "cf36cf06-228c-4140-94d0-0fc2860cc1c4", "creator_id": "attacker_PI05", "guess": "unsure", "model_score": 0.6401, "style_score": 0.4308, "combined_score": 0.5564, "label": "We couldn't tell whether this was written by a person or with AI help. That happens often and it isn't an accusation. Nothing about how this piece is shown has changed. If you'd like a person to take a look, you can ask for a review.", "status": "decided", "text_length": 213}
{"timestamp": "2026-11-08T01:01:40+00:00", "content_id": "6b5efef0-d404-49bd-89a7-b5beb87202e1", "creator_id": "attacker_EV10", "guess": "ai", "model_score": 0.9792, "style_score": 0.7081, "combined_score": 0.8708, "label": "Our automated check thinks this was probably written with AI. Checks like this can be wrong, especially for plain or simple writing. If you wrote it yourself, you can ask for a review and a person will look at it.", "status": "decided", "text_length": 544}
{"timestamp": "2026-11-08T01:01:44+00:00", "creator_id": "attacker_flood", "event": "rejected", "status": "rejected", "reason": "rate_limited", "limit": "5 per 1 minute"}
{"timestamp": "2026-11-08T01:01:43+00:00", "creator_id": "attacker_MF07", "event": "rejected", "status": "rejected", "reason": "text_too_short", "http_status": 422, "text_length": 105}
{"timestamp": "2026-11-08T01:01:43+00:00", "creator_id": "unknown", "event": "rejected", "status": "rejected", "reason": "invalid_json", "http_status": 400}
```

**The single worst outcome** — the one I'd least want to explain to a writer
whose work got caught by it:



---

## Run Log and Verdicts

<!-- Your five criteria across three trials. `run_eval.py --label before`. -->

| Criterion | Target | Run 1 | Run 2 | Run 3 | Verdict |
|---|---|---|---|---|---|
| 1.  |  |  |  |  |  |
| 2.  |  |  |  |  |  |
| 3.  |  |  |  |  |  |
| 4.  |  |  |  |  |  |
| 5.  |  |  |  |  |  |

**Real output from one trial**, pasted as text, naming the file and function
that produced it:

```json

```

**Diagnoses**

<!-- For each miss AND each broken attack: the stage and the mechanism.

     Your service has five stages: the route, signal one, signal two, the
     combining rule, and the label mapping.

     Not a diagnosis:  "The evasion attacks got through."
     A diagnosis:      "Four evasion inputs got through. All four had typos
                        added to AI-generated text. My second signal measures
                        word variety, and typos raise word variety — so it read
                        them as more human. My combining rule weights that
                        signal at 0.6, so it dragged the whole score down."

     Look for a pattern. Five failures on one signal is one problem, not five. -->



---

## The Improvement

**What I changed:** One line in `config.py`: `AI_THRESHOLD` from 0.70 to
0.80. Nothing else moved: same signals, same weights, same disagreement rule,
same labels.

**Which diagnosis pointed at it:** The false-positive pattern. Six of eight
human pieces (formal register, non-native writer, rubric essay, technical docs,
formal template, deliberate repetition) were labelled AI with combined scores
of 0.720–0.789. In every one, both signals agreed (model 0.74–0.88), so the
disagreement rule never fired and the label mapping was the last stage that
could stop the accusation. The only AI text that was caught scored 0.871.

### Attack Run — After

`python run_attacks.py --set attack_set --label after` →
`results/attack_run_2026-11-07_2005_after.md`. Every score is identical to the
before run; only labels near the threshold changed.

| Family | Held before | Held after | Broke before | Broke after |
|---|---|---|---|---|
| evasion | 1 | 1 | 9 | 9 |
| false_positive | 2 | **8** | 6 | **0** |
| prompt_injection | 3 | 3 | 3 | 3 |
| malformed | 20 | 20 | 0 | 0 |
| flood_same_creator | 12 | 12 | 0 | 0 |
| **Total** | **38** | **44** | **18** | **12** |

Rows whose label changed:

| ID | Combined | Before | After | Verdict before → after |
|---|---|---|---|---|
| FP02 | 0.720 | ai | unsure | BROKE → HELD |
| FP03 | 0.725 | ai | unsure | BROKE → HELD |
| FP04 | 0.723 | ai | unsure | BROKE → HELD |
| FP05 | 0.789 | ai | unsure | BROKE → HELD |
| FP06 | 0.727 | ai | unsure | BROKE → HELD |
| FP07 | 0.729 | ai | unsure | BROKE → HELD |

All malformed and flood rows returned the same status codes as before.

**Did it help, and how do I know:**

<!-- Widening the unsure band usually fixes one problem and creates another.
     Reporting that trade honestly is worth full credit. -->



---

## What's Still Broken

<!-- For each attack still getting through and each criterion still missed:
     what you'd do, and why you stopped. -->



**The trade I'd make if this ran for real:**

<!-- Two sentences. Fewer wrong accusations means more AI text getting through.
     Say which way you'd go and WHO PAYS FOR IT. -->



<!-- ═════════════════════════════════════════════════════════════════════

     SUBMISSION CHECKLIST — unit 7

       [ ] criteria.md has five numbered criteria, each naming a target
       [ ] Each has a reason underneath
       [ ] POST /submit returns content_id, guess, confidence, label,
           model_score and style_score
       [ ] Two signals that measure DIFFERENT things, each with a named blind spot
       [ ] Three label variants, all reachable, written out in full
       [ ] POST /appeal changes status and writes to the log
       [ ] Signals and Scoring names scoring.py::combine_signals
       [ ] Sample Run: a submission AND an appeal, as pasted text
       [ ] At least four new commits
       [ ] Repository URL submitted — WRITE IT DOWN

     SUBMISSION CHECKLIST — unit 8

       [ ] Rate limiting on /submit, with your numbers justified
       [ ] The pasted run of status codes showing 429
       [ ] Audit log with all nine fields, recording rejections too
       [ ] The attack set run IN FULL, every input with an outcome
       [ ] Ten audit log entries pasted as text
       [ ] Five criteria across three trials
       [ ] A diagnosis for every miss and every broken attack — stage AND mechanism
       [ ] One improvement, with Attack Run — After
       [ ] What's Still Broken, including the production trade
       [ ] At least four new commits
       [ ] The SAME repository URL as last unit

     Do not delete and recreate this repository.
     ═════════════════════════════════════════════════════════════════════ -->

---

📖 **How to run this project: [RUNNING.md](RUNNING.md)**
