from polygon import RESTClient
import os, pprint


import market.ally.price

a_price = market.ally.price.Price()


print(a_price.get_price('AAPL'))





