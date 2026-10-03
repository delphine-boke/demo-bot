# Multilingual NLU for African languages (Rasa)

Talk companion for **Technical Implementation of Multilingual NLP Pipelines for African Languages Using Python and Rasa**.

Shared intents, one domain, three NLU files. English, Swahili, and Ekegusii (`guz`). Sparse DIET pipeline so we are not blocked on a spaCy model that does not exist for Ekegusii.

Ekegusii examples are drafts. Do not treat `data/nlu/nlu_guz.yml` as validated until a native speaker has reviewed it.

## Layout

```
actions/            custom actions (action server)
chat.html           thin demo client against the Rasa REST channel
config.yml          NLU + policy pipeline
data/nlu/           nlu_en.yml, nlu_sw.yml, nlu_guz.yml
data/rules.yml
domain.yml
endpoints.yml
requirements.txt
```

Not in git, on purpose:

| Path | Why |
|---|---|
| `.venv/` | local env |
| `.rasa/` | training cache |
| `.env` | `OPENAI_API_KEY` |
| `models/` | rebuild with `rasa train` |
| `stuff.txt`, `data/nlu.yml` | scratch / old single-file NLU |

## Setup

Python 3.10. Rasa 3.x does not support 3.12+.

```bash
python3.9 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pip install -r requirements.txt
```

`.env` (never commit this):

```
OPENAI_API_KEY=sk-...
```

## Train and run

```bash
rasa train
rasa run actions          # terminal 1, if domain.yml has custom actions
rasa run --enable-api --cors "*"   # terminal 2
```

Open `chat.html` against `http://localhost:5005/webhooks/rest/webhook`.

Interactive check:

```bash
rasa shell
rasa test nlu
```

A model tarball lands in `models/`. Git ignores that directory. CI trains from `data/` and `config.yml`; it does not download a committed artifact.

## Pipeline

`config.yml` is the sparse path, not spaCy:

- `WhitespaceTokenizer`
- `CountVectorsFeaturizer` (word + `char_wb`)
- `DIETClassifier`
- `FallbackClassifier` into the LLM path when intent confidence is low

Word boundaries are whitespace. Subword `char_wb` features are what carry Swahili and Ekegusii, where a pretrained English tokenizer would split the morphology wrong.

Intents are shared across languages. Only the examples differ, in `data/nlu/nlu_*.yml`. Adding a language means a new examples file, not a new domain.

## LLM fallback

Low-confidence turns go to OpenAI from the action server (`actions/actions.py`), using `OPENAI_API_KEY`. Rasa still owns the dialogue state. The LLM does not replace DIET; it covers the tail the training set does not.

## Talk notes

- Domain framing: government and education services. Fintech cost figure (about 50% ops reduction from LLM automation) is a client result, not a number this repo reproduces.
- Demo path: train, `rasa run`, `chat.html`, one utterance per language, then a fallback utterance.
- Do not ship `nlu_guz.yml` as production data without native-speaker review.
