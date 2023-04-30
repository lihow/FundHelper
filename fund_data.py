#!/usr/bin/python3

class FundEstimateData:
    def __init__(self):
        self.code = -1
        self.name = 'None'
        self.actual_value = -1
        self.date = -1
        self.estimate_value = -1
        self.estimate_growth_rate = -1
        self.estimate_time = -1       
        
    def init_by_html(self, estimate_data):
        self.code = estimate_data['fundcode']
        self.name = estimate_data['name']
        self.actual_value = float(estimate_data['dwjz'])
        self.date = estimate_data['jzrq']
        self.estimate_value = float(estimate_data['gsz'])
        self.estimate_growth_rate = float(estimate_data['gszzl'])
        self.estimate_time = estimate_data['gztime']
        
    def print(self):
        print('-------基金详情------')
        print('基金编码: '+str(self.code))
        print('基金名称: '+str(self.name))
        print('单位净值: '+str(self.actual_value))
        print('净值日期: '+str(self.date))
        print('估 算 值: '+str(self.estimate_value))
        print('估算增量: '+str(self.estimate_growth_rate))
        print('估值时间: '+str(self.estimate_time))

class FundHistoryDate:
    def __init__(self, code):
        self.code = code
        self.history_dates = []
        self.history_values = []
        self.history_growth_rates = []
    
    def append(self, date, value, growth_rate, reverse=True):
#         print(date, value, growth_rate)
        date = str(date)
        value = value
        growth_rate = str(growth_rate)
        if growth_rate is 'nan' or growth_rate is 'NaN':
            growth_rate = 0
        elif growth_rate[-1] is '%':
            growth_rate = float(growth_rate[:-1])   
        else:
            growth_rate = float(growth_rate)
    
        if reverse:
            if len(self.history_dates) > 0 and self.history_dates[0] == date:
                print('Error in FundHistoryDate: data is same '+self.history_dates[0]+'=='+date)
                return
            self.history_dates.insert(0, date)
            self.history_values.insert(0, value)
            self.history_growth_rates.insert(0, growth_rate)
        else:
            if len(self.history_dates) > 0 and self.history_dates[-1] == date:
                print('Error in FundHistoryDate: data is same '+self.history_dates[-1]+'=='+date)
                return            
            self.history_dates.append(date)
            self.history_values.append(value)
            self.history_growth_rates.append(growth_rate)


