# Capstone run — before

- 2026-11-24 13:31 · model `gemini-3.5-flash-lite` · cache off · 20 labelled queries from `capstone_queries.py` × 3 trials
- Produced by `run_capstone.py::run_trials`, calling `agent.py::run_agent`; scored from the logs in `logs/capstone_before_trial*.jsonl`
- Log records per trial: 20/20, 20/20, 20/20

| Criterion | Target | Run 1 | Run 2 | Run 3 | Verdict |
|---|---|---|---|---|---|
| 1. Off-topic queries are rejected | ≥ 8 of 10 | 8/10 | 8/10 | 8/10 | MET |
| 2. Real clothing queries get through | ≥ 9 of 10 | 9/10 | 9/10 | 9/10 | MET |
| 3. A rejection costs nothing (0 model, 0 search calls) | every rejection | 9/9 | 9/9 | 9/9 | MET |
| 4. Rejection message has 'clothing' + an example in quotes | every rejection | 9/9 | 9/9 | 9/9 | MET |
| 5. Normal path still ends with a fit card ≥ 150 chars | every passing query with results | 8/8 | 2/8 | 2/8 | MISSED |

## Every query, every trial

| Query | Label | Run 1 | Run 2 | Run 3 |
|---|---|---|---|---|
| give me a plaid skirt styling ideas | on_topic | ok, 2 calls, card 255 chars | ok, 2 calls, card 264 chars | model_unavailable, 1 calls |
| blue sweater | on_topic | no_results, 0 calls | no_results, 0 calls | no_results, 0 calls |
| how to style black denim jeans | on_topic | ok, 2 calls, card 266 chars | ok, 2 calls, card 327 chars | model_unavailable, 1 calls |
| brown suede jacket | on_topic | ok, 2 calls, card 213 chars | model_unavailable, 1 calls | ok, 2 calls, card 247 chars |
| coffee colored shirt | on_topic | ok, 2 calls, card 288 chars | model_unavailable, 1 calls | model_unavailable, 1 calls |
| linen shirts for summer or winter? | on_topic | ok, 2 calls, card 204 chars | model_unavailable, 1 calls | model_unavailable, 1 calls |
| floral dresses styling ideas | on_topic | ok, 2 calls, card 274 chars | model_unavailable, 1 calls | ok, 2 calls, card 251 chars |
| something to wear for an Indian wedding | on_topic | off_topic, 0 calls | off_topic, 0 calls | off_topic, 0 calls |
| light washed denim jean with boot cut | on_topic | ok, 2 calls, card 259 chars | model_unavailable, 1 calls | model_unavailable, 2 calls |
| bandana colors that go with a light colored t shirt | on_topic | ok, 2 calls, card 247 chars | model_unavailable, 1 calls | model_unavailable, 1 calls |
| tell me a joke | off_topic | off_topic, 0 calls | off_topic, 0 calls | off_topic, 0 calls |
| cranberry cookies recipe | off_topic | off_topic, 0 calls | off_topic, 0 calls | off_topic, 0 calls |
| can you give some recipe cards for high protein meals? | off_topic | off_topic, 0 calls | off_topic, 0 calls | off_topic, 0 calls |
| give me ideas to decorate my laptop. | off_topic | off_topic, 0 calls | off_topic, 0 calls | off_topic, 0 calls |
| vintage car under $30 | off_topic | off_topic, 0 calls | off_topic, 0 calls | off_topic, 0 calls |
| recommend a black coffee | off_topic | off_topic, 0 calls | off_topic, 0 calls | off_topic, 0 calls |
| Is the color of taj-mahal off white? | off_topic | off_topic, 0 calls | off_topic, 0 calls | off_topic, 0 calls |
| where to buy orange color snoopy coffee mug? | off_topic | off_topic, 0 calls | off_topic, 0 calls | off_topic, 0 calls |
| how do I wash a denim jacket | off_topic | model_unavailable, 1 calls | model_unavailable, 1 calls | ok, 2 calls, card 336 chars |
| what's the history of the sneaker | off_topic | no_results, 0 calls | no_results, 0 calls | no_results, 0 calls |
