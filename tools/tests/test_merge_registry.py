"""registry/papers.jsonl is merged per DOI when two pipeline branches meet."""

from tools.merge_registry import merge


def row(doi, tier, updated="2026-11-09", **extra):
    return {"doi": doi, "tier": tier, "updated": updated, **extra}


def test_rows_added_on_each_side_are_all_kept():
    base = {"10.1/a": row("10.1/a", "C")}
    ours = {**base, "10.1/b": row("10.1/b", "B")}
    theirs = {**base, "10.1/c": row("10.1/c", "rejected")}
    assert set(merge(base, ours, theirs)) == {"10.1/a", "10.1/b", "10.1/c"}


def test_a_row_only_one_side_changed_takes_that_side():
    base = {"10.1/a": row("10.1/a", "pending")}
    theirs = {"10.1/a": row("10.1/a", "B", outcome="evidence")}
    assert merge(base, dict(base), theirs)["10.1/a"]["tier"] == "B"
    assert merge(base, theirs, dict(base))["10.1/a"]["tier"] == "B"


def test_both_changed_takes_the_later_update_then_the_higher_tier():
    base = {}
    pending = {"10.1/a": row("10.1/a", "pending")}
    evidence = {"10.1/a": row("10.1/a", "B")}
    assert merge(base, pending, evidence)["10.1/a"]["tier"] == "B"
    assert merge(base, evidence, pending)["10.1/a"]["tier"] == "B"
    newer = {"10.1/a": row("10.1/a", "C", updated="2026-11-23")}
    assert merge(base, evidence, newer)["10.1/a"]["tier"] == "C"


def test_a_row_deleted_on_one_side_and_untouched_on_the_other_is_deleted():
    base = {"10.1/a": row("10.1/a", "C")}
    assert merge(base, {}, dict(base)) == {}
