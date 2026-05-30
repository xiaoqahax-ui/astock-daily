"""
astock-daily CLI — A股每日复盘
"""
from __future__ import annotations

import sys
from datetime import datetime

try:
    import typer
except ImportError:
    print("请先安装依赖: pip install typer")
    sys.exit(1)

from . import __version__
from . import provider as pvd

app = typer.Typer(name="astock-daily", add_completion=False)


@app.callback()
def main(version: bool = typer.Option(False, "--version", "-V")) -> None:
    if version:
        print(f"astock-daily v{__version__}")
        raise typer.Exit()


@app.command()
def overview():
    """大盘行情 — 三大指数实时行情"""
    try:
        m = pvd.get_market_overview()
        print(pvd.format_market(m))
    except Exception as e:
        print(f"\033[91m数据获取失败: {e}\033[0m")
        print("提示：数据源为腾讯行情，请检查网络")


@app.command(name="limit-up")
def limit_up():
    """涨停板 — 今日涨停个股"""
    try:
        stocks = pvd.get_limit_up_list()
        print(pvd.format_limit_up(stocks))
    except Exception as e:
        print(f"\033[91m数据获取失败: {e}\033[0m")


@app.command()
def sectors(top: int = typer.Option(10, "--top", "-n")):
    """行业板块 — 申万行业涨跌幅排行"""
    try:
        secs = pvd.get_hot_sectors(top_n=top)
        print(pvd.format_sectors(secs))
    except Exception as e:
        print(f"\033[91m数据获取失败: {e}\033[0m")


@app.command()
def all():
    """完整复盘 — 大盘 + 涨停 + 板块"""
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    print(f"\n\033[1m[ A股每日复盘 ]  {now}\033[0m")
    print("=" * 36)

    try:
        m = pvd.get_market_overview()
        print(f"\n{pvd.format_market(m)}")
    except Exception as e:
        print(f"\n  大盘数据获取失败: {e}")

    try:
        stocks = pvd.get_limit_up_list()
        if stocks:
            print(f"\n{pvd.format_limit_up(stocks)}")
    except Exception as e:
        print(f"\n  涨停数据获取失败: {e}")

    try:
        secs = pvd.get_hot_sectors()
        if secs:
            print(f"\n{pvd.format_sectors(secs)}")
    except Exception as e:
        print(f"\n  板块数据获取失败: {e}")

    print(f"\n{'=' * 36}")
    print("数据来源: 腾讯行情 | 开源免费, 欢迎打赏 ☕")
    print()


def entry():
    app()


if __name__ == "__main__":
    entry()
