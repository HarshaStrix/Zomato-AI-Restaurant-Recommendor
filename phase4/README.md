# Phase 4: LLM Integration Layer (Groq)

## Overview

Phase 4 integrates **Groq** as the LLM provider to generate human-readable explanations for restaurant recommendations. When the Groq API key is not set or the API fails, the service falls back to template-based explanations.

## Folder Structure

```
phase4/
├── clients/
│   ├── base_client.py      # Abstract LLM client interface
│   └── groq_client.py      # Groq API client
├── prompts/
│   ├── templates.py        # System & user prompt templates
│   └── prompt_builder.py   # Builds prompts from context
├── parsers/
│   └── response_parser.py  # Parse LLM JSON response
├── cache/
│   └── llm_cache.py        # In-memory cache (TTL)
├── fallback/
│   └── default_generator.py # Template explanations when LLM unavailable
├── tests/
├── config.py
├── llm_service.py          # Main service (orchestrator)
└── run_tests.sh
```

## Setup

1. **Install dependencies**
   ```bash
   pip install groq
   ```

2. **Set Groq API key** (optional; fallback used if unset)
   ```bash
   export GROQ_API_KEY=your_groq_api_key
   ```
   Get a key at [Groq Console](https://console.groq.com).

## Configuration (environment)

| Variable | Default | Description |
|----------|---------|-------------|
| `GROQ_API_KEY` | - | Groq API key (required for real LLM calls) |
| `GROQ_MODEL` | `llama-3.1-8b-instant` | Model name |
| `GROQ_TEMPERATURE` | `0.7` | Sampling temperature |
| `GROQ_MAX_TOKENS` | `600` | Max response tokens |
| `GROQ_TIMEOUT` | `15` | Request timeout (seconds) |
| `LLM_CACHE_ENABLED` | `true` | Use in-memory cache |
| `LLM_CACHE_TTL_SECONDS` | `86400` | Cache TTL (24h) |

## Usage

```python
from phase4.llm_service import LLMService

service = LLMService()

restaurants = [
    {"id": 1, "name": "Bella Italia", "rating": 4.5, "cuisine": "Italian", "price_bucket": "medium", "votes": 500},
]

result = service.generate_explanations(
    restaurants,
    location="Bangalore",
    cuisine="Italian",
    price_range="2-3",
)

# result["explanations"] -> list of {restaurant_name, explanation}
# result["summary"] -> overall summary
# result["from_cache"] -> True if from cache
# result["from_fallback"] -> True if template fallback used

# Attach explanations to restaurant dicts
enriched = service.attach_explanations_to_restaurants(restaurants, result)
```

## Running Tests

**Without Groq API key** (uses fallback; all tests that don’t call Groq run):

```bash
./phase4/run_tests.sh
# or
PYTHONPATH=. python -m pytest phase4/tests/ -v -m "not groq_integration"
```

**With Groq API key** (include real Groq integration tests):

```bash
export GROQ_API_KEY=your_key
PYTHONPATH=. python -m pytest phase4/tests/ -v
```

- **15 tests** run by default (prompts, parser, fallback, cache, LLM service with fallback).
- **2 tests** are marked `groq_integration` and run only when you don’t exclude them (and key is set).

## Test Coverage

- **PromptBuilder**: build prompts from context
- **ResponseParser**: parse JSON, get explanation by name
- **DefaultExplanationGenerator**: template explanations
- **LLMCache**: set/get, key difference, disabled
- **LLMService**: empty list, fallback when no key, attach explanations
- **GroqClient** (integration): `is_available`, `complete` — run once Groq API key is connected
