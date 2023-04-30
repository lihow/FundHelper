#!/usr/bin/python3

import matplotlib.pyplot as plt
import numpy as np
import datetime
import time

from fund_data import FundEstimateData, FundHistoryDate
from fund_querier import FundQuerier
from fund_analyzer import FundAnalyzer

class FundSimulator:
    def __init__(self, code, purchase_period_days=7):
        self.fund_code = code
        self.querier = FundQuerier(code)
        self.analyzer = FundAnalyzer(code, purchase_period_days)

        self.last_purchase_date = None

    def str2date(self, datestr):
        return datetime.datetime.strptime(datestr,'%Y-%m-%d')

    def history_simulate(self, show=True):
        history_value = self.querier.history_value()
        history_dates = history_value.history_dates
        history_values = history_value.history_values
        history_growth_rates = history_value.history_growth_rates
        
        sell_out = []
        purchase = []
        fund_history_data = FundHistoryDate(self.fund_code)
        
        for i in range(len(history_values) - 1):
            # history data
            date = history_dates[i]
            value = history_values[i]
            growth_rate = history_growth_rates[i]
            fund_history_data.append(date, value, growth_rate, reverse=False)
            if i < 30:
                self.last_purchase_date = date
                continue
            
            if (self.str2date(date) - self.str2date(self.last_purchase_date)).days < self.analyzer.purchase_period_days:
                continue
                
            self.last_purchase_date = date
            # today data
            today_data = FundEstimateData()
            today_data.code = self.fund_code
            today_data.date = history_dates[i+1]
            today_data.estimate_value = history_values[i+1]
            today_data.estimate_growth_rate = history_growth_rates[i+1]
        
            strategy = self.analyzer.evaluate(fund_history_data, today_data)
            if strategy == 1:
                sell_out.append(i+1)
            elif strategy == -1:
                purchase.append(i+1)

        if show:  
            fig = plt.figure(figsize=(15,4))
            p_ax = plt.subplot(1, 1, 1)
            p_ax.set_title('trading strategy')
            p_ax.plot(history_dates, history_values, label='value')
            p_ax.plot([history_dates[i] for i in sell_out] ,[history_values[i] for i in sell_out], ls='', marker='o', label='sellout')
            p_ax.plot([history_dates[i] for i in purchase] ,[history_values[i] for i in purchase], ls='', marker='v', label='purchase')
            p_ax.grid()      
            p_ax.legend()      
            plt.show()    


    def run_realtime(self, start_time='14:00:00', end_time='14:30:00'):
        if self.last_purchase_date is None:
            self.history_simulate(show=False)

        today_date = str(datetime.date.today())
        if (self.str2date(today_date) - self.str2date(self.last_purchase_date)).days < self.analyzer.purchase_period_days:
            print(today_date, self.last_purchase_date, self.analyzer.purchase_period_days)
            return None

        now_time = time.strftime("%H:%M:%S", time.localtime())
        if start_time < now_time < end_time:
            self.last_purchase_date = today_date

            fund_history_data = self.querier.history_value()
            today_data = self.querier.today_estimate()

            strategy = self.analyzer.evaluate(fund_history_data, today_data)
            return strategy
        return None



if __name__ == '__main__':
    fund_code = '000751' #嘉实兴业
    # fund_code = '002190' #农银新能源---
    # fund_code = '005827' #易方达蓝筹
    fund_code = '110035' #易方达双债-
    # fund_code = '040040' #华安纯债
    # fund_code = '110003' #易方达上证50
    # fund_code = '519674' #银河创新混合

    simulator = FundSimulator(fund_code)
    simulator.history_simulate()   