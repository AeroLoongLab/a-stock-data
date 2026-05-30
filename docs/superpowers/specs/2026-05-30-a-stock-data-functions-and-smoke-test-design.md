# a-stock-data 函数索引 + Smoke Test 设计

**日期：** 2026-05-30
**状态：** 已批准

---

## 目标

1. **A：** 建立标准化的函数索引，让不同 AI agent（Claude Code、Codex、Hermes 等）都能可靠地调用正确的端点函数，减少提取错误
2. **C：** 建立自动化 smoke test，验证 28 个端点的可用性（接口是否挂了 / 字段结构是否正确）

---

## 方案 A：函数索引

### 文件结构

```
a-stock-data/
├── SKILL.md                     # 现有的自包含 skill 文件，不动
├── functions.md                 # 人类可读函数索引
├── functions.json               # 机器可读签名（供 agent 解析）
└── tests/                       # smoke test
```

### `functions.md` — 人类可读索引

所有 agent 都能解析的 Markdown 表格，按层组织：

```markdown
# A股数据端点 — 函数索引

## Layer 1: 行情层

### `ths_hot_reason(date=None) -> pd.DataFrame`
同花顺当日强势股 + 题材归因（同花顺编辑部人工标注）

参数：
- `date: str` — YYYY-MM-DD，None=今天

返回字段：代码, 名称, 涨幅%, 题材归因, 成交额, 换手率%

代码位置：`SKILL.md#L573-L624`

---

### `dragon_tiger_board(code, trade_date, look_back=30) -> dict`
龙虎榜席位 + 买卖席位 TOP5 + 机构动向

参数：
- `code: str` — 6位股票代码
- `trade_date: str` — YYYY-MM-DD
- `look_back: int` — 回看天数，默认30

返回：`{"records": [...], "seats": {"buy": [...], "sell": [...]}, "institution": {"buy_amt": float, "sell_amt": float, "net_amt": float}}`

代码位置：`SKILL.md#L853-L937`
```

覆盖全部 28 个端点。

### `functions.json` — 机器可读签名

供 agent 提取函数签名的 JSON Schema：

```json
{
  "version": "3.1",
  "generated": "2026-05-30",
  "functions": [
    {
      "name": "ths_hot_reason",
      "layer": 1,
      "description": "同花顺当日强势股+题材归因（独家 reason tags）",
      "parameters": {
        "type": "object",
        "properties": {
          "date": {
            "type": "string",
            "description": "YYYY-MM-DD，None=今天"
          }
        }
      },
      "returns": "pd.DataFrame",
      "file_reference": "SKILL.md#L573-L624",
      "data_source": "同花顺 zx.10jqka.com.cn",
      "auth_required": false
    }
  ]
}
```

---

## 方案 C：Smoke Test

### 文件结构

```
tests/
├── conftest.py                  # 共享 fixture
├── test_layer1_market.py        # 行情层（mootdx/腾讯/百度）
├── test_layer2_research.py      # 研报层（东财/同花顺/iwencai）
├── test_layer3_signals.py       # 信号层（热点/北向/概念/资金流/龙虎榜/解禁/行业）
├── test_layer4_capital.py       # 资金面（两融/大宗/股东/分红/资金流120d）
├── test_layer5_news.py          # 新闻层
├── test_layer6_fundamentals.py  # 基础数据层
└── test_layer7_filings.py       # 公告层
```

### 测试策略

**不测数据准确性，只测：**
1. 端点返回非空数据
2. 字段结构正确（关键字段存在）
3. 类型正确（DataFrame / dict / list）

**网络策略：**
- `pytest.mark.unit` — mock 测试，测解析逻辑（本地，不走网络）
- `pytest.mark.smoke` — 真实网络测试，验证接口可用性
- 真实网络测试需要 ticker 参数，默认用 `600519`（贵州茅台）

```python
# 示例
def test_ths_hot_reason_smoke():
    """验证同花顺热点接口活着 + 字段结构正确"""
    result = ths_hot_reason()
    assert isinstance(result, pd.DataFrame)
    assert not result.empty
    # 验证关键字段存在（兼容中英文列名）
    assert any(col in result.columns for col in ["code", "代码", "CODE"])
    assert any(col in result.columns for col in ["reason", "题材归因"])

@pytest.mark.smoke
def test_ths_hot_reason_real_network():
    """真实网络测试（需要网络连接）"""
    result = ths_hot_reason()
    assert len(result) > 0
```

**数据源：**
- 测试数据默认用 `600519`（贵州茅台，全 A 股最常用验证标的）
- 每个端点的 smoke test 都有明确的 assert，避免假阳性

---

## 实现计划

### Phase 1：建立函数索引（独立文件）
1. 扫描 `SKILL.md` 提取全部 28 个端点的函数签名
2. 生成 `functions.md`（人类可读）
3. 生成 `functions.json`（机器可读）

### Phase 2：Smoke Test
1. 建立 `tests/conftest.py`
2. 按 layer 组织测试文件
3. 每个端点至少一个 smoke test
4. 配置 pytest marker（unit / smoke）

---

## 已知约束

- mootdx 需要 TCP 连通达信服务器（7709），海外环境会超时
- iwencai 需要 API Key，部分测试需要 `IWENCAI_API_KEY` 环境变量
- 部分端点（如龙虎榜）依赖特定交易日，数据可能为空（不是 bug，是市场原因）

---

## 验收标准

- [ ] `functions.md` 列出全部 28 个端点，格式统一
- [ ] `functions.json` 有效 JSON Schema，agent 可解析
- [ ] `tests/` 覆盖全部 28 个端点
- [ ] `pytest tests/ -m unit` 在无网络环境下通过
- [ ] `pytest tests/ -m smoke` 在有网络环境下通过