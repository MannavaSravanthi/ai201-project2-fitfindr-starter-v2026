"""
The FitFindr planning loop.

This is the file that makes FitFindr an agent rather than a script. It decides
which tool to run next based on what the last one returned.

If your loop calls all three tools no matter what comes back, you have a list
of function calls. A loop looks at the last result before it picks the next
step. **That branch is the graded part of this unit.**

Build and test your three tools in `tools.py` first. Then come here.

    python agent.py          runs both example paths below
"""

import config
import trace
import re
from tools import suggest_outfit, create_fit_card, compare_price
from mcp_client import call_tool  # search_listings now goes through MCP — unit 4, Milestone 1
from generate import ModelUnavailable


# ── session state ─────────────────────────────────────────────────────────────

def new_session(query: str, wardrobe: dict) -> dict:
    """
    A fresh session for one user interaction.

    The session is the single source of truth for a run. Every tool result goes
    in here, and the next tool reads it back out.

    You could pass values straight from one call to the next. It would work,
    and you would not be able to test it — you can't print a variable you have
    already overwritten. Going through the session is what makes the state
    visible, and unit 4 has you write a criterion about exactly that.

    Add fields if you need them.
    """
    return {
        "query": query,              # what the user typed
        "parsed": {},                # description / size / max_price you pulled out of it
        "search_results": [],        # everything search_listings returned
        "selected_item": None,       # the one you chose — goes into suggest_outfit
        "wardrobe": wardrobe,        # the user's wardrobe
        "outfit_suggestion": None,   # what suggest_outfit returned
        "fit_card": None,            # what create_fit_card returned
        "price_comparison": None,    # what compare_price returned
        "error": None,               # set when the run ended early
    }


# ── planning loop ─────────────────────────────────────────────────────────────

_SIZE_WORDS = {
    "small": "small", "s": "small",
    "medium": "medium", "m": "medium",
    "large": "large", "l": "large",
    "extra large": "extra large", "xl": "extra large",
    "xxl": "xxl",
}

_FILLER_WORDS = {
    "find", "me", "a", "an", "the", "for", "under", "size", "sized",
    "and", "give", "ideas", "to", "style", "it", "looking", "with",
    "please", "want", "show",
}


# ── capstone: off-topic check ─────────────────────────────────────────────────
#
# A query has to name a clothing item to reach search. Only ITEM words are in
# here — never colours (black), styles (vintage) or fabrics (denim, linen),
# because those are exactly the words that let "recommend a black coffee" and
# "vintage car under $30" match a listing by accident.
#
# Built from the five categories in data/listings.json (tops, bottoms,
# outerwear, shoes, accessories) plus common items the data doesn't have yet.

_CLOTHING_WORDS = {
    # tops
    "tee", "shirt", "top", "blouse", "sweater", "sweatshirt", "hoodie",
    "cardigan", "crewneck", "henley", "polo", "tank", "camisole", "vest",
    "jersey", "kurta",
    # bottoms
    "jeans", "jean", "pants", "pant", "trousers", "shorts", "skirt",
    "leggings", "joggers", "cargos",
    # dresses
    "dress", "gown", "jumpsuit", "romper", "saree", "sari", "lehenga",
    # outerwear
    "jacket", "coat", "blazer", "windbreaker", "bomber", "shacket", "parka",
    "puffer", "trench",
    # shoes
    "shoe", "sneaker", "boot", "sandal", "heel", "loafer", "flat", "jane",
    # accessories
    "belt", "hat", "cap", "bag", "scarf", "bandana", "beanie", "purse",
}

OFF_TOPIC_MESSAGE = (
    "FitFindr only helps find secondhand clothing, and I couldn't find a "
    "clothing item in that. Try naming the piece you want, like "
    "'vintage graphic tee under $30'."
)


def is_clothing_query(query: str) -> bool:
    """
    True if the query names at least one clothing item from _CLOTHING_WORDS.

    Plurals: a word also counts if dropping a trailing "s" or "es" gives a
    word in the list, so "shirts" -> "shirt" and "dresses" -> "dress".
    """
    for word in re.findall(r"[a-z]+", query.lower()):
        forms = {word}
        if word.endswith("es"):
            forms.add(word[:-2])
        if word.endswith("s"):
            forms.add(word[:-1])
        if forms & _CLOTHING_WORDS:
            return True
    return False


def parse_query(query: str) -> dict:
    """
    Pull description/size/max_price out of a plain-language query.
    Regex/string-splitting, not a model call — see README Planning Loop.
    """
    working = query.lower()

    max_price = None
    price_match = re.search(r"\$\s*(\d+(?:\.\d+)?)", working)
    if price_match:
        max_price = float(price_match.group(1))
        working = working.replace(price_match.group(0), " ")

    size = None
    for word in sorted(_SIZE_WORDS, key=len, reverse=True):
        if re.search(rf"\b{re.escape(word)}\b", working):
            size = word
            working = re.sub(rf"\b{re.escape(word)}\b", " ", working, count=1)
            break

    words = [w for w in re.findall(r"[a-z]+", working) if w not in _FILLER_WORDS]

    return {
        "description": " ".join(words),
        "size": size,
        "max_price": max_price,
    }

def run_agent(query: str, wardrobe: dict) -> dict:
    """
    Run the loop once and return the finished session.

    Args:
        query:    what the user asked for, in plain language
                  (e.g. "vintage graphic tee under $30, size M").
        wardrobe: a wardrobe dict — get_example_wardrobe() or
                  get_empty_wardrobe() from utils/data_loader.py.

    Returns:
        The session dict. **Check session["error"] first** — if it isn't None,
        the run ended early and the later fields will still be None.

    ─────────────────────────────────────────────────────────────────────────
    TODO — build this, following the branch rule you wrote in Milestone 2.

      1. Start a session with new_session().

      2. Count the times round the loop, and call trace.check_iterations(count)
         on each one before you go again. It raises when the count passes
         MAX_ITERATIONS in config.py — see trace.py.

      3. Parse the query into a description, a size, and a max_price. Regex,
         string splitting, or asking the model are all fine — say which you
         chose in your README. Put the result in session["parsed"].

      4. Call search_listings() with what you parsed.
         Put the results in session["search_results"].

         ⚠️ THIS IS THE BRANCH. If nothing came back:
              - put a message in session["error"] saying what the user could
                change — "No results" is not that message
              - return the session
              - do NOT call suggest_outfit with nothing

      5. Choose an item — the first result is fine. Put it in
         session["selected_item"].

      6. Call suggest_outfit() with the selected item and the wardrobe.
         Put the result in session["outfit_suggestion"].

      7. Call create_fit_card() with the outfit and the item.
         Put the result in session["fit_card"].

      8. Return the session.

    ─────────────────────────────────────────────────────────────────────────
    IN UNIT 4 you come back and add two things:

      • Trace calls. One per step. `trace.step("search_listings", inputs=...,
        returned=...)` — see trace.py. Your README needs the output.

      • A handler for ModelUnavailable, so a bad key produces a message rather
        than a stack trace. The import is already at the top of this file.
    """
    session = new_session(query, wardrobe)

    trace.check_iterations(1)

    parsed = parse_query(query)
    session["parsed"] = parsed

    # Capstone: reject off-topic queries before search, so they cost no MCP
    # search call and no model calls (criterion 3).
    if not is_clothing_query(query):
        session["error"] = OFF_TOPIC_MESSAGE
        trace.step(
            "branch: off-topic check",
            inputs={"query": query},
            note=f"no clothing word — stopping before search_listings. {OFF_TOPIC_MESSAGE}",
        )
        return session

    results = call_tool("search_listings", {
        "description": parsed["description"],
        "size": parsed["size"],
        "max_price": parsed["max_price"],
    })
    session["search_results"] = results
    trace.step("search_listings (via MCP)", inputs=parsed, returned=results)

    if not results:
        pieces = [f"'{parsed['description']}'"]
        if parsed["size"]:
            pieces.append(f"size {parsed['size']}")
        if parsed["max_price"] is not None:
            pieces.append(f"under ${parsed['max_price']:.0f}")
        session["error"] = (
            f"No listings matched {', '.join(pieces)}. Try a broader "
            f"description, a different size, or a higher price limit."
        )
        trace.step(
            "branch: search_results",
            note=f"empty — stopping before suggest_outfit. {session['error']}",
        )
        return session

    selected = results[0]
    session["selected_item"] = selected
    session["price_comparison"] = compare_price(selected)
    trace.step(
        "compare_price",
        inputs={"item": selected.get("title")},
        returned=session["price_comparison"],
    )

    try:
        session["outfit_suggestion"] = suggest_outfit(selected, wardrobe)
        trace.step(
            "suggest_outfit",
            inputs={
                "item": selected.get("title"),
                "wardrobe_items": len(wardrobe.get("items", [])),
            },
            returned=session["outfit_suggestion"],
        )

        session["fit_card"] = create_fit_card(session["outfit_suggestion"], selected)
        trace.step(
            "create_fit_card",
            inputs={"outfit": session["outfit_suggestion"], "item": selected.get("title")},
            returned=session["fit_card"],
        )
    except ModelUnavailable as exc:
        session["error"] = str(exc)
        trace.step("model call", note=f"ModelUnavailable — stopping. {exc}")
        return session

    return session


# ── running it directly ───────────────────────────────────────────────────────

def _show(session: dict) -> None:
    if session["error"]:
        print(f"  stopped: {session['error']}")
        print(f"  fit_card is {session['fit_card']!r} — it should still be None here")
        return

    item = session["selected_item"] or {}
    print(f"  found:    {item.get('title')} — ${item.get('price')} on {item.get('platform')}")
    print(f"  outfit:   {session['outfit_suggestion']}")
    print(f"  fit card: {session['fit_card']}")
    print(f"  price comparison: {session['price_comparison']}")


if __name__ == "__main__":
    from utils.data_loader import get_example_wardrobe

    print("=== A query the data can match ===")
    _show(run_agent(
        query="looking for a vintage graphic tee under $30",
        wardrobe=get_example_wardrobe(),
    ))

    print("\n=== A query it can't ===")
    _show(run_agent(
        query="designer ballgown size XXS under $5",
        wardrobe=get_example_wardrobe(),
    ))

    print(
        "\nThe second one should stop before the fit card. If both paths look "
        "the same,\nthe branch isn't doing anything yet."
    )
