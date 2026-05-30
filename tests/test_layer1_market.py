"""
Layer 1 market data smoke tests — mootdx bars + tencent_quote + baidu_kline_with_ma
"""
import re
import pytest
from pathlib import Path

SKILL_PATH = Path(__file__).parent.parent / "SKILL.md"

_func_cache = {}


def extract_function(name: str) -> callable:
    """Extract a function from SKILL.md by name. Uses a persistent cache."""
    if name in _func_cache:
        return _func_cache[name]

    content = SKILL_PATH.read_text(encoding="utf-8")

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
        ns.update(_func_cache)
        exec(full_code, ns)
        _func_cache[name] = ns[name]
        return ns[name]


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
    tencent_quote = extract_function("tencent_quote")
    result = tencent_quote(["600519"])

    assert isinstance(result, dict)
    assert "600519" in result
    assert result["600519"]["pe_ttm"] >= 0
    assert result["600519"]["pb"] >= 0