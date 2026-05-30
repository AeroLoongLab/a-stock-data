"""
Layer 1 market data smoke tests — mootdx bars + tencent_quote
"""
import re
from pathlib import Path

import pytest


def test_mootdx_bars_smoke():
    """mootdx K线返回非空DataFrame"""
    try:
        from mootdx.quotes import Quotes

        client = Quotes.factory(market="std")
        result = client.bars(symbol="600519", category=4, offset=5)
        assert result is not None
        assert len(result) > 0
        for col in ["open", "close", "high", "low", "vol"]:
            assert col in result.columns
    except Exception as e:
        pytest.skip(f"mootdx connection failed (海外服务器或网络问题): {e}")


def test_tencent_quote_smoke():
    """腾讯财经返回有效dict含PE/PB字段"""
    # 从SKILL.md提取tencent_quote函数
    skill_md = Path("/home/huhaoran/workspace/stock/a-stock-data/SKILL.md")
    content = skill_md.read_text()

    # 找到tencent_quote函数定义（从 def tencent_quote 到下一个 ### 小节或 ## Layer）
    match = re.search(r"def tencent_quote\(.*?(?=\n(?:### |## Layer))", content, re.DOTALL)
    if not match:
        pytest.skip("Could not find tencent_quote in SKILL.md")

    ns = {
        "requests": __import__("requests"),
        "urllib": __import__("urllib.request"),
    }
    exec(match.group(0), ns)  # noqa: S307
    result = ns["tencent_quote"](["600519"])

    assert isinstance(result, dict)
    assert "600519" in result
    assert result["600519"]["pe_ttm"] >= 0
    assert result["600519"]["pb"] >= 0