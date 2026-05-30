# astock-daily 🐂

**A 股每日复盘 CLI 工具 — 30 秒了解今日市场**

一键获取：大盘行情、涨停梯队、行业板块涨跌排行。数据来自腾讯行情 API，**免费开源、无需注册、无需 API Key**。

---

## 安装

```bash
pip install typer
git clone https://github.com/xiaoqahax-ui/astock-daily.git
cd astock-daily
pip install -e .
```

## 使用

```bash
# 完整复盘（大盘 + 涨停 + 板块）
astock-daily all

# 只看大盘
astock-daily overview

# 只看涨停板
astock-daily limit-up

# 只看行业板块
astock-daily sectors --top 10
```

### 输出示例

```
[ A股每日复盘 ]  2026-05-30 12:46
====================================

━━━ 大盘概览 ━━━
  上证 4068.57  -0.73%  (-30.07)
  深证 15575.13  -1.81%  (-286.76)
  创业板 4037.95  -2.11%  (-87.12)

━━━ 涨停板 (8只) ━━━
  000037 深南电A
  002608 江苏国信
  000767 晋控电力
  ...

━━━ 行业板块 TOP10 ━━━
  1. 煤炭           +2.34%
  2. 公用事业       +1.87%
  ...

====================================
数据来源: 腾讯行情 | 开源免费
```

## 数据说明

| 数据 | 来源 | 延迟 |
|-----|------|------|
| 三大指数 | 腾讯行情 | 实时 |
| 涨停板 | 新浪财经 | 实时 |
| 行业板块 | 腾讯行情 | 实时 |

所有数据均来自公开 API，无需任何账号或 Token。

## 项目结构

```
astock-daily/
├── astock_daily/
│   ├── __init__.py
│   ├── cli.py          # CLI 命令
│   └── provider.py     # 数据源（腾讯/Sina）
├── setup.py
└── README.md
```

## 技术栈

- Python 3.8+
- [typer](https://github.com/fastapi/typer) — CLI 框架
- 腾讯行情 API `qt.gtimg.cn` — 数据源
- 新浪财经 — 涨停板数据

## 协议

MIT License

---

**如果这个工具对你有帮助，欢迎请我喝杯咖啡 ☕**

| 支持方式 | 说明 |
|:--------|:----|
| 微信支付 | 扫下方二维码 |

![微信收款码](wechat_pay.jpg)

感谢你的支持！每一份打赏都会让这个工具变得更好 🚀
