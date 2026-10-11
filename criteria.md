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
