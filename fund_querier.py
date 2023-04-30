#!/usr/bin/python3

import requests
import json
import re
import datetime
import pandas as pd

from fund_data import FundEstimateData, FundHistoryDate

class FundQuerier:
    def __init__(self, fund_code):
        #print(fund_code)
        self.fund_code = fund_code

    def today_estimate(self):
        query_url = 'http://fundgz.1234567.com.cn/js/%s.js' % str(self.fund_code) + '?rt=1463558676006'
        html = requests.get(query_url)
        data = json.loads(re.match(".*?({.*}).*", html.text, re.S).group(1))
        # print(data)
        fund_data = FundEstimateData()
        fund_data.init_by_html(data)
        # fund_data.print()
        return fund_data

    def history_value(self, days_from_today=365):
        fund_history_data = FundHistoryDate(self.fund_code)
        
        today_date = datetime.date.today()
        start_date = today_date - datetime.timedelta(days=days_from_today) 
        first_page = self.get_history_html(str(start_date), str(today_date))

        pattern = 'pages:(.*),'
        pages = re.search(pattern, first_page).group(1)
        try:
            pages = int(pages)
        except Exception as e:
            print("Error: "+str(e))
            return
        
        fund_df_list = []
        for i in range(pages):
            if i == 0:
                fund_data = self.parses_history_table(first_page)
            else:
                next_page = self.get_history_html(str(start_date), str(today_date), page=i+1)
                fund_data = self.parses_history_table(next_page)
            fund_df_list.append(fund_data)
        
        fund_df = pd.concat(fund_df_list, ignore_index=True) # pandas
        
        for index, row in fund_df.iterrows():
#             print(row['净值日期'], row['单位净值'], row['日增长率'])
            fund_history_data.append(row['净值日期'], row['单位净值'], row['日增长率']) 
        
        # print(fund_df)
        return fund_history_data
    
    def get_history_html(self, start_date, end_date, page=1, per=40):
        query_url =  f'http://fund.eastmoney.com/f10/F10DataApi.aspx?type=lsjz&code={self.fund_code}&page={page}&sdate={start_date}&edate={end_date}&per={per}'
#         print(query_url)
        html = requests.get(query_url)
        content = html.text
        return content

    def parses_history_table(self, html):
        pattern = 'content:"<table(.*)</table>",'
        table = re.search(pattern, html).group(1)
        table = '<table' + table + '</table>'
        fund_data = pd.read_html(table)[0]
        return fund_data
    

if __name__ == '__main__':
    fun_code = '000751'
    querier = FundQuerier(fun_code)
    today_data = querier.today_estimate()
    today_data.print()

    histroy_data = querier.history_value()
    # print(len(histroy_data.history_values))