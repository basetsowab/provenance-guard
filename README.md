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

**Moment 1: Understanding the project structure**

- *What I asked for:* help understanding how to organize the backend: how
  an API endpoint receives text, validates the request, processes the
  submission and returns a classification.
- *What came back:* an explanation of how the parts (submission,
  classification, API responses, storing results) could communicate, which
  let me break the project into smaller tasks.
- *What I changed:* I still had to review the suggested code and understand
  how the components worked together, rather than relying on it as is.

**Moment 2: Debugging and testing scenarios**

- *What I asked for:* help thinking through potential bugs and testing
  scenarios.
- *What came back:* examples of invalid requests, API errors and cases where
  classification might be wrong: an empty paragraph, badly formatted JSON, an
  appeal against a classification that doesn't exist.
- *What I changed:* I used them to think more carefully about input
  validation and error handling, and to understand why those errors happen.

**Moment 3 (unit 8): Claude Code for the eval run**

- *What I asked for:* to check what was still missing from the assignment,
  then to do the whole assignment.
- *What came back:* a list of gaps (blank `criteria.md`, placeholder
  `scenarios.py`, empty run log and How I Used AI). It declined to write my
  criteria or invent "my own writing", and gave me a fill-in-the-blank
  template instead. I wrote my five criteria from that template. Claude then
  formatted them into `criteria.md`, built the eval scenarios (AI texts it
  wrote, pre-1900 public-domain human texts, 10 bad requests, 5 appeals),
  added appeal testing to `run_eval.py`, ran both evals, and drafted the run
  log, verdicts and diagnoses.
- *What I changed:* *(to fill in: what I checked or rewrote in the drafted
  diagnoses and verdicts.)*

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

The worst outcome I can imagine for Provenance Guard would be incorrectly
identifying someone's original writing as AI-generated and having that
classification used against them. For example, a student could spend several
hours writing an essay independently, only for the system to classify it as
AI-generated. If a professor or institution trusted that result without
further investigation, the student could face academic penalties despite
doing nothing wrong.

This is especially concerning because certain writing styles may be more
likely to trigger incorrect classifications. I believe false accusations can
be more harmful than failing to detect some AI-generated content, so I would
not want Provenance Guard to be treated as definitive proof that someone used
AI. The appeals process is important because it gives users a way to
challenge incorrect results.



---

## Run Log and Verdicts

Targets are from `criteria.md`. Produced by `run_eval.py::main` (appeals by
`run_eval.py::run_appeals`) against `app.py::submit` and `app.py::appeal`.
Scenarios are in `scenarios.py`.

- **Before** = the system as it was before my one improvement
  (`AI_THRESHOLD = 0.70`), re-created by setting that one line back for the
  run: `results/run_2026-11-14_2339_before.md`.
- **After** = the current system (`AI_THRESHOLD = 0.80`):
  `results/run_2026-11-14_2340_after.md`.

The threshold change can only move labels, so the before run is a faithful
replay: every score in both runs is identical, and identical across all
three trials, as expected from two deterministic signals.

### Before (AI_THRESHOLD 0.70)

| Criterion | Target | Run 1 | Run 2 | Run 3 | Verdict |
|---|---|---|---|---|---|
| 1. My own writing labelled AI | ≤ 2 of 10, every trial | not run | not run | not run | **MISSED (not tested)** |
| 2. Invalid requests get a 4xx, no crash | 10 of 10 | 10/10 | 10/10 | 10/10 | **MET** |
| 3. Appeals reach `under_review` and are logged | 5 of 5 | 5/5 | 5/5 | 5/5 | **MET** |
| 4. All three labels reachable | 3 of 3 | 2/3 (ai, unsure) | 2/3 | 2/3 | **MISSED** |
| 5. Valid requests succeed | ≥ 95% | 13/13 (100%) | 13/13 | 13/13 | **MET** |

### After (AI_THRESHOLD 0.80)

| Criterion | Target | Run 1 | Run 2 | Run 3 | Verdict |
|---|---|---|---|---|---|
| 1. My own writing labelled AI | ≤ 2 of 10, every trial | not run | not run | not run | **MISSED (not tested)** |
| 2. Invalid requests get a 4xx, no crash | 10 of 10 | 10/10 | 10/10 | 10/10 | **MET** |
| 3. Appeals reach `under_review` and are logged | 5 of 5 | 5/5 | 5/5 | 5/5 | **MET** |
| 4. All three labels reachable | 3 of 3 | 2/3 (ai, unsure) | 2/3 | 2/3 | **MISSED** |
| 5. Valid requests succeed | ≥ 95% | 13/13 (100%) | 13/13 | 13/13 | **MET** |

**How each verdict was decided**

1. **Not tested, so not met.** The criterion needs 10 pieces of my own
   writing and I did not supply any, so `scenarios.py` has that scenario
   commented out. I am not counting a test that never ran as a pass. The
   nearest evidence is the attack set's human pieces: before the fix, 6 of 8
   were labelled AI (FP02–FP07), which would have missed a ≤ 2 target.
2. **Met, with one caveat.** All 10 came back 400, 413 or 422 in trials 1 and
   2, and no request crashed the service in any trial. In trial 3 the last
   request (no `creator_id`) came back **429**, not 400. Requests without a
   usable `creator_id` count against my address, and two such requests per
   trial (this one and the `creator_id`-is-an-object one) means the sixth
   lands in trial 3 and is over the 5-a-minute limit. 429 is a 4xx and nothing
   crashed, so the target as written holds. But that request never reached my
   route, so trial 3 doesn't show the route handling a missing `creator_id`.
   Trials 1 and 2 do (400).
3. **Met.** All 15 appeals across three trials: submit 200, appeal 200, the
   appeal response says `under_review`, `GET /log` holds an `"event": "appeal"`
   entry for that `content_id`, and its latest status is `under_review`.
4. **Missed.** `ai` and `unsure` came back. `human` never did, in any trial,
   for any input: the AI texts, five pieces of pre-1900 human writing, or the
   appeal texts. A generous reading would say the label is "reachable"
   because the attack run produced it twice (EV05 at 0.304, PI02 at 0.264).
   But both of those were **AI text**. My criterion says the labels should
   come up "under the appropriate conditions", and the only text that ever
   reached `human` was AI text. That is a miss.
5. **Met.** "Valid requests" = every well-formed submission in the run: 3 AI
   texts, 5 human texts and 5 appeal submissions, 13 per trial. All 13 came
   back 200 in every trial, so 39/39.

**Real output, one trial each** (`results/run_2026-11-14_2340_after.md`,
trial 1, produced by `run_eval.py::main` / `run_eval.py::run_appeals`):

Criterion 2, a missing `text` field and a one-character text:

```json
{"status": 400, "guess": null, "confidence": null, "model_score": null, "style_score": null, "label": null, "sent": "{\"creator_id\": \"eval_bad_missing\"}"}
{"status": 422, "guess": null, "confidence": null, "model_score": null, "style_score": null, "label": null, "sent": "a"}
```

Criterion 3, one appeal end to end:

```json
{
  "sent": "In today's fast-paced digital landscape, effective communication has b",
  "submit_status": 200,
  "content_id": "6ca6c979-2dd0-4630-ad21-91957c192aef",
  "guess": "unsure",
  "appeal_status": 200,
  "appeal_response_status": "under_review",
  "log_entries": 2,
  "appeal_logged": true,
  "log_status": "under_review"
}
```

Criteria 4 and 5: the only AI label after the fix, and the lowest-model-score
human text (Whitman), which still landed in `unsure`:

```json
{"status": 200, "guess": "ai", "confidence": 0.8198, "model_score": 0.9469, "style_score": 0.6292, "label": "Our automated check thinks this was probably written with AI. Checks like this can be wrong, especially for plain or simple writing. If you wrote it yourself, you can ask for a review and a person will look at it.", "sent": "Climate change is one of the most pressing challenges facing humanity "}
{"status": 200, "guess": "unsure", "confidence": 0.4373, "model_score": 0.1704, "style_score": 0.6809, "label": "We couldn't tell whether this was written by a person or with AI help. That happens often and it isn't an accusation. Nothing about how this piece is shown has changed. If you'd like a person to take a look, you can ask for a review.", "sent": "I celebrate myself, and sing myself, And what I assume you shall assum"}
```

Every score, both runs (identical in all three trials):

| Input | Model | Style | Combined | Before | After |
|---|---|---|---|---|---|
| AI 1 (communication) | 0.845 | 0.621 | 0.755 | ai | unsure |
| AI 2 (climate) | 0.947 | 0.629 | 0.820 | ai | ai |
| AI 3 (exercise) | 0.946 | 0.573 | 0.797 | ai | unsure |
| Twain, *Huck Finn* ch. 8 | 0.637 | 0.368 | 0.530 | unsure | unsure |
| Twain, *Huck Finn* ch. 1 | 0.461 | 0.374 | 0.426 | unsure | unsure |
| Thoreau, *Walden* | 0.623 | 0.653 | 0.635 | unsure | unsure |
| Douglass, *Narrative* | 0.520 | 0.471 | 0.501 | unsure | unsure |
| Whitman, *Song of Myself* | 0.170 | 0.681 | 0.437 | unsure | unsure |

**Diagnoses**

*Criterion 1 (not tested).* There is no pipeline failure to diagnose. The
gap is in the test: the scenario that needs my own writing was never filled.

*Criterion 4: the `human` label is unreachable for real human writing.*
Stage: **the label mapping**, with signals one and two keeping scores up and
**the combining rule** making it worse. To get `human`, the combined score has
to be under 0.35, which with weights 0.6/0.4 means both signals have to be low
at once. That never happens for real human text:

- **Signal two can't go low on short text.** Every eval text is 55–76 words.
  `stylometry.style_signal` pulls anything under 120 words toward 0.5 in
  proportion to its length, so a 70-word piece gets only about 60% of the
  pull away from the middle. The lowest style score any human text got was
  0.368.
- **Signal one rates famous human prose as predictable.** Thoreau, Douglass
  and Twain score 0.46–0.64. These passages are very likely in the
  detector model's training data, so their perplexity is low. Probing before
  the run, I found the opening of *A Tale of Two Cities* scored 0.949 model /
  0.818 combined, which is a confident AI label on Dickens.
- **The disagreement rule pulls the one low score back up.** Whitman got the
  lowest model score (0.170), but style read the long comma-joined verse
  line as AI-like (0.681). The 0.51 gap is over `DISAGREEMENT_GAP` (0.4), so
  `scoring.combine_signals` shrank the raw 0.374 halfway toward 0.5,
  giving 0.437.

Mechanism in one line: `HUMAN_THRESHOLD = 0.35` sits below where human writing
actually lands (0.43–0.64 here, 0.39–0.79 in the attack set), so only text
with unusual tokens that break signal one, which in this project means AI
text, ever gets under it.

*Broken attacks (Attack Run — Before).* The six false positives are diagnosed
under The Improvement. The other twelve:

| ID | Model | Style | Combined | Stage | Mechanism |
|---|---|---|---|---|---|
| EV01 typos | 0.164 | 0.677 | 0.435 | signal one, then combining rule | The attack aimed at signal two, but typos are rare tokens, so perplexity jumped and signal one read the text as human. The 0.51 gap triggered the disagreement rule, which pulled it to 0.435. |
| EV02 broken-up sentences | 0.594 | 0.154 | 0.459 | signal two, then combining rule | Chopping sentences raised sentence-length spread, which is half of signal two's weight. Style dropped to 0.15, and the 0.44 gap triggered the shrink toward 0.5. |
| EV03 pasted quotation | 0.666 | 0.299 | 0.519 | signal two | A quotation adds sentences of a different length and extra punctuation, so spread and punctuation density both read human. |
| EV04 unusual words | 0.611 | 0.679 | 0.639 | signal one | Rare vocabulary raises perplexity. Signal one fell to 0.61, so the score stayed below even the old 0.70 line with style still AI-like. |
| EV05 heavy human edit | 0.321 | 0.277 | 0.304 | both signals | After a real editing pass, both signals measure human-like text, because by both measures it is. No single stage is wrong. Neither signal can see where the text came from, only what it looks like now. |
| EV06 one long + one short sentence | 0.573 | 0.308 | 0.467 | signal two | Two extreme sentence lengths are enough to send the coefficient of variation into the human range. |
| EV07 punctuation padding | 0.586 | 0.298 | 0.471 | signal two | Punctuation density maps 4+ marks per 100 words to fully human. Padding hits that directly. |
| EV08 below token window | 0.245 | 0.517 | 0.354 | signal one | Very short text gives the detector little context, so perplexity is high and unreliable. Style is shrunk to near 0.5 by the short-text rule. |
| EV09 human opening bolted on | 0.704 | 0.480 | 0.614 | both signals, whole-document scoring | Both signals average over the whole text, so a human paragraph dilutes the AI part. Nothing scores sections separately. |
| PI01 "ignore the check" | 0.463 | 0.406 | 0.440 | signal one | Neither signal follows instructions. The injected sentence is odd, out-of-place text, which raises perplexity and lowers signal one. |
| PI02 fake system message | 0.204 | 0.354 | 0.264 | signal one | Same mechanism, stronger: the "SYSTEM:" line dropped signal one from 0.754 (same text, no prefix) to 0.204, low enough for a `human` label. |
| PI03 instruction in the writer's voice | 0.594 | 0.447 | 0.535 | signal one | Same mechanism, milder: the prefix reads more naturally, so perplexity rose less. |

**The pattern.** These are three problems, not twelve:

1. **Signal two measures surface shape, which takes seconds to change**
   (EV02, EV03, EV06, EV07). Each attack moved one of its three measures on
   purpose.
2. **Signal one reads anything unusual as human** (EV01, EV04, EV08,
   PI01–PI03). Typos, rare words, short length and injected instructions all
   raise perplexity. The injection attacks didn't work because the model
   obeyed them. They worked because they are strange text.
3. **The AI band is narrow.** Clean AI text scores only 0.75–0.87, so any
   attack that moves either signal by about 0.15 drops it out of the AI band.
   The disagreement rule (EV01, EV02) helps those attacks by pulling split
   scores toward 0.5. The 0.80 threshold makes this worse: two of my three
   clean AI texts no longer reach it.

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

For false positives, yes: 0 of 8 human pieces are labelled AI now, against 6
of 8 before, from the same scores. It did nothing for evasion (still 9 of 10
broke), because those were already below 0.70.

The cost: the AI label is now much harder to reach. In the attack set only
EV10 (0.871) gets it. My unit 7 "clearly AI" calibration paragraph scored
0.778, so it would now be "unsure" instead of flagged. The fix moved the
accused human writers into "unsure" without separating them from AI text:
human pieces still score 0.72–0.79, higher than most AI text in the set.

My own eval run shows the same cost. With the same scores, my three clean
AI texts went from **3 of 3 labelled AI** at 0.70 to **1 of 3** at 0.80 (0.755
and 0.797 are now `unsure`). Criteria 2, 3 and 5 were unaffected, and
criterion 4 stayed missed both ways, because the change moved the AI line,
not the human one.


---

## What's Still Broken

| Still broken | What I'd do | Why I stopped |
|---|---|---|
| Criterion 1 never tested | Collect 10 pieces of my own writing, uncomment the scenario in `scenarios.py`, and run `run_eval.py` again. | I didn't supply the samples in time. Until it runs, I can't say whether my most important criterion holds. |
| Criterion 4: `human` unreachable for human text | Recalibrate `HUMAN_THRESHOLD` against real human writing (it sits under where human text lands), and stop the disagreement rule pulling low-model-score text back toward 0.5. | That would be a second change to the scoring, and the unit allows one, so the before/after stays comparable. |
| Evasion: 9 of 10 still get through | Problem 1: make signal two harder to game, e.g. count punctuation per sentence instead of per word, and ignore single outlier sentences in the spread. Problem 3: score sections separately so a bolted-on human paragraph (EV09) can't dilute the rest. | Each is a signal change. Problem 2 (signal one reads anything odd as human) has no cheap fix: perplexity-based detection is built on exactly the property the attacks exploit. |
| Prompt injection: 3 of 6 still lower the score | Strip lines that look like instructions or system messages ("SYSTEM:", "ignore…") before scoring, and log that they were removed. | It's an input-cleaning change, a second improvement. It also risks removing real writing that happens to contain those words. |
| AI band now very narrow (only 0.80+) | This is the cost of my fix. I'd accept it rather than go back to accusing formal human writers, but pair it with a better signal so AI text scores higher. | Moving the threshold again would undo the one change I measured. |
| Malformed rows RQ10/RQ11 never reached the route | Run them again from a fresh address, or give address-limited requests their own bucket, so the route's handling is actually tested. | It's a test gap, not a service failure. Both got a 4xx and nothing crashed. |

**The trade I'd make if this ran for real:**

If I deployed Provenance Guard in a real environment, I would prioritize
reducing false positives, even if that meant the system failed to identify
some AI-generated content. I believe protecting people from incorrect
accusations is more important than maximizing the number of AI-generated
submissions detected. The people who pay for that choice are the writers
competing against undetected AI text, and the site's readers. Writers who
would otherwise have been wrongly accused don't pay it.

I would also keep the `uncertain` classification and appeals process because
they allow the application to acknowledge its limitations instead of
presenting every prediction as a fact.

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

---

## Capstone

**What This Extends**

Provenance Guard, the AI-text detection service from Project 4 (units 7–8). It already refuses bad *input* cleanly: invalid JSON, a missing or blank `creator_id` or `text`, text that's too long or too short, and rate-limited requests all get a 4xx JSON answer and an audit-log entry. What it didn't handle was the service's *own* parts failing. If `detector.model_signal` raised anything other than `DetectorUnavailable`/`ValueError`, hung, or ran slowly, or if the audit log couldn't be written, `/submit` returned Flask's default HTML 500 page (or just kept the caller waiting) and left no record. What's new is internal-failure handling on `/submit`: a time limit on the detector, a JSON answer plus a record for any unexpected exception, and a refusal to hand out a `content_id` that was never written to the audit log (an id that can't be appealed). Every request also gets a structured request-log record so the failures can be counted afterwards.

**The Shape**

B — Harden against failure. The bad path here is the service's internals breaking (the detector raising, hanging, or the audit log being unwritable) rather than the caller sending bad input, which unit 8 already covered.

Out of scope:
- **The signals, the weights and the thresholds.** `detector.py`'s scoring, `stylometry.py` and `scoring.py` aren't changed. Whether a label is *right* isn't this unit's question.
- **Retries.** The detector is a local model, not a remote API. Retrying a crash or a hang on the same machine with the same input mostly reproduces it, so a failure is reported, not retried.
- **Hosting.** The detector loads gpt2 (~550 MB on disk, more in memory) inside the process, which doesn't fit the course's 512 MB free tier. This runs on Path B, local with logs.
- **`/appeal` and the rate limiter.** Their behaviour stays as unit 8 left it (rate limits still in `memory://`).
