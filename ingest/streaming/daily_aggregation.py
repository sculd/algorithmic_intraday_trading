import pandas as pd, numpy as np
import datetime, os
import util.logging as logging
from ingest.streaming.aggregation import BarWithTime, Bar, Aggregation, AggregationsRun


class DailyAggregation(Aggregation):
    def get_daily_df(self):
        df_minute = self.get_minute_df()
        print('Aggregation.get_daily_df for {symbol}, df_minute length: {l}'.format(symbol=self.symbol, l=len(df_minute )))
        df_daily = pd.DataFrame(columns = BarWithTime.get_daily_tuple_names()).append(
            {
                'date': df_minute.datetime.dt.date.iloc[0],
                'symbol': df_minute.symbol.iloc[0],
                'open': df_minute.open.iloc[0],
                'high': df_minute.high.max(),
                'low': df_minute.low.min(),
                'close': df_minute.close.iloc[-1],
                'volume': df_minute.volume.sum()
            }, ignore_index=True)
        return df_daily

class DailyAggregationsRun(AggregationsRun):
    def on_trade(self, trade):
        if trade.symbol not in self.aggregation_per_symbol:
            self.aggregation_per_symbol[trade.symbol] = DailyAggregation(trade.symbol)
        super().on_trade(trade)

    def on_bar_with_time(self, bar_with_time):
        symbol = bar_with_time.bar.symbol
        if symbol not in self.aggregation_per_symbol:
            self.aggregation_per_symbol[symbol] = DailyAggregation(symbol)
        super().on_bar_with_time(bar_with_time)

    def to_minute_csv(self, csv_filename, epoch_seconds_start = None, epoch_seconds_end = None):
        logging.info('DailyAggregationsRun.to_minute_csv for {l_s} symbols'.format(l_s=len(self.aggregation_per_symbol)))
        if len(self.aggregation_per_symbol) == 0:
            return
        with open(csv_filename, 'w') as csv_file:
            csv_file.write(','.join(BarWithTime.get_minute_tuple_names()) + '\n')
            for symbol, aggregation in self.aggregation_per_symbol.copy().items():
                aggregation.append_to_minute_csv(csv_file, epoch_seconds_start=epoch_seconds_start, epoch_seconds_end=epoch_seconds_end)

    def save_daily_df(self, base_dir='data'):
        logging.info('upload_daily_df')
        self.daily_trade_started = False
        t_1 = datetime.datetime.utcnow()
        df_daily = self.get_daily_df()
        t_2 = datetime.datetime.utcnow()
        dt_21 = t_2 - t_1
        logging.info('[save_daily_df] {s} seconds took to get daily_df'.format(s=dt_21.seconds))
        if not os.path.exists(base_dir):
            os.mkdir(base_dir)
        df_daily.to_csv('{base_dir}/daily.csv'.format(base_dir=base_dir))
        return df_daily

    def on_daily_trade_end(self, base_dir='data'):
        logging.info('on_daily_trade_end')
        self.daily_trade_started = False
        t_1 = datetime.datetime.utcnow()
        df_minute = self.get_minute_df()
        t_2 = datetime.datetime.utcnow()
        dt_21 = t_2 - t_1
        logging.info('{s} seconds took to get minute_df'.format(s=dt_21.seconds))
        df_daily = self.get_daily_df()
        t_3 = datetime.datetime.utcnow()
        dt_32 = t_3 - t_2
        logging.info('{s} seconds took to get daily_df'.format(s=dt_32.seconds))
        if not os.path.exists(base_dir):
            os.mkdir(base_dir)
        df_minute.to_csv('{base_dir}/minute.csv'.format(base_dir=base_dir))
        df_daily.to_csv('{base_dir}/daily.csv'.format(base_dir=base_dir))
        self.clean()

    def get_daily_df(self):
        logging.info('Aggregations.get_daily_df for {l_s} symbols'.format(l_s=len(self.aggregation_per_symbol)))
        df = pd.DataFrame(columns=BarWithTime.get_daily_tuple_names())
        for symbol, aggregation in self.aggregation_per_symbol.items():
            t_1 = datetime.datetime.utcnow()
            df_ = aggregation.get_daily_df()
            t_2 = datetime.datetime.utcnow()
            dt_21 = t_2 - t_1
            logging.info('{s} seconds {ms} microseconds took to get minute_df for symbol {symbol}'.format(
                s=dt_21.seconds, ms=dt_21.microseconds, symbol=symbol))
            df = df.append(df_)
            t_3 = datetime.datetime.utcnow()
            dt_32 = t_3 - t_2
            logging.info('{s} seconds {ms} microseconds took to append for symbol {symbol}'.format(
                s=dt_32.seconds, ms=dt_32.microseconds, symbol=symbol))

        return df.set_index('date')

