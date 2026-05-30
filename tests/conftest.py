# tests/conftest.py
import pytest
import os

# 默认测试股票（贵州茅台，全A最常用验证标的）
DEFAULT_TICKER = "600519"
DEFAULT_TRADE_DATE = "2026-05-16"  # 一个已知有龙虎榜数据的交易日

@pytest.fixture
def default_ticker():
    return DEFAULT_TICKER

@pytest.fixture
def default_trade_date():
    return DEFAULT_TRADE_DATE

@pytest.fixture
def iwencai_api_key():
    key = os.environ.get("IWENCAI_API_KEY", "")
    if not key:
        pytest.skip("IWENCAI_API_KEY not set")
    return key