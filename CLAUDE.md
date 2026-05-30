# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is an **A-Share full-stack data toolkit** delivered as a Claude Code Skill file (`SKILL.md`). It provides 28 data endpoints across 7 layers from 13 Chinese financial data sources (Eastmoney, Tencent, THS, Baidu, Sina, mootdx, cninfo, CLS, etc.).

The skill file is self-contained — all Python code is embedded directly in `SKILL.md`. To use it, place `SKILL.md` in `~/.claude/skills/a-stock-data/`.

## Architecture

```
A-Share Full-Stack Data · 7-Layer · V3.1
│
├── Layer 1: Market Data     mootdx (TCP) + Tencent (HTTP) + Baidu K-line
├── Layer 2: Research        Eastmoney reportapi + THS consensus EPS + iwencai NL
├── Layer 3: Signals         THS hot stocks + northbound + Baidu concepts + Eastmoney fund flow + dragon tiger + lockup + industry ranking
├── Layer 4: Capital Flow    Eastmoney datacenter (margin/blocks/holders/dividends/fund flow 120d)
├── Layer 5: News           Eastmoney + CLS flash + global news
├── Layer 6: Fundamentals   mootdx finance (37 fields) + F10 + Eastmoney stock info + Sina statements
└── Layer 7: Filings        cninfo (full market announcements) + mootdx F10
```

## Dependencies

```bash
pip install mootdx requests pandas stockstats
python -m pytest tests/ -v
```

V3.0 removed akshare entirely — all data sources are direct HTTP API calls (except mootdx which uses TCP on port 7709).

## Key Patterns

**Market prefix mapping** (used throughout):
```python
def get_prefix(code: str) -> str:
    if code.startswith(("6", "9")): return "sh"   # Shanghai
    elif code.startswith("8"): return "bj"          # Beijing
    else: return "sz"                               # Shenzhen
```

**Ticker normalization**: All functions accept `688017`, `SH688017`, `688017.SH`, etc. and normalize to 6-digit strings internally.

**Eastmoney datacenter helper**: Dragon tiger board, lockup expiry, margin trading, block trades, shareholder count, and dividends all share the same base URL and request pattern (`eastmoney_datacenter()` function in SKILL.md).

**iwencai only requires auth**: All data sources are free except iwencai semantic search (requires API key from https://www.iwencai.com/skillhub).

## Skills Directory

```
skills/                # Sub-skills (e.g. report-search/)
```

## Common Tasks

**Adding a new endpoint**: Add Python code directly to `SKILL.md` under the appropriate layer section. Follow the existing patterns — most endpoints use `requests.get()` with a consistent `UA` header and return `list[dict]`.

**Testing an endpoint**: Run smoke tests with `pytest tests/`, or execute Python code directly:

```bash
.venv/bin/python -c "from mootdx.quotes import Quotes; ..."
```

**V3.1 breaking changes to remember**:
- Fund flow (signal layer) switched from Baidu PAE to Eastmoney push2
- Block trade report name changed from `RPT_DATA_OCCURTRADE` to `RPT_DATA_BLOCKTRADE`
- Dragon tiger institution detail changed from `RPT_ORGANIZATION_BUSSINESS` to BUY/SELL seat filtering with `OPERATEDEPT_CODE="0"`
- Eastmoney global news requires `req_trace` UUID parameter (returns 403 without it)
- cninfo filing `stock` param format changed from `"{code},{plate}"` to `"{code},{orgId}"` (e.g., `600519,gssh0600519`)

## Network Environment

When routing through a VPN/proxy (e.g., Mac network sharing), **push2.eastmoney.com and push2his.eastmoney.com may return empty responses** ("Empty reply from server"). Other Eastmoney endpoints (datacenter-web, search-api-web) work normally. This is a server-side IP rejection, not a code bug. Run from a direct Chinese IP for full coverage.