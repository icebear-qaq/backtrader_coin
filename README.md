# backtrader_coin 回测工具  
[English](#english) | 中文

## 简介
`backtrader_coin` 是一个自研的加密货币交易回测框架，核心模块包括 `FakeBroker`（模拟交易）、多种内置策略（双均线、布林带、ATR 等）以及 Web UI 结果展示。未来计划接入 Binance 实盘交易（开发中），目前专注于高效回测和策略开发。

## 功能
- 自研回测引擎：通过 `BacktestEngine` 和 `FakeBroker` 模拟交易，支持自定义初始资金、杠杆、手续费、止损止盈等。
- 多种策略：内置双均线、布林带+RSI、ATR 等策略，也支持自定义。
- 数据支持：从 Binance 获取 K 线数据（或其他数据源）。
- Web UI 展示：回测结果以网页形式展示，包含资金曲线、交易记录等。
- 未来计划：接入 Binance 实盘交易（开发中）。

## 安装
1. 确保你有 Python 3.6+。
2. 克隆项目：
    git clone https://github.com/icebear-qaq/backtrader_coin.git
    cd backtrader_coin


