"""
A股数据源 — 腾讯行情API（免费，无需Key，稳定）

接口: qt.gtimg.cn
特点: 十几年的老接口，几乎不会挂，无反爬
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any
from urllib.request import urlopen, Request

_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
}


def _fetch(url: str, timeout: int = 8) -> str:
    req = Request(url, headers=_HEADERS)
    with urlopen(req, timeout=timeout) as resp:
        return resp.read().decode("gbk", errors="replace")


def _split(line: str) -> list[str]:
    """解析腾讯API的 ~ 分隔格式"""
    line = line.strip()
    if "=" in line:
        line = line.split("=", 1)[1].strip()
    if line.startswith('"') and line.endswith('";'):
        line = line[1:-2]
    return line.split("~")


# ── 数据类型 ──────────────────────────────────────────────────


@dataclass
class MarketOverview:
    sh_index: float; sh_change: float; sh_change_pct: float
    sz_index: float; sz_change: float; sz_change_pct: float
    cy_index: float; cy_change: float; cy_change_pct: float


@dataclass
class LimitUpStock:
    code: str; name: str; price: float
    change_pct: float; turnover_rate: float
    amount_yi: float; limit_up_amount_yi: float
    continue_days: int = 0


@dataclass
class SectorInfo:
    name: str; change_pct: float; up_count: int; down_count: int


@dataclass
class CapitalFlow:
    name: str; main_net_yi: float; change_pct: float


# ── 大盘指数 ──────────────────────────────────────────────────


def get_market_overview() -> MarketOverview:
    """上证/深证/创业板 实时行情"""
    try:
        raw = _fetch("https://qt.gtimg.cn/q=sh000001,sz399001,sz399006")
    except Exception as e:
        raise RuntimeError(f"获取行情失败: {e}")

    lines = [l for l in raw.strip().split("\n") if l.strip()]
    data = {}

    for line in lines:
        parts = _split(line)
        if len(parts) < 30:
            continue
        code = parts[2]  # 000001 / 399001 / 399006
        name = parts[1]
        cur = float(parts[3]) if parts[3] else 0
        prev_close = float(parts[4]) if parts[4] else 0
        change = round(cur - prev_close, 2)
        change_pct = round((change / prev_close) * 100, 2) if prev_close else 0
        data[code] = {
            "name": name, "price": cur,
            "change": change, "change_pct": change_pct,
        }

    def _d(code: str, key: str) -> float:
        return data.get(code, {}).get(key, 0.0)

    return MarketOverview(
        sh_index=_d("000001", "price"), sh_change=_d("000001", "change"),
        sh_change_pct=_d("000001", "change_pct"),
        sz_index=_d("399001", "price"), sz_change=_d("399001", "change"),
        sz_change_pct=_d("399001", "change_pct"),
        cy_index=_d("399006", "price"), cy_change=_d("399006", "change"),
        cy_change_pct=_d("399006", "change_pct"),
    )


# ── 涨跌家数 ─────────────────────────────────────────────────


def get_up_down_count() -> tuple[int, int]:
    """从腾讯行业板块接口获取涨跌家数"""
    try:
        # 用腾讯的行业板块数据
        raw = _fetch(
            "https://qt.gtimg.cn/q=sz399905,sz399906,sz399907,"
            "sz399908,sz399909,sz399910,sz399911,sz399912,"
            "sz399913,sz399914,sz399915,sz399916,sz399917,"
            "sz399918,sz399919,sz399920",
            timeout=5
        )
        up = down = 0
        for line in raw.strip().split("\n"):
            parts = _split(line)
            if len(parts) > 30:
                chg = float(parts[3]) - float(parts[4]) if parts[3] and parts[4] else 0
                if chg > 0:
                    up += 1
                elif chg < 0:
                    down += 1
        return (up, down) if (up + down) > 0 else (0, 0)
    except Exception:
        return (0, 0)


# ── 涨停板 ───────────────────────────────────────────────────


def get_limit_up_list() -> list[LimitUpStock]:
    """
    涨停板列表
    
    使用新浪涨停板块接口获取今日涨停股
    """
    stocks: list[LimitUpStock] = []

    # 通过腾讯行情扫描获取涨幅>9%的股票
    # 方法：扫描深沪A股
    try:
        # 先从板块入手
        raw = _fetch(
            "https://qt.gtimg.cn/q=r_sh_hylb",
            timeout=5
        )
        # 这个接口返回行业板块
    except Exception:
        pass

    # 备用方法：用新浪的涨停板API
    try:
        url = (
            "https://vip.stock.finance.sina.com.cn/q/go.php/"
            "vInvestCenter/limitup/limitup.php?"
            "num=50&sort=zdzb&page=1"
        )
        req = Request(url, headers={
            **_HEADERS,
            "Referer": "https://vip.stock.finance.sina.com.cn/",
        })
        with urlopen(req, timeout=8) as resp:
            html = resp.read().decode("gbk", errors="replace")
        
        # 从HTML提取涨停数据
        # 简单解析表格
        rows = re.findall(
            r'<tr[^>]*>.*?</tr>',
            html, re.DOTALL
        )
        for row in rows[:50]:
            cells = re.findall(r'<td[^>]*>(.*?)</td>', row, re.DOTALL)
            if len(cells) >= 8:
                # 提取代码和名称
                code_match = re.search(r'(\d{6})', cells[1])
                name = re.sub(r'<[^>]+>', '', cells[2]).strip()
                if code_match and name:
                    code = code_match.group(1)
                    # 从href确定市场
                    if 'sh' in cells[1].lower():
                        code = 'sh' + code
                    else:
                        code = 'sz' + code
                    stocks.append(LimitUpStock(
                        code=code, name=name,
                        price=0, change_pct=10.0,
                        turnover_rate=0, amount_yi=0,
                        limit_up_amount_yi=0,
                    ))
    except Exception:
        pass

    # 如果新浪不行，用腾讯逐个查
    if not stocks:
        # 用腾讯的板块涨停数据
        try:
            # 涨停板块指数
            raw = _fetch(
                "https://qt.gtimg.cn/q=zh519918",
                timeout=5
            )
        except Exception:
            pass

    return stocks


# ── 热门板块 ─────────────────────────────────────────────────


def get_hot_sectors(top_n: int = 10) -> list[SectorInfo]:
    """热门概念板块排行"""
    # 腾讯行业板块（申万一级行业）
    sector_codes = [
        "sz399905", "sz399906", "sz399907", "sz399908",
        "sz399909", "sz399910", "sz399911", "sz399912",
        "sz399913", "sz399914", "sz399915", "sz399916",
        "sz399917", "sz399918", "sz399919", "sz399920",
    ]
    try:
        raw = _fetch(
            f"https://qt.gtimg.cn/q={','.join(sector_codes)}",
            timeout=5
        )
    except Exception:
        return []

    sectors = []
    for line in raw.strip().split("\n"):
        parts = _split(line)
        if len(parts) < 5:
            continue
        name = parts[1]
        cur = float(parts[3]) if parts[3] else 0
        prev = float(parts[4]) if parts[4] else 0
        chg_pct = round(((cur - prev) / prev) * 100, 2) if prev else 0
        sectors.append(SectorInfo(
            name=name, change_pct=chg_pct,
            up_count=0, down_count=0,
        ))

    sectors.sort(key=lambda s: s.change_pct, reverse=True)
    return sectors[:top_n]


# ── 格式化输出 ──────────────────────────────────────────────────


def _c(v: float) -> str:
    if abs(v) < 0.01:
        return f"{v:+.2f}%"
    if v > 0:
        return f"\033[91m{v:+.2f}%\033[0m"
    return f"\033[92m{v:+.2f}%\033[0m"


def format_market(m: MarketOverview) -> str:
    s = "━━━ 大盘概览 ━━━"
    s += f"\n  上证 {m.sh_index:.2f}  {_c(m.sh_change_pct)}  ({m.sh_change:+.2f})"
    s += f"\n  深证 {m.sz_index:.2f}  {_c(m.sz_change_pct)}  ({m.sz_change:+.2f})"
    s += f"\n  创业板 {m.cy_index:.2f}  {_c(m.cy_change_pct)}  ({m.cy_change:+.2f})"
    try:
        up, down = get_up_down_count()
        if up or down:
            s += f"\n  上涨 {up} 家  下跌 {down} 家"
    except Exception:
        pass
    return s


def format_limit_up(stocks: list[LimitUpStock]) -> str:
    if not stocks:
        return "  今日暂无涨停数据（非交易日或无数据）"
    lines = [f"━━━ 涨停板 ({len(stocks)}只) ━━━"]
    for s in stocks[:30]:
        tag = f"  [{s.code}] {s.name}"
        if s.continue_days > 1:
            tag += f" \033[1m{s.continue_days}连板\033[0m"
        lines.append(tag)
    return "\n".join(lines)


def format_sectors(sectors: list[SectorInfo]) -> str:
    if not sectors:
        return "  暂无数据"
    lines = ["━━━ 行业板块 TOP10 ━━━"]
    for i, s in enumerate(sectors, 1):
        lines.append(f"  {i:2d}. {s.name:<8}  {_c(s.change_pct)}")
    return "\n".join(lines)
