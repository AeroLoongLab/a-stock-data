# A-Stock-Data Defects Fix Design

**日期：** 2026-05-30
**状态：** 已批准

---

## 目标

修复 SKILL.md 中 6 个已确认的 defect（2 个 Critical/High 逻辑 bug + 2 个 API 问题 + 2 个已知问题）

---

## Defect 清单

### 1. `dragon_tiger_board` (line 853) — Critical

**问题：** `buy_data`/`sell_data` 在 `if records:` 块内定义（第 884-910 行），但第 915 行无条件访问：`for detail_data, side in [(buy_data, "buy"), (sell_data, "sell")]`

**修复：** 在 institution 循环前加 `if not records:` guard
```python
# 第 912-914 行修改为：
institution = {"buy_amt": 0, "sell_amt": 0, "net_amt": 0}
if not records:
    return {"records": records, "seats": seats, "institution": institution}
```

---

### 2. `baidu_kline_with_ma` (line 333) — High

**问题：** `md.get("marketData", "").split(";")` — 若 API 返回 `null`，`.get()` 返回 None 而非 ""，调用 `.split()` 时 AttributeError

**修复：**
```python
# 第 331-333 行修改为：
md = result.get("newMarketData", {}) or {}
market_data = md.get("marketData", "")
rows = market_data.split(";") if isinstance(market_data, str) else []
```

---

### 3. `eastmoney_stock_info` (line 1534) — High

**问题：** `r.json().get("data", {})` — 若 API 返回 `{"data": null}`，得到 None，`d.get("f57", "")` 触发 `AttributeError: 'NoneType' object has no attribute 'get'`

**修复：**
```python
# 第 1531 行修改为：
resp = r.json()
d = resp.get("data") if isinstance(resp, dict) else {}
if not d:
    return {"code": code, "name": "", "industry": "", "total_shares": 0,
            "float_shares": 0, "mcap": 0, "float_mcap": 0, "list_date": "", "price": 0}
```

---

### 4. `full_valuation` (line 1762/1766) — High

**问题 4a：** `vals[39]` 无长度检查，腾讯返回字段不足时 IndexError

**问题 4b：** `ths_eps_forecast(code)` pandas 3.0 下崩溃

**修复：**
```python
# vals 访问前加长度检查
vals = data.split('"')[1].split("~")
if len(vals) < 53:
    raise ValueError(f"腾讯API返回字段不足: {len(vals)}")

# ths_eps_forecast 加 try/except
try:
    eps_df = ths_eps_forecast(code)
    if eps_df.empty:
        eps_forecast = None
    else:
        eps_forecast = float(eps_df.iloc[0]["均值"]) if "均值" in eps_df.columns else None
except Exception:
    eps_forecast = None
```

---

### 5. `ths_eps_forecast` (line 434) — Known

**问题：** pandas 3.0 改变了 `pd.read_html()` 的行为，导致 HTML 解析崩溃

**修复：**
```python
# 第 448 行修改为：
dfs = pd.read_html(StringIO(r.text), flavor="html5lib")
```

---

### 6. `cls_telegraph` (line 1405) — Known

**问题：** 财联社 `nodeapi/telegraphList` 端点返回 404（API 已变更）

**修复：** 异常时返回空列表，不阻塞流程
```python
def cls_telegraph(page_size: int = 50) -> list[dict]:
    url = "https://www.cls.cn/nodeapi/telegraphList"
    try:
        r = requests.get(url, params={"rn": str(page_size), "page": "1"},
                        headers={"User-Agent": UA, "Referer": "https://www.cls.cn/"}, timeout=10)
        if r.status_code != 200:
            raise ValueError(f"cls API status: {r.status_code}")
        d = r.json()
    except Exception:
        return []  # API 不可用时返回空列表，不阻塞流程
    rows = []
    for item in d.get("data", {}).get("roll_data", []):
        rows.append({
            "title": item.get("title", "") or item.get("brief", ""),
            "content": item.get("content", "") or item.get("brief", ""),
            "time": item.get("ctime", ""),
        })
    return rows
```

---

## 验收标准

- [ ] `dragon_tiger_board` — 无 records 时不报 NameError
- [ ] `baidu_kline_with_ma` — API 返回 null 时不 crash
- [ ] `eastmoney_stock_info` — API 返回 `{"data": null}` 时不 crash
- [ ] `full_valuation` — vals 字段不足时不 IndexError，`ths_eps_forecast` 失败时优雅降级
- [ ] `ths_eps_forecast` — pandas 3.0 下不崩溃
- [ ] `cls_telegraph` — API 不可用时返回空列表而非抛异常
- [ ] `pytest tests/ -v` — 15 passed, 1 skipped（mootdx）, 0 failed

---

## 已知约束

- `cls_telegraph` 修复只是优雅失败，API 本身需要后续找到新端点才能恢复功能
- 测试在海外环境运行，部分 API（腾讯/东财）需代理才能访问