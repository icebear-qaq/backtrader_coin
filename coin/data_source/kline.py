class Kline:
    def __init__(self, open_time, open_price, high, low, close, volume, close_time, quote_volume, num_trades, taker_buy_base_asset_volume, taker_buy_quote_asset_volume, ignore):
        self.open_time = open_time
        self.open_price = float(open_price)
        self.high = float(high)
        self.low = float(low)
        self.close = float(close)
        self.volume = float(volume)
        self.close_time = close_time
        self.quote_volume = float(quote_volume)
        self.num_trades = int(num_trades)
        self.taker_buy_base_asset_volume = float(taker_buy_base_asset_volume)
        self.taker_buy_quote_asset_volume = float(taker_buy_quote_asset_volume)
        self.ignore = ignore

    def get_open_time(self):
        return self.open_time

    def get_open_price(self):
        return self.open_price

    def get_high(self):
        return self.high

    def get_low(self):
        return self.low

    def get_close(self):
        return self.close

    def get_volume(self):
        return self.volume

    def get_close_time(self):
        return self.close_time

    def get_quote_volume(self):
        return self.quote_volume

    def get_num_trades(self):
        return self.num_trades

    def get_taker_buy_base_asset_volume(self):
        return self.taker_buy_base_asset_volume

    def get_taker_buy_quote_asset_volume(self):
        return self.taker_buy_quote_asset_volume

    def get_ignore(self):
        return self.ignore

    def __repr__(self):
        return (f"Kline(open_time={self.open_time}, open={self.open_price}, high={self.high}, "
                f"low={self.low}, close={self.close}, volume={self.volume})")