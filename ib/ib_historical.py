"""
Created on Fri Sep 20 19:25:01 2019

@author: Thibaut Salvador
"""

import pandas as pd
from ibapi import wrapper
from ibapi.client import EClient
from ibapi.wrapper import EWrapper
from ibapi.contract import Contract as IBcontract
from time import time
from ibapi.utils import iswrapper
from ibapi.common import *
from ibapi.contract import *
from ibapi.ticktype import *
from time import sleep    
import os


class TestApp(wrapper.EWrapper, EClient):

    def __init__(self):
        wrapper.EWrapper.__init__(self)
        EClient.__init__(self, wrapper=self)
        self.histo_data_dict = {}
        
        '''
        inspiration: https://stackoverflow.com/questions/45793114/how-to-get-series-of-requests-in-ibapi-on-python
                    https://qoppac.blogspot.com/2017/03/historic-data-from-native-ib-pyhon-api.html
                    https://qoppac.blogspot.com/2014/04/
        '''

    @iswrapper
    def historicalData(self, reqId:int, bar: BarData):
        # called once per date
        histo_dic_loc = self.histo_data_dict
        histo_dic_loc[pd.Timestamp(bar.date)] = {'Open':  bar.open, 
                                                 # 'High':  bar.high, 
                                                 # 'Low' :  bar.low, 
                                                 'Close': bar.close}
        # edit after 08/01/2020: without the below, it keeps hanging indefinitely, while
        # the exact same code was working fine a day before
        self.done = True

    @iswrapper
    def historicalDataEnd(self, reqId: int, start: str, end: str):
        self.i = self.i+1
        self.disconnect() 
        # Disconnect here: get out of app.run() when all data processed

         
            
    @iswrapper
    def error(self, id, errorCode, errorString):
        # Seems code always hit here even for warnings (code 21xx)
        # it goes here before fetching market data and after
        if str(errorCode)[:2] == '21' and len(str(errorCode)) == 4:
            pass
        else:
            print('IB error code : ', errorCode, errorString)
            self.disconnect()


def genContract(typ, ticker, exchange, expiry=''):
    '''
    typ: STK for stock/ETF
         FUT for futures
         CONTFUT for continuous futures
         CASH for FX
    '''
    print(ticker)
    contract = Contract()
    contract.symbol = ticker
    contract.secType = typ
    contract.currency = 'USD'
    contract.exchange = exchange
    
    if typ == 'FUT':
        if expiry == '':
            contract.secType = 'CONTFUT'
        contract.lastTradeDateOrContractMonth = expiry
    
    return contract


def reqHistorical(i, app, contract, duration):
    
    '''
    reqHistoricalData (native api function) arguments:
        
    tickerId,       A unique identifier which will serve to identify the incoming data.
    contract,       The IBApi.Contract you are interested in.
    endDateTime,    The request's end date and time (the empty string indicates current present moment).
    durationString, The amount of time (or Valid Duration String units) to go back from the request's given end date and time.
    barSizeSetting, The data's granularity or Valid Bar Sizes
    whatToShow,     The type of data to retrieve. See Historical Data Types
    useRTH,         Whether (1) or not (0) to retrieve data generated only within Regular Trading Hours (RTH)
    formatDate,     The format in which the incoming bars' date should be presented. Note that for day bars, only yyyyMMdd format is available.
    keepUpToDate,   Whether a subscription is made to return updates of unfinished real time bars as they are available (True), or all data is returned on a one-time basis 
    '''

    app.reqHistoricalData(i, contract, '', duration, '1 day', 'Adjusted_Last', 1, 1, False, []) 



def reqItdTwaps(i, app, contract, duration, end_date):

    app.reqHistoricalData(i, contract, end_date, duration, '1 secs', 'Midpoint', 1, 1, False, []) 

    
#%%
    
def reqData(ticker, exchange, duration, typ='STK', expiry='',
            intraday=False, end_date=''):

    is_live = False
    port = 4001 if is_live else 4002

    app = TestApp()
    app.connect('127.0.0.1', port, clientId=1234)

    app.i = 0
    app.t = time()
    contract = genContract(typ, ticker, exchange, expiry)
    if not intraday:
        reqHistorical(app.i, app, contract, duration)
    else:
        reqItdTwaps(app.i, app, contract, duration, end_date)
    app.run()
    
    histo_dic_lst = app.histo_data_dict
    ret = pd.DataFrame(histo_dic_lst).transpose()
    
    # data fetching on server is too fast and doesn't fill properly without
    # a pause between two calls. The sleep is not necessary on host machine
    if os.name != 'nt':
        sleep(1)
    
    return ret

# EOD Test - Note IBGateway needs to be connected.
if False:
    y_0 = reqData('MES',      'GLOBEX', '2 M', 'FUT')
    y_x = reqData('WrongTkr', 'ARCA',   '2 M', 'STK')
    y_f = reqData('SPY',      'ARCA',   '2 M', 'STK')
    y_e = reqData('FXI',      'ARCA','2 M', 'STK')

# ITD Test
if False:
    x_0 = reqData('MES',      'GLOBEX', '60 S', 'FUT', '', True, '20211223 05:25:00')
    x_c = reqData('XINA50',      'SGX', '180 S','FUT', '', True, '20211224 09:03:00')


        
