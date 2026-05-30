"""
Layer 4 capital flow smoke tests.
Extracts functions from SKILL.md and runs basic smoke checks.
"""
import re
import pytest
from pathlib import Path

SKILL_PATH = Path(__file__).parent.parent / "SKILL.md"


def extract_function(name: str) -> callable:
    """Extract a single function from SKILL.md by name."""
    content = SKILL_PATH.read_text(encoding="utf-8")
    # Match from def name(...) to the next def or end of file
    pattern = rf'def {name}\(.*?(?=\n(?:def [a-zA-Z_]|---))'
    match = re.search(pattern, content, re.DOTALL)
    if not match:
        raise ValueError(f"Function {name} not found in SKILL.md")
    ns = {
        "requests": __import__("requests"),
        "pd": __import__("pandas"),
        "datetime": __import__("datetime"),
        "Path": __import__("pathlib").Path,
        "UA": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
    }
    exec(match.group(0), ns)
    return ns[name]


# === Extract functions ===

eastmoney_datacenter = extract_function("eastmoney_datacenter")
margin_trading = extract_function("margin_trading")
block_trade = extract_function("block_trade")
holder_num_change = extract_function("holder_num_change")
dividend_history = extract_function("dividend_history")
stock_fund_flow_120d = extract_function("stock_fund_flow_120d")


# === Smoke tests ===

def test_margin_trading_smoke():
    """融资融券返回list[dict]含date/rzye/rqye字段"""
    result = margin_trading("600519", page_size=5)
    assert isinstance(result, list)
    if result:
        assert "date" in result[0]
        assert "rzye" in result[0]
        assert "rqye" in result[0]


def test_block_trade_smoke():
    """大宗交易返回list[dict]"""
    result = block_trade("600519", page_size=5)
    assert isinstance(result, list)


def test_holder_num_change_smoke():
    """股东户数变化返回list[dict]含date/holder_num字段"""
    result = holder_num_change("600519", page_size=5)
    assert isinstance(result, list)
    if result:
        assert "date" in result[0]
        assert "holder_num" in result[0]


def test_dividend_history_smoke():
    """分红送转历史返回list[dict]"""
    result = dividend_history("600519", page_size=5)
    assert isinstance(result, list)


def test_stock_fund_flow_120d_smoke():
    """个股资金流120日返回list[dict]含date/main_net字段"""
    result = stock_fund_flow_120d("600519")
    assert isinstance(result, list)
    if result:
        assert "date" in result[0]
        assert "main_net" in result[0]