#!/usr/bin/python3

import matplotlib.pyplot as plt
import numpy as np
import datetime

from fund_data import FundEstimateData, FundHistoryDate
from fund_querier import FundQuerier

class FundAnalyzer:
    def __init__(self, code, purchase_period_days=7):
        self.fund_code = code
        self.purchase_period_days = purchase_period_days
        
    def growth_rate(self, prev, curr):
        return (curr-prev)/prev
            
    def str2date(self, datestr):
        return datetime.datetime.strptime(datestr,'%Y-%m-%d')
    
    def evaluate(self, history_data, today_estimate_data):
        # 最大值和均值和最小值比较
        # 距离最大值小于1%的差距-->适合卖
        # 距离均值小于3%的差距--->适合保留
        # 距离最小值小于1%的差距--->适合买
        today_value =  today_estimate_data.estimate_value
        history_values = history_data.history_values
#         print(today_value,history_values )
        
        lastest_mean = np.mean(history_values)
        win30days_means, _, _ = self.get_window_history_value(history_values, 30)
        win30days_mean = win30days_means[-1]
#         print(lastest_mean, win30days_mean)
        
        strategy = 0
        if self.growth_rate(today_value, win30days_mean) > 0.002:
            strategy = -1
        if self.growth_rate(today_value, win30days_mean) < -0.002:
            strategy = 1
        return strategy
        
    def test(self, history_data):
        data = history_data
        history_dates = data.history_dates
        history_values = data.history_values
        history_growth_rates = data.history_growth_rates
        
        sell_out = []
        purchase = []
        fund_history_data = FundHistoryDate(self.fund_code)
        last_purchase_date = 'None'
        for i in range(len(history_values) - 1):
            # history data
            date = history_dates[i]
            value = history_values[i]
            growth_rate = history_growth_rates[i]
            fund_history_data.append(date, value, growth_rate, reverse=False)
            if i < 30:
                last_purchase_date = date
                continue
            
            if (self.str2date(date) - self.str2date(last_purchase_date)).days < self.purchase_period_days:
                continue
                
            last_purchase_date = date
            # today data
            today_data = FundEstimateData()
            today_data.code = self.fund_code
            today_data.date = history_dates[i+1]
            today_data.estimate_value = history_values[i+1]
            today_data.estimate_growth_rate = history_growth_rates[i+1]
        
            strategy = self.evaluate(fund_history_data, today_data)
            if strategy == 1:
                sell_out.append(i+1)
            elif strategy == -1:
                purchase.append(i+1)
            
        fig = plt.figure(figsize=(15,4))
        p_ax = plt.subplot(1, 1, 1)
        p_ax.set_title('trading strategy')
        # 指标
        # 净值
        p_ax.plot(history_dates, history_values, label='value')
        # 到最新时刻Mean
        lastest_mean = []
        temp_history = []
        for value in data.history_values:
            temp_history.append(value)
            lastest_mean.append(np.mean(temp_history))
        
            
        # 窗口均值 
        # 1years
        w1years_mean, _, _ = self.get_window_history_value(data.history_values, 365) 
        # 30days
        w30days_mean, w30days_max, w30days_min = self.get_window_history_value(data.history_values, 30)        
        p_ax.plot(data.history_dates, data.history_values, label='value')
        p_ax.plot(data.history_dates, lastest_mean, label='lastest mean')
        p_ax.plot(data.history_dates, w30days_mean, label='window mean')
        
        p_ax.plot([history_dates[i] for i in sell_out] ,[history_values[i] for i in sell_out], ls='', marker='o', label='sellout')
        p_ax.plot([history_dates[i] for i in purchase] ,[history_values[i] for i in purchase], ls='', marker='v', label='purchase')
        p_ax.grid()      
        p_ax.legend()                  
    
    def get_window_history_value(self, history_values, window_days=30):    
        temp_window_history = []
        window_mean = []
        window_max = []
        window_min = []
        for value in history_values:
            temp_window_history.append(value)
            if len(temp_window_history) > window_days:
                temp_window_history.pop(0)
            window_mean.append(np.mean(temp_window_history))  
            window_max.append(np.max(temp_window_history))
            window_min.append(np.min(temp_window_history))
        return window_mean, window_max, window_min   
    
    
    def get_MACD(self, history_data, fast_period_days=12, slow_period_days=26, DEA_period_days=9):
        data = history_data
        history_values = data.history_values
        
        fast_EMA, slow_EMA = [], []
        DIF = []
        DEA = []
        MACD_bar = []
        for i in range(len(history_values)):
            cur_value = history_values[i]
            
            fast_ema = cur_value
            slow_ema = cur_value
            if i > 0:
                fast_ema = fast_EMA[-1]*(fast_period_days-1)/(fast_period_days+1) + cur_value*2/(fast_period_days+1)
                slow_ema = slow_EMA[-1]*(slow_period_days-1)/(slow_period_days+1) + cur_value*2/(slow_period_days+1)
            fast_EMA.append(fast_ema)
            slow_EMA.append(slow_ema)
            #print(fast_ema, slow_ema)
            
            dif = fast_ema - slow_ema
            dea = dif
            if i > 0:
                dea = DEA[-1]*(DEA_period_days-1)/(DEA_period_days+1) + dif*2/(DEA_period_days+1)
            DIF.append(dif)
            DEA.append(dea)
            #print(dif)
            
            bar = dif - dea
            MACD_bar.append(bar)
        
        return DIF, DEA, MACD_bar
    
    def get_KDJ(self, history_data, period_days=9):
        data = history_data
        history_values = data.history_values
        
        RSV = []
        K = []
        D = []
        J = []
        
        period_values = []
        for i in range(len(history_values)):
            cur_value = history_values[i]
            
            period_values.append(cur_value)
            max_value = cur_value
            min_value = cur_value
            #print(period_values)
            if len(period_values) >= period_days:
                max_value = np.max(period_values)
                min_value = np.min(period_values)
                period_values.pop(0)
            
            if i < period_days:
                RSV.append(1)
                K.append(50)
                D.append(50)
                J.append(50)
                continue
                
            # RSV
            rsv = 100*(cur_value-min_value)/(max_value-min_value)
            RSV.append(rsv)
            # K
            k = K[-1]*2/3 + rsv/3
            K.append(k)
            # D
            d = D[-1]*2/3 + k/3
            D.append(d)
            # J
            j = 3*k - 2*d
            #j = 3*d - 2*k
            J.append(j)
            
        return K, D, J
    
    def plot_indicator(self, history_data):
        data = history_data
        
        # 到最新时刻Mean
        lastest_mean = []
        temp_history = []
        for value in data.history_values:
            temp_history.append(value)
#             print(temp_history)
            lastest_mean.append(np.mean(temp_history))
        # 窗口均值 
        # 1years
        w1years_mean, _, _ = self.get_window_history_value(data.history_values, 365) 
        w180days_mean, _, _ = self.get_window_history_value(data.history_values, 180)
        w90days_mean, _, _ = self.get_window_history_value(data.history_values, 90)
        # 30days
        w30days_mean, w30days_max, w30days_min = self.get_window_history_value(data.history_values, 30)
        w14days_mean, w14days_max, w14days_min = self.get_window_history_value(data.history_values, 14)
        

        
        fig = plt.figure(figsize=(15,8))
        p_ax = plt.subplot(2, 1, 1)
        p_ax.set_title('Mean Trend')
        p_ax.plot(data.history_dates, data.history_values, label='value')
#         p_ax.plot(data.history_dates, lastest_mean, label='lastest mean')
        p_ax.plot(data.history_dates, w180days_mean, label='180days mean')
        p_ax.plot(data.history_dates, w90days_mean, label='90days mean')
        p_ax.plot(data.history_dates, w30days_mean, label='30days mean')
        p_ax.plot(data.history_dates, w14days_mean, label='14days_mean')
#         p_ax.plot(data.history_dates, w30days_max, label='window max')
#         p_ax.plot(data.history_dates, w30days_min, label='window min')
        p_ax.grid() 
        p_ax.legend()
       
         # MACD指标
        macd_difs, macd_deas, mac_bars = self.get_MACD(history_data)
        
        p_ax = plt.subplot(2, 1, 2)
        p_ax.set_title('MACD Trend')
        p_ax.plot(data.history_dates, macd_difs, label='DIF')
        p_ax.plot(data.history_dates, macd_deas, label='DEA')
        p_ax.bar(data.history_dates, mac_bars, label='MACD_BAR')
        p_ax.grid()      
        p_ax.legend()        

        plt.show()

        # KDJ指标
#         kdj_k, kdj_d, kdj_j = self.get_KDJ(history_data)
#         p_ax = plt.subplot(3, 1, 3)
#         p_ax.set_title('KDJ Trend')
#         p_ax.plot(data.history_dates, kdj_k, label='K')
#         p_ax.plot(data.history_dates, kdj_d, label='D')
#         p_ax.plot(data.history_dates, kdj_j, label='J')
#         p_ax.grid()      
#         p_ax.legend() 
    
    def plot_pandas_history(self, history_data_pandas):
        fund_df = history_data_pandas
#         print(fund_df)
#         print('---')
#         print(fund_df.loc[fund_df['单位净值'].idxmax()])
        fund_max = fund_df.loc[fund_df['单位净值'].idxmax()]
        fund_min = fund_df.loc[fund_df['单位净值'].idxmin()]
#         print(fund_max, fund_min)
        
        ax = plt.gca()
        ax.annotate(f'({fund_max[0]},{fund_max[1]})', xy=(fund_max[0], fund_max[1]), color='red')
        ax.annotate(f'({fund_min[0]},{fund_min[1]})', xy=(fund_min[0], fund_min[1]), color='green')
        plt.plot(fund_df['净值日期'],fund_df['单位净值'], color="c")
        
        plt.title('Trend')
        plt.grid()
        plt.xticks(rotation=30)
        plt.xlabel('date')
        plt.ylabel('value')


if __name__ == '__main__':
    fund_code = '000751' #嘉实兴业
    # fund_code = '002190' #农银新能源---
    # fund_code = '005827' #易方达蓝筹
    # fund_code = '110035' #易方达双债-
    # fund_code = '040040' #华安纯债
    # fund_code = '110003' #易方达上证50
    # fund_code = '519674' #银河创新混合
    querier = FundQuerier(fund_code)
    analyzer = FundAnalyzer(fund_code)
    days_from_today = 180*2

    history_value = querier.history_value(days_from_today)
    today_data = querier.today_estimate()
    today_date = str(datetime.date.today())
    today_data.print()
    # history_value.append(today_date, today_data.estimate_value, today_data.estimate_growth_rate, reverse=False)

    analyzer.plot_indicator(history_value)
    #analyzer.test(querier.history_value())