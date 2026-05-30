"""
Layer 5 news smoke tests — eastmoney_stock_news, cls_telegraph, eastmoney_global_news
"""
import re
import pytest
from pathlib import Path

SKILL_PATH = Path(__file__).parent.parent / "SKILL.md"


def extract_function(name: str):
    """Extract and exec a function from SKILL.md code block. Returns function object."""
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
        exec(full_code, ns)
        return ns[name]


# Smoke tests — extract_function called INSIDE test so no HTTP call at import time

def test_eastmoney_stock_news_smoke():
    """东财个股新闻返回list[dict]含title/time字段"""
    func = extract_function("eastmoney_stock_news")
    result = func("600519", page_size=5)
    assert isinstance(result, list)
    if result:
        assert "title" in result[0]
        assert "time" in result[0]


def test_cls_telegraph_smoke():
    """财联社快讯返回list[dict]含title/time字段"""
    func = extract_function("cls_telegraph")
    result = func(page_size=5)
    assert isinstance(result, list)
    if result:
        assert "title" in result[0]
        assert "time" in result[0]


def test_eastmoney_global_news_smoke():
    """东财全球资讯返回list[dict]含title/summary/time字段"""
    func = extract_function("eastmoney_global_news")
    result = func(page_size=5)
    assert isinstance(result, list)
    if result:
        assert "title" in result[0]
        assert "time" in result[0]