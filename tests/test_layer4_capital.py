"""
Layer 4 capital flow smoke tests.
Extracts functions from SKILL.md and runs basic smoke checks.
"""
import re
import pytest
from pathlib import Path

SKILL_PATH = Path(__file__).parent.parent / "SKILL.md"


# Module-level cache of extracted functions
_func_cache = {}


def extract_function(name: str) -> callable:
    """Extract a function from SKILL.md by name.

    Uses a persistent cache so that helper functions (like eastmoney_datacenter)
    are extracted once and reused when extracting dependent functions.
    """
    if name in _func_cache:
        return _func_cache[name]

    content = SKILL_PATH.read_text(encoding="utf-8")

    # Find the code block containing this function
    parts = re.split(r'```python', content)
    for i in range(1, len(parts)):
        block = parts[i]
        if f'\ndef {name}(' not in block and f'\nasync def {name}(' not in block:
            continue
        end = block.find('```')
        if end == -1:
            raise ValueError(f"Function {name}: code block not closed")
        code = block[:end]

        func_match = re.search(rf'def {name}\(', code)
        if not func_match:
            func_match = re.search(rf'async def {name}\(', code)

        # Extract from beginning of block to end of this function
        code_before_func = code[:func_match.start()]
        func_and_after = code[func_match.start():]

        lines = func_and_after.split('\n')
        func_lines = []
        func_started = False

        for line in lines:
            stripped = line.strip()
            if not func_started:
                func_lines.append(line)
                if stripped.startswith('def ') or stripped.startswith('async def '):
                    func_started = True
                continue
            if not stripped:
                func_lines.append(line)
                continue
            indent = len(line) - len(line.lstrip())
            if (stripped.startswith('def ') or stripped.startswith('async def ')) and indent == 0:
                break
            func_lines.append(line)

        full_code = code_before_func + '\n'.join(func_lines)

        ns = {
            "requests": __import__("requests"),
            "pd": __import__("pandas"),
            "datetime": __import__("datetime"),
            "Path": __import__("pathlib").Path,
            "UA": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
        }
        # Put cached functions into namespace so they can be called
        ns.update(_func_cache)
        exec(full_code, ns)
        _func_cache[name] = ns[name]
        return ns[name]

    raise ValueError(f"Function {name} not found in SKILL.md")


# === Extract functions (helpers first, so dependents can reference them) ===

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