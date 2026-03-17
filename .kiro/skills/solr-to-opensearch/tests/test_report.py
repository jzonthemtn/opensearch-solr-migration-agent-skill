"""Tests for report.py"""
import sys
import os
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))
from report import MigrationReport


def test_generate_contains_header():
    report = MigrationReport()
    output = report.generate()
    assert "# Solr to OpenSearch Migration Report" in output


def test_generate_milestones():
    report = MigrationReport(milestones=["Step A", "Step B"])
    output = report.generate()
    assert "1. Step A" in output
    assert "2. Step B" in output


def test_generate_blockers():
    report = MigrationReport(blockers=["Blocker 1", "Blocker 2"])
    output = report.generate()
    assert "- Blocker 1" in output
    assert "- Blocker 2" in output


def test_generate_no_blockers_default_message():
    report = MigrationReport()
    output = report.generate()
    assert "No immediate blockers identified." in output


def test_generate_implementation_points():
    report = MigrationReport(implementation_points=["Do X", "Do Y"])
    output = report.generate()
    assert "- Do X" in output
    assert "- Do Y" in output


def test_generate_cost_estimates():
    report = MigrationReport(cost_estimates={"Infrastructure": "$500/mo", "Effort": "2 weeks"})
    output = report.generate()
    assert "Infrastructure" in output
    assert "$500/mo" in output
    assert "Effort" in output
    assert "2 weeks" in output


def test_generate_no_cost_estimates_default_message():
    report = MigrationReport()
    output = report.generate()
    assert "TBD" in output


def test_generate_empty_report():
    report = MigrationReport()
    output = report.generate()
    assert "## Major Milestones" in output
    assert "## Potential Blockers" in output
    assert "## Implementation Points" in output
    assert "## Cost Estimates" in output


def test_generate_returns_string():
    report = MigrationReport(milestones=["m1"], blockers=["b1"])
    assert isinstance(report.generate(), str)
