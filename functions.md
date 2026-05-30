# A股数据工具包 - 函数索引

七层架构，29 个端点，全部实测可用。

---

## Layer 1: 行情层

### `mootdx_bars(symbol, category=4, offset=10) -> DataFrame`
mootdx K线数据（TCP 7709，连通达信服务器）

**参数：**
- `symbol: str` — 6位股票代码
- `category: int` — K线周期（4=日线，5=周线，6=月线，7=1分钟，8=5分钟，9=15分钟，10=30分钟，11=60分钟）
- `offset: int` — 返回数量

**返回字段：** open, close, high, low, vol, amount, datetime

**代码位置：** `SKILL.md#L180`

---

### `tencent_quote(codes: list[str]) -> dict[str, dict]`
腾讯财经实时行情（HTTP GBK，不封IP）

**参数：**
- `codes: list[str]` — 6位股票代码列表，支持指数（000001/000300/399006）和ETF（510050/510300）

**返回字段：** name, price, pe_ttm, pb, mcap_yi, float_mcap_yi, turnover_pct, limit_up, limit_down, change_amt, change_pct, high, low, last_close, open, amplitude_pct, vol_ratio, pe_static...

**代码位置：** `SKILL.md#L208`

---

### `baidu_kline_with_ma(code: str, start_time: str = "") -> dict`
百度股市通K线（自带MA5/MA10/MA20均价）

**参数：**
- `code: str` — 6位股票代码
- `start_time: str` — 起始时间（空字符串则返回最近）

**返回字段：** keys（含 ma5avgprice, ma10avgprice, ma20avgprice）, rows（time, open, close, high, low, volume, amount...）

**代码位置：** `SKILL.md#L310`

---

## Layer 2: 研报层

### `eastmoney_reports(code: str, max_pages: int = 5) -> list[dict]`
东财研报列表（reportapi.eastmoney.com，免费无key）

**参数：**
- `code: str` — 6位股票代码
- `max_pages: int` — 最大页数

**返回字段：** title, publishDate, orgSName, infoCode, predictThisYearEps, predictNextYearEps, predictNextTwoYearEps, emRatingName, indvInduName...

**代码位置：** `SKILL.md#L361`

---

### `download_pdf(record: dict, target_dir: str = "./reports") -> str | None`
下载研报PDF

**参数：**
- `record: dict` — eastmoney_reports 返回的记录，需包含 infoCode
- `target_dir: str` — 保存目录

**返回：** 保存路径或 None

**代码位置：** `SKILL.md#L386`

---

### `ths_eps_forecast(code: str) -> pd.DataFrame`
同花顺机构一致预期EPS（直连 basic.10jqka.com.cn）

**参数：**
- `code: str` — 6位股票代码

**返回字段：** 年度, 预测机构数, 最小值, 均值, 最大值（"均值" = 机构一致预期EPS）

**代码位置：** `SKILL.md#L434`

---

### `iwencai_search(query: str, channel: str = "report", size: int = 50) -> list[dict]`
iwencai NL语义搜索研报（需 API Key + X-Claw Headers）

**参数：**
- `query: str` — 自然语言查询
- `channel: str` — "report"(研报) / "announcement"(公告) / "news"(新闻)
- `size: int` — 返回数量（默认10，最大50）

**返回字段：** uid, title, publish_date, score, extra (organization...)

**代码位置：** `SKILL.md#L487`

---

### `iwencai_query(query: str, page: int = 1, limit: int = 50) -> list[dict]`
iwencai NL数据查询（结构化字段）

**参数：**
- `query: str` — 自然语言查询
- `page: int` — 页码
- `limit: int` — 每页数量

**返回字段：** DataFrame-like rows

**代码位置：** `SKILL.md#L515`

---

## Layer 3: 信号层

### `ths_hot_reason(date: str = None) -> pd.DataFrame`
同花顺当日强势股归因（零鉴权，73ms）

**参数：**
- `date: str` — 'YYYY-MM-DD' 格式，None=今天

**返回字段：** 代码, 名称, 收盘价, 涨跌额, 涨幅%, 换手率%, 成交额, 成交量, 大单净量, 市场, **题材归因**（核心字段，人工运营tags）

**代码位置：** `SKILL.md#L577`

---

### `hsgt_realtime() -> pd.DataFrame`
同花顺北向资金当日实时分钟流向（沪股通+深股通）

**参数：** 无

**返回字段：** time, hgt_yi（沪股通累计净买入，亿元）, sgt_yi（深股通累计净买入，亿元）

**代码位置：** `SKILL.md#L660`

---

### `baidu_concept_blocks(code: str) -> dict`
百度股市通概念板块归属（行业/概念/地域三维分类）

**参数：**
- `code: str` — 6位股票代码

**返回字段：** industry（行业）, concept（概念）, region（地域）, concept_tags（概念标签列表）

**代码位置：** `SKILL.md#L741`

---

### `eastmoney_fund_flow_minute(code: str) -> list[dict]`
东财 push2 个股资金流向（分钟级，当日盘中）

**参数：**
- `code: str` — 6位股票代码

**返回字段：** time, main_net, small_net, mid_net, large_net, super_net（单位：元）

**代码位置：** `SKILL.md#L792`

---

### `dragon_tiger_board(code: str, trade_date: str, look_back: int = 30) -> dict`
龙虎榜席位（个股上榜记录+买卖席位TOP5+机构动向）

**参数：**
- `code: str` — 6位股票代码
- `trade_date: str` — YYYY-MM-DD
- `look_back: int` — 回看天数

**返回字段：** records（date, reason, net_buy, turnover）, seats（buy, sell）, institution（buy_amt, sell_amt, net_amt）

**代码位置：** `SKILL.md#L853`

---

### `lockup_expiry(code: str, trade_date: str, forward_days: int = 90) -> dict`
限售解禁日历（历史解禁+未来90天待解禁）

**参数：**
- `code: str` — 6位股票代码
- `trade_date: str` — YYYY-MM-DD
- `forward_days: int` — 向前天数

**返回字段：** history（date, type, shares, ratio）, upcoming（同上）

**代码位置：** `SKILL.md#L946`

---

### `industry_comparison(top_n: int = 20) -> dict`
东财行业板块涨跌幅排名（全市场行业轮动）

**参数：**
- `top_n: int` — 返回前N名和后N名

**返回字段：** top（rank, name, change_pct, code, up_count, down_count, leader, leader_change）, bottom, total

**代码位置：** `SKILL.md#L1011`

---

### `daily_dragon_tiger(trade_date: str = None, min_net_buy: float = None) -> dict`
全市场龙虎榜（当日所有上榜股票+净买额排名）

**参数：**
- `trade_date: str` — YYYY-MM-DD（默认当日）
- `min_net_buy: float` — 净买入下限（万元），None 不过滤

**返回字段：** date, total_records, stocks（code, name, reason, close, change_pct, net_buy_wan, buy_wan, sell_wan, turnover_pct）

**代码位置：** `SKILL.md#L1067`

---

## Layer 4: 资金面 / 筹码层

### `margin_trading(code: str, page_size: int = 30) -> list[dict]`
融资融券明细（日级）

**参数：**
- `code: str` — 6位股票代码
- `page_size: int` — 返回数量

**返回字段：** date, rzye（融资余额）, rzmre（融资买入）, rzche（融资偿还）, rqye（融券余额）, rqmcl（融券卖出量）, rqchl（融券偿还量）, rzrqye（融资融券余额合计）

**代码位置：** `SKILL.md#L1156`

---

### `block_trade(code: str, page_size: int = 20) -> list[dict]`
大宗交易记录

**参数：**
- `code: str` — 6位股票代码
- `page_size: int` — 返回数量

**返回字段：** date, price, close, premium_pct, vol, amount, buyer, seller

**代码位置：** `SKILL.md#L1190`

---

### `holder_num_change(code: str, page_size: int = 10) -> list[dict]`
股东户数变化（季度级）

**参数：**
- `code: str` — 6位股票代码
- `page_size: int` — 返回数量

**返回字段：** date, holder_num, change_num, change_ratio（环比%）, avg_shares（户均持股）

**代码位置：** `SKILL.md#L1227`

---

### `dividend_history(code: str, page_size: int = 20) -> list[dict]`
分红送转历史

**参数：**
- `code: str` — 6位股票代码
- `page_size: int` — 返回数量

**返回字段：** date, bonus_rmb（每股派息）, transfer_ratio（每10股转增）, bonus_ratio（每10股送股）, plan（进度）

**代码位置：** `SKILL.md#L1259`

---

### `stock_fund_flow_120d(code: str) -> list[dict]`
个股资金流（120日，日级）

**参数：**
- `code: str` — 6位股票代码

**返回字段：** date, main_net, small_net, mid_net, large_net, super_net（单位：元）

**代码位置：** `SKILL.md#L1292`

---

## Layer 5: 新闻层

### `eastmoney_stock_news(code: str, page_size: int = 20) -> list[dict]`
东财个股新闻（search-api-web JSONP接口）

**参数：**
- `code: str` — 6位股票代码
- `page_size: int` — 返回数量

**返回字段：** title, content, time, source, url

**代码位置：** `SKILL.md#L1355`

---

### `cls_telegraph(page_size: int = 50) -> list[dict]`
财联社快讯（全市场实时电报）

**参数：**
- `page_size: int` — 返回数量

**返回字段：** title, content, time

**代码位置：** `SKILL.md#L1405`

---

### `eastmoney_global_news(page_size: int = 50) -> list[dict]`
东财全球资讯（7x24滚动）

**参数：**
- `page_size: int` — 返回数量

**返回字段：** title, summary, time

**代码位置：** `SKILL.md#L1438`

---

## Layer 6: 基础数据层

### `mootdx_finance(symbol: str) -> dict`
mootdx 财务快照（37字段季报数据）

**参数：**
- `symbol: str` — 6位股票代码

**返回字段：** liutongguben, zongguben, eps, bvps, roe, profit, income, meigujingzichan, meigugongjijin, meiguweifeipeili 等37个字段

**代码位置：** `SKILL.md#L1481`

---

### `mootdx_f10(symbol: str, name: str) -> str`
mootdx F10 公司文本资料（9大类）

**参数：**
- `symbol: str` — 6位股票代码
- `name: str` — 类别（"最新提示"/"公司概况"/"财务分析"/"股东研究"/"股本结构"/"资本运作"/"业内点评"/"行业分析"/"公司大事"）

**返回：** 文本内容

**代码位置：** `SKILL.md#L1495`

---

### `eastmoney_stock_info(code: str) -> dict`
东财个股基本面信息（直连 push2 API）

**参数：**
- `code: str` — 6位股票代码

**返回字段：** code, name, industry, total_shares, float_shares, mcap, float_mcap, list_date, price

**代码位置：** `SKILL.md#L1517`

---

### `sina_financial_report(code: str, report_type: str = "lrb") -> list[dict]`
新浪财报三表（资产负债表/利润表/现金流量表）

**参数：**
- `code: str` — 6位股票代码
- `report_type: str` — "fzb"(资产负债表) / "lrb"(利润表) / "llb"(现金流量表)

**返回：** 按报告期排序的财务数据列表

**代码位置：** `SKILL.md#L1554`

---

## Layer 7: 公告层

### `cninfo_announcements(code: str, page_size: int = 30) -> list[dict]`
巨潮公告全文检索（cninfo.com.cn）

**参数：**
- `code: str` — 6位股票代码
- `page_size: int` — 返回数量

**返回字段：** title, type, date, url

**代码位置：** `SKILL.md#L1611`

---

## 附录：辅助函数

### `eastmoney_datacenter(report_name: str, columns: str = "ALL", filter_str: str = "", page_size: int = 50, sort_columns: str = "", sort_types: str = "-1") -> list[dict]`
东财数据中心统一查询（龙虎榜/解禁/融资融券/大宗交易/股东户数/分红共用）

**代码位置：** `SKILL.md#L154`

---

### `get_prefix(code: str) -> str`
6位代码转市场前缀（sh/sz/bj）

**代码位置：** `SKILL.md#L122`

---

### `_cninfo_ts_to_date(ts) -> str`
巨潮 Unix 毫秒时间戳转日期字符串

**代码位置：** `SKILL.md#L1605`

---

### `dedup_articles(articles: list[dict]) -> list[dict]`
iwencai 搜索结果去重（同uid仅保留score最高）

**代码位置：** `SKILL.md#L543`

---

### `_northbound_cache_path() -> Path`
北向资金本地 CSV 缓存路径

**代码位置：** `SKILL.md#L682`

---

### `_save_northbound_snapshot(date: str, hgt: float, sgt: float)`
写入北向资金缓存

**代码位置：** `SKILL.md#L688`

---

### `_load_northbound_history(n: int = 20) -> pd.DataFrame`
读取北向资金历史

**代码位置：** `SKILL.md#L703`