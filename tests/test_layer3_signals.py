"""
Layer 3 signals smoke tests.
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
    }
    exec(match.group(0), ns)
    return ns[name]


# === Extract functions ===

ths_hot_reason = extract_function("ths_hot_reason")
hsgt_realtime = extract_function("hsgt_realtime")
eastmoney_fund_flow_minute = extract_function("eastmoney_fund_flow_minute")
dragon_tiger_board = extract_function("dragon_tiger_board")
industry_comparison = extract_function("industry_comparison")
# dragon_tiger_board depends on this helper
eastmoney_datacenter = extract_function("eastmoney_datacenter")


# === Smoke tests ===

def test_ths_hot_reason_smoke():
    """同花顺热点接口返回含code/reason列的DataFrame"""
    result = ths_hot_reason()
    if result.empty:
        pytest.skip("Empty result, possibly non-trading day")
    has_code = any(col in result.columns for col in ["code", "代码", "CODE"])
    has_reason = any(col in result.columns for col in ["reason", "题材归因"])
    assert has_code, f"缺少code列，当前列: {result.columns.tolist()}"
    assert has_reason, f"缺少reason列，当前列: {result.columns.tolist()}"


def test_hsgt_realtime_smoke():
    """沪深股通实时分钟流向返回DataFrame含hgt/sgt列"""
    result = hsgt_realtime()
    if result.empty:
        pytest.skip("Empty result, possibly non-trading day")
    assert any(col in result.columns for col in ["time", "hgt_yi", "sgt_yi"])


def test_dragon_tiger_board_smoke():
    """龙虎榜返回dict含records/seats/institution字段"""
    result = dragon_tiger_board("600519", "2026-05-16", look_back=10)
    assert isinstance(result, dict)
    assert "records" in result
    assert "seats" in result
    assert "institution" in result


def test_industry_comparison_smoke():
    """东财行业涨跌幅排名返回dict含top/total字段"""
    result = industry_comparison(20)
    assert isinstance(result, dict)
    assert "top" in result
    assert "total" in result
    assert result["total"] > 0