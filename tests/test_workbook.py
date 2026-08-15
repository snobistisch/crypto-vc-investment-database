"""Tests on the written Excel file.

These tests open the real XLSX file. They check the formatting requirements
from the brief: frozen header, filters, no merged cells, real numbers, real
dates, real booleans, clickable URLs, and consistent counts across sheets.
"""

import csv
import os
import sys

import pytest
from openpyxl import load_workbook

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
from funds import FUNDS  # noqa: E402

XLSX = os.path.join(ROOT, "outputs", "vc-investments-full.xlsx")
CSV = os.path.join(ROOT, "outputs", "vc-investments-full.csv")
N_FUNDS = len(FUNDS)

SHEETS = ["README", "Funds", "Investments", "Rounds", "Portfolio Companies",
          "Coverage", "Sources", "Conflicts", "Unknown", "Aliases"]

REQUIRED_COLUMNS = [
    "investment_id", "round_id", "fund_slug", "fund_name", "fund_name_in_source",
    "project_slug", "project_name", "project_name_in_source", "previous_project_name",
    "announcement_date", "round_date", "round_type", "investment_type", "fund_role",
    "is_lead", "round_size_usd", "valuation_usd", "valuation_type", "fund_ticket_usd",
    "currency_original", "amount_original", "country", "sector", "chain_or_ecosystem",
    "token_ticker", "token_exists", "acquisition_or_exit", "acquirer", "exit_price_usd",
    "primary_source_url", "secondary_source_url", "aggregator_source_url",
    "source_consulted_date", "verification_status", "confidence", "conflict_flag", "notes",
]


@pytest.fixture(scope="module")
def wb():
    if not os.path.exists(XLSX):
        pytest.skip("workbook is missing; run build_workbook.py first")
    return load_workbook(XLSX)


def test_opens_without_warning(wb):
    assert wb.sheetnames == SHEETS


def test_all_required_columns(wb):
    header = [c.value for c in wb["Investments"][1]]
    for col in REQUIRED_COLUMNS:
        assert col in header, col


def test_header_frozen_and_filter_on_every_data_table(wb):
    for name in SHEETS[1:]:
        ws = wb[name]
        assert ws.freeze_panes == "A2", name
        assert ws.tables or ws.auto_filter.ref, name


def test_no_merged_cells(wb):
    for name in SHEETS:
        assert not wb[name].merged_cells.ranges, name


def test_amounts_are_numbers_and_never_zero(wb):
    ws = wb["Investments"]
    header = [c.value for c in ws[1]]
    for field in ("round_size_usd", "valuation_usd", "fund_ticket_usd", "exit_price_usd"):
        i = header.index(field)
        for row in ws.iter_rows(min_row=2, max_row=ws.max_row):
            v = row[i].value
            assert v is None or isinstance(v, (int, float)), (field, v)
            assert v != 0, (field, row[0].value)


def test_dates_are_date_cells(wb):
    ws = wb["Investments"]
    header = [c.value for c in ws[1]]
    i = header.index("round_date")
    for row in ws.iter_rows(min_row=2, max_row=ws.max_row):
        v = row[i].value
        assert v is None or hasattr(v, "year")


def test_booleans_are_booleans(wb):
    ws = wb["Investments"]
    header = [c.value for c in ws[1]]
    for field in ("is_lead", "token_exists", "conflict_flag"):
        i = header.index(field)
        for row in ws.iter_rows(min_row=2, max_row=ws.max_row):
            v = row[i].value
            assert v is None or isinstance(v, bool), (field, v)


def test_urls_are_clickable(wb):
    ws = wb["Investments"]
    header = [c.value for c in ws[1]]
    i = header.index("aggregator_source_url")
    with_link = sum(1 for row in ws.iter_rows(min_row=2, max_row=ws.max_row)
                    if row[i].value and row[i].hyperlink)
    total = sum(1 for row in ws.iter_rows(min_row=2, max_row=ws.max_row) if row[i].value)
    assert with_link == total and total > 0


def test_conditional_formatting_on_conflicts(wb):
    """Conflicts red, uncertain records yellow — two rules over the same range.

    openpyxl bundles rules with the same range under one key, so count the
    rules themselves, not the number of ranges.
    """
    ws = wb["Investments"]
    rules = [r for rule_list in ws.conditional_formatting._cf_rules.values()
             for r in rule_list]
    assert len(rules) >= 2
    formulas = " ".join(f for r in rules for f in (r.formula or []))
    assert "conflict_flag" in formulas or "TRUE" in formulas
    assert "uncertain" in formulas


def test_all_funds_on_funds_coverage_and_aliases(wb):
    assert wb["Aliases"].max_row - 1 == N_FUNDS
    assert wb["Coverage"].max_row - 1 == N_FUNDS
    slugs = {wb["Funds"].cell(row=r, column=1).value
             for r in range(2, N_FUNDS + 2)}
    assert len(slugs) == N_FUNDS


def test_counts_consistent_across_sheets(wb):
    inv = wb["Investments"]
    header = [c.value for c in inv[1]]
    ri = header.index("round_id")
    fi = header.index("fund_slug")
    round_ids = set()
    per_fund = {}
    for row in inv.iter_rows(min_row=2, max_row=inv.max_row):
        round_ids.add(row[ri].value)
        per_fund[row[fi].value] = per_fund.get(row[fi].value, 0) + 1

    rounds_sheet = {wb["Rounds"].cell(row=r, column=1).value
                    for r in range(2, wb["Rounds"].max_row + 1)}
    assert round_ids == rounds_sheet

    for r in range(2, N_FUNDS + 2):
        slug = wb["Funds"].cell(row=r, column=1).value
        count = wb["Funds"].cell(row=r, column=4).value
        assert count == per_fund.get(slug, 0), slug


def test_coverage_never_counts_higher_than_investments(wb):
    inv = wb["Investments"]
    header = [c.value for c in inv[1]]
    fi, pi = header.index("fund_slug"), header.index("project_slug")
    companies = {}
    for row in inv.iter_rows(min_row=2, max_row=inv.max_row):
        companies.setdefault(row[fi].value, set()).add(row[pi].value)
    for r in range(2, N_FUNDS + 2):
        slug = wb["Coverage"].cell(row=r, column=1).value
        own = wb["Coverage"].cell(row=r, column=3).value
        assert own == len(companies.get(slug, set())), slug


PER_FUND = os.path.join(ROOT, "outputs", "per-fund")


@pytest.fixture(scope="module")
def fund_slugs():
    return list(FUNDS)


def test_one_file_per_fund(fund_slugs):
    if not os.path.isdir(PER_FUND):
        pytest.skip("per-fund directory is missing; run build_workbook.py first")
    for slug in fund_slugs:
        assert os.path.exists(os.path.join(PER_FUND, "vc-investments-%s.xlsx" % slug)), slug
    assert len([f for f in os.listdir(PER_FUND) if f.endswith(".xlsx")]) == N_FUNDS


def test_fund_file_contains_only_its_own_fund(fund_slugs):
    if not os.path.isdir(PER_FUND):
        pytest.skip("per-fund directory is missing")
    for slug in fund_slugs:
        fwb = load_workbook(os.path.join(PER_FUND, "vc-investments-%s.xlsx" % slug))
        assert fwb.sheetnames == SHEETS, slug
        ws = fwb["Investments"]
        header = [c.value for c in ws[1]]
        i = header.index("fund_slug")
        found = {row[i].value for row in ws.iter_rows(min_row=2, max_row=ws.max_row)}
        assert found <= {slug}, (slug, found)
        assert fwb["Aliases"].max_row - 1 == 1, slug
        assert fwb["Coverage"].max_row - 1 == 1, slug


def test_fund_files_sum_to_the_overview(wb, fund_slugs):
    if not os.path.isdir(PER_FUND):
        pytest.skip("per-fund directory is missing")
    total = 0
    for slug in fund_slugs:
        ws = load_workbook(os.path.join(
            PER_FUND, "vc-investments-%s.xlsx" % slug))["Investments"]
        total += ws.max_row - 1 if ws.max_row > 1 else 0
    assert total == wb["Investments"].max_row - 1


def test_fund_file_keeps_co_investors(fund_slugs):
    """Rounds shows ALL investors, including funds outside this file."""
    if not os.path.isdir(PER_FUND):
        pytest.skip("per-fund directory is missing")
    ws = load_workbook(os.path.join(PER_FUND, "vc-investments-paradigm.xlsx"))["Rounds"]
    header = [c.value for c in ws[1]]
    i = header.index("all_investors")
    values = [row[i].value for row in ws.iter_rows(min_row=2, max_row=ws.max_row)]
    # At least one round names co-investors alongside Paradigm itself.
    assert any(v and ";" in v for v in values)


def test_csv_matches_investments(wb):
    if not os.path.exists(CSV):
        pytest.skip("CSV is missing")
    with open(CSV, encoding="utf-8") as fh:
        rows = list(csv.reader(fh))
    assert len(rows) - 1 == wb["Investments"].max_row - 1
    assert rows[0][0] == "investment_id"
    for col in REQUIRED_COLUMNS:
        assert col in rows[0], col
