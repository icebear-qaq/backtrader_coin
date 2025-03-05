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

## 使用方法

### 1. 运行默认回测
直接跑入口文件（假设为 `main.py`）：
'''bash
python main.py

'''python
# 导入所需的模块和类
# BacktestEngine: 用于运行回测的核心引擎
# FakeBroker: 模拟经纪人，用于虚拟交易环境
# binance_data_source: 从Binance获取数据的模块
# get_kline_data: 获取K线数据的函数
# 各种策略类（ATR、布林带、双均线等）: 不同的交易策略实现
from coin.backtest_engine.engine import BacktestEngine
from coin.broker.fake_broker import FakeBroker
from coin.data_source import binance_data_source
from coin.data_source.binance_data_source import get_kline_data
from coin.strategy.atr import ATRSellStrategy
from coin.strategy.bband import BollingerRSIStrategy
from coin.strategy.double_ma import DoubleMAStrategy
from coin.strategy.rsib import RSIBollingerStrategy


def test():
    # 初始化 FakeBroker（模拟经纪人）
    # initial_balance: 初始资金，这里设置为1000（单位通常为USDT）
    # leverage: 杠杆倍数，这里设置为100倍，放大收益和风险
    # fee_rate: 交易手续费率，这里为0.04%（即0.0004）
    # open_ratio: 开仓比例，0.2表示每次交易使用20%的可用资金
    # stop_loss: 止损比例，0.04表示下跌4%时自动平仓止损
    # take_profit: 止盈比例，0.08表示上涨8%时自动平仓止盈
    broker = FakeBroker(
        initial_balance=1000,
        leverage=100,
        fee_rate=0.0004,
        open_ratio=0.2,
        stop_loss=0.04,
        take_profit=0.08
    )

    # 初始化交易策略
    # 这里提供了多种策略供选择，通过注释切换不同策略
    # BollingerRSIStrategy: 结合布林带和RSI指标的策略
    # ATRSellStrategy: 基于ATR（平均真实波幅）的卖出策略
    # RSIBollingerStrategy: 结合RSI和布林带的策略
    # DoubleMAStrategy: 双均线策略（默认使用此策略）
    # 你可以根据需要取消注释并选择不同的策略进行测试
    # strategy = BollingerRSIStrategy(
    #     bollinger_window=20,  # 布林带窗口期
    #     bollinger_std=2,     # 布林带标准差倍数
    #     rsi_window=14,       # RSI计算窗口期
    #     rsi_threshold=60     # RSI阈值
    # )
    # strategy = ATRSellStrategy()
    # strategy = RSIBollingerStrategy()
    strategy = DoubleMAStrategy()

    # 初始化回测引擎
    # BacktestEngine 需要两个参数：
    # broker: 模拟经纪人对象，用于执行虚拟交易
    # strategy: 交易策略对象，用于决定买卖信号
    engine = BacktestEngine(broker, strategy)

    # 获取K线数据用于回测
    # get_kline_data 参数说明：
    # "BTCUSDT": 交易对，这里使用比特币对USDT
    # "30m": 时间周期，这里为30分钟K线
    # 5000: 获取最近5000条K线数据
    data = binance_data_source.get_kline_data("BTCUSDT", "30m", 5000)

    # 运行回测
    # engine.run 会根据提供的数据和策略，模拟交易并计算结果
    # 结果通常包括盈亏、交易次数、胜率等统计信息
    engine.run(data)

# 程序入口
# 当文件作为主程序运行时，执行 test() 函数
if __name__ == '__main__':
    test()

默认会用 `DoubleMAStrategy` 策略，基于 BTCUSDT 的 30 分钟 K 线回测 5000 条数据。

回测完成后，程序会启动一个本地 Web 服务器（默认 `http://localhost:5000`），自动打开浏览器展示结果。界面包括：
- 资金曲线图
- 交易记录表格
- 统计数据（总收益、胜率、最大回撤等）

#### Web UI 示例
下面是回测结果的 Web UI 截图：  
![Web UI 示例](screenshots/web-ui-example.png)



