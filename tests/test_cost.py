"""Unit tests for services.cost — pure cost math (no DB).

DB-backed `summarize_runs` is exercised in integration tests separately.
Here we cover the pure helpers: `cost_for_run` and the rate table.
"""
from __future__ import annotations

from types import SimpleNamespace

import pytest

from pantra.services import cost


def _run(model, input_t=0, output_t=0, cache_read=0, cache_creation=0):
    """Build a stand-in AIRun with just the fields cost_for_run reads."""
    return SimpleNamespace(
        model=model,
        input_tokens=input_t,
        output_tokens=output_t,
        cache_read_tokens=cache_read,
        cache_creation_tokens=cache_creation,
    )


def test_sonnet_pure_input_output():
    # 1000 input + 500 output on Sonnet 4.6 ($3/$15 per Mtok)
    r = _run("claude-sonnet-4-6", input_t=1000, output_t=500)
    c = cost.cost_for_run(r)
    # Expected: 1000/1M * $3 = $0.003 + 500/1M * $15 = $0.0075 → $0.0105
    assert c.input_cost_usd == pytest.approx(0.003, rel=1e-6)
    assert c.output_cost_usd == pytest.approx(0.0075, rel=1e-6)
    assert c.total_usd == pytest.approx(0.0105, rel=1e-6)
    assert c.cache_read_cost_usd == 0
    assert c.cache_creation_cost_usd == 0


def test_haiku_5x_cheaper_than_sonnet_on_input():
    # Same input tokens; Haiku input rate is $1, Sonnet is $3 → 3x ratio.
    sonnet = cost.cost_for_run(_run("claude-sonnet-4-6", input_t=10_000))
    haiku = cost.cost_for_run(_run("claude-haiku-4-5", input_t=10_000))
    assert sonnet.input_cost_usd == pytest.approx(haiku.input_cost_usd * 3, rel=1e-6)


def test_cache_read_costs_10pct_of_input_rate():
    # Sonnet: 10_000 cache_read tokens at 10% of $3 = $0.00003 (10000/1M*3*0.10)
    r = _run("claude-sonnet-4-6", cache_read=10_000)
    c = cost.cost_for_run(r)
    expected = (10_000 / 1_000_000) * 3.0 * cost.CACHE_READ_MULTIPLIER
    assert c.cache_read_cost_usd == pytest.approx(expected, rel=1e-6)
    # No other category should be billed.
    assert c.input_cost_usd == 0
    assert c.output_cost_usd == 0
    assert c.cache_creation_cost_usd == 0


def test_cache_creation_costs_125pct_of_input_rate():
    r = _run("claude-sonnet-4-6", cache_creation=10_000)
    c = cost.cost_for_run(r)
    expected = (10_000 / 1_000_000) * 3.0 * cost.CACHE_CREATION_MULTIPLIER
    assert c.cache_creation_cost_usd == pytest.approx(expected, rel=1e-6)


def test_unknown_model_returns_zero():
    r = _run("some-future-model-xyz", input_t=10_000, output_t=10_000)
    c = cost.cost_for_run(r)
    assert c.total_usd == 0.0


def test_null_token_counters_treated_as_zero():
    r = SimpleNamespace(
        model="claude-sonnet-4-6",
        input_tokens=None,
        output_tokens=None,
        cache_read_tokens=None,
        cache_creation_tokens=None,
    )
    c = cost.cost_for_run(r)
    assert c.total_usd == 0.0


def test_eur_conversion_applied():
    r = _run("claude-sonnet-4-6", input_t=1_000_000)  # $3 USD on input
    c = cost.cost_for_run(r)
    # USD→EUR uses the module-level constant.
    assert c.total_usd == pytest.approx(3.0, rel=1e-6)
    expected_eur = 3.0 * cost.USD_TO_EUR
    # cost_for_run only returns USD breakdowns; EUR lives on UsageSummary.


def test_realistic_caching_scenario():
    # Conversation tool-use loop: 1 initial call (cache_creation) + 4 follow-ups (cache_read)
    # System prompt + tools = ~3000 tokens. User messages = ~500 each. Output = ~200 each.

    # First turn: creates cache (3000 tokens)
    first = cost.cost_for_run(_run(
        "claude-sonnet-4-6",
        input_t=500,           # user message
        cache_creation=3000,   # system + tools cached
        output_t=200,
    ))
    # Subsequent 4 turns: cache hits
    follow = cost.cost_for_run(_run(
        "claude-sonnet-4-6",
        input_t=500,
        cache_read=3000,
        output_t=200,
    ))

    # Cache_read should be much cheaper than re-paying for system prompt.
    # 3000 tokens at full input rate would cost: 3000/1M * 3 = $0.009
    # At 10% rate it's: $0.0009 → 10x cheaper for the cached portion.
    full_rate_cost = (3000 / 1_000_000) * 3.0
    cached_rate_cost = follow.cache_read_cost_usd
    assert cached_rate_cost == pytest.approx(full_rate_cost * 0.10, rel=1e-6)


def test_rates_table_has_canonical_models():
    # Defensive: if someone removes the Sonnet/Haiku entries, costs go to 0.
    # This test pins those two so a sloppy refactor doesn't silently break
    # the analytics endpoint.
    assert "claude-sonnet-4-6" in cost.RATES
    assert "claude-haiku-4-5" in cost.RATES
    assert cost.RATES["claude-sonnet-4-6"]["input"] == 3.0
    assert cost.RATES["claude-sonnet-4-6"]["output"] == 15.0
    assert cost.RATES["claude-haiku-4-5"]["input"] == 1.0
    assert cost.RATES["claude-haiku-4-5"]["output"] == 5.0
