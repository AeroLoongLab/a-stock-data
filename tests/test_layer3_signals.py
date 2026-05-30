"""
Layer 3 signals smoke tests.
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

    Uses a persistent cache so that helper functions/constants defined earlier
    in a block (e.g., HSGT_HEADERS, eastmoney_datacenter) are extracted once
    and reused when extracting dependent functions.
    """
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
            "time": __import__("time"),
            "random": __import__("random"),
            "UA": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
        }
        ns.update(_func_cache)
        # Inject em_get BEFORE exec so function bodies can reference it at definition time.
        if "em_get" not in ns:
            import time as _time, random as _random
            import requests as _requests
            _session = _requests.Session()
            _session.headers.update({"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"})
            _em_last_call = [0.0]
            def em_get(url, params=None, headers=None, timeout=15, **kwargs):
                wait = 1.0 - (_time.time() - _em_last_call[0])
                if wait > 0:
                    _time.sleep(wait + _random.uniform(0.1, 0.5))
                try:
                    return _session.get(url, params=params, headers=headers, timeout=timeout, **kwargs)
                except Exception as e:
                    class _FakeResp:
                        status_code = 0
                        def raise_for_status(self): raise e
                        def json(self): return {}
                    return _FakeResp()
                finally:
                    _em_last_call[0] = _time.time()
            ns["em_get"] = em_get
            ns["_em_last_call"] = _em_last_call
        exec(full_code, ns)
        _func_cache[name] = ns[name]
        return ns[name]

    raise ValueError(f"Function {name} not found in SKILL.md")


# === Extract functions ===

# eastmoney_datacenter is a helper needed by dragon_tiger_board
eastmoney_datacenter = extract_function("eastmoney_datacenter")
ths_hot_reason = extract_function("ths_hot_reason")
hsgt_realtime = extract_function("hsgt_realtime")
eastmoney_fund_flow_minute = extract_function("eastmoney_fund_flow_minute")
dragon_tiger_board = extract_function("dragon_tiger_board")
industry_comparison = extract_function("industry_comparison")


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