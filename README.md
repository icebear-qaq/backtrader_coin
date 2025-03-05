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
    ```bash
    git clone https://github.com/icebear-qaq/backtrader_coin.git
    cd backtrader_coin
3. 安装依赖：
    ```bash
    pip install -r requirements.txt
（如果没有 `requirements.txt`，推荐手动安装 `pandas`、`numpy`、`requests`、`flask` 等库。）

#如何使用
请打开main.py查看

#如何用AI编写策略来回测

想实现自己的策略？可以用 AI（比如 ChatGPT）帮忙写。以下是具体步骤：
3.1 参考默认策略
我们先看一个内置的 DoubleMAStrategy（双均线策略）实现，代码简化后如下（假设在 coin/strategy/double_ma.py 中）：
python

import pandas as pd

class DoubleMAStrategy:
    def __init__(self, fast_window=5, slow_window=20):
        self.fast_window = fast_window  # 快均线周期
        self.slow_window = slow_window  # 慢均线周期

    def on_data(self, data):
        # 计算快慢均线
        data['fast_ma'] = data['close'].rolling(window=self.fast_window).mean()
        data['slow_ma'] = data['close'].rolling(window=self.slow_window).mean()

        # 最后一根K线
        last_row = data.iloc[-1]
        prev_row = data.iloc[-2]

        # 买入信号：快均线上穿慢均线
        if (prev_row['fast_ma'] < prev_row['slow_ma'] and 
            last_row['fast_ma'] > last_row['slow_ma']):
            return 'buy'
        # 卖出信号：快均线下穿慢均线
        elif (prev_row['fast_ma'] > prev_row['slow_ma'] and 
              last_row['fast_ma'] < last_row['slow_ma']):
            return 'sell'
        return None

这个策略的核心是：
用 fast_window 和 slow_window 计算两条均线。

在 on_data 方法中，基于均线交叉生成买卖信号。

3.2 让 AI 模仿写新策略
假设你想写一个“MACD 策略”，可以把上面的 DoubleMAStrategy 代码发给 AI（比如 ChatGPT），然后描述需求：
模仿这个 DoubleMAStrategy 的写法，帮我写一个 MACD 策略，规则是：MACD 线（快线减慢线）上穿信号线时买入，下穿时卖出。快线用 12 周期，慢线用 26 周期，信号线用 9 周期。

AI 可能会生成类似下面的代码：
python

import pandas as pd

class MACDStrategy:
    def __init__(self, fast_period=12, slow_period=26, signal_period=9):
        self.fast_period = fast_period
        self.slow_period = slow_period
        self.signal_period = signal_period

    def on_data(self, data):
        # 计算快线和慢线（EMA）
        fast_ema = data['close'].ewm(span=self.fast_period, adjust=False).mean()
        slow_ema = data['close'].ewm(span=self.slow_period, adjust=False).mean()
        
        # 计算 MACD 线
        macd_line = fast_ema - slow_ema
        # 计算信号线
        signal_line = macd_line.ewm(span=self.signal_period, adjust=False).mean()

        # 最后一根和前一根的数据
        last_macd = macd_line.iloc[-1]
        last_signal = signal_line.iloc[-1]
        prev_macd = macd_line.iloc[-2]
        prev_signal = signal_line.iloc[-2]

        # 买入信号：MACD 上穿信号线
        if prev_macd < prev_signal and last_macd > last_signal:
            return 'buy'
        # 卖出信号：MACD 下穿信号线
        elif prev_macd > prev_signal and last_macd < last_signal:
            return 'sell'
        return None

3.3 使用新策略
把 AI 写的策略保存到 coin/strategy 文件夹，比如 macd.py，然后在主程序里调用：
python

from coin.strategy.macd import MACDStrategy

strategy = MACDStrategy()
engine = BacktestEngine(broker, strategy)
engine.run(data)



