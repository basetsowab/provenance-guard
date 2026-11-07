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
- Thresholds: human ≤ 0.35, unsure between, AI ≥ 0.70. The AI threshold is set
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
| unsure | above 0.35, below 0.70 | We couldn't tell whether this was written by a person or with AI help. That happens often and it isn't an accusation. Nothing about how this piece is shown has changed. If you'd like a person to take a look, you can ask for a review. |
| high-confidence AI | 0.70 – 1.00 | Our automated check thinks this was probably written with AI. Checks like this can be wrong, especially for plain or simple writing. If you wrote it yourself, you can ask for a review and a person will look at it. |

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

**My limits:** ___ per minute, ___ per day

**Why those numbers and not others:**
<!-- Think about two people: a real writer submitting their own work a few
     times an hour, and a script sending a thousand variations to map your
     thresholds. Your numbers have to be liveable for the first and hostile to
     the second. -->

**What a caller counts as:** <!-- per address, or per creator_id? They fail
differently — one script can look like a thousand callers, and one household
can look like one. -->

**The run of status codes when I pushed past it:**

<!-- python run_attacks.py --flood 15 -->

```

```

---

## Attack Run — Before

<!-- Every attack with its outcome and a held-or-broke mark.
     `run_attacks.py --label before` produces the table. -->



**Ten audit log entries from the run**

<!-- Choose entries that show the interesting failures, not the ten easiest. -->

```json

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

**What I changed:**

**Which diagnosis pointed at it:**

### Attack Run — After

<!-- Same format. `run_attacks.py --label after` -->



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
