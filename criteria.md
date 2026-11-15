# Acceptance criteria — Provenance Guard

> **When these were written:** 2026-11-14. That is after the unit 8 attack run
> (2026-11-07) and the threshold change it led to, and before any run of
> `run_eval.py`. The attack results were known when I wrote these; the eval
> results were not.

---

## 1. False positives

**Of my 10 original writing samples, at most 2 should get labeled as AI in every trial.**

**Why this target:** One of the biggest concerns with AI detection systems is that they can incorrectly identify human-written content as AI-generated. This can become a serious issue in academic environments, where students might be accused of using AI even when they completed their assignments independently.

For my project, I want to make sure the system is reasonably accurate without being overly aggressive. I chose a maximum of 2 false positives out of 10 samples as an initial testing threshold because I want the detector to recognize most human-written content correctly. However, this is only a starting point, and I would want to reduce that number further before using the application in a real environment.

I would test the system using different types of my own writing, including essays, discussion posts, homework assignments, and informal paragraphs. This would help me determine whether the detector performs differently depending on writing style, vocabulary, or sentence structure.

---

## 2. Bad input handling

**Of 10 intentionally invalid requests, all 10 should return a 4xx error, and none should crash the service.**

**Why this target:** An application should be able to handle unexpected input without failing. Users might accidentally submit empty text, invalid data, or requests that do not follow the expected structure. I want the backend to recognize invalid requests and return appropriate HTTP error codes instead of crashing or producing confusing results.

I would test empty submissions, unusually long submissions, incorrect data types, and missing fields. Reliable error handling improves both security and the overall user experience.

---

## 3. Appeals process

**Of 5 valid appeals, all 5 should move the associated item to `under_review` and appear in the appeal log.**

**Why this target:** Since AI detection is not completely reliable, users should have an opportunity to challenge classifications they believe are incorrect. When an appeal is submitted successfully, the system should update the item's status to `under_review` and create a corresponding entry in the log, so an administrator can track appeals and investigate possible classification mistakes.

I chose 5 appeals as an initial functional test because it is a manageable number for checking whether the status change and logging work correctly.

---

## 4. Classification labels

**All three classification labels should be reachable: `human`, `uncertain`, and `AI`.**

**Why this target:** A detection system should not always be forced to classify content as either human-written or AI-generated. Some writing has characteristics of both, for example an essay improved with a grammar checker, or an AI paragraph edited heavily by a person. Because of that, the `uncertain` label matters, but so do the other two.

I would submit original human-written paragraphs, clearly AI-generated examples, and ambiguous examples, and check that all three labels come back. If the system only ever produces one or two labels, its thresholds or classification logic have a problem.

---

## 5. Reliability

**At least 95% of valid requests should receive a successful response during testing.**

**Why this target:** Even if the detection works well, the application would not be useful if the API frequently crashes, times out, or fails to return results. I would test using multiple valid requests with different text lengths and writing styles. 95% is my initial target, although I would aim for a higher percentage before deploying the application for real users.

---

<!-- ─────────────────────────────────────────────────────────────────────────
     UNIT 8 — read this before you change anything above.

     If a criterion turns out to be BROKEN rather than merely unmet, you can
     revise it, and that earns credit. But never delete or edit the original
     line. Add the revision underneath, like this:

         ## 2. Uncertain cases land in the unsure band

         The system handles uncertain cases well.

         **Why this target:** ...

         > **Revised in unit 8:** Text I judged borderline scores between
         > 0.4 and 0.6 in at least 4 of 5 cases.
         >
         > **Why revised:** "well" gave me nothing to check. I couldn't
         > reach a verdict from it at all.

     That's a revision because the criterion couldn't be MEASURED.

     Lowering a target because you missed it is not a revision, and it costs
     you the point:

         ✗ "At most 1 of 10 of my own pieces flagged as AI" → "at most 3
            of 10", because 1 of 10 turned out to be hard.

     A number you missed stays where it is, gets diagnosed, and gets a fix
     attempted. That's where the points are.
     ───────────────────────────────────────────────────────────────────────── -->

---

# Capstone criteria — internal-failure hardening (shape B)

> **When these were written:** 2026-11-15, after the extension was built and one
> logged session was run (the cost measurement in the README), and before any
> capstone trial run. Criteria 1–3 are about the extension; 4 and 5 are about
> the bad path.

## C1. Timeout handling

**Simulate a slow model response → return 503 within 11 seconds, 3/3 tests.**

**Why this target:** requests shouldn't hang.

## C2. Model failure

**Simulate the AI model crashing → return a clear error without crashing the server, 3/3 tests.**

**Why this target:** failures should be handled safely.

## C3. Error logging

**Trigger a processing failure → record the failure in the audit log, 3/3 tests.**

**Why this target:** errors need to be traceable.

## C4. Invalid endpoint

**Submit a request to an invalid endpoint → return 404, 3/3 tests.**

**Why this target:** nonexistent routes should be rejected.

## C5. Invalid input

**Submit empty or malformed JSON → return a 4xx error with a clear reason, 3/3 tests.**

**Why this target:** bad requests shouldn't reach the classifier.
