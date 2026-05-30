"""
Layer 6 fundamentals smoke tests — eastmoney_stock_info, sina_financial_report
"""
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
        "datetime": __import__("datetime"),
        "uuid": __import__("uuid"),
    }
    exec(match.group(0), ns)  # noqa: S307
    return ns[func_name]


def test_eastmoney_stock_info_smoke():
    """东财个股基本面返回dict含code/name/industry字段"""
    skill_md = Path("/home/huhaoran/workspace/stock/a-stock-data/SKILL.md")
    func = extract_function(skill_md, "eastmoney_stock_info")
    result = func("600519")
    assert isinstance(result, dict)
    assert "code" in result
    assert "name" in result
    assert "industry" in result


def test_sina_financial_report_smoke():
    """新浪财报三表返回list[dict]"""
    skill_md = Path("/home/huhaoran/workspace/stock/a-stock-data/SKILL.md")
    func = extract_function(skill_md, "sina_financial_report")
    result = func("600519", "lrb")
    assert isinstance(result, list)