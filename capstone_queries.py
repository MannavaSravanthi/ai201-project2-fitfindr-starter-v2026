"""
Capstone test set — labelled before any code was written.

Each query is labelled with what FitFindr SHOULD do:
    "on_topic"  — a clothing request; it should go through to search
    "off_topic" — not a clothing request; it should be rejected

Labels were decided up front, before building or running anything, so
results are scored against this list, not against judgment after the fact.
"""

TEST_QUERIES = [
    # ── on-topic ─────────────────────────────────────────────────────────────
    ("give me a plaid skirt styling ideas",                  "on_topic"),
    ("blue sweater",                                         "on_topic"),
    ("how to style black denim jeans",                       "on_topic"),
    ("brown suede jacket",                                   "on_topic"),
    ("coffee colored shirt",                                 "on_topic"),
    ("linen shirts for summer or winter?",                   "on_topic"),
    ("floral dresses styling ideas",                         "on_topic"),
    ("something to wear for an Indian wedding",              "on_topic"),
    ("light washed denim jean with boot cut",                "on_topic"),
    ("bandana colors that go with a light colored t shirt",  "on_topic"),

    # ── off-topic: clearly not about clothing ───────────────────────────────
    ("tell me a joke",                                       "off_topic"),
    ("cranberry cookies recipe",                             "off_topic"),
    ("can you give some recipe cards for high protein meals?", "off_topic"),
    ("give me ideas to decorate my laptop.",                 "off_topic"),

    # ── off-topic: borderline, shares a word with listings ──────────────────
    ("vintage car under $30",                                "off_topic"),
    ("recommend a black coffee",                             "off_topic"),
    ("Is the color of taj-mahal off white?",                 "off_topic"),
    ("where to buy orange color snoopy coffee mug?",         "off_topic"),

    # ── off-topic: contains a clothing word, not a shopping request ─────────
    ("how do I wash a denim jacket",                         "off_topic"),
    ("what's the history of the sneaker",                    "off_topic"),
]


if __name__ == "__main__":
    on = sum(1 for _, label in TEST_QUERIES if label == "on_topic")
    print(f"{len(TEST_QUERIES)} queries: {on} on_topic, {len(TEST_QUERIES) - on} off_topic")
