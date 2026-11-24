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
- *What came back:* Regex and string splitting pull the price out with a
  `$` regex, match size words against a lookup table, treat whatever words
  are left (minus fillers like "find", "me", "under") as the description.
- *What changed:* The first version checked size words in plain dict order,
  so a query like "extra large tee" matched "large" first, cut just that
  out, and left `size: "large"` instead of `"extra large"`. I changed
  `_SIZE_WORDS` to be checked longest word first
  (`sorted(_SIZE_WORDS, key=len, reverse=True)` in `parse_query` in
  `agent.py`), so "extra large" gets matched and removed before "large" can
  grab a piece of it.

<!-- ═══════════════════════ UNIT 4 — THE TEST ═══════════════════════

     Don't fill these in during unit 3.
     ═══════════════════════════════════════════════════════════════════ -->

---

## Run Log — Before

| Criterion | Target | Try 1 | Try 2 | Try 3 | Try 4 | Try 5 | Verdict |
|---|---|---|---|---|---|---|---|
| 1. A matching query completes all three tools | 4 of 5 | PASS | PASS | PASS | PASS | PASS | MET (5/5) |
| 2. An impossible query stops before the second tool | 5 of 5 | PASS | PASS | PASS | PASS | PASS | MET (5/5) |
| 3. The same item reaches every tool | 5 of 5 | PASS | PASS | PASS | PASS | PASS | MET (5/5) |
| 4. The fit card mentions the price and the style | 4 of 5 | FAIL | PASS | FAIL | PASS | PASS | MISSED (3/5) |
| 5. Results respect the price ceiling | 5 of 5 | PASS | PASS | PASS | PASS | PASS | MET (5/5) |

**Real output, one try per criterion**, from `agent.py::run_agent` via `run_eval.py::run_once`:

**Criterion 1 — Try 1** (query: `vintage graphic tee under $30`, example wardrobe)

```
selected_item: Y2K Baby Tee — Butterfly Print ($18.0, depop)
search_results: 10

Fit card:
Scored this little butterfly tee on Depop for $18 and I'm obsessed. Runs a little small, but it's the exact 2000s fit I wanted. Going to lean into the Bratz energy today with baggy dark denim and an unzipped hoodie, but tomorrow I'm definitely pairing it with my wide-leg khakis.

Trace:
[1] search_listings (via MCP)  → 10 items
[2] compare_price               → dict with keys: average_price, this_price, compared_against, verdict
[3] suggest_outfit              → two outfit ideas
[4] create_fit_card             → fit card above
```

**Criterion 2 — Try 1** (query: `designer ballgown size XXS under $5`, example wardrobe)

```
stopped early: yes — No listings matched 'designer ballgown xxs', under $5. Try a broader description, a different size, or a higher price limit.
selected_item: (none)
search_results: 0

Trace:
[1] search_listings (via MCP)
      out: [] (empty)
[2] branch: search_results
      →    empty — stopping before suggest_outfit. No listings matched 'designer ballgown xxs', under $5. Try a broader description, a different size, or a higher price limit.
```

**Criterion 3 — Try 1** (query: `90s track jacket in size M`, example wardrobe)

```
selected_item: 90s Track Jacket — Navy/White Stripe ($45.0, poshmark)
search_results: 9

Fit card:
Snagged this authentic 90s navy track jacket on Poshmark for $45 and I'm obsessed. I've been living for the half-zip look over a white tank and baggy dark wash jeans for easy off-duty days, but it also looks so good layered over a grey crewneck with khaki trousers. Total vintage score.
```

In `agent.py::run_agent`, `selected = results[0]` is assigned to `session["selected_item"]`
and that exact same `selected` object is the second argument to
`create_fit_card(session["outfit_suggestion"], selected)` — same Python
object, not a copy, so the id passed to `create_fit_card` and the id in
`session["selected_item"]` can never diverge. All 5 tries completed with a
non-null `selected_item` and a fit card, confirming no exception or edge
case broke that invariant.

**Criterion 4 — Try 1** (query: `vintage graphic tee under $30`, example wardrobe) — a MISS

```
selected_item: Y2K Baby Tee — Butterfly Print ($18.0, depop)
style_tags: ['y2k', 'vintage', 'graphic tee', 'cottagecore']

Fit card:
Scored this little butterfly baby tee on Depop for just $18 and I am obsessed. It runs a bit small, but it's the ultimate fitted crop. I'm leaning into total Bratz doll energy today with baggy dark-wash jeans and a zip hoodie, but honestly, it looks just as good dressed down with khaki trousers.
```

The price ($18) is there, but none of `y2k`, `vintage`, `graphic tee`, or
`cottagecore` appear anywhere in the card "Bratz doll energy" describes a
vibe, not the item's actual style tags. Try 3 missed the same way. Full
diagnosis under Verdicts and Diagnoses below.

**Criterion 5 — Try 1** (query: `denim jacket under $50`, example wardrobe)

```
search_results (6 items, all with price in parentheses):
  Denim Jacket — Light Wash, Cropped ($42.0)
  Vintage Levi's 501 Jeans — Medium Wash ($38.0)
  90s Track Jacket — Navy/White Stripe ($45.0)
  High-Waisted Denim Shorts — Cutoff ($24.0)
  Straight Leg Black Jeans — Faded ($30.0)
  Denim Vest — Medium Wash, Studded ($27.0)
```

All 6 are at or under $50. Verified against `tools.py::search_listings`,
where the filter is `if max_price is not None and listing["price"] > max_price: continue`
— a strict greater-than comparison, so the ceiling is inclusive, exactly as
documented. The same 6 items, in the same order, appeared in every one of
the 5 tries expected, since `search_listings` doesn't call the model and
has nothing to vary between runs.

---

## Verdicts and Diagnoses

| # | Criterion | Target | Verdict | How I decided |
|---|---|---|---|---|
| 1 | A matching query completes all three tools | 4 of 5 | **MET (5/5)** | All 5 tries had `session["error"]` unset and a non-empty `fit_card`. 5 ≥ 4, so the target holds comfortably. |
| 2 | An impossible query stops before the second tool | 5 of 5 | **MET (5/5)** | All 5 tries had `search_results == []`, `session["error"]` set, and the trace shows only `search_listings` and the branch step — `suggest_outfit` never appears. 5 of 5. |
| 3 | The same item reaches every tool | 5 of 5 | **MET (5/5)** | `agent.py::run_agent` assigns `selected = results[0]` once, stores it as `session["selected_item"]`, and passes that same object into `create_fit_card(session["outfit_suggestion"], selected)`. Same Python object, not a copy — the two ids can't diverge by construction. All 5 tries completed with a non-null `selected_item`, confirming nothing broke that invariant. |
| 4 | The fit card mentions the price and the style | 4 of 5 | **MISSED (3/5)** | Checked each of the 5 fit cards against the item's real `style_tags` (`y2k`, `vintage`, `graphic tee`, `cottagecore`). Price was mentioned in all 5. The style tag was mentioned in only 3 of 5 — the other 2 described a vibe ("Bratz doll energy", "grunge it up") instead of using an actual tag word. 3 < 4, so this misses the target. |
| 5 | Results respect the price ceiling | 5 of 5 | **MET (5/5)** | All 6 results from the `denim jacket under $50` scenario — $42, $38, $45, $24, $30, $27 — are at or under $50, in every one of the 5 tries (deterministic, no model involved, so no variance was expected). |

**Diagnoses**

**Criterion 4 missed — model output, not a tool bug.** `create_fit_card`'s prompt (in `tools.py`) tells the model: "Mention the price and platform naturally, and reference the styling idea" — it never asks the model to use the item's actual `style_tags`. The model only sees the item's `title` and `description` plus whatever `suggest_outfit` generated, so it reaches for a vibe word of its own ("Bratz doll energy," "grunge it up") rather than the literal tag words (`y2k`, `vintage`, `graphic tee`, `cottagecore`) it was never told to use. `search_listings`, `compare_price`, and the branch logic all worked correctly on every try — the gap is specifically in what the `create_fit_card` prompt asks for, which is exactly the kind of thing criteria.md predicted for this criterion: "depends on the model's phrasing rather than just code logic."

**No pattern across tools.** This is the only miss, and it's isolated to one tool's prompt, not spread across multiple tools or the loop's branching — so there's one fix to make here, not several. Everything deterministic (the branch, the price filter, the object identity between `selected_item` and `create_fit_card`) passed 5/5 every time, as criteria.md predicted it should.

---

## Loop Trace

**Happy path**

```
$ python app.py ask 'vintage graphic tee under $30' --trace
[1] search_listings (via MCP)
      in:  dict with keys: description, size, max_price
      out: 10 items: Y2K Baby Tee — Butterfly Print, Graphic Tee — 2003 Tour Bootleg Style, Vintage Band Tee — Faded Grey … +7 more
[2] compare_price
      in:  dict with keys: item
      out: dict with keys: average_price, this_price, compared_against, verdict
[3] suggest_outfit
      in:  dict with keys: item, wardrobe_items
      out: Here are two specific ways to style your new Y2K butterfly baby tee using pieces you already own:  **Outfit 1:…
[4] create_fit_card
      in:  dict with keys: outfit, item
      out: Scored this little butterfly tee on Depop for just $18 and I'm obsessed. Squeezed into the medium (definitely…

  Found:    Y2K Baby Tee — Butterfly Print — $18.0 on depop

  Outfit:   Here are two specific ways to style your new Y2K butterfly baby tee using pieces you already own:

**Outfit 1: Bratz Doll Streetwear**
*   **Top:** Y2K Butterfly Baby Tee
*   **Bottoms:** Baggy straight-leg jeans (dark wash)
*   **Outerwear:** Black cropped zip hoodie (wear it unzipped or slung off the shoulders)
*   **Shoes:** Chunky white sneakers
*   **Bag:** Black crossbody bag
*   *Why it works:* The fitted crop of the baby tee balances out the baggy, low-slung look of the dark wash jeans. Layering the cropped zip hoodie on top keeps the Y2K silhouette going, and the chunky sneakers tie the whole streetwear vibe together.

**Outfit 2: Soft Contrast Grunge**
*   **Top:** Y2K Butterfly Baby Tee
*   **Bottoms:** Wide-leg khaki trousers
*   **Outerwear:** Vintage black denim jacket
*   **Shoes:** Black combat boots
*   **Accessories:** Brown leather belt
*   *Why it works:* This plays with the mix of cottagecore and Y2K by adding some edge. Tuck the baby tee into the khaki trousers and cinch them with the brown leather belt. Throwing the black denim jacket and combat boots on gives the sweet butterfly graphic a cool, grunge-inspired contrast.

  Fit card: Scored this little butterfly tee on Depop for just $18 and I'm obsessed. Squeezed into the medium (definitely runs like a small), but it's worth it. Today I'm leaning all the way into the Bratz doll aesthetic with dark baggy denim and my chunkiest sneakers.

2 model calls this session, 774 prompt + 356 output tokens
```

**Empty search**

```
$ python app.py ask 'designer ballgown size XXS under $5'
[1] search_listings (via MCP)
      in:  dict with keys: description, size, max_price
      out: [] (empty)
[2] branch: search_results
      →    empty — stopping before suggest_outfit. No listings matched 'designer ballgown xxs', under $5. Try a broader description, a different size, or a higher price limit.

  No listings matched 'designer ballgown xxs', under $5. Try a broader description, a different size, or a higher price limit.

0 model calls this session
```

The empty-search trace is 2 steps against the happy path's 4 — the branch stops before `suggest_outfit` and `create_fit_card` ever run, exactly as the Planning Loop branch rule says it should.

**Failure modes triggered (Milestone 2)**

- **Empty search** — `python app.py ask 'designer ballgown size XXS under $5'`. Trace above. Stops at step 2 with a message naming what to change (broader description, different size, higher price).
- **Empty wardrobe** — `python app.py ask 'denim jacket under $50' --empty-wardrobe`. `suggest_outfit` still returned two full outfit ideas built from "basic staples you probably already have," not a crash and not an empty string — the `if not items:` branch in `tools.py` already handled this correctly from Unit 3.
- **Model unavailable** — broke one character of `GEMINI_API_KEY` in `.env`, then ran a fresh query (`python app.py ask 'platform sneakers size 8'`):
  ```
  [3] model call
        →    ModelUnavailable — stopping. The model rejected your API key. Check GEMINI_API_KEY in your .env file, or create a fresh key at aistudio.google.com.

    The model rejected your API key. Check GEMINI_API_KEY in your .env file, or create a fresh key at aistudio.google.com.

  1 model calls this session
  ```
  Before this unit, that exception had no handler in `run_agent()` — it would propagate up and get caught generically by `app.py`'s top-level handler, printing the raw exception with no guidance. Now `run_agent()` catches `ModelUnavailable` directly (`agent.py`, around the `suggest_outfit`/`create_fit_card` calls), sets `session["error"]` to the message `generate.py` already builds, and stops cleanly — same shape as the empty-search branch. Key restored afterward.

**On the MCP move:** `search_listings` is registered in `mcp_server.py` with a full
description (units, types, empty case) and typed inputs matching the Tool
Inventory. `run_agent()` in `agent.py` now calls it via
`mcp_client.call_tool("search_listings", {...})` instead of importing and
calling the function directly. Verified with `python mcp_client.py` (the tool
lists correctly) and with full queries end to end — the return shape didn't
change: still a list of listing dicts, best match first, empty list when
nothing matches. The only visible difference is a small added latency, since
`call_tool` starts a fresh server subprocess over stdio for every call rather
than holding one open — noticeable but not disruptive for a single-query CLI.



---

## The Improvement

<!-- What you changed, why your diagnosis pointed at it, and the after-run in
     the same table format. One change, measured properly.

     `python run_eval.py --label after` -->

**What I changed:** Rewrote `create_fit_card`'s prompt in `tools.py`. Two
things: (1) `item_description` now includes the item's actual `style_tags`
(`style: y2k, vintage, graphic tee, cottagecore`) — before, the model never
even saw them, only `title`/`description`/`price`/`platform`. (2) Added an
explicit instruction, `style_instruction`, telling the model to "work in one
of these exact style words, naturally." Nothing else in `create_fit_card`,
`suggest_outfit`, `search_listings`, or the loop changed.

**Which failure it was meant to fix:** Criterion 4 — "the fit card mentions
the price and the style" — missed 3/5 in the before-run. The diagnosis
(Verdicts and Diagnoses, above) found the misses weren't random: the model
reached for its own vibe words ("Bratz doll energy") instead of a real style
tag, because the prompt never gave it the tags or asked for one. This change
targets exactly that gap.

### Run Log — After

| Criterion | Target | Try 1 | Try 2 | Try 3 | Try 4 | Try 5 | Verdict |
|---|---|---|---|---|---|---|---|
| 1. A matching query completes all three tools | 4 of 5 | PASS | PASS | PASS | PASS | PASS | MET (5/5) |
| 2. An impossible query stops before the second tool | 5 of 5 | PASS | PASS | PASS | PASS | PASS | MET (5/5) |
| 3. The same item reaches every tool | 5 of 5 | PASS | PASS | PASS | PASS | PASS | MET (5/5) |
| 4. The fit card mentions the price and the style | 4 of 5 | PASS | PASS | PASS | PASS | PASS | MET (5/5) |
| 5. Results respect the price ceiling | 5 of 5 | PASS | PASS | PASS | PASS | PASS | MET (5/5) |

**Criterion 4 — Try 1** (query: `vintage graphic tee under $30`, example wardrobe) — now a PASS

```
selected_item: Y2K Baby Tee — Butterfly Print ($18.0, depop)
style_tags: ['y2k', 'vintage', 'graphic tee', 'cottagecore']

Fit card:
Scored this sweet little y2k butterfly baby tee on Depop for just 18 bucks. It runs a bit small, but it's the ultimate cropped fit. I've been living in it with my baggy jeans and a zip hoodie, but I'm dying to try it with wide-leg trousers and combat boots next.
```

Compare that to the same scenario's before-run Try 1, which produced "Bratz doll energy" instead of a real tag — this try (and all 5 in this run) names an actual `style_tags` word (`y2k`) directly, plus the price. I checked all 5 after-run fit cards against the item's real `style_tags` the same way I checked the before-run ones: every one of the 5 now says `y2k` explicitly (one also adds `graphic tee`), and every one mentions the price. 5/5, up from 3/5.

Criteria 1, 2, 3, and 5 didn't move — their logic (the branch, the price filter, the `selected_item` object identity) lives in code the fix never touched, and the after-run confirms that: same 5/5 results as the before-run, just re-verified on a fresh run.

**Did it help, and how do I know:** Yes. Criterion 4 went from MISSED (3/5) to MET (5/5), and I know because I read all 5 after-run fit cards against the item's actual `style_tags` the same way I diagnosed the miss — not by assuming the prompt change worked. Nothing regressed: criteria 1, 2, 3, and 5 are still 5/5, which is expected since the fix only changed `create_fit_card`'s prompt and nothing in `search_listings`, the branch logic, or the `selected_item` plumbing.

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

---

## Capstone

**What This Extends**

FitFindr (Project 2), the thrift-shopping agent that searches listings over MCP, compares the price, suggests an outfit and writes a fit card. Right now, FitFindr assumes every query is a clothing request. A fully off-topic query like "tell me a joke" falls into the empty-search branch and is told to "try a broader description", which is the wrong advice. Worse, an off-topic query that shares one word with a listing, like "vintage car under $30" (*vintage*) or "recommend a black coffee" (*black*), goes all the way through: `search_listings` counts a single shared word as a match, so FitFindr picks a tee or a pair of shoes and spends 2 model calls writing a fit card nobody asked for. After this unit, a check against a clothing word list runs before search. Queries with no clothing word are rejected with a message that says FitFindr helps with clothing and gives an example query, with no model or search calls.

**The Shape**

Shape B: Harden against failure. An off-topic query is bad input that FitFindr currently doesn't survive: it either gives the user the wrong message or quietly produces a confident, irrelevant result. The extension is the check that catches that bad input before it reaches the tools.

Out of scope, considered and decided against:
- I'm not using the model to classify queries. It would handle cases a word list misses, but it would spend a model call on every query, including the ones it rejects.
- I'm not changing how `search_listings` scores matches. Requiring more shared words would be a different fix, and it would change results for real clothing queries too.
- I'm not hosting it. It runs locally with a committed log (Path B).

**Running It**

Path B: local with logs. One command starts it (`python app.py ask '...'`), and every run appends a structured record to `logs/runs.jsonl`. The steps from a clean checkout, what the environment needs, and how to read the log are in [RUNNING.md](RUNNING.md).


**Instrumentation**

Every call to `agent.py::run_agent` writes one JSON record to `logs/runs.jsonl` (or the file named in `FITFINDR_LOG`) through `runlog.py::write`. `run_agent` wraps the planning loop (`_run_agent`) and writes the record in a `finally`, so rejected, failed and crashed runs are logged too. `python runlog.py` prints the last 10.

| Field | What it holds |
|---|---|
| `ts` | UTC timestamp, milliseconds |
| `query` | what came in, as typed |
| `outcome` | `ok`, `off_topic`, `no_results`, `model_unavailable` or `crashed` |
| `error` | the message the user saw, or the exception for a crash |
| `search_called` | whether `search_listings` ran (criteria 1–3) |
| `results_count`, `selected_item` | what search found and what was picked |
| `fit_card`, `fit_card_chars` | what came out, and its length (criterion 5) |
| `model_calls`, `prompt_tokens`, `output_tokens` | what the run spent, from `generate.py`'s own counters |
| `duration_ms` | end-to-end time for the run |

All 20 records from trial 2 of the before run (`logs/capstone_before_trial2.jsonl`). They include rejected runs (`off_topic`), an empty search (`no_results`), and failed runs (`model_unavailable`, Gemini 503). `fit_card` and long `error` text are shortened here to fit; the committed file has them in full.

```
{"ts": "2026-11-24T19:29:59.322+00:00", "query": "give me a plaid skirt styling ideas", "outcome": "ok", "error": null, "search_called": true, "results_count": 2, "selected_item": "Oversized Flannel Shirt — Plaid Red/Black", "fit_card": "Scored this vintage red and black flannel on thredUp for just $22 and …", "fit_card_chars": 264, "model_calls": 2, "prompt_tokens": 794, "output_tokens": 352, "duration_ms": 3037}
{"ts": "2026-11-24T19:29:59.712+00:00", "query": "blue sweater", "outcome": "no_results", "error": "No listings matched 'blue sweater'. Try a broader description, a different size, or a higher price limit.", "search_called": true, "results_count": 0, "selected_item": null, "fit_card": null, "fit_card_chars": 0, "model_calls": 0, "prompt_tokens": 0, "output_tokens": 0, "duration_ms": 388}
{"ts": "2026-11-24T19:30:02.704+00:00", "query": "how to style black denim jeans", "outcome": "ok", "error": null, "search_called": true, "results_count": 10, "selected_item": "Straight Leg Black Jeans — Faded", "fit_card": "Scored these perfectly faded black straight-leg jeans on thredUp for j…", "fit_card_chars": 327, "model_calls": 2, "prompt_tokens": 758, "output_tokens": 335, "duration_ms": 2992}
{"ts": "2026-11-24T19:30:04.135+00:00", "query": "brown suede jacket", "outcome": "model_unavailable", "error": "Couldn't reach the model: 503 UNAVAILABLE. {'error': {'code': 503, 'message': 'This model is currently experiencing high…", "search_called": true, "results_count": 6, "selected_item": "90s Track Jacket — Navy/White Stripe", "fit_card": null, "fit_card_chars": 0, "model_calls": 1, "prompt_tokens": 0, "output_tokens": 0, "duration_ms": 1430}
{"ts": "2026-11-24T19:30:06.387+00:00", "query": "coffee colored shirt", "outcome": "model_unavailable", "error": "Couldn't reach the model: 503 UNAVAILABLE. {'error': {'code': 503, 'message': 'This model is currently experiencing high…", "search_called": true, "results_count": 2, "selected_item": "Oversized Flannel Shirt — Plaid Red/Black", "fit_card": null, "fit_card_chars": 0, "model_calls": 1, "prompt_tokens": 0, "output_tokens": 0, "duration_ms": 2251}
{"ts": "2026-11-24T19:30:12.330+00:00", "query": "linen shirts for summer or winter?", "outcome": "model_unavailable", "error": "Couldn't reach the model: 503 UNAVAILABLE. {'error': {'code': 503, 'message': 'This model is currently experiencing high…", "search_called": true, "results_count": 10, "selected_item": "Vintage Linen Blazer — Cream", "fit_card": null, "fit_card_chars": 0, "model_calls": 1, "prompt_tokens": 0, "output_tokens": 0, "duration_ms": 5941}
{"ts": "2026-11-24T19:30:14.479+00:00", "query": "floral dresses styling ideas", "outcome": "model_unavailable", "error": "Couldn't reach the model: 503 UNAVAILABLE. {'error': {'code': 503, 'message': 'This model is currently experiencing high…", "search_called": true, "results_count": 1, "selected_item": "90s Silk Slip Dress — Floral, Midi Length", "fit_card": null, "fit_card_chars": 0, "model_calls": 1, "prompt_tokens": 0, "output_tokens": 0, "duration_ms": 2148}
{"ts": "2026-11-24T19:30:14.480+00:00", "query": "something to wear for an Indian wedding", "outcome": "off_topic", "error": "FitFindr only helps find secondhand clothing, and I couldn't find a clothing item in that. Try naming the piece you want…", "search_called": false, "results_count": 0, "selected_item": null, "fit_card": null, "fit_card_chars": 0, "model_calls": 0, "prompt_tokens": 0, "output_tokens": 0, "duration_ms": 0}
{"ts": "2026-11-24T19:30:16.322+00:00", "query": "light washed denim jean with boot cut", "outcome": "model_unavailable", "error": "Couldn't reach the model: 503 UNAVAILABLE. {'error': {'code': 503, 'message': 'This model is currently experiencing high…", "search_called": true, "results_count": 10, "selected_item": "Vintage Levi's 501 Jeans — Medium Wash", "fit_card": null, "fit_card_chars": 0, "model_calls": 1, "prompt_tokens": 0, "output_tokens": 0, "duration_ms": 1841}
{"ts": "2026-11-24T19:30:28.097+00:00", "query": "bandana colors that go with a light colored t shirt", "outcome": "model_unavailable", "error": "Couldn't reach the model: 503 UNAVAILABLE. {'error': {'code': 503, 'message': 'This model is currently experiencing high…", "search_called": true, "results_count": 7, "selected_item": "Vintage Polo Shirt — Forest Green", "fit_card": null, "fit_card_chars": 0, "model_calls": 1, "prompt_tokens": 0, "output_tokens": 0, "duration_ms": 11775}
{"ts": "2026-11-24T19:30:28.098+00:00", "query": "tell me a joke", "outcome": "off_topic", "error": "FitFindr only helps find secondhand clothing, and I couldn't find a clothing item in that. Try naming the piece you want…", "search_called": false, "results_count": 0, "selected_item": null, "fit_card": null, "fit_card_chars": 0, "model_calls": 0, "prompt_tokens": 0, "output_tokens": 0, "duration_ms": 0}
{"ts": "2026-11-24T19:30:28.099+00:00", "query": "cranberry cookies recipe", "outcome": "off_topic", "error": "FitFindr only helps find secondhand clothing, and I couldn't find a clothing item in that. Try naming the piece you want…", "search_called": false, "results_count": 0, "selected_item": null, "fit_card": null, "fit_card_chars": 0, "model_calls": 0, "prompt_tokens": 0, "output_tokens": 0, "duration_ms": 0}
{"ts": "2026-11-24T19:30:28.099+00:00", "query": "can you give some recipe cards for high protein meals?", "outcome": "off_topic", "error": "FitFindr only helps find secondhand clothing, and I couldn't find a clothing item in that. Try naming the piece you want…", "search_called": false, "results_count": 0, "selected_item": null, "fit_card": null, "fit_card_chars": 0, "model_calls": 0, "prompt_tokens": 0, "output_tokens": 0, "duration_ms": 0}
{"ts": "2026-11-24T19:30:28.100+00:00", "query": "give me ideas to decorate my laptop.", "outcome": "off_topic", "error": "FitFindr only helps find secondhand clothing, and I couldn't find a clothing item in that. Try naming the piece you want…", "search_called": false, "results_count": 0, "selected_item": null, "fit_card": null, "fit_card_chars": 0, "model_calls": 0, "prompt_tokens": 0, "output_tokens": 0, "duration_ms": 0}
{"ts": "2026-11-24T19:30:28.100+00:00", "query": "vintage car under $30", "outcome": "off_topic", "error": "FitFindr only helps find secondhand clothing, and I couldn't find a clothing item in that. Try naming the piece you want…", "search_called": false, "results_count": 0, "selected_item": null, "fit_card": null, "fit_card_chars": 0, "model_calls": 0, "prompt_tokens": 0, "output_tokens": 0, "duration_ms": 0}
{"ts": "2026-11-24T19:30:28.100+00:00", "query": "recommend a black coffee", "outcome": "off_topic", "error": "FitFindr only helps find secondhand clothing, and I couldn't find a clothing item in that. Try naming the piece you want…", "search_called": false, "results_count": 0, "selected_item": null, "fit_card": null, "fit_card_chars": 0, "model_calls": 0, "prompt_tokens": 0, "output_tokens": 0, "duration_ms": 0}
{"ts": "2026-11-24T19:30:28.101+00:00", "query": "Is the color of taj-mahal off white?", "outcome": "off_topic", "error": "FitFindr only helps find secondhand clothing, and I couldn't find a clothing item in that. Try naming the piece you want…", "search_called": false, "results_count": 0, "selected_item": null, "fit_card": null, "fit_card_chars": 0, "model_calls": 0, "prompt_tokens": 0, "output_tokens": 0, "duration_ms": 0}
{"ts": "2026-11-24T19:30:28.101+00:00", "query": "where to buy orange color snoopy coffee mug?", "outcome": "off_topic", "error": "FitFindr only helps find secondhand clothing, and I couldn't find a clothing item in that. Try naming the piece you want…", "search_called": false, "results_count": 0, "selected_item": null, "fit_card": null, "fit_card_chars": 0, "model_calls": 0, "prompt_tokens": 0, "output_tokens": 0, "duration_ms": 0}
{"ts": "2026-11-24T19:30:30.043+00:00", "query": "how do I wash a denim jacket", "outcome": "model_unavailable", "error": "Couldn't reach the model: 503 UNAVAILABLE. {'error': {'code': 503, 'message': 'This model is currently experiencing high…", "search_called": true, "results_count": 7, "selected_item": "Vintage Levi's 501 Jeans — Medium Wash", "fit_card": null, "fit_card_chars": 0, "model_calls": 1, "prompt_tokens": 0, "output_tokens": 0, "duration_ms": 1941}
{"ts": "2026-11-24T19:30:30.457+00:00", "query": "what's the history of the sneaker", "outcome": "no_results", "error": "No listings matched 'what history of sneaker', size s. Try a broader description, a different size, or a higher price li…", "search_called": true, "results_count": 0, "selected_item": null, "fit_card": null, "fit_card_chars": 0, "model_calls": 0, "prompt_tokens": 0, "output_tokens": 0, "duration_ms": 414}
```

A crashed run, from the after run (`logs/capstone_after_trial1.jsonl`), shortened:

```
{"query": "brown suede jacket", "outcome": "crashed", "error": "RuntimeError: Still rate limited after 5 attempts ... Last error: 503 UNAVAILABLE ...", "search_called": false, "results_count": 0, "model_calls": 5, "duration_ms": 39795}
```

**What It Costs**

Measured with `python run_capstone.py --cost`: the query "vintage graphic tee under $30" (example wardrobe), 10 times, cache off. Tokens come from `generate.py`'s counters, which add up the `usage_metadata` Gemini returns on each response. Raw records are in `logs/capstone_cost.jsonl` and the averages in `results/capstone_cost.json`.

Gemini was overloaded during the measurement: **6 of 10 runs succeeded**, and the other 4 got `503 UNAVAILABLE`. The averages are over the 6 that succeeded.

| Measure | Per successful run (average of 6) |
|---|---|
| Model calls | 2.0 (suggest_outfit + create_fit_card) |
| Tokens | 750.5 prompt + 293.3 output = **1,043.8 tokens** |
| Time | **8.0 s** average (2.9 s min, 22.1 s max) |

In money it cost $0, because it runs on the Gemini free tier. I didn't convert tokens to dollars because I didn't measure a paid bill.

A hundred people a day, one query each:
- Tokens: 1,043.8 × 100 = **104,380 tokens a day**
- Requests: 2 × 100 = **200 model requests a day**
- Time: 8.0 s × 100 = 800 s ≈ **13.4 minutes of run time a day**

The real limit is the rate, not the daily total: 15 requests a minute ÷ 2 per run ≈ 7 runs a minute. An off-topic query that's rejected costs 0 model calls and 0 search calls (criterion 3), so rejected queries don't eat into that.

**Run Log and Verdicts**

Five criteria from `criteria.md`, 20 labelled queries from `capstone_queries.py`, three trials (`python run_capstone.py --label before`, cache off). Scores are computed from the run logs by `run_capstone.py::score`. Every query's outcome per trial is in `results/capstone_before.md`.

| Criterion | Target | Run 1 | Run 2 | Run 3 | Verdict |
|---|---|---|---|---|---|
| 1. Off-topic queries are rejected | ≥ 8 of 10 | 8/10 | 8/10 | 8/10 | MET |
| 2. Real clothing queries get through | ≥ 9 of 10 | 9/10 | 9/10 | 9/10 | MET |
| 3. A rejection costs nothing (0 model, 0 search calls) | every rejection | 9/9 | 9/9 | 9/9 | MET |
| 4. Rejection message has 'clothing' + an example in quotes | every rejection | 9/9 | 9/9 | 9/9 | MET |
| 5. Normal path still ends with a fit card ≥ 150 chars | every passing query with results | 8/8 | 2/8 | 2/8 | MISSED |

Real output, from `logs/capstone_before_trial2.jsonl` (written by `runlog.py::write` from `agent.py::run_agent`):
- **Criterion 1**, "vintage car under $30": `"outcome": "off_topic", "search_called": false, "model_calls": 0`
- **Criterion 2**, "coffee colored shirt": `"search_called": true`. It passed the check even though it shares *coffee* with "recommend a black coffee", because it names *shirt*.
- **Criterion 3**, "tell me a joke": `"model_calls": 0, "search_called": false`
- **Criterion 4**, every rejection's `error`: "FitFindr only helps find secondhand clothing, and I couldn't find a clothing item in that. Try naming the piece you want, like 'vintage graphic tee under $30'."
- **Criterion 5**, "brown suede jacket": `"outcome": "model_unavailable", "error": "Couldn't reach the model: 503 UNAVAILABLE ... experiencing high demand ..."`

Criteria 1 and 2 came out exactly where I set them when I wrote the criteria. "something to wear for an Indian wedding" was rejected because it has no clothing word, and "how do I wash a denim jacket" and "what's the history of the sneaker" got through because they do.

**Diagnosis of the miss, criterion 5 (8/8, 2/8, 2/8).** All 12 failures in trials 2 and 3 were `model_unavailable` with Gemini's 503 "high demand" error. None was a short or empty fit card: when the model answered, every card was 204–336 characters. The stage is the model call in `generate.py::generate()`. The mechanism is that `generate()` only retries errors it recognises as rate limits (429, "resource exhausted", "rate limit"). A 503 matches none of them, so it raises `ModelUnavailable` on the first try, even though Gemini's own message says the overload is usually temporary. The fit card criterion missed because of how one error type was handled, not because of the fit card.

**The Improvement**

What I changed: in `generate.py::generate()`, the `rate_limited` check now also matches "503" and "unavailable", so a 503 goes into the existing wait-and-retry loop (up to 5 attempts, with growing waits) instead of failing on the first try. It's two lines, aimed directly at the diagnosis above.

Run Log — After (`python run_capstone.py --label after`, same five criteria, same format; detail in `results/capstone_after.md`):

| Criterion | Target | Run 1 | Run 2 | Run 3 | Verdict |
|---|---|---|---|---|---|
| 1. Off-topic queries are rejected | ≥ 8 of 10 | 8/10 | 8/10 | 8/10 | MET |
| 2. Real clothing queries get through | ≥ 9 of 10 | 8/10 | 9/10 | 9/10 | MISSED |
| 3. A rejection costs nothing (0 model, 0 search calls) | every rejection | 9/9 | 9/9 | 9/9 | MET |
| 4. Rejection message has 'clothing' + an example in quotes | every rejection | 9/9 | 9/9 | 9/9 | MET |
| 5. Normal path still ends with a fit card ≥ 150 chars | every passing query with results | 7/7 | 8/8 | 8/8 | MET |

Did it help? For what it targeted, yes. Fit cards for queries that passed the check and found results went from **12 of 24** before (8 + 2 + 2) to **23 of 24** after. Criterion 5 now shows MET.

But it made something else worse, and criterion 2 caught it. In trial 1, "brown suede jacket" hit a 503 five times in a row. After the fifth try, `generate.py` gives up by raising a `RuntimeError` ("Still rate limited after 5 attempts"), and `run_agent` only catches `ModelUnavailable`, so the run **crashed** after 39.8 s. Before my change the same 503 failed cleanly in about a second.

The crash also exposed a logging bug. When a run crashes, `_run_agent` never returns its session, so the log wrapper wrote `"search_called": false` for a query that *did* reach search. My scorer reads only the log, so it counted "brown suede jacket" as rejected by the off-topic check, and criterion 2 dropped to 8/10 in trial 1. The off-topic check didn't fail; the log misreported a crash. The same artifact means trial 1's criterion 5 cell (7/7) left the crashed query out. The honest count is **7/8**, so criterion 5 isn't fully met after the change either.

The trade, named:
- **Better:** 23 of 24 passing runs now produce a fit card, instead of 12 of 24.
- **Worse:** a run whose retries all fail now crashes after up to about 40 s instead of failing cleanly in about 1 s, and retries raised the average model calls per successful run from 2.0 to 2.6–4.2.

**What's Still Broken**

- **Criterion 2 (missed after the improvement), the crash on exhausted retries.** What I'd do: catch the `RuntimeError` from `generate.py` in `run_agent` alongside `ModelUnavailable`, and have the log wrapper keep the partial session on a crash so `search_called` is recorded truthfully. Why I stopped: the brief asks for one improvement, and fixing this would be a second change needing its own re-run.
- **Criterion 1 (met at 8/10), clothing words in non-shopping questions.** "how do I wash a denim jacket" passes the check every time and, after the retry fix, gets a full fit card for a laundry question every time. A word list can't tell a clothing *question* from a clothing *request*. Fixing that needs something that understands intent, like a model classifier, which I scoped out because it costs a call on every query.
- **Criterion 2 (met at 9/10 before), clothing requests with no clothing word.** "something to wear for an Indian wedding" is rejected in every trial. Adding *wear* and *outfit* would let it through, but would also let through things like "what to wear to an interview: tips?", which is the same problem as above.
- **Things the log showed that my test set didn't cover:**
  - "blue sweater" finds nothing because the listings have a sweatshirt but no sweater.
  - "give me a plaid skirt styling ideas" picks a plaid *flannel shirt*, because search matches *plaid*, not *skirt*.
  - The word list also accepts "jane" (for Mary Janes), "tank" and "flat", so "a Jane Austen novel" or "fish tank" would pass.
- **Targets:** criteria 1 and 2 landed exactly on their targets, so they weren't set low. Criterion 5's 150-character bar was loose: the shortest real card in both runs was 204 characters, so I'd tighten it to 200.

**What I'd do next:** the first thing would be to fix the crash path, by catching the exhausted-retry error in `run_agent` and logging the partial session. Right now a Gemini overload can still crash a run, and the log misreports it as an off-topic rejection, which makes every other number harder to trust.

**How I Used AI**

I used Claude throughout this unit. I made the decisions: the system, the shape, the labelled test set, and the criteria's targets and reasons. Claude helped me sharpen the criteria wording and wrote most of the code (the word list check, the run log, the test runner) and the first drafts of these README sections, which I reviewed and edited. The one code change I made myself was the 503 retry in Moment 2.

**Moment 1**

- *What I asked for:* My new run log showed that "designer ballgown size XXS under $5", the course's own no-results example, was being rejected as off-topic. My word list had *gown* but not *ballgown*. I asked to fix it before running any tests.
- *What came back:* Two options. (A) Add *ballgown* and other compound words to `_CLOTHING_WORDS` explicitly. (B) Match word *endings*, so any word ending in a clothing word counts, which would also catch *sweatpants* and *overshirt* automatically.
- *What I changed:* I went with option A. Before choosing, we ran option B against my labelled test set, and it would have let "give me ideas to decorate my laptop" through (*lap**top*** ends in *top*), and almost any question through, because *what* and *that* end in *hat*. That would have made criterion 1 worse to fix one query outside my test set. The compound words are now listed whole at the end of `_CLOTHING_WORDS` in `agent.py`, with a comment explaining why ending-matching was rejected, and the test set still scored the same (17 of 20) afterwards.

**Moment 2**

- *What I asked for:* My before run missed criterion 5 (8/8, 2/8, 2/8), and every failure in the log was Gemini's `503 UNAVAILABLE` "high demand" error. At first I guessed the failing stage was MCP. I asked for an explanation of where the failure actually was and why it wasn't being retried.
- *What came back:* The trace showed `search_listings (via MCP)` succeeding with 10 items, and the failure happening at the model call after it. The explanation walked through the `except` block in `generate.py::generate()`: the `rate_limited` check only matches "429", "resource exhausted" and "rate limit", so a 503 skips the retry loop and raises `ModelUnavailable` on the first try, even though Gemini says the overload is temporary.
- *What I changed:* I added two lines to the `rate_limited` check myself, `or "503" in message` and `or "unavailable" in message`, so a 503 goes into the existing wait-and-retry loop. Fit cards went from 12 of 24 to 23 of 24. The after run then showed the trade-off I hadn't predicted: when all 5 retries fail, `generate.py` raises a `RuntimeError` that `run_agent` doesn't catch, so "brown suede jacket" crashed, and the crash made the log record `search_called: false`. I reported that as a criterion 2 miss caused by my own improvement, instead of re-running until it passed.
