"""
Layer 7 filings smoke tests — cninfo_announcements
"""
from pathlib import Path

import pytest
import re


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


def test_cninfo_announcements_smoke():
    """巨潮公告返回list[dict]含title/date/url字段"""
    skill_md = Path("/home/huhaoran/workspace/stock/a-stock-data/SKILL.md")
    func = extract_function(skill_md, "cninfo_announcements")
    result = func("600519", page_size=5)
    assert isinstance(result, list)
    if result:
        assert "title" in result[0]
        assert "date" in result[0]
        assert "url" in result[0]