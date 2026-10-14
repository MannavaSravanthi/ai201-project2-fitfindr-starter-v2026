"""
The three FitFindr tools.

Each one is a standalone function you can call and test on its own, before any
of them are wired into the loop. Build and test them one at a time — three
untested tools joined by a loop is one problem that looks like six, because you
can't tell which layer is lying to you.

    search_listings(description, size, max_price)  → list[dict]
    suggest_outfit(new_item, wardrobe)             → str
    create_fit_card(outfit, new_item)              → str

All three are stubs right now. They run and they do nothing — that's the
starting position and it's deliberate.

⚠️ Before you write any of them, fill in the **Tool Inventory** section of your
README (Milestone 2). Four lines per tool: what it does, each input with its
type, exactly what it returns, and what it returns when it has nothing to give.
That last line is what your loop branches on. "Returns a list" earns nothing —
the description has to say what is *in* the list.
"""

import config  # noqa: F401 — you'll use this in search_listings
from generate import generate
from utils.data_loader import load_listings
import re


# ── Tool 1: search_listings ───────────────────────────────────────────────────

def search_listings(
    description: str,
    size: str | None = None,
    max_price: float | None = None,
) -> list[dict]:
    """
    Search the listings data for items matching a description, and optionally a
    size and a price ceiling.

    This is the tool that doesn't call the model, which makes it the easiest one
    to test and the one to move onto MCP in unit 4.

    Args:
        description: keywords describing what the user wants
                     (e.g. "vintage graphic tee").
        size:        a size string to filter by, or None to skip size filtering.
                     Match case-insensitively — "M" should match "S/M".

                     ⚠️ Read the sizes in the data before you reach for a plain
                     substring test. `"s" in "us 9"` is True, and so is
                     `"l" in "xl"`. A filter that returns shoes when someone
                     asked for a small top reads like a broken search, and it
                     will quietly cost you in unit 4 when you test criterion 1.
                     What counts as a size match is part of your spec — decide
                     it and write it into your Tool Inventory.
        max_price:   maximum price, inclusive, or None to skip price filtering.

    Returns:
        A list of matching listing dicts, best match first.
        **Returns an empty list when nothing matches — an empty list, not None,
        and not an exception.** Your loop branches on this.

    Each listing dict has these fields:
        id, title, description, category, style_tags (list), size,
        condition, price (float), colors (list), brand (str or None), platform

    Note that `brand` is None for most listings. That is deliberate and
    realistic — thrift listings often have no brand. If something you write
    assumes a brand is always there, you will find out in unit 4.

    TODO:
        1. Load every listing with load_listings().
        2. Filter by max_price and by size, when each is provided.
        3. Score what's left by keyword overlap with `description`.
        4. Drop anything scoring zero.
        5. Sort by score, highest first, and return the listing dicts —
           at most config.SEARCH_RESULT_LIMIT of them.

    Test it from a terminal before you move on:
        python -c "from tools import search_listings; print(search_listings('graphic tee', max_price=30))"
    """
    # TODO: replace this with your implementation
    listings = load_listings()

    size_words = {
        "small": "s", "s": "s",
        "medium": "m", "m": "m",
        "large": "l", "l": "l",
        "extra large": "xl", "xl": "xl", "xxl": "xxl",
    }

    def size_tokens(raw: str) -> list[str]:
        # "S/M" -> ["s", "m"], "XL (oversized)" -> ["xl", "oversized"]
        raw = re.sub(r"[()]", " ", raw.lower())
        return re.split(r"[\s/]+", raw.strip())

    target_size = None
    if size:
        normalized = size.strip().lower()
        target_size = size_words.get(normalized, normalized)

    query_words = set(description.lower().split())

    scored = []
    for listing in listings:
        if max_price is not None and listing["price"] > max_price:
            continue

        if target_size is not None:
            if target_size not in size_tokens(listing.get("size", "")):
                continue

        haystack = set(listing.get("title", "").lower().split())
        haystack |= set(listing.get("description", "").lower().split())
        for tag in listing.get("style_tags", []):
            haystack |= set(tag.lower().split())
        score = len(query_words & haystack)
        if score > 0:
            scored.append((score, listing))

    scored.sort(key=lambda pair: pair[0], reverse=True)
    return [listing for _, listing in scored[: config.SEARCH_RESULT_LIMIT]]


# ── Tool 2: suggest_outfit ────────────────────────────────────────────────────

def suggest_outfit(new_item: dict, wardrobe: dict) -> str:
    """
    Given a thrifted item and the user's wardrobe, suggest one or two outfits.

    This one calls the model, through `generate()`. You don't need to think
    about rate limits — the adapter handles pacing for you.

    Args:
        new_item: a listing dict — the item the user is considering.
        wardrobe: a wardrobe dict with an 'items' key holding a list of items.
                  **It may be empty.** Handle that.

    Returns:
        A non-empty string with outfit suggestions.
        With an empty wardrobe, return general styling advice rather than
        raising or returning "". Unit 4 has you trigger the empty wardrobe on
        purpose, so decide now what it should do.

    TODO:
        1. Check whether wardrobe['items'] is empty.
        2. If it is, ask the model for general styling ideas for this item.
        3. If it isn't, format the wardrobe items into the prompt and ask for
           specific combinations naming pieces the user already owns.
        4. Return the model's response.

    Test it from a terminal before you move on:
        python -c "from tools import suggest_outfit; from utils.data_loader import get_example_wardrobe, load_listings; print(suggest_outfit(load_listings()[0], get_example_wardrobe()))"
    """
    # TODO: replace this with your implementation
    items = wardrobe.get("items", [])

    item_description = (
        f"{new_item.get('title', 'this item')} — {new_item.get('description', '')} "
        f"(category: {new_item.get('category', 'unknown')}, "
        f"colors: {', '.join(new_item.get('colors', [])) or 'unknown'}, "
        f"style: {', '.join(new_item.get('style_tags', [])) or 'unknown'})"
    )

    system = (
        "You are a casual styling assistant for secondhand fashion finds. "
        "Give specific, concrete outfit suggestions, not generic advice."
    )

    if not items:
        prompt = (
            f"A user is considering this thrifted item:\n{item_description}\n\n"
            "They don't have any other wardrobe items on file yet. Suggest one "
            "or two general outfit ideas for how to style this piece on its "
            "own or with commonly-owned basics."
        )
    else:
        wardrobe_lines = "\n".join(
            f"- {w.get('name')} ({w.get('category')}, "
            f"colors: {', '.join(w.get('colors', [])) or 'unknown'}, "
            f"style: {', '.join(w.get('style_tags', [])) or 'unknown'})"
            for w in items
        )
        prompt = (
            f"A user is considering this thrifted item:\n{item_description}\n\n"
            f"Here is their existing wardrobe:\n{wardrobe_lines}\n\n"
            "Suggest one or two outfit ideas that pair the new item with "
            "specific pieces from their wardrobe above, naming the pieces by "
            "name."
        )

    return generate(prompt, system=system)


# ── Tool 3: create_fit_card ───────────────────────────────────────────────────

def create_fit_card(outfit: str, new_item: dict) -> str:
    """
    Write a short caption someone would actually post about the find.

    This calls the model too.

    Args:
        outfit:   the outfit suggestion string from suggest_outfit().
        new_item: the listing dict for the item.

    Returns:
        A two-to-four sentence caption.
        If `outfit` is empty or whitespace, return a descriptive message rather
        than raising.

    The caption should read like a real post rather than a product description,
    mention the item and its price and platform once each, and be specific about
    the vibe.

    It should also come out **differently for different inputs**. If you run
    this three times on the same item and get three word-for-word identical
    strings, it's one of two things, and both are near the top of `config.py`:

        • CACHE_ENABLED — the adapter handed back an answer it already had
        • TEMPERATURE   — at 0.0 the model gives the same words every time

    TODO:
        1. Guard against an empty or whitespace-only `outfit`.
        2. Build a prompt with the item details and the outfit.
        3. Call generate() and return the response.

    Test it from a terminal before you move on:
        python -c "from tools import create_fit_card; from utils.data_loader import load_listings; print(create_fit_card('jeans and white sneakers', load_listings()[0]))"
    """
    # TODO: replace this with your implementation
    outfit = (outfit or "").strip()

    # Unit 4, Milestone 5 — the improvement. Criterion 4 missed 3/5 because
    # this prompt never told the model the item's actual style_tags, so it
    # reached for its own vibe words ("Bratz doll energy") instead of a real
    # tag. Now the tags are in item_description AND the prompt explicitly
    # asks for one of the exact words.
    style_tags = new_item.get("style_tags") or []

    item_description = (
        f"{new_item.get('title', 'this item')} — {new_item.get('description', '')} "
        f"(${new_item.get('price', '?')}, via {new_item.get('platform', 'a secondhand platform')}, "
        f"style: {', '.join(style_tags) if style_tags else 'unspecified'})"
    )

    style_instruction = (
        f"Work in one of these exact style words, naturally: {', '.join(style_tags)}."
        if style_tags
        else "No style tags are available for this item, so skip that."
    )

    system = (
        "You write short, casual captions for secondhand fashion finds — the "
        "kind someone would post about their own outfit. Natural and "
        "specific, not a product description."
    )

    if not outfit:
        prompt = (
            f"Write a short 2-4 sentence caption about finding this item, "
            f"without describing how to style it (no styling info is "
            f"available yet):\n{item_description}\n\n"
            f"Mention the price and the platform naturally. {style_instruction}"
        )
    else:
        prompt = (
            f"Write a short 2-4 sentence caption someone would post about "
            f"this find and how they're styling it.\n\n"
            f"Item: {item_description}\n\n"
            f"Styling idea: {outfit}\n\n"
            f"Mention the price and platform naturally, and reference the "
            f"styling idea. {style_instruction}"
        )

    return generate(prompt, system=system)

# ── Tool 4: compare_price (stretch) ──────────────────────────────────────────

def compare_price(item: dict) -> dict:
    """
    Compare a listing's price against other listings sharing its category and
    at least one style tag, and say whether it's a good deal.

    Args:
        item: a listing dict — the item to evaluate.

    Returns:
        A dict with:
            average_price:    float — average price of the comparison group,
                               or None if there wasn't enough data.
            this_price:       float — the item's own price.
            compared_against: int — how many listings it was compared to.
            verdict:          str — "below average", "above average",
                               "about average" (within 10% of the average),
                               or "not enough data to compare".

    When fewer than 2 other listings share both the category and a style
    tag, returns verdict="not enough data to compare" with average_price
    as None, instead of computing an average from 0 or 1 items.
    """
    listings = load_listings()
    item_category = item.get("category")
    item_tags = {tag.lower() for tag in item.get("style_tags", [])}
    this_price = item.get("price")

    comparable_prices = []
    for listing in listings:
        if listing.get("id") == item.get("id"):
            continue  # don't compare the item against itself
        if listing.get("category") != item_category:
            continue
        listing_tags = {tag.lower() for tag in listing.get("style_tags", [])}
        if not (item_tags & listing_tags):
            continue
        comparable_prices.append(listing["price"])

    if len(comparable_prices) < 2:
        return {
            "average_price": None,
            "this_price": this_price,
            "compared_against": len(comparable_prices),
            "verdict": "not enough data to compare",
        }

    average_price = sum(comparable_prices) / len(comparable_prices)
    diff_ratio = (this_price - average_price) / average_price

    if diff_ratio < -0.10:
        verdict = "below average"
    elif diff_ratio > 0.10:
        verdict = "above average"
    else:
        verdict = "about average"

    return {
        "average_price": average_price,
        "this_price": this_price,
        "compared_against": len(comparable_prices),
        "verdict": verdict,
    }
