import pandas as pd
from numba import jit
from tqdm import tqdm

from coin.data_source.kline import Kline


class BacktestEngine:
    def __init__(self, broker, strategy):
        """
        初始化回测引擎
        :param broker: FakeBroker 实例
        :param strategy: 交易策略实例
        """
        self.broker = broker
        self.strategy = strategy

    def run(self, data):
        """
        运行回测
        :param data: DataFrame，包含K线数据
        """
        # 将DataFrame转换为Kline对象列表
        if isinstance(data, list):
            header = [
                'Open Time', 'Open', 'High', 'Low', 'Close', 'Volume',
                'Close Time', 'Quote Volume', 'Number of Trades',
                'Taker Buy Base Asset Volume', 'Taker Buy Quote Asset Volume', 'Ignore'
            ]
            data = pd.DataFrame(data, columns=header)

        klines = [Kline(*row) for row in data.itertuples(index=False)]

        # 使用 tqdm 显示进度条
        for kline in tqdm(klines, desc="回测进度", unit="K线"):
            # 获取当前价格
            current_price = kline.get_close()
            timestamp = kline.get_close_time()

            # 检查止损止盈
            self.broker.check_stop_loss_take_profit(current_price, timestamp)

            # 生成交易信号
            signal = self.strategy.process_kline(kline)
            # 执行交易
            if signal == 'sell':
                self.broker.sell(current_price, timestamp)
            if signal == 'buy':
                self.broker.buy(current_price, timestamp)
            elif signal == 'close_long':
                self.broker.close_long(current_price, timestamp)
            elif signal == 'close_short':
                self.broker.close_short(current_price, timestamp)

        # 回测结束后生成分析报告test
        self.broker.analyze_trades()

    def __repr__(self):
        return f"BacktestEngine(Broker: {self.broker}, Strategy: {self.strategy})"