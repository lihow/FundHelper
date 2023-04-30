#!/usr/bin/python3
from fund_simulator import FundSimulator
from send_email import EmailSender
import datetime
import time

def is_workday(date):
    if date.weekday() in [0, 1, 2, 3, 4]:
        return True
    else:
        return False

if __name__ == '__main__':
    funds = [['000751', '嘉实兴业'],
             ['002190', '农银新能源'],
             ['110035', '易方达双债'],
             ['519674', '银河创新混合'],
             ['110003', '易方达双债']]
    fund_simulators = []
    print('Init simulator and email sender')
    for i in range(len(funds)):
        fund_simulators.append(FundSimulator(funds[i][0], 2))
        fund_simulators[-1].history_simulate(show=False)
        print('  '+funds[i][1]+'['+funds[i][0]+'] simulator: inited')
    email_sender = EmailSender()

    while True:
        # today_date = datetime.date.today()
        today_date = datetime.datetime.strptime("2023-04-27",'%Y-%m-%d')

        sleep_s = 60*60 #60 minutes
        if is_workday(today_date) is False:
            print(str(today_date)+': is not workday')
            time.sleep(sleep_s)
            continue

        # start_time, end_time ='14:00:00', '14:30:00'
        start_time, end_time ='18:00:00', '18:30:00'
        now_time = time.strftime("%H:%M:%S", time.localtime())
        if start_time < now_time < end_time: 
            try:   
                print(str(today_date)+': starting analysis')
                today_result = []
                for i in range(len(funds)):
                    strategy = fund_simulators[i].run_realtime(start_time, end_time)
                    if strategy is not None:
                        res = funds[i][1]+'['+funds[i][0]+']: '
                        if strategy > 0:
                            res += 'should sell out'
                        elif strategy < 0:
                            res += 'should purchase'
                        else:
                            res += 'should wait'
                        print('  '+res)
                        today_result.append(res)
                            
                if len(today_result) > 0:
                    message = ''
                    for res in today_result:
                        message = (message + res + ' \n')
                    # print(str(today_date)+': result '+message)
                    email_sender.send(message)
                else:
                     print(str(today_date)+': result Empty')
            except Exception as e:
                print(str(today_date)+': Program Exception!')
            time.sleep(sleep_s)
            continue
        else:
            # print(str(today_date)+': '+str(now_time)+' is not in analysis time')
            sleep_s = 10*60
            time.sleep(sleep_s)
            continue

            

