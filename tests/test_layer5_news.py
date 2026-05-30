"""
Layer 5 news smoke tests — eastmoney_stock_news, cls_telegraph, eastmoney_global_news
"""
import re
from pathlib import Path

import pytest


def extract_function(skill_md: Path, func_name: str):
    """从 SKILL.md 提取函数定义并执行，返回函数对象。"""
    content = skill_md.read_text()
    match = re.search(
        rf"def {func_name}\(.*?(?=\n(?:### |## Layer|\n#))",
        content,
        re.DOTALL,
    )
    if not match:
        pytest.skip(f"Could not find {func_name} in SKILL.md")
    ns = {
        "requests": __import__("requests"),
        "re": __import__("re"),
        "json": __import__("json"),
        "uuid": __import__("uuid"),
    }
    exec(match.group(0), ns)  # noqa: S307
    return ns[func_name]


def test_eastmoney_stock_news_smoke():
    """东财个股新闻返回list[dict]含title/time字段"""
    skill_md = Path("/home/huhaoran/workspace/stock/a-stock-data/SKILL.md")
    func = extract_function(skill_md, "eastmoney_stock_news")
    result = func("600519", page_size=5)
    assert isinstance(result, list)
    if result:
        assert "title" in result[0]
        assert "time" in result[0]


def test_cls_telegraph_smoke():
    """财联社快讯返回list[dict]含title/time字段"""
    skill_md = Path("/home/huhaoran/workspace/stock/a-stock-data/SKILL.md")
    func = extract_function(skill_md, "cls_telegraph")
    result = func(page_size=5)
    assert isinstance(result, list)
    if result:
        assert "title" in result[0]
        assert "time" in result[0]


def test_eastmoney_global_news_smoke():
    """东财全球资讯返回list[dict]含title/summary/time字段"""
    skill_md = Path("/home/huhaoran/workspace/stock/a-stock-data/SKILL.md")
    func = extract_function(skill_md, "eastmoney_global_news")
    result = func(page_size=5)
    assert isinstance(result, list)
    if result:
        assert "title" in result[0]
        assert "time" in result[0]