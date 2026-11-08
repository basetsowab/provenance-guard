# Attack run — before

- Produced by: `run_attacks.py::main`
- Service: `app.py::submit`
- 56 attacks · 2026-11-07 20:01
- Auto-marked BROKE (5xx, crash, no response): **0**
- Left for you to judge: **56**

The Verdict column is blank where a script can't honestly decide. Whether
an evasion worked depends on where you put your thresholds — read the
`targets` column, look at what came back, and write HELD or BROKE yourself.

Each attack submits as creator_id `attacker_<id>`, and the content_id it
came back with is in the table — either one will match this run against your
audit log when you go looking for the ten entries to paste.

| ID | Family | Targeting | Status | Content ID | Guess | Score | Verdict |
|---|---|---|---|---|---|---|---|
| EV01 | evasion | signal two: typos raise word variety | 200 | `77d3b309-c31e-4d34-9d89-553a1fffe7f3` | unsure | 0.434 |  |
| EV02 | evasion | signal two: broken-up sentences raise length spread | 200 | `bf63b196-7869-44c5-b5f7-4f83ae5ff991` | unsure | 0.459 |  |
| EV03 | evasion | signal two: a pasted quotation changes the shape | 200 | `754cf6c8-f1fc-4506-97b3-61bc5a214f4a` | unsure | 0.519 |  |
| EV04 | evasion | signal one: unusual words raise perplexity | 200 | `4b82ba91-6982-4e31-9053-c19c65e48a2a` | unsure | 0.638 |  |
| EV05 | evasion | both signals: heavy human editing pass | 200 | `45cb273a-d25f-40aa-8852-5f83a20fcc01` | human | 0.304 |  |
| EV06 | evasion | signal two: one very long sentence and one very short | 200 | `7c6b438e-4a60-4d69-8f25-8c5b3d5691e9` | unsure | 0.467 |  |
| EV07 | evasion | signal two: padding with punctuation | 200 | `8de24bcb-d801-447f-9bb8-f33643652fa5` | unsure | 0.471 |  |
| EV08 | evasion | signal one: text below the token window | 200 | `05056284-76d3-46f6-bdde-96f712fb7dd1` | unsure | 0.354 |  |
| EV09 | evasion | both: AI text with a human opening paragraph bolted on | 200 | `26255fd3-d080-4fe7-9787-a70b2dcf981d` | unsure | 0.614 |  |
| EV10 | evasion | signal two: repeated stanza structure | 200 | `6b5efef0-d404-49bd-89a7-b5beb87202e1` | ai | 0.871 |  |
| FP01 | false_positive | plain, clear human writing with no flourishes | 200 | `bdadbbde-3028-4e09-821b-94db8ab2169f` | unsure | 0.567 |  |
| FP02 | false_positive | human writing in a formal register | 200 | `ed8ada1b-55cb-4062-90fa-1f0f6c5390cd` | ai | 0.720 |  |
| FP03 | false_positive | a non-native English speaker writing carefully | 200 | `277d818c-124a-478f-a0ff-b70d638647c6` | ai | 0.725 |  |
| FP04 | false_positive | a student essay written to a rubric | 200 | `94b18517-b904-4541-bc8e-ce645e306452` | ai | 0.723 |  |
| FP05 | false_positive | technical documentation written by a person | 200 | `ab1b7ac4-c441-4681-987a-86cff7273413` | ai | 0.789 |  |
| FP06 | false_positive | a person imitating a formal template | 200 | `d02c9971-c10e-4507-82f1-b613c9ad4795` | ai | 0.727 |  |
| FP07 | false_positive | human writing that repeats a phrase deliberately | 200 | `62881d26-77be-4fa8-88de-6407ef3e6ca0` | ai | 0.729 |  |
| FP08 | false_positive | very short genuine human submission | 200 | `c666d73e-b5d1-492f-92c8-02befb55cb29` | unsure | 0.394 |  |
| PI01 | prompt_injection | instruction to ignore the check | 200 | `4ad5780e-f3d0-4151-92e5-b1c72fc17360` | unsure | 0.440 |  |
| PI02 | prompt_injection | instruction disguised as a system message | 200 | `70880e04-6448-4d49-8b67-d011e42e713e` | human | 0.264 |  |
| PI03 | prompt_injection | instruction wrapped in the writer's voice | 200 | `5cfc7039-9521-4569-9e4f-7d6d07cbc620` | unsure | 0.535 |  |
| PI04 | prompt_injection | attempt to make the label text hostile | 200 | `9cc4f2dc-a93e-47e9-8cec-c33715389e57` | unsure | 0.470 |  |
| PI05 | prompt_injection | attempt to inject into the audit log | 200 | `cf36cf06-228c-4140-94d0-0fc2860cc1c4` | unsure | 0.556 |  |
| PI06 | prompt_injection | instruction plus real human text | 200 | `7da6e70e-0efa-4dc1-988a-80a7d05080ce` | unsure | 0.537 |  |
| MF01 | malformed | text is only whitespace | 400 | `—` | — | — |  |
| MF02 | malformed | text is a single character | 422 | `—` | — | — |  |
| MF03 | malformed | text is control characters | 422 | `—` | — | — |  |
| MF04 | malformed | text is only punctuation | 422 | `—` | — | — |  |
| MF05 | malformed | text is a very long single word | 422 | `—` | — | — |  |
| MF06 | malformed | text is emoji only | 422 | `—` | — | — |  |
| MF07 | malformed | text is right-to-left script | 422 | `—` | — | — |  |
| MF08 | malformed | text is 60,000 characters | 413 | `—` | — | — |  |
| RQ01 | malformed | no text field at all | 400 | `—` | — | — |  |
| RQ02 | malformed | no creator_id | 400 | `—` | — | — |  |
| RQ03 | malformed | text is a number | 400 | `—` | — | — |  |
| RQ04 | malformed | text is a list | 400 | `—` | — | — |  |
| RQ05 | malformed | text is null | 400 | `—` | — | — |  |
| RQ06 | malformed | creator_id is an object | 400 | `—` | — | — |  |
| RQ07 | malformed | body is a JSON array, not an object | 400 | `—` | — | — |  |
| RQ08 | malformed | body is unparseable JSON | 400 | `—` | — | — |  |
| RQ09 | malformed | body is empty | 400 | `—` | — | — |  |
| RQ10 | malformed | body is form-encoded, not JSON | 429 | `—` | — | — |  |
| RQ11 | malformed | body is JSON claiming to be plain text | 429 | `—` | — | — |  |
| RQ12 | malformed | deeply nested JSON | 400 | `—` | — | — |  |
| FL01_01 | flood_same_creator | 20 rapid submissions from one creator | 200 | `5b702f53-ddc2-4b27-a798-dd1a77db239c` | unsure | 0.359 |  |
| FL01_02 | flood_same_creator | 20 rapid submissions from one creator | 200 | `519002a8-db09-497e-8f8a-0b73f6bc6f9b` | unsure | 0.359 |  |
| FL01_03 | flood_same_creator | 20 rapid submissions from one creator | 200 | `ab288923-bd14-468d-a442-3465bf511907` | unsure | 0.359 |  |
| FL01_04 | flood_same_creator | 20 rapid submissions from one creator | 200 | `e5d6f4a9-261f-4d1a-8a5d-9b724b702f7f` | unsure | 0.359 |  |
| FL01_05 | flood_same_creator | 20 rapid submissions from one creator | 200 | `a95c00f2-6415-4c61-bfec-708257ab0cf7` | unsure | 0.359 |  |
| FL01_06 | flood_same_creator | 20 rapid submissions from one creator | 429 | `—` | — | — |  |
| FL01_07 | flood_same_creator | 20 rapid submissions from one creator | 429 | `—` | — | — |  |
| FL01_08 | flood_same_creator | 20 rapid submissions from one creator | 429 | `—` | — | — |  |
| FL01_09 | flood_same_creator | 20 rapid submissions from one creator | 429 | `—` | — | — |  |
| FL01_10 | flood_same_creator | 20 rapid submissions from one creator | 429 | `—` | — | — |  |
| FL01_11 | flood_same_creator | 20 rapid submissions from one creator | 429 | `—` | — | — |  |
| FL01_12 | flood_same_creator | 20 rapid submissions from one creator | 429 | `—` | — | — |  |

---

## By family

| Family | Attacks | Auto-BROKE | Left to judge |
|---|---|---|---|
| `evasion` | 10 | 0 | 10 |
| `false_positive` | 8 | 0 | 8 |
| `flood_same_creator` | 12 | 0 | 12 |
| `malformed` | 20 | 0 | 20 |
| `prompt_injection` | 6 | 0 | 6 |

> The **false_positive** family is the one to look at hardest. Those are
> written to be genuine human writing that reads as machine-like. Every one
> your service calls AI is a real writer it would have accused.

---

## What came back

The detail behind the table. Paste the interesting failures into your
README — the ones that show something, not the ten easiest.

### EV01 — `evasion`

*Targeting:* signal two: typos raise word variety

```json
{
  "id": "EV01",
  "status": 200,
  "content_id": "77d3b309-c31e-4d34-9d89-553a1fffe7f3",
  "creator_id": "attacker_EV01",
  "guess": "unsure",
  "confidence": 0.4345,
  "model_score": 0.1635,
  "style_score": 0.6771,
  "label": "We couldn't tell whether this was written by a person or with AI help. That happens often and it isn't an accusation. Nothing about how this piece is shown has changed. If you'd like a person to take a look, you can ask for a review.",
  "error": null,
  "verdict": ""
}
```

### EV02 — `evasion`

*Targeting:* signal two: broken-up sentences raise length spread

```json
{
  "id": "EV02",
  "status": 200,
  "content_id": "bf63b196-7869-44c5-b5f7-4f83ae5ff991",
  "creator_id": "attacker_EV02",
  "guess": "unsure",
  "confidence": 0.4591,
  "model_score": 0.5943,
  "style_score": 0.1542,
  "label": "We couldn't tell whether this was written by a person or with AI help. That happens often and it isn't an accusation. Nothing about how this piece is shown has changed. If you'd like a person to take a look, you can ask for a review.",
  "error": null,
  "verdict": ""
}
```

### EV03 — `evasion`

*Targeting:* signal two: a pasted quotation changes the shape

```json
{
  "id": "EV03",
  "status": 200,
  "content_id": "754cf6c8-f1fc-4506-97b3-61bc5a214f4a",
  "creator_id": "attacker_EV03",
  "guess": "unsure",
  "confidence": 0.5193,
  "model_score": 0.6662,
  "style_score": 0.299,
  "label": "We couldn't tell whether this was written by a person or with AI help. That happens often and it isn't an accusation. Nothing about how this piece is shown has changed. If you'd like a person to take a look, you can ask for a review.",
  "error": null,
  "verdict": ""
}
```

### EV04 — `evasion`

*Targeting:* signal one: unusual words raise perplexity

```json
{
  "id": "EV04",
  "status": 200,
  "content_id": "4b82ba91-6982-4e31-9053-c19c65e48a2a",
  "creator_id": "attacker_EV04",
  "guess": "unsure",
  "confidence": 0.6385,
  "model_score": 0.6114,
  "style_score": 0.6792,
  "label": "We couldn't tell whether this was written by a person or with AI help. That happens often and it isn't an accusation. Nothing about how this piece is shown has changed. If you'd like a person to take a look, you can ask for a review.",
  "error": null,
  "verdict": ""
}
```

### EV05 — `evasion`

*Targeting:* both signals: heavy human editing pass

```json
{
  "id": "EV05",
  "status": 200,
  "content_id": "45cb273a-d25f-40aa-8852-5f83a20fcc01",
  "creator_id": "attacker_EV05",
  "guess": "human",
  "confidence": 0.3036,
  "model_score": 0.3212,
  "style_score": 0.2771,
  "label": "We think this was written by a person. Our automated check found nothing that suggests AI was used.",
  "error": null,
  "verdict": ""
}
```

### EV06 — `evasion`

*Targeting:* signal two: one very long sentence and one very short

```json
{
  "id": "EV06",
  "status": 200,
  "content_id": "7c6b438e-4a60-4d69-8f25-8c5b3d5691e9",
  "creator_id": "attacker_EV06",
  "guess": "unsure",
  "confidence": 0.4669,
  "model_score": 0.5727,
  "style_score": 0.3083,
  "label": "We couldn't tell whether this was written by a person or with AI help. That happens often and it isn't an accusation. Nothing about how this piece is shown has changed. If you'd like a person to take a look, you can ask for a review.",
  "error": null,
  "verdict": ""
}
```

### EV07 — `evasion`

*Targeting:* signal two: padding with punctuation

```json
{
  "id": "EV07",
  "status": 200,
  "content_id": "8de24bcb-d801-447f-9bb8-f33643652fa5",
  "creator_id": "attacker_EV07",
  "guess": "unsure",
  "confidence": 0.4709,
  "model_score": 0.5862,
  "style_score": 0.2979,
  "label": "We couldn't tell whether this was written by a person or with AI help. That happens often and it isn't an accusation. Nothing about how this piece is shown has changed. If you'd like a person to take a look, you can ask for a review.",
  "error": null,
  "verdict": ""
}
```

### EV08 — `evasion`

*Targeting:* signal one: text below the token window

```json
{
  "id": "EV08",
  "status": 200,
  "content_id": "05056284-76d3-46f6-bdde-96f712fb7dd1",
  "creator_id": "attacker_EV08",
  "guess": "unsure",
  "confidence": 0.3541,
  "model_score": 0.2452,
  "style_score": 0.5174,
  "label": "We couldn't tell whether this was written by a person or with AI help. That happens often and it isn't an accusation. Nothing about how this piece is shown has changed. If you'd like a person to take a look, you can ask for a review.",
  "error": null,
  "verdict": ""
}
```

### EV09 — `evasion`

*Targeting:* both: AI text with a human opening paragraph bolted on

```json
{
  "id": "EV09",
  "status": 200,
  "content_id": "26255fd3-d080-4fe7-9787-a70b2dcf981d",
  "creator_id": "attacker_EV09",
  "guess": "unsure",
  "confidence": 0.6144,
  "model_score": 0.7042,
  "style_score": 0.4797,
  "label": "We couldn't tell whether this was written by a person or with AI help. That happens often and it isn't an accusation. Nothing about how this piece is shown has changed. If you'd like a person to take a look, you can ask for a review.",
  "error": null,
  "verdict": ""
}
```

### EV10 — `evasion`

*Targeting:* signal two: repeated stanza structure

```json
{
  "id": "EV10",
  "status": 200,
  "content_id": "6b5efef0-d404-49bd-89a7-b5beb87202e1",
  "creator_id": "attacker_EV10",
  "guess": "ai",
  "confidence": 0.8708,
  "model_score": 0.9792,
  "style_score": 0.7081,
  "label": "Our automated check thinks this was probably written with AI. Checks like this can be wrong, especially for plain or simple writing. If you wrote it yourself, you can ask for a review and a person will look at it.",
  "error": null,
  "verdict": ""
}
```

### FP01 — `false_positive`

*Targeting:* plain, clear human writing with no flourishes

```json
{
  "id": "FP01",
  "status": 200,
  "content_id": "bdadbbde-3028-4e09-821b-94db8ab2169f",
  "creator_id": "attacker_FP01",
  "guess": "unsure",
  "confidence": 0.5673,
  "model_score": 0.6175,
  "style_score": 0.4919,
  "label": "We couldn't tell whether this was written by a person or with AI help. That happens often and it isn't an accusation. Nothing about how this piece is shown has changed. If you'd like a person to take a look, you can ask for a review.",
  "error": null,
  "verdict": ""
}
```

### FP02 — `false_positive`

*Targeting:* human writing in a formal register

```json
{
  "id": "FP02",
  "status": 200,
  "content_id": "ed8ada1b-55cb-4062-90fa-1f0f6c5390cd",
  "creator_id": "attacker_FP02",
  "guess": "ai",
  "confidence": 0.7203,
  "model_score": 0.7387,
  "style_score": 0.6927,
  "label": "Our automated check thinks this was probably written with AI. Checks like this can be wrong, especially for plain or simple writing. If you wrote it yourself, you can ask for a review and a person will look at it.",
  "error": null,
  "verdict": ""
}
```

### FP03 — `false_positive`

*Targeting:* a non-native English speaker writing carefully

```json
{
  "id": "FP03",
  "status": 200,
  "content_id": "277d818c-124a-478f-a0ff-b70d638647c6",
  "creator_id": "attacker_FP03",
  "guess": "ai",
  "confidence": 0.7252,
  "model_score": 0.8051,
  "style_score": 0.6053,
  "label": "Our automated check thinks this was probably written with AI. Checks like this can be wrong, especially for plain or simple writing. If you wrote it yourself, you can ask for a review and a person will look at it.",
  "error": null,
  "verdict": ""
}
```

### FP04 — `false_positive`

*Targeting:* a student essay written to a rubric

```json
{
  "id": "FP04",
  "status": 200,
  "content_id": "94b18517-b904-4541-bc8e-ce645e306452",
  "creator_id": "attacker_FP04",
  "guess": "ai",
  "confidence": 0.7233,
  "model_score": 0.8329,
  "style_score": 0.559,
  "label": "Our automated check thinks this was probably written with AI. Checks like this can be wrong, especially for plain or simple writing. If you wrote it yourself, you can ask for a review and a person will look at it.",
  "error": null,
  "verdict": ""
}
```

### FP05 — `false_positive`

*Targeting:* technical documentation written by a person

```json
{
  "id": "FP05",
  "status": 200,
  "content_id": "ab1b7ac4-c441-4681-987a-86cff7273413",
  "creator_id": "attacker_FP05",
  "guess": "ai",
  "confidence": 0.7891,
  "model_score": 0.8005,
  "style_score": 0.7721,
  "label": "Our automated check thinks this was probably written with AI. Checks like this can be wrong, especially for plain or simple writing. If you wrote it yourself, you can ask for a review and a person will look at it.",
  "error": null,
  "verdict": ""
}
```

### FP06 — `false_positive`

*Targeting:* a person imitating a formal template

```json
{
  "id": "FP06",
  "status": 200,
  "content_id": "d02c9971-c10e-4507-82f1-b613c9ad4795",
  "creator_id": "attacker_FP06",
  "guess": "ai",
  "confidence": 0.7272,
  "model_score": 0.8814,
  "style_score": 0.4958,
  "label": "Our automated check thinks this was probably written with AI. Checks like this can be wrong, especially for plain or simple writing. If you wrote it yourself, you can ask for a review and a person will look at it.",
  "error": null,
  "verdict": ""
}
```

### FP07 — `false_positive`

*Targeting:* human writing that repeats a phrase deliberately

```json
{
  "id": "FP07",
  "status": 200,
  "content_id": "62881d26-77be-4fa8-88de-6407ef3e6ca0",
  "creator_id": "attacker_FP07",
  "guess": "ai",
  "confidence": 0.729,
  "model_score": 0.8816,
  "style_score": 0.5,
  "label": "Our automated check thinks this was probably written with AI. Checks like this can be wrong, especially for plain or simple writing. If you wrote it yourself, you can ask for a review and a person will look at it.",
  "error": null,
  "verdict": ""
}
```

### FP08 — `false_positive`

*Targeting:* very short genuine human submission

```json
{
  "id": "FP08",
  "status": 200,
  "content_id": "c666d73e-b5d1-492f-92c8-02befb55cb29",
  "creator_id": "attacker_FP08",
  "guess": "unsure",
  "confidence": 0.3939,
  "model_score": 0.3223,
  "style_score": 0.5014,
  "label": "We couldn't tell whether this was written by a person or with AI help. That happens often and it isn't an accusation. Nothing about how this piece is shown has changed. If you'd like a person to take a look, you can ask for a review.",
  "error": null,
  "verdict": ""
}
```

### PI01 — `prompt_injection`

*Targeting:* instruction to ignore the check

```json
{
  "id": "PI01",
  "status": 200,
  "content_id": "4ad5780e-f3d0-4151-92e5-b1c72fc17360",
  "creator_id": "attacker_PI01",
  "guess": "unsure",
  "confidence": 0.44,
  "model_score": 0.4625,
  "style_score": 0.4062,
  "label": "We couldn't tell whether this was written by a person or with AI help. That happens often and it isn't an accusation. Nothing about how this piece is shown has changed. If you'd like a person to take a look, you can ask for a review.",
  "error": null,
  "verdict": ""
}
```

### PI02 — `prompt_injection`

*Targeting:* instruction disguised as a system message

```json
{
  "id": "PI02",
  "status": 200,
  "content_id": "70880e04-6448-4d49-8b67-d011e42e713e",
  "creator_id": "attacker_PI02",
  "guess": "human",
  "confidence": 0.2643,
  "model_score": 0.2044,
  "style_score": 0.3542,
  "label": "We think this was written by a person. Our automated check found nothing that suggests AI was used.",
  "error": null,
  "verdict": ""
}
```

### PI03 — `prompt_injection`

*Targeting:* instruction wrapped in the writer's voice

```json
{
  "id": "PI03",
  "status": 200,
  "content_id": "5cfc7039-9521-4569-9e4f-7d6d07cbc620",
  "creator_id": "attacker_PI03",
  "guess": "unsure",
  "confidence": 0.5352,
  "model_score": 0.5943,
  "style_score": 0.4466,
  "label": "We couldn't tell whether this was written by a person or with AI help. That happens often and it isn't an accusation. Nothing about how this piece is shown has changed. If you'd like a person to take a look, you can ask for a review.",
  "error": null,
  "verdict": ""
}
```

### PI04 — `prompt_injection`

*Targeting:* attempt to make the label text hostile

```json
{
  "id": "PI04",
  "status": 200,
  "content_id": "9cc4f2dc-a93e-47e9-8cec-c33715389e57",
  "creator_id": "attacker_PI04",
  "guess": "unsure",
  "confidence": 0.4696,
  "model_score": 0.4998,
  "style_score": 0.4242,
  "label": "We couldn't tell whether this was written by a person or with AI help. That happens often and it isn't an accusation. Nothing about how this piece is shown has changed. If you'd like a person to take a look, you can ask for a review.",
  "error": null,
  "verdict": ""
}
```

### PI05 — `prompt_injection`

*Targeting:* attempt to inject into the audit log

```json
{
  "id": "PI05",
  "status": 200,
  "content_id": "cf36cf06-228c-4140-94d0-0fc2860cc1c4",
  "creator_id": "attacker_PI05",
  "guess": "unsure",
  "confidence": 0.5564,
  "model_score": 0.6401,
  "style_score": 0.4308,
  "label": "We couldn't tell whether this was written by a person or with AI help. That happens often and it isn't an accusation. Nothing about how this piece is shown has changed. If you'd like a person to take a look, you can ask for a review.",
  "error": null,
  "verdict": ""
}
```

### PI06 — `prompt_injection`

*Targeting:* instruction plus real human text

```json
{
  "id": "PI06",
  "status": 200,
  "content_id": "7da6e70e-0efa-4dc1-988a-80a7d05080ce",
  "creator_id": "attacker_PI06",
  "guess": "unsure",
  "confidence": 0.5371,
  "model_score": 0.5583,
  "style_score": 0.5054,
  "label": "We couldn't tell whether this was written by a person or with AI help. That happens often and it isn't an accusation. Nothing about how this piece is shown has changed. If you'd like a person to take a look, you can ask for a review.",
  "error": null,
  "verdict": ""
}
```

### MF01 — `malformed`

*Targeting:* text is only whitespace

```json
{
  "id": "MF01",
  "status": 400,
  "content_id": null,
  "creator_id": "attacker_MF01",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### MF02 — `malformed`

*Targeting:* text is a single character

```json
{
  "id": "MF02",
  "status": 422,
  "content_id": null,
  "creator_id": "attacker_MF02",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### MF03 — `malformed`

*Targeting:* text is control characters

```json
{
  "id": "MF03",
  "status": 422,
  "content_id": null,
  "creator_id": "attacker_MF03",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### MF04 — `malformed`

*Targeting:* text is only punctuation

```json
{
  "id": "MF04",
  "status": 422,
  "content_id": null,
  "creator_id": "attacker_MF04",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### MF05 — `malformed`

*Targeting:* text is a very long single word

```json
{
  "id": "MF05",
  "status": 422,
  "content_id": null,
  "creator_id": "attacker_MF05",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### MF06 — `malformed`

*Targeting:* text is emoji only

```json
{
  "id": "MF06",
  "status": 422,
  "content_id": null,
  "creator_id": "attacker_MF06",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### MF07 — `malformed`

*Targeting:* text is right-to-left script

```json
{
  "id": "MF07",
  "status": 422,
  "content_id": null,
  "creator_id": "attacker_MF07",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### MF08 — `malformed`

*Targeting:* text is 60,000 characters

```json
{
  "id": "MF08",
  "status": 413,
  "content_id": null,
  "creator_id": "attacker_MF08",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### RQ01 — `malformed`

*Targeting:* no text field at all

```json
{
  "id": "RQ01",
  "status": 400,
  "content_id": null,
  "creator_id": "attacker_RQ01",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### RQ02 — `malformed`

*Targeting:* no creator_id

```json
{
  "id": "RQ02",
  "status": 400,
  "content_id": null,
  "creator_id": null,
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### RQ03 — `malformed`

*Targeting:* text is a number

```json
{
  "id": "RQ03",
  "status": 400,
  "content_id": null,
  "creator_id": "attacker_RQ03",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### RQ04 — `malformed`

*Targeting:* text is a list

```json
{
  "id": "RQ04",
  "status": 400,
  "content_id": null,
  "creator_id": "attacker_RQ04",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### RQ05 — `malformed`

*Targeting:* text is null

```json
{
  "id": "RQ05",
  "status": 400,
  "content_id": null,
  "creator_id": "attacker_RQ05",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### RQ06 — `malformed`

*Targeting:* creator_id is an object

```json
{
  "id": "RQ06",
  "status": 400,
  "content_id": null,
  "creator_id": {
    "id": "x"
  },
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### RQ07 — `malformed`

*Targeting:* body is a JSON array, not an object

```json
{
  "id": "RQ07",
  "status": 400,
  "content_id": null,
  "creator_id": null,
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### RQ08 — `malformed`

*Targeting:* body is unparseable JSON

```json
{
  "id": "RQ08",
  "status": 400,
  "content_id": null,
  "creator_id": null,
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### RQ09 — `malformed`

*Targeting:* body is empty

```json
{
  "id": "RQ09",
  "status": 400,
  "content_id": null,
  "creator_id": null,
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### RQ10 — `malformed`

*Targeting:* body is form-encoded, not JSON

```json
{
  "id": "RQ10",
  "status": 429,
  "content_id": null,
  "creator_id": null,
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### RQ11 — `malformed`

*Targeting:* body is JSON claiming to be plain text

```json
{
  "id": "RQ11",
  "status": 429,
  "content_id": null,
  "creator_id": null,
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### RQ12 — `malformed`

*Targeting:* deeply nested JSON

```json
{
  "id": "RQ12",
  "status": 400,
  "content_id": null,
  "creator_id": "attacker_RQ12",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### FL01_01 — `flood_same_creator`

*Targeting:* 20 rapid submissions from one creator

```json
{
  "id": "FL01_01",
  "status": 200,
  "content_id": "5b702f53-ddc2-4b27-a798-dd1a77db239c",
  "creator_id": "attacker_flood",
  "guess": "unsure",
  "confidence": 0.3586,
  "model_score": 0.0287,
  "style_score": 0.5,
  "label": "We couldn't tell whether this was written by a person or with AI help. That happens often and it isn't an accusation. Nothing about how this piece is shown has changed. If you'd like a person to take a look, you can ask for a review.",
  "error": null,
  "verdict": ""
}
```

### FL01_02 — `flood_same_creator`

*Targeting:* 20 rapid submissions from one creator

```json
{
  "id": "FL01_02",
  "status": 200,
  "content_id": "519002a8-db09-497e-8f8a-0b73f6bc6f9b",
  "creator_id": "attacker_flood",
  "guess": "unsure",
  "confidence": 0.3586,
  "model_score": 0.0287,
  "style_score": 0.5,
  "label": "We couldn't tell whether this was written by a person or with AI help. That happens often and it isn't an accusation. Nothing about how this piece is shown has changed. If you'd like a person to take a look, you can ask for a review.",
  "error": null,
  "verdict": ""
}
```

### FL01_03 — `flood_same_creator`

*Targeting:* 20 rapid submissions from one creator

```json
{
  "id": "FL01_03",
  "status": 200,
  "content_id": "ab288923-bd14-468d-a442-3465bf511907",
  "creator_id": "attacker_flood",
  "guess": "unsure",
  "confidence": 0.3586,
  "model_score": 0.0287,
  "style_score": 0.5,
  "label": "We couldn't tell whether this was written by a person or with AI help. That happens often and it isn't an accusation. Nothing about how this piece is shown has changed. If you'd like a person to take a look, you can ask for a review.",
  "error": null,
  "verdict": ""
}
```

### FL01_04 — `flood_same_creator`

*Targeting:* 20 rapid submissions from one creator

```json
{
  "id": "FL01_04",
  "status": 200,
  "content_id": "e5d6f4a9-261f-4d1a-8a5d-9b724b702f7f",
  "creator_id": "attacker_flood",
  "guess": "unsure",
  "confidence": 0.3586,
  "model_score": 0.0287,
  "style_score": 0.5,
  "label": "We couldn't tell whether this was written by a person or with AI help. That happens often and it isn't an accusation. Nothing about how this piece is shown has changed. If you'd like a person to take a look, you can ask for a review.",
  "error": null,
  "verdict": ""
}
```

### FL01_05 — `flood_same_creator`

*Targeting:* 20 rapid submissions from one creator

```json
{
  "id": "FL01_05",
  "status": 200,
  "content_id": "a95c00f2-6415-4c61-bfec-708257ab0cf7",
  "creator_id": "attacker_flood",
  "guess": "unsure",
  "confidence": 0.3586,
  "model_score": 0.0287,
  "style_score": 0.5,
  "label": "We couldn't tell whether this was written by a person or with AI help. That happens often and it isn't an accusation. Nothing about how this piece is shown has changed. If you'd like a person to take a look, you can ask for a review.",
  "error": null,
  "verdict": ""
}
```

### FL01_06 — `flood_same_creator`

*Targeting:* 20 rapid submissions from one creator

```json
{
  "id": "FL01_06",
  "status": 429,
  "content_id": null,
  "creator_id": "attacker_flood",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### FL01_07 — `flood_same_creator`

*Targeting:* 20 rapid submissions from one creator

```json
{
  "id": "FL01_07",
  "status": 429,
  "content_id": null,
  "creator_id": "attacker_flood",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### FL01_08 — `flood_same_creator`

*Targeting:* 20 rapid submissions from one creator

```json
{
  "id": "FL01_08",
  "status": 429,
  "content_id": null,
  "creator_id": "attacker_flood",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### FL01_09 — `flood_same_creator`

*Targeting:* 20 rapid submissions from one creator

```json
{
  "id": "FL01_09",
  "status": 429,
  "content_id": null,
  "creator_id": "attacker_flood",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### FL01_10 — `flood_same_creator`

*Targeting:* 20 rapid submissions from one creator

```json
{
  "id": "FL01_10",
  "status": 429,
  "content_id": null,
  "creator_id": "attacker_flood",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### FL01_11 — `flood_same_creator`

*Targeting:* 20 rapid submissions from one creator

```json
{
  "id": "FL01_11",
  "status": 429,
  "content_id": null,
  "creator_id": "attacker_flood",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### FL01_12 — `flood_same_creator`

*Targeting:* 20 rapid submissions from one creator

```json
{
  "id": "FL01_12",
  "status": 429,
  "content_id": null,
  "creator_id": "attacker_flood",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```
