# Acceptance criteria — FitFindr

Five criteria that say what "working" means for this agent, written in unit 3
**before** any results existed.

An acceptance criterion names a target: a number, a count, a rate, or something
a person could plainly observe. *"The agent handles errors"* is an opinion.
*"When search returns nothing, the agent stops before calling the second tool,
in 5 of 5 tries"* is a criterion.

Under each one, write a sentence or two on **why that target** and not a
stricter one. A reason that says something about your tools, your loop, or the
data earns credit; *"80% seemed reasonable"* does not.

> Missing your own targets next unit costs you nothing. Setting a target so
> easy you can't miss it does.

**Two are written for you. You write three.**

---

## 1. A matching query completes all three tools

Given a query that matches at least one listing, the agent completes all three
tool calls and returns a fit card — in at least 4 of 5 tries.

**Why this target:**
My search is a plain keyword overlap match, so a query phrased differently
from a listing's own wording could score zero even on a reasonable match.
4 of 5 accounts for that without masking a real bug.

---

## 2. An impossible query stops before the second tool

Given a query that matches no listings, the agent stops before calling
`suggest_outfit` and returns a message naming what to change — 5 of 5 tries.

**Why this target:**
This branch is just a data check, whether `search_listings` returned
anything. No model is involved in deciding to stop, so there's no reason
for it to behave inconsistently.

---

## 3. The same item reaches every tool

Given a query that matches at least one listing, the `id` of the item passed
into `create_fit_card` is the same as the `id` in `session["selected_item"]`
in 5 of 5 tries.

**Why this target:**
This is a direct comparison of two values in code, with no model involved,
so there's no reason to expect it to pass inconsistently.

---

## 4. The fit card mentions the price and the style

Given a query that matches at least one listing, the resulting fit card
mentions the item's price and at least one of its `style_tags` in 4 of 5
tries.

**Why this target:**
Unlike criterion 3, this depends on the model's phrasing rather than just
code logic, and a generative model can occasionally produce vaguer wording
that skips a literal price or style-tag word even with a good prompt 4 of
5 accounts for that normal variance without being so loose it stops meaning
anything.

---

## 5. Results respect the price ceiling

Given a query with a `max_price`, every listing in the returned results has
a `price` at or below that value in 5 of 5 tries.

**Why this target:**
This is a deterministic comparison with no model involved, so there's no
reason to expect it to pass inconsistently.

---

<!-- ─────────────────────────────────────────────────────────────────────────
     UNIT 4 — read this before you change anything above.

     If a criterion turns out to be BROKEN rather than merely unmet, you can
     revise it, and that earns credit. But never delete or edit the original
     line. Add the revision underneath it, like this:

         ## 4. Something about the fit card

         The fit card is different every time.

         **Why this target:** ...

         > **Revised in unit 4:** For 5 different items, the 5 fit cards share
         > no opening sentence.
         >
         > **Why revised:** "different" wasn't checkable — two cards that
         > differed by one word still counted. The new version is something I
         > can actually score.

     That's a revision because the criterion couldn't be MEASURED.

     Lowering a target because you missed it is not a revision, and it costs
     you the point:

         ✗ "I said the empty search stops it 5 of 5 times, but I got 3 of 5,
            so 3 of 5 is more realistic."

     A number you missed stays where it is, gets diagnosed, and gets a fix
     attempted. That's where the points are.
     ───────────────────────────────────────────────────────────────────────── -->

---

## Capstone criteria

Test set: `capstone_queries.py` (10 on_topic, 10 off_topic, labelled before any code was written).

**1. Off-topic queries are rejected.**
Of the 10 queries labelled `off_topic` in `capstone_queries.py`, at least 8 are rejected — `session["error"]` is set and `search_listings` is never called — in each of the 3 trials.
Why 8: two of the off-topic queries, "how do I wash a denim jacket" and "what's the history of the sneaker", contain clothing words, so a clothing word list will likely let them through. Letting an off-topic query through costs 2 model calls and shows the user an unrelated fit card, which is less bad than rejecting a real clothing request.

**2. Real clothing queries get through.**
Of the 10 queries labelled `on_topic` in `capstone_queries.py`, at least 9 pass the check and reach `search_listings`, in each of the 3 trials.
Why 9: "something to wear for an Indian wedding" is a real clothing request with no clothing word in it, so a clothing word list may reject it. Every other on-topic query names a clothing item and should pass. This target is stricter than criterion 1's because rejecting a real clothing request is the worse mistake: the user asked for something FitFindr can do, is told it can't help, and leaves.

**3. A rejection costs nothing.**
Every query rejected as off-topic makes 0 model calls and 0 calls to `search_listings`, in each of the 3 trials.
Why 0 and 0: FitFindr runs on the free tier, which allows 15 model requests a minute. If unrelated queries use up calls, there may be none left for real clothing queries. Search is skipped too, because each MCP search call starts a new server process, which takes time even though it costs no quota. A word-list check doesn't need either tool, so there's no reason to allow even one call.

**4. The rejection message says why, and what to try instead.**
Every rejection message contains the word "clothing" and one example query in quotes, and is different from the "No listings matched…" message, in each of the 3 trials.
Why: a user whose real clothing request gets rejected (like "something to wear for an Indian wedding", which has no clothing word) believes they asked a correct question. If the message only says nothing matched, they'll think FitFindr failed. Saying FitFindr helps with clothing and showing an example query tells them how to ask again so it gets through. The "No listings matched… try a broader description" message would point them the wrong way.

**5. The normal path still works.**
Every `on_topic` query that passes the check (and gets search results) still ends with `session["error"]` as None and a fit card of at least 150 characters, in each of the 3 trials.
Why 150: a fit card is meant to be 2–4 sentences that mention the item's price and platform. Two short sentences with both come to about 150 characters, and my Project 2 fit cards were 240–350. Anything under 150 means the model's answer was cut short or nearly empty, which is a broken result even though the run didn't crash. Why every passing query: this is the only criterion that involves the model, so it's the one that can differ between trials, and the off-topic check must not break any request it lets through.
