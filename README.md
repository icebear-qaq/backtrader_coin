## 简介
`backtrader_coin` 是一个自研的加密货币交易回测框架，核心模块包括 `FakeBroker`（模拟交易）、多种内置策略（双均线、布林带、ATR 等）以及 Web UI 结果展示。未来计划接入 Binance 实盘交易（开发中），目前专注于高效回测和策略开发。

![photo](images/p1.jpg)  ![photo](images/p2.jpg)
![photo](images/p3.jpg)
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

# 如何使用
请打开main.py查看

# 如何用AI编写策略来回测

想实现自己的策略？可以用 AI（比如 ChatGPT）帮忙写。以下是具体步骤：
1. coin/strategy/下随便找一个策略，复制里面的代码
2. 扔到大模型，然后把自己想实现的策略告诉它
3. 把 AI 写的策略保存到 coin/strategy 文件夹，比如 macd.py，然后在主程序里调用：

把 AI 写的策略保存到 coin/strategy 文件夹，比如 macd.py，然后在主程序里调用：
```
strategy = MACDStrategy()
engine = BacktestEngine(broker, strategy)
engine.run(data)
```

# 贡献
欢迎提 issue 或 PR！有啥问题直接在 GitHub 上吼我。

# 最后
用着顺手的话，给个 star 呗～ 





