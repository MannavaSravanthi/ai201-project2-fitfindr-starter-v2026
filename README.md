# FitFindr

> ### 👋 Start here
>
> **New to this repo? Read [RUNNING.md](RUNNING.md) first** — setup, every
> command, and what to do when something breaks.
>
> Once `python test.py` passes:
>
> ```bash
> python app.py listings --full -n 6      # read the data (Milestone 1)
> python app.py fields                    # what you can filter on
> python app.py ask 'vintage graphic tee under $30'
> ```
>
> All three tools are stubs, so that last command will do nothing useful yet.
> That's the starting position.
>
> **The rest of this file is your submission.** Fill it in as you go.

---

<!-- ─────────────────────────────────────────────────────────────────────────
     HOW TO USE THIS FILE

     This is your submission. Fill each section in as you finish the milestone
     it belongs to — don't leave it all to the end.

     Unit 3 asks for the first five sections. Unit 4 adds the five below them.
     Leave the unit 4 sections alone until then; they're here so you know
     what's coming.

     Everything is pasted as TEXT. No screenshots, no images, no video links.
     A typed block of output gets full credit; a picture of the same output
     gets none.
     ───────────────────────────────────────────────────────────────────────── -->

<!-- ═══════════════════════ UNIT 3 — THE BUILD ═══════════════════════ -->

## What This Does

<!-- Three or four sentences: what a user asks for, and what they get back. -->
FitFindr turns a plain language thrifting request into a styled, shareable pick. A user describes what they want for example, “find me a large size vintage shirt under $20 and give me ideas to style it” and the agent searches secondhand listings for a match, builds outfit ideas by pairing the item with pieces from the user’s own wardrobe, and writes a short caption describing the fit. It also compares the item's price against similar listings to flag whether it's a good deal. Instead of searching, comparing, and imagining the outfit themselves, the user gets back a specific listing, a styling suggestion, and text they could actually post.

---

## Tool Inventory

<!-- Four lines per tool. This is worth 2 points and it's the single most
     common place students lose them.

     "Returns a list" earns NOTHING. The description has to say what is IN
     the list.

     The empty case isn't optional either — it's the thing your loop branches
     on, and if you don't decide it here you'll discover it as a crash in
     Milestone 5. -->

### `search_listings`

- **What it does:**
  Searches the listings data for items matching a free text description, a size, and a maximum price, and returns the ones that match.
- **Inputs:** <!-- name and type each: `max_price` (float), not "a price" -->
  `description` (str), `size` (str or None. no size filter when omitted), `max_price` (float)
- **Returns:**
  A list of dicts, one per matching listing, each matching listing’s full dict (all fields from data/listings.json)
- **When it has nothing:**
  An empty list (`[]`)

### `suggest_outfit`

- **What it does:**
  Takes a new item (the listing `search_listings` found) and the user's wardrobe, and asks the model for outfit ideas that pair the new item with pieces already   in the wardrobe.
- **Inputs:**
  `new_item` (dict, a listing dict with fields like `title`,`category`, `colors`, `style_tags`), `wardrobe` (dict with an `items` list of wardrobe item dicts, as defined in `wardrobe_schema.json`)
- **Returns:**
  A string containing one or two outfit ideas in prose, describing how to style the new item with specific wardrobe pieces.
- **When it has nothing:**
  If the wardrobe's `items` list is empty, it still returns general styling advice for the new item alone, instead of failing or returning an empty list.

### `create_fit_card`

- **What it does:**
  Takes a new item and its outfit ideas, and asks the model to write a short caption describing the fit, something a user could actually post.
- **Inputs:**
  outfit (string, the outfit ideas from suggest_outfit), new_item (dict the listing dict, same shape search_listings returns)
- **Returns:**
  A string. The caption text
- **When it has nothing:**
  If `outfit` is an empty or whitespace only string, it writes a caption from `new_item`'s own details alone (no styling mentioned), instead of failing.

### `compare_price` (stretch)

- **What it does:** Compares a listing's price against other listings that share both its category and at least one style tag, and says whether
  it's a good deal relative to similar items.
- **Inputs:** `item` (dict, the listing to compare)
- **Returns:** A dict with `average_price` (float, average of the matching comparison listings), `this_price` (float, the item's own
  price), `compared_against` (int, how many listings it was compared to), and `verdict` (str, "below average", "above average", or "about
  average", using a small tolerance band, e.g. within 10% counts as "about average")
- **When it has nothing:** If fewer than 2 other listings share both the category and a style tag, returns `verdict: "not enough data to
  compare"` and the other fields as `None`, instead of computing an average from 0 or 1 items.

---

## Planning Loop

<!-- Your branch rule, stated as a rule — the condition AND both paths — plus
     the file and function that holds it.

     Like this:
       "If search_listings returns an empty list, put a message in the session
        and stop. Otherwise take the first result and go to suggest_outfit."
        — agent.py::run_agent

     The grader checks your code against what you claim here, so the file and
     function have to be real. -->

**Branch rule:** If `search_listings` returns an empty list, write a message
to `session["error"]` describing what the user could change and return the
session immediately — `compare_price`, `suggest_outfit`, and `create_fit_card`
are never called. Otherwise, take the first result as `session["selected_item"]`,
run `compare_price` on it, then call `suggest_outfit` followed by
`create_fit_card`, storing each result back into the session.

**Where it lives:** `agent.py::run_agent`

**How the query is parsed:** Regex and string splitting, not a model call. A
regex pulls out a `$` price, a size word is matched against a lookup table,
and whatever's left is split into words with filler words removed to form the
description.

**What moves through the session:** `query` (the raw input) ; `parsed`
(description/size/max_price extracted from it) ; `search_results` (all
matches from `search_listings`) ; `selected_item` (the first match, chosen to
move forward) ; `wardrobe` (passed in, not derived) ; `price_comparison`
(from `compare_price` on the selected item) ; `outfit_suggestion` (from
`suggest_outfit`) ; `fit_card` (from `create_fit_card`) ; `error` (set only
if the run stopped early at the branch).

---

## Sample Run

**One full query**

```
$ python app.py ask 'vintage graphic tree under $30'

  Found:    Y2K Baby Tee — Butterfly Print — $18.0 on depop

  Outfit:   Here are two specific ways to style your new Y2K butterfly baby tee using pieces you already own:

### Outfit 1: 2000s Streetwear Contrast
Play up the nostalgic Y2K vibe of the tee by pairing it with baggy denim and adding some edge. 
* **Top:** Y2K Butterfly Baby Tee
* **Bottoms:** Baggy straight-leg jeans (dark wash)
* **Outerwear:** Black cropped zip hoodie (wear it unzipped so the graphic shows)
* **Shoes:** Chunky white sneakers
* **Bag:** Black crossbody bag

### Outfit 2: Elevated Earth Tones
Let the pastel pink and purple in the butterfly graphic pop against neutral trousers for a more balanced, everyday look.
* **Top:** Y2K Butterfly Baby Tee (tucked in slightly)
* **Bottoms:** Wide-leg khaki trousers
* **Accessories:** Brown leather belt (to cinch the trousers and pull in a warm tone)
* **Outerwear:** Vintage black denim jacket (draped over the shoulders if it's chilly)
* **Shoes:** Chunky white sneakers

  Fit card: Found this little butterfly tee on Depop for $18 and I'm obsessed, even if it runs a little small. Definitely leaning into the nostalgic streetwear look todaywith baggy dark denim and a zip hoodie. Thinking about trying it with khaki trousers and a belt next time to make the colors pop!

2 model calls this session, 720 prompt + 297 output tokens
```

**The three tools, tested one at a time**

```
$ python -c "from tools import search_listings; print(search_listings('graphic tee', max_price=30))"
[{'id': 'lst_002', 'title': 'Y2K Baby Tee — Butterfly Print', 'description': 'Super cute early 2000s baby tee with butterfly graphic. Fitted crop length. Tag says medium but fits like a small.', 'category': 'tops', 'style_tags': ['y2k', 'vintage', 'graphic tee', 'cottagecore'], 'size': 'S/M', 'condition': 'excellent', 'price': 18.0, 'colors': ['white', 'pink', 'purple'], 'brand': None, 'platform': 'depop'}, {'id': 'lst_006', 'title': 'Graphic Tee — 2003 Tour Bootleg Style', 'description': 'Vintage-style bootleg tee with faded graphic. Slightly boxy fit. 100% cotton, soft and worn-in.', 'category': 'tops', 'style_tags': ['graphic tee', 'vintage', 'grunge', 'streetwear', 'bandtee'], 'size': 'L', 'condition': 'good', 'price': 24.0, 'colors': ['black'], 'brand': None, 'platform': 'depop'}, {'id': 'lst_017', 'title': 'Mesh Long-Sleeve Top — Black', 'description': 'Sheer black mesh long-sleeve. Great for layering under a graphic tee or over a bralette. Stretchy material, fits true to size.', 'category': 'tops', 'style_tags': ['y2k', 'grunge', 'goth', 'layering'], 'size': 'S/M', 'condition': 'excellent', 'price': 15.0, 'colors': ['black'], 'brand': None, 'platform': 'depop'}, {'id': 'lst_033', 'title': 'Vintage Band Tee — Faded Grey', 'description': 'Faded grey band-style tee with distressed graphic. Crew neck. Fits boxy. Well-loved but no holes or major damage.', 'category': 'tops', 'style_tags': ['vintage', 'grunge', 'band tee', 'graphic tee', 'streetwear'], 'size': 'L', 'condition': 'fair', 'price': 19.0, 'colors': ['grey', 'charcoal'], 'brand': None, 'platform': 'depop'}, {'id': 'lst_015', 'title': 'Vintage Graphic Hoodie — Faded Black', 'description': 'Faded black pullover hoodie with barely-visible vintage graphic on the chest. Cozy interior. Some pilling but adds to the worn-in look.', 'category': 'tops', 'style_tags': ['vintage', 'grunge', 'graphic', 'streetwear'], 'size': 'L', 'condition': 'fair', 'price': 26.0, 'colors': ['black', 'charcoal'], 'brand': None, 'platform': 'depop'}]
```

```
$ python -c "from tools import suggest_outfit; from utils.data_loader import get_example_wardrobe, load_listings; print(suggest_outfit(load_listings()[0], get_example_wardrobe()))"
Here are two specific outfit ideas using your new Vintage Levi's 501 Jeans and pieces straight from your wardrobe:

### Look 1: 90s Off-Duty Streetwear
*Lean into the vintage 501s with an effortless, casual-cool combo that plays with proportions.*

*   **Tops:** White ribbed tank top (tucked in to show off the waistband)
*   **Outerwear:** Oversized grey crewneck sweatshirt (draped over the shoulders or worn on top)
*   **Shoes:** Chunky white sneakers
*   **Accessories:** Black crossbody bag
*   *Why it works:* The fitted white tank balances out the relaxed fit of the vintage Levi's and the oversized grey crewneck. Throw on the chunky sneakers and black crossbody, and you've got the ultimate 90s errands-running uniform.

### Look 2: Grunge-Edged Denim
*Mix black and blue denim for an effortless, high-contrast look with a bit of an attitude.*

*   **Tops:** Black cropped zip hoodie
*   **Outerwear:** Vintage black denim jacket (layered over the hoodie)
*   **Shoes:** Black combat boots
*   **Accessories:** Brown leather belt (use this to break up the black and blue tones)
*   *Why it works:* The black cropped zip hoodie and black combat boots give the classic medium-wash 501s an instant edge. Adding the vintage black denim jacket creates acool double-denim moment, while the brown leather belt adds a nice, unexpected vintage contrast.
```

```
$ python -c "from tools import create_fit_card; from utils.data_loader import load_listings; print(create_fit_card('jeans and white sneakers', load_listings()[0]))"
Score these vintage Levi's 501s on Depop for just $38 and I am never taking them off. Love the natural fading at the knees — they honestly fit like a glove. Just threw them on with my favorite white sneakers for the easiest everyday uniform.
```

---

## How I Used AI

<!-- Two specific moments. What you asked, what came back, what you changed.

     "I used Claude to help me code" is not enough.

     "I gave Claude my search_listings spec. It returned None on no match
     instead of an empty list, so I changed it" is the level we want. -->

**Moment 1**

- *What I asked for:* How `compare_price` should decide whether a listing's
  price — like $18 for the Y2K baby tee — actually counts as a good deal.
- *What came back:* Two options. (A) A rule-based comparison: average the
  price of other listings sharing the same category and at least one style
  tag, then bucket the item as below/above/about average by a threshold.
  (B) Ask the model to judge whether the price is a good deal using its
  general sense of value.
- *What I changed:* I went with option A. Option B would've been
  non-deterministic and cost a model call every time, and it has no
  grounding in the actual listings data — it could call something a "great
  deal" that's actually expensive relative to everything else in
  `data/listings.json`. The rule-based version is what's in `compare_price`
  in `tools.py` now: comparable items need the same category and an
  overlapping style tag, at least 2 of them to compare against, and the
  verdict is "below average" / "above average" / "about average" based on
  whether the price is more than 10% off the group's average.

**Moment 2**

- *What I asked for:* A way to pull `description`/`size`/`max_price` out of
  the raw query string without burning a model call on every request, since
  an extra call per query is expensive.
- *What came back:* Regex and string splitting — pull the price out with a
  `$` regex, match size words against a lookup table, treat whatever words
  are left (minus fillers like "find", "me", "under") as the description.
- *What changed:* The first version checked size words in plain dict order,
  so a query like "extra large tee" matched "large" first, cut just that
  out, and left `size: "large"` instead of `"extra large"`. I changed
  `_SIZE_WORDS` to be checked longest-word-first
  (`sorted(_SIZE_WORDS, key=len, reverse=True)` in `parse_query` in
  `agent.py`), so "extra large" gets matched and removed before "large" can
  grab a piece of it.

<!-- ═══════════════════════ UNIT 4 — THE TEST ═══════════════════════

     Don't fill these in during unit 3.
     ═══════════════════════════════════════════════════════════════════ -->

---

## Run Log — Before

<!-- Five criteria, five tries each, in this exact format.

     Five, because your criteria are written out of five. Mark each try PASS
     or FAIL, count the passes, and read that count against your target — a
     row targeting 4 of 5 with three PASS cells is MISSED (3/5).

     `python run_eval.py --label before` runs everything and writes the table
     into results/. Paste it here and fill in the verdicts. -->

| Criterion | Target | Try 1 | Try 2 | Try 3 | Try 4 | Try 5 | Verdict |
|---|---|---|---|---|---|---|---|
| 1.  |  |  |  |  |  |  |  |
| 2.  |  |  |  |  |  |  |  |
| 3.  |  |  |  |  |  |  |  |
| 4.  |  |  |  |  |  |  |  |
| 5.  |  |  |  |  |  |  |  |

**Real output from one try**, pasted as text, naming the file and function
that produced it:

```

```

---

## Verdicts and Diagnoses

<!-- MET or MISSED per criterion against LAST UNIT's target, plus a sentence on
     how you decided.

     Then, for every miss: which of the four places it happened — a tool, the
     loop's branch, the session, or the model's output — AND the mechanism.

     Not a diagnosis:  "The fit card was bad."
     A diagnosis:      "The fit card criterion missed on 2 of 5 items. Both had
                        an empty brand field. My prompt puts the brand in the
                        first sentence, so the card opened with a blank and read
                        like a fragment. The tool worked; the prompt assumed a
                        field that isn't always there."

     Look for a pattern. Three misses on the same tool is one problem, not
     three. -->

| # | Criterion | Target | Verdict | How I decided |
|---|---|---|---|---|
| 1 |  |  |  |  |
| 2 |  |  |  |  |
| 3 |  |  |  |  |
| 4 |  |  |  |  |
| 5 |  |  |  |  |

**Diagnoses**



---

## Loop Trace

<!-- One full run, printed step by step, with the MCP call visible in it.

     `python app.py ask '...' --trace` once you've added the trace.step()
     calls in Milestone 2.

     Worth pasting BOTH the happy path and the empty-search path. The empty
     one should be visibly shorter, because it stops. If your two traces are
     the same length, your branch isn't working — and this is the fastest way
     anyone will ever find that out. -->

**Happy path**

```

```

**Empty search**

```

```

**On the MCP move:** <!-- what changed in your code, and whether anything
behaved differently afterwards. If the rewire didn't work, say exactly where it
broke — the error text and the last thing that worked. That earns the point in
full. -->



---

## The Improvement

<!-- What you changed, why your diagnosis pointed at it, and the after-run in
     the same table format. One change, measured properly.

     `python run_eval.py --label after` -->

**What I changed:**

**Which failure it was meant to fix:**

### Run Log — After

| Criterion | Target | Try 1 | Try 2 | Try 3 | Try 4 | Try 5 | Verdict |
|---|---|---|---|---|---|---|---|
| 1.  |  |  |  |  |  |  |  |
| 2.  |  |  |  |  |  |  |  |
| 3.  |  |  |  |  |  |  |  |
| 4.  |  |  |  |  |  |  |  |
| 5.  |  |  |  |  |  |  |  |

**Did it help, and how do I know:**

<!-- If it made things worse, say that. Honestly reported, that earns full
     credit and is more interesting than one that worked. -->



---

## What's Still Broken

<!-- For each criterion still missed: what you'd do, and why you stopped where
     you did. "I ran out of time" is fine if it's true. Pretending nothing is
     left is not. -->



<!-- ═════════════════════════════════════════════════════════════════════

     SUBMISSION CHECKLIST — unit 3

       [ ] criteria.md has five numbered criteria, each with a target
       [ ] Each criterion has a reason underneath it
       [ ] All five unit 3 sections above have real content
       [ ] Tool Inventory: all three tools, inputs WITH TYPES, a specific
           return value, and the empty case
       [ ] Planning Loop names the branch rule and agent.py::run_agent
       [ ] Sample Run: one full query plus the three per-tool tests, as text
       [ ] At least four new commits
       [ ] Repository URL submitted — WRITE IT DOWN, you submit the same one
           next unit

     SUBMISSION CHECKLIST — unit 4

       [ ] mcp_server.py exists with one tool registered
           (or a written record of exactly where the rewire broke)
       [ ] Run Log — Before, five criteria, five tries each
       [ ] Real output pasted underneath, naming file and function
       [ ] A verdict on every criterion
       [ ] A diagnosis for every miss, naming a place AND a mechanism
       [ ] Loop Trace, with the MCP call visible in it
       [ ] All three failure modes triggered and handled
       [ ] One improvement, with Run Log — After in the same format
       [ ] What's Still Broken
       [ ] At least four new commits
       [ ] The SAME repository URL as last unit

     Do not delete and recreate this repository. Your commit history is what
     shows your criteria existed before your results did.
     ═════════════════════════════════════════════════════════════════════ -->

---

📖 **How to run this project: [RUNNING.md](RUNNING.md)**
