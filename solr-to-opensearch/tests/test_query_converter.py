"""Tests for QueryConverter."""

import pytest

from solr_to_opensearch.query_converter import QueryConverter


@pytest.fixture()
def converter() -> QueryConverter:
    return QueryConverter()


# ---------------------------------------------------------------------------
# match_all
# ---------------------------------------------------------------------------

def test_match_all_star_colon_star(converter):
    result = converter.convert("*:*")
    assert result == {"query": {"match_all": {}}}


# ---------------------------------------------------------------------------
# Simple field:value
# ---------------------------------------------------------------------------

def test_simple_field_value(converter):
    result = converter.convert("title:opensearch")
    assert result == {"query": {"match": {"title": "opensearch"}}}


def test_field_value_with_spaces_in_value(converter):
    """Unquoted multi-word value goes to match query."""
    result = converter.convert("category:search engine")
    # The field:value RE will capture "search engine" as the value.
    assert result["query"]["match"]["category"] == "search engine"


# ---------------------------------------------------------------------------
# Phrase queries
# ---------------------------------------------------------------------------

def test_phrase_query(converter):
    result = converter.convert('title:"open search"')
    assert result == {"query": {"match_phrase": {"title": "open search"}}}


# ---------------------------------------------------------------------------
# Wildcard queries
# ---------------------------------------------------------------------------

def test_wildcard_suffix(converter):
    result = converter.convert("title:open*")
    assert result == {"query": {"wildcard": {"title": "open*"}}}


def test_wildcard_prefix(converter):
    result = converter.convert("title:*search")
    assert result == {"query": {"wildcard": {"title": "*search"}}}


def test_wildcard_question_mark(converter):
    result = converter.convert("title:op?n")
    assert result == {"query": {"wildcard": {"title": "op?n"}}}


# ---------------------------------------------------------------------------
# Range queries
# ---------------------------------------------------------------------------

def test_inclusive_range(converter):
    result = converter.convert("price:[10 TO 100]")
    assert result == {"query": {"range": {"price": {"gte": 10, "lte": 100}}}}


def test_exclusive_range(converter):
    result = converter.convert("price:{10 TO 100}")
    assert result == {"query": {"range": {"price": {"gt": 10, "lt": 100}}}}


def test_open_low_range(converter):
    result = converter.convert("price:[* TO 100]")
    assert result == {"query": {"range": {"price": {"lte": 100}}}}


def test_open_high_range(converter):
    result = converter.convert("price:[10 TO *]")
    assert result == {"query": {"range": {"price": {"gte": 10}}}}


def test_mixed_range(converter):
    result = converter.convert("price:{10 TO 100]")
    assert result == {"query": {"range": {"price": {"gt": 10, "lte": 100}}}}


def test_float_range(converter):
    result = converter.convert("rating:[3.5 TO 5.0]")
    assert result == {"query": {"range": {"rating": {"gte": 3.5, "lte": 5.0}}}}


# ---------------------------------------------------------------------------
# Boolean AND / OR
# ---------------------------------------------------------------------------

def test_and_query(converter):
    result = converter.convert("title:search AND category:docs")
    assert "bool" in result["query"]
    assert "must" in result["query"]["bool"]
    clauses = result["query"]["bool"]["must"]
    assert {"match": {"title": "search"}} in clauses
    assert {"match": {"category": "docs"}} in clauses


def test_or_query(converter):
    result = converter.convert("title:search OR title:find")
    assert "bool" in result["query"]
    assert "should" in result["query"]["bool"]
    assert result["query"]["bool"]["minimum_should_match"] == 1


# ---------------------------------------------------------------------------
# NOT queries
# ---------------------------------------------------------------------------

def test_not_query(converter):
    result = converter.convert("NOT title:spam")
    assert result == {"query": {"bool": {"must_not": [{"match": {"title": "spam"}}]}}}


# ---------------------------------------------------------------------------
# +/- prefix queries
# ---------------------------------------------------------------------------

def test_required_prohibited(converter):
    result = converter.convert("+title:search -category:spam")
    bool_q = result["query"]["bool"]
    assert {"match": {"title": "search"}} in bool_q["must"]
    assert {"match": {"category": "spam"}} in bool_q["must_not"]


# ---------------------------------------------------------------------------
# Outer parentheses
# ---------------------------------------------------------------------------

def test_outer_parens_stripped(converter):
    result_with = converter.convert("(title:opensearch)")
    result_without = converter.convert("title:opensearch")
    assert result_with == result_without


# ---------------------------------------------------------------------------
# Boost stripping
# ---------------------------------------------------------------------------

def test_boost_is_stripped(converter):
    result = converter.convert("title:opensearch^2")
    assert result == {"query": {"match": {"title": "opensearch"}}}


# ---------------------------------------------------------------------------
# Fallback to query_string
# ---------------------------------------------------------------------------

def test_bare_term_fallback(converter):
    result = converter.convert("opensearch")
    assert result == {"query": {"query_string": {"query": "opensearch"}}}


# ---------------------------------------------------------------------------
# Error handling
# ---------------------------------------------------------------------------

def test_empty_query_raises(converter):
    with pytest.raises(ValueError):
        converter.convert("")


def test_whitespace_only_raises(converter):
    with pytest.raises(ValueError):
        converter.convert("   ")
