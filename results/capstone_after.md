# Capstone run — after

- 2026-11-24 14:37 · model `gemini-3.5-flash-lite` · cache off · 20 labelled queries from `capstone_queries.py` × 3 trials
- Produced by `run_capstone.py::run_trials`, calling `agent.py::run_agent`; scored from the logs in `logs/capstone_after_trial*.jsonl`
- Log records per trial: 20/20, 20/20, 20/20

| Criterion | Target | Run 1 | Run 2 | Run 3 | Verdict |
|---|---|---|---|---|---|
| 1. Off-topic queries are rejected | ≥ 8 of 10 | 8/10 | 8/10 | 8/10 | MET |
| 2. Real clothing queries get through | ≥ 9 of 10 | 8/10 | 9/10 | 9/10 | MISSED |
| 3. A rejection costs nothing (0 model, 0 search calls) | every rejection | 9/9 | 9/9 | 9/9 | MET |
| 4. Rejection message has 'clothing' + an example in quotes | every rejection | 9/9 | 9/9 | 9/9 | MET |
| 5. Normal path still ends with a fit card ≥ 150 chars | every passing query with results | 7/7 | 8/8 | 8/8 | MET |

## Every query, every trial

| Query | Label | Run 1 | Run 2 | Run 3 |
|---|---|---|---|---|
| give me a plaid skirt styling ideas | on_topic | ok, 2 calls, card 324 chars | ok, 6 calls, card 329 chars | ok, 3 calls, card 294 chars |
| blue sweater | on_topic | no_results, 0 calls | no_results, 0 calls | no_results, 0 calls |
| how to style black denim jeans | on_topic | ok, 2 calls, card 311 chars | ok, 4 calls, card 242 chars | ok, 3 calls, card 334 chars |
| brown suede jacket | on_topic | crashed, 5 calls | ok, 8 calls, card 256 chars | ok, 2 calls, card 324 chars |
| coffee colored shirt | on_topic | ok, 5 calls, card 299 chars | ok, 2 calls, card 236 chars | ok, 3 calls, card 271 chars |
| linen shirts for summer or winter? | on_topic | ok, 2 calls, card 273 chars | ok, 4 calls, card 297 chars | ok, 4 calls, card 303 chars |
| floral dresses styling ideas | on_topic | ok, 3 calls, card 252 chars | ok, 5 calls, card 212 chars | ok, 2 calls, card 219 chars |
| something to wear for an Indian wedding | on_topic | off_topic, 0 calls | off_topic, 0 calls | off_topic, 0 calls |
| light washed denim jean with boot cut | on_topic | ok, 4 calls, card 251 chars | ok, 3 calls, card 253 chars | ok, 2 calls, card 247 chars |
| bandana colors that go with a light colored t shirt | on_topic | ok, 6 calls, card 316 chars | ok, 3 calls, card 287 chars | ok, 2 calls, card 331 chars |
| tell me a joke | off_topic | off_topic, 0 calls | off_topic, 0 calls | off_topic, 0 calls |
| cranberry cookies recipe | off_topic | off_topic, 0 calls | off_topic, 0 calls | off_topic, 0 calls |
| can you give some recipe cards for high protein meals? | off_topic | off_topic, 0 calls | off_topic, 0 calls | off_topic, 0 calls |
| give me ideas to decorate my laptop. | off_topic | off_topic, 0 calls | off_topic, 0 calls | off_topic, 0 calls |
| vintage car under $30 | off_topic | off_topic, 0 calls | off_topic, 0 calls | off_topic, 0 calls |
| recommend a black coffee | off_topic | off_topic, 0 calls | off_topic, 0 calls | off_topic, 0 calls |
| Is the color of taj-mahal off white? | off_topic | off_topic, 0 calls | off_topic, 0 calls | off_topic, 0 calls |
| where to buy orange color snoopy coffee mug? | off_topic | off_topic, 0 calls | off_topic, 0 calls | off_topic, 0 calls |
| how do I wash a denim jacket | off_topic | ok, 2 calls, card 278 chars | ok, 3 calls, card 345 chars | ok, 2 calls, card 250 chars |
| what's the history of the sneaker | off_topic | no_results, 0 calls | no_results, 0 calls | no_results, 0 calls |
