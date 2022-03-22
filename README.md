# strategies
A set of helpers in python for trading strategies.

ib:
- ib_historical.py allows you to download market data from IB API, both EOD and intraday.
- ib_order.py allows you to place simple orders on your account through the API. 
Warning: if IB Gateway is connected to real account ant the port is correctly configured, it indeed will send orders. It's not limited to paper accounts.
