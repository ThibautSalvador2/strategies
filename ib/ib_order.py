# -*- coding: utf-8 -*-
"""
Created on Wed Sep 18 19:15:38 2019

@author: Thibaut Salvador
"""

from ibapi.client import EClient
from ibapi.wrapper import EWrapper
from ibapi.contract import Contract
from ibapi.order import Order
from ibapi.order import *
from time import sleep
from ibapi.utils import iswrapper

# inspiration: https://stackoverflow.com/questions/57435940/place-order-with-api-ib

class TestApp(EClient, EWrapper):
    def __init__(self, symbol, exchange, buy_sell, quantity, on_open, expiry):
        EClient.__init__(self, self)
        self.symbol = symbol
        self.exchange = exchange
        self.buy_sell = buy_sell
        self.quantity = quantity
        self.on_open = on_open
        self.expiry = expiry

    @iswrapper
    def nextValidId(self, orderId:int):
        '''
        It calls orderStatus once per pending order, if any.
        Note it's pending orders within the current login session and then 
        it calls nextValidId which places order then disconnect.
        orderStatus is not re-called after placing
        
        So when first connecting, we place the order without even going 
        to orderStatus, but it still places the order.
        
        The id is persistent even after closing the ib gateway session
        it can be reset in the options of gateway.
        '''
        
        print(self.reqManagedAccts())
        
        self.nextOrderId = orderId
        print('OrderId: ', orderId)
        self.start()
    
        
    def start(self):

        contract = Contract()
        contract.symbol = self.symbol
        if self.expiry == '':
            contract.secType = 'STK'
        else:
            contract.secType = 'FUT'
            contract.lastTradeDateOrContractMonth = self.expiry
            
        contract.currency = 'USD'
        contract.exchange = self.exchange

        order = Order()
        order.action = self.buy_sell
        order.orderType = 'MKT'
        order.totalQuantity = self.quantity
        if self.on_open:
            order.Tif = 'OPG'

        # doesn't print anything
        self.placeOrder(self.nextOrderId+1, contract, order)
        self.disconnect()
        
        return self.nextOrderId


    @iswrapper
    def orderStatus(self,
                    orderId:int, 
                    status: str, 
                    filled: float,
                    remaining: float, 
                    avgFillPrice: float, 
                    permId: int,
                    parentId: int, 
                    lastFillPrice: float, 
                    clientId: int,
                    whyHeld: str, 
                    mktCapPrice: float):
        
         super().orderStatus(orderId, status, filled, remaining,
                                 avgFillPrice, permId, parentId, lastFillPrice, clientId, whyHeld, mktCapPrice)
         
         print("OrderStatus. Id:", orderId, "Status:", status, "Filled:", filled)


    @iswrapper
    def error(self, id, errorCode, errorString):
        # Seems code always hit here even for warnings (code 21xx)
        # it goes here before fetching market data and after
        if str(errorCode)[:2] == '21' and len(str(errorCode)) == 4:
            pass
        else:
            print('IB error code : ', errorCode, errorString)
            self.disconnect()


def place_market(symbol, exchange, buy_sell, quantity, on_open=False, expiry=''):
        
    success = False
    is_live = True
    port = 4001 if is_live else 4002
    
    try:
        print(symbol)

        ## resolve the contract
        bs = buy_sell.capitalize()
        app=TestApp(symbol, exchange, bs, quantity, on_open, expiry)
        app.connect('127.0.0.1', port, clientId = 1234)
        app.nextOrderId = 0
        app.run()

    except Exception as e:
        print(e)
        return {'success': False,
                'error'  : str(e)}

    else:
        success = True
            
    return {'success': success,
            'error'  : ''}

# Market order test - IBGateway needs to be connected.
if False:
    x = place_market('USO', 'ARCA', 'buy', 1.0)
