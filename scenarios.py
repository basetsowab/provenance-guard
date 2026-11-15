"""
What your test runs. ← UNIT 8, MILESTONE 3

Each of your five criteria needs something run against it. A criterion about
false positives needs your own writing. One about label coverage needs inputs
across the score range. One about the appeal path needs a real content_id.

Working that out is Milestone 3's first step, and this file is where you write
it down. `run_eval.py` runs everything here three times.

Two are filled in as examples. Replace them with what your criteria actually
need — these are a shape, not a set.

A scenario carries **either** of these:

    "texts"   a list of strings. Each is sent as {"text": ..., "creator_id": ...}
              with a creator_id made up for you. Use this for most criteria.

    "bodies"  a list of whole request bodies, sent exactly as written. Use this
              when the malformed request IS the point — empty text, no `text`
              field at all, something enormous. A bad-input criterion needs it,
              because you cannot express "the field is missing" as a string.
"""

# Criterion numbers are left as None until criteria.md is written; set each
# one to the criterion it tests.

# Machine-written on purpose: generic, polished, the register AI detectors are
# built for. Written by Claude for this test, not taken from the attack set.
CLEARLY_AI = [
    "In today's fast-paced digital landscape, effective communication has become more important than ever. By leveraging innovative tools and fostering a culture of collaboration, organizations can unlock new opportunities for growth. Furthermore, it is essential to recognize that clear communication builds trust among team members. Ultimately, investing in communication skills is a key driver of long-term success.",
    "Climate change is one of the most pressing challenges facing humanity today. Rising global temperatures are leading to more frequent extreme weather events, melting ice caps, and rising sea levels. To address this issue, governments, businesses, and individuals must work together to reduce greenhouse gas emissions. By embracing renewable energy and sustainable practices, we can create a healthier planet for future generations.",
    "Regular exercise offers numerous benefits for both physical and mental health. It helps maintain a healthy weight, strengthens the cardiovascular system, and improves overall energy levels. Additionally, exercise has been shown to reduce stress and anxiety. Incorporating even small amounts of physical activity into your daily routine can make a significant difference in your well-being.",
]

# Human-written beyond doubt: public-domain prose from before any language
# model existed (Twain 1884, Thoreau 1854, Douglass 1845, Whitman 1855).
CLEARLY_HUMAN = [
    "Jim said bees wouldn't sting idiots; but I didn't believe that, because I had tried them lots of times myself, and they wouldn't sting me. I had heard about some of these things before, but not all of them. Jim knowed all kinds of signs. He said he knowed most everything. I said it looked to me like all the signs was about bad luck, and so I asked him if there warn't any good-luck signs.",
    "You don't know about me without you have read a book by the name of The Adventures of Tom Sawyer; but that ain't no matter. That book was made by Mr. Mark Twain, and he told the truth, mainly. There was things which he stretched, but mainly he told the truth. That is nothing. I never seen anybody but lied one time or another, without it was Aunt Polly, or the widow, or maybe Mary.",
    "I went to the woods because I wished to live deliberately, to front only the essential facts of life, and see if I could not learn what it had to teach, and not, when I came to die, discover that I had not lived. I did not wish to live what was not life, living is so dear; nor did I wish to practise resignation, unless it was quite necessary.",
    "I was born in Tuckahoe, near Hillsborough, and about twelve miles from Easton, in Talbot county, Maryland. I have no accurate knowledge of my age, never having seen any authentic record containing it. By far the larger part of the slaves know as little of their ages as horses know of theirs, and it is the wish of most masters within my knowledge to keep their slaves thus ignorant.",
    "I celebrate myself, and sing myself, And what I assume you shall assume, For every atom belonging to me as good belongs to you. I loafe and invite my soul, I lean and loafe at my ease observing a spear of summer grass. My tongue, every atom of my blood, form'd from this soil, this air.",
]

SCENARIOS = [
    # ⚠️ YOUR OWN WRITING GOES HERE, and only yours: not AI text, not someone
    # else's prose. Uncomment, paste ~10 pieces, and set the criterion number.
    #
    # {
    #     "name": "my own writing",
    #     "criterion": None,
    #     "texts": [
    #         "...",
    #     ],
    # },
    {
        "name": "clearly AI",
        "criterion": None,
        "texts": CLEARLY_AI,
    },
    {
        "name": "clearly human",
        "criterion": None,
        "texts": CLEARLY_HUMAN,
    },
    {
        "name": "bad input",
        "criterion": None,
        # Raw bodies. Each has its own creator_id so the three trials don't
        # trip the per-address limit and hide what the route does.
        "bodies": [
            {"text": "", "creator_id": "eval_bad_empty"},
            {"text": "   \n\t  ", "creator_id": "eval_bad_blank"},
            {"creator_id": "eval_bad_missing"},
            {"text": None, "creator_id": "eval_bad_null"},
            {"text": 12345, "creator_id": "eval_bad_number"},
            {"text": "word " * 50000, "creator_id": "eval_bad_huge"},
        ],
    },
    {
        "name": "appeal path",
        "criterion": None,
        # Each text is submitted, then appealed against the content_id that
        # came back, then GET /log is read to confirm the status moved.
        # Handled by run_eval.py::run_appeals.
        "appeals": CLEARLY_AI[:2] + CLEARLY_HUMAN[:3],
        "reasoning": "I wrote this myself and can show my drafts.",
    },
]


def validate() -> list[str]:
    """
    Complain about anything malformed, before a long run rather than during.

    A "bodies" scenario is deliberately exempt from the empty check — an empty
    string is the whole point of a bad-input case, and refusing to run one
    would make that criterion untestable.
    """
    problems = []
    for i, scenario in enumerate(SCENARIOS, 1):
        if not scenario.get("name"):
            problems.append(f"scenario {i} has no name")

        texts = scenario.get("texts")
        bodies = scenario.get("bodies")
        appeals = scenario.get("appeals")

        if appeals:
            if texts or bodies:
                problems.append(f"scenario {i} mixes appeals with texts or bodies")
            elif not all(isinstance(t, str) and t.strip() for t in appeals):
                problems.append(f"scenario {i} has an empty appeal text")
            continue

        if texts and bodies:
            problems.append(
                f"scenario {i} ('{scenario.get('name')}') has both texts and "
                f"bodies — pick one"
            )
            continue

        if bodies:
            for j, body in enumerate(bodies, 1):
                if not isinstance(body, dict):
                    problems.append(
                        f"scenario {i}, body {j} is not a dict — bodies are whole "
                        f"request bodies, like {{'text': '', 'creator_id': 'x'}}"
                    )
            continue

        if not texts:
            problems.append(f"scenario {i} has no texts and no bodies")
            continue

        for j, text in enumerate(texts, 1):
            if not str(text).strip():
                problems.append(
                    f"scenario {i}, text {j} is empty — if an empty submission is what "
                    f"you're testing, use 'bodies' instead of 'texts'"
                )
            elif str(text).startswith("REPLACE ME"):
                problems.append(
                    f"scenario {i} ('{scenario.get('name')}'), text {j} is still "
                    f"the placeholder"
                )
    return problems
