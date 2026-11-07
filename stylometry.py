"""
Signal two: the style signal. ← YOU BUILD THIS IN MILESTONE 4

Signal one reads the text for meaning. This one measures it *as text* — the
shape of it, without understanding a word.

Three measures are stubbed below because the brief names those three. They are
stubs, not implementations: what they compute is yours, and so is how you
combine them.

    sentence_length_spread   do sentences vary in length, or march in step?
    type_token_ratio         how much of the vocabulary repeats?
    punctuation_density      how much punctuation, and how varied?

Why these might differ between human and AI writing: generated prose tends
toward even, mid-length sentences and a narrower band of vocabulary, because
that's what "most likely next word" produces on average. Human writing is
lumpier — a three-word sentence next to a forty-word one.

⚠️ **The blind spot, which you have to name in Milestone 1.**

This signal cannot read. It has no idea what the text says. Anything that
changes the shape without changing the substance moves it — adding typos,
breaking up sentences, pasting in a quotation. That is a very cheap thing for
someone to do on purpose, and unit 8's attack set will do it to you.

Build each function on its own and call it from a terminal before you wire
anything together:

    python stylometry.py "some text to look at"
"""

import re
import statistics


def sentences(text: str) -> list[str]:
    """Split into sentences. Rough and good enough — given to you."""
    parts = re.split(r"(?<=[.!?])\s+", text.strip())
    return [p for p in parts if p.strip()]


def words(text: str) -> list[str]:
    """Split into lowercase words, punctuation stripped. Given to you."""
    return re.findall(r"[a-z0-9']+", text.lower())


# ── The three measures ───────────────────────────────────────────────────────

def sentence_length_spread(text: str) -> float:
    """
    How much sentence length varies: the coefficient of variation (standard
    deviation of words-per-sentence divided by the mean).

    Scale: 0.0 and up. 0.0 means every sentence is the same length. Typical
    prose lands roughly between 0.2 and 0.9.
    Direction: HIGHER means more human (lumpier sentences).

    Edge case: with fewer than two sentences there is no spread to measure, so
    this returns 0.0. `style_signal` treats that case as "no evidence" rather
    than as "very even", so a one-sentence poem isn't pushed toward AI.
    """
    lengths = [len(words(s)) for s in sentences(text)]
    lengths = [n for n in lengths if n > 0]
    if len(lengths) < 2:
        return 0.0
    mean = statistics.mean(lengths)
    if mean == 0:
        return 0.0
    return round(statistics.stdev(lengths) / mean, 4)


def type_token_ratio(text: str, window: int = 50) -> float:
    """
    Unique words over total words, averaged over a sliding window
    (moving-average type-token ratio).

    Scale: 0.0 to 1.0. Direction: HIGHER means more varied vocabulary.

    A plain type-token ratio falls as text gets longer, because common words
    repeat. Averaging it over fixed 50-word windows makes a 60-word piece and a
    600-word piece comparable. Texts shorter than one window fall back to the
    plain ratio.
    """
    tokens = words(text)
    if not tokens:
        return 0.0
    if len(tokens) <= window:
        return round(len(set(tokens)) / len(tokens), 4)
    ratios = [
        len(set(tokens[i:i + window])) / window
        for i in range(len(tokens) - window + 1)
    ]
    return round(statistics.mean(ratios), 4)


# Punctuation beyond the plain full stop and comma. These vary far more
# between writers than full stops do. Apostrophes are left out so
# contractions like "don't" don't count as punctuation.
_EXPRESSIVE_PUNCTUATION = re.compile(r"[;:!?()\[\]\"“”—–…]|--|\.\.\.")


def punctuation_density(text: str) -> float:
    """
    Expressive punctuation marks per 100 words: semicolons, colons, dashes,
    brackets, quotation marks, exclamation and question marks, ellipses.
    Full stops and commas are left out on purpose, because almost everyone
    uses them at similar rates.

    Scale: 0.0 and up (marks per 100 words). Direction: HIGHER means more
    human-ish in this design.
    """
    n_words = len(words(text))
    if n_words == 0:
        return 0.0
    marks = len(_EXPRESSIVE_PUNCTUATION.findall(text))
    return round(100.0 * marks / n_words, 4)


# ── Combining them ───────────────────────────────────────────────────────────

# Where each raw measure maps onto 0 (human-ish) … 1 (AI-ish).
# value at or past HUMAN end -> 0.0, value at or past AI end -> 1.0, linear between.
SPREAD_AI_END, SPREAD_HUMAN_END = 0.25, 0.65        # coefficient of variation
TTR_AI_END, TTR_HUMAN_END = 0.66, 0.80              # moving-average TTR
PUNCT_AI_END, PUNCT_HUMAN_END = 0.0, 4.0            # marks per 100 words

# How much each measure counts inside the style signal.
STYLE_WEIGHTS = {"spread": 0.5, "ttr": 0.25, "punctuation": 0.25}

# Below this many words the measures are mostly noise, so the signal is pulled
# toward 0.5 ("no opinion") in proportion to how short the text is.
FULL_EVIDENCE_WORDS = 120


def _to_ai_scale(value: float, ai_end: float, human_end: float) -> float:
    """Map a raw measure onto 0–1 where 1 means AI-ish. Works either direction."""
    if human_end == ai_end:
        return 0.5
    position = (value - ai_end) / (human_end - ai_end)  # 0 at AI end, 1 at human end
    return min(max(1.0 - position, 0.0), 1.0)


def style_parts(text: str) -> dict:
    """Each measure, raw and on the 0–1 AI scale. Handy for debugging."""
    n_sentences = len(sentences(text))
    spread = sentence_length_spread(text)
    ttr = type_token_ratio(text)
    punct = punctuation_density(text)

    spread_ai = (
        _to_ai_scale(spread, SPREAD_AI_END, SPREAD_HUMAN_END)
        if n_sentences >= 2 else 0.5   # one sentence: no evidence either way
    )
    return {
        "spread": spread,
        "ttr": ttr,
        "punctuation": punct,
        "spread_ai": round(spread_ai, 4),
        "ttr_ai": round(_to_ai_scale(ttr, TTR_AI_END, TTR_HUMAN_END), 4),
        "punctuation_ai": round(_to_ai_scale(punct, PUNCT_AI_END, PUNCT_HUMAN_END), 4),
    }


def style_signal(text: str) -> float:
    """
    The style signal as a 0–1 score. **Higher means more likely AI.**

    1. Each measure is mapped onto 0–1 with 1 = AI-ish. All three raw measures
       point "higher = more human", so all three are flipped by the mapping.
       The cut-off points are the *_AI_END / *_HUMAN_END constants above.
    2. Weighted average: spread 0.50, vocabulary 0.25, punctuation 0.25.
       Spread gets the most weight because it is the measure most directly
       tied to how generated text is produced.
    3. Short texts are shrunk toward 0.5. A 30-word piece gets a quarter of
       the pull away from the middle that a 120-word piece gets.
    """
    if not words(text):
        return 0.5

    parts = style_parts(text)
    raw = (
        STYLE_WEIGHTS["spread"] * parts["spread_ai"]
        + STYLE_WEIGHTS["ttr"] * parts["ttr_ai"]
        + STYLE_WEIGHTS["punctuation"] * parts["punctuation_ai"]
    )

    evidence = min(len(words(text)) / FULL_EVIDENCE_WORDS, 1.0)
    score = 0.5 + (raw - 0.5) * evidence
    return round(min(max(score, 0.0), 1.0), 4)


if __name__ == "__main__":
    import sys

    text = " ".join(sys.argv[1:]) or (
        "The system works well. It handles most cases correctly and provides "
        "good results. Users generally find it easy to use and understand."
    )

    parts = style_parts(text)
    print(f"{len(sentences(text))} sentences, {len(words(text))} words\n")
    print(f"sentence_length_spread   {parts['spread']:<8}  -> AI-scale {parts['spread_ai']}")
    print(f"type_token_ratio         {parts['ttr']:<8}  -> AI-scale {parts['ttr_ai']}")
    print(f"punctuation_density      {parts['punctuation']:<8}  -> AI-scale {parts['punctuation_ai']}")
    print(f"style_signal             {style_signal(text)}   (higher = more likely AI)")
