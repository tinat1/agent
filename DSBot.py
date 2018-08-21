"""
This is a template for Project 1, Task 1 (Induced demand-supply)
"""

from enum import Enum
from fmclient import Agent, OrderSide, Order, OrderType

# Group details
GROUP_MEMBERS = {"751965": "Huishan Feng", "830843": "Tina Tian", "790373": "Jennifer Lilian Tobagus"}

# ------ Add a variable called DS_REWARD_CHARGE -----
DS_REWARD_CHARGE = 800

# Enum for the roles of the bot
# why Enum???
class Role(Enum):
    BUYER = 0,
    SELLER = 1

# Let us define another enumeration to deal with the type of bot
class BotType(Enum):
    MARKET_MAKER = 0,
    REACTIVE = 1

class DSBot(Agent):
    # ------ Add an extra argument bot_type to the constructor -----
    def __init__(self, account, email, password, marketplace_id):
        super().__init__(account, email, password, marketplace_id, name="DSBot")
        self._waiting_for_server = False
        self._market_id = -1
        self._role = None
        self._bot_type = bot_type
        self._widgets_bought = 0
        self._have_an_order = False
        self._required_profit = 100
        self._orders_ref = 0

        # comment one out to set BotType
        self._bot_type = BotType.MARKET_MAKER
        # self._bot_type = BotType.REACTIVE

    def role(self):
        cash_avail = self.holdings["cash"]["available_cash"]
        if self.cash_avail > 0:
            self._role = Role.BUYER
        else:
            self._role = Role.SELLER

        print(self._role)
        return self._role

    def initialised(self):
        for market_id, market_info in self.markets.items():
            self.inform("I can trade in market " + market_info["name"] + " with id " + str(market_id))
            self.inform("The tick size is " + str(market_info["tick"]))
            self.market_id = market_id #what is the point of this

# this whole section needs work vvv
    def order_accepted(self, order):
        self._waiting_for_server = False
        self.inform("Your order was accepted!")

    def order_rejected(self, info, order):
        self._waiting_for_server = False
        self.inform("Your order was rejected!")

        # also I'm getting this error from time to time
        # then usually the agent will keep sending the same order and continue to get rejected
        # Couldn't parse response from server as JSON. Perhaps use a custom data parser if expecting response in different format

    def received_order_book(self, order_book, market_id):
        # should these variable names not be preluded with _?
        sell_orders = [order for order in order_book if order.side == OrderSide.SELL and not order.mine]
        buy_orders = [order for order in order_book if order.side == OrderSide.BUY and not order.mine]
        my_orders = [order for order in order_book if order.mine]


        sell_orders.sort(key=lambda x: x.price)
        buy_orders.sort(key=lambda x: x.price)
        # best_bid_order and best_ask_order contain the order with the best bid or ask
        # they are set to None if there is no buy or sell order in the order book
        best_bid_order = None if not buy_orders else buy_orders[-1]
        best_ask_order = None if not sell_orders else sell_orders[0]

        #what is this line of code meant to do?
        self._have_an_order = my_orders != []

        # CASE 1: reactive bot
        if self._bot_type == BotType.REACTIVE:
            # I am a buyer, and reward is higher than price to buy
            if best_ask_order is not None and self._role == Role.BUYER and \
                    best_ask_order.price < DS_REWARD_CHARGE and self._widgets_bought <5:
                self._print_trade_opportunity(best_ask_order)
            # I am a seller, and the price I can sell at is higher than the charge
            elif best_bid_order is not None and self._role == Role.SELLER and \
                    best_bid_order.price < DS_REWARD_CHARGE:
                self._print_trade_opportunity(best_bid_order)

        # CASE 2: the bot is a market maker
        else:
            widgets_avail = self.holdings["markets"][self._market_id]["available_units"]

            # if I am a buyer with non-zero balance
            if self._role == Role.BUYER and not (self._have_an_order \
                    or self._waiting_for_server) and cash_avail >= 5:
                if best_ask_order is None:
                    limit_price = min(cash_avail, DS_REWARD_CHARGE - self._required_profit)
                    order = Order(limit_price, 1, OrderType.LIMIT, OrderSide.BUY, \
                                  self._market_id, ref="o{}".format(self._orders_ref))
                    self._orders_ref += 1
                    self.send_order(order)
                    self._waiting_for_server = True
                    self.inform("I have sent a buy order with reference o{}".format(self._orders_ref))
                else:
                    limit_price = min(cash_avail, DS_REWARD_CHARGE - self._required_profit, best_ask_order.price - self._required_profit)
                    order = Order(limit_price, 1, OrderType.LIMIT, OrderSide.BUY, self._market_id, ref="o{}".format(self._orders_ref))
                    self._orders_ref += 1
                    self.send_order(order)
                    self._waiting_for_server = True
                    self.inform("I have sent a buy order with reference o{}".format(self._orders_ref))

            # if I am a seller with at least one widget
            elif self._role == Role.SELLER and not (self._have_an_order or self._waiting_for_server) and widgets_avail > 0:
                if best_bid_order is None:
                    limit_price = DS_REWARD_CHARGE + self._required_profit
                    order = Order(limit_price, 1, OrderType.LIMIT, OrderSide.SELL, self._market_id, ref="o{}".format(self._orders_ref))
                    self._orders_ref += 1
                    self.send_order(order)
                    self._waiting_for_server = True
                    self.inform("I have sent a sell order with reference o{}".format(self._orders_ref))
                else:
                    limit_price = max(DS_REWARD_CHARGE + self._required_profit,
                                      best_bid_order.price + self._required_profit)
                    order = Order(limit_price, 1, OrderType.LIMIT, OrderSide.SELL, self._market_id,
                                  ref="o{}".format(self._orders_ref))
                    self._orders_ref += 1
                    self.send_order(order)
                    self._waiting_for_server = True
                    self.inform("I have sent a sell order with reference o{}".format(self._orders_ref))
            else:
                if self._have_an_order:
                    reason = "I already have an order in the order book"
                elif self._waiting_for_server:
                    reason = "I am still waiting for the server"
                elif self._role == Role.BUYER and cash_avail < 5:
                    reason = "I do not have enough cash available"
                elif self._role == Role.SELLER and widgets_avail == 0:
                    reason = "I do not have any widgets"
                self.inform("I cannot trade any units because {}".format(reason))

    def _print_trade_opportunity(self, other_order):
        order_type = "Sell" if other_order.side == OrderSide.BUY else "Buy"
        self.inform("Opportunity: {} one unit at price of ${:<5.2f}".format(order_type, other_order.price/100))

        if self._role == Role.BUYER:
            #do we really need to define this again?
            # cash_avail =self.holdings["cash"]["available_cash"]
            can_buy = cash_avail >= other_order.price
            #why are there massive gaps here
            self.inform("           : Profit is ${:.2f} per unit".format(int(DS_REWARD_CHARGE - other_order.price) / 100))
            self.inform("           : With ${:.2f} of available cash I can buy at least {} units".format(cash_avail / 100, cash_avail // other_order.price))
            self.inform("           : There are {} units for sale at this price".format(other_order.units))
            #I feel some of the code here overlaps what we've previously done
            #is there a way to call the other method instead of repeating this code?
            #although this is only a suggestion
            if can_buy and self._bot_type == BotType.REACTIVE and not (self._have_an_order or self._waiting_for_server):
                self.inform("           : I will buy one unit of widget at the price of {}".format(other_order.price))
                order = Order(other_order.price, 1, OrderType.LIMIT, OrderSide.BUY, self._market_id, ref="o{}".format(self._orders_ref))
                self._orders_ref += 1
                self.send_order(order)
                self._waiting_for_server = True
                self.inform("The buy order reference is: o{}".format(self._orders_ref))
            else:
                reason = "I do not have enough cash"
                if self._bot_type != BotType.REACTIVE:
                    reason = "I am not a reactive trader"
                elif self._have_an_order:
                    reason = "I already have an order placed in the order book"
                elif self._waiting_for_server:
                    reason = "I am still waiting for the server"
                self.inform("           : I cannot buy any units because {}".format(reason))

        else:
            #you don't need this line because you've already defined it above, right?
            # widgets_avail = self.holdings["markets"][self._market_id]["available_units"]
            can_sell = widgets_avail > 0
            self.inform("           : Profit is {} per unit".format(other_order.price - DS_REWARD_CHARGE))
            self.inform("           : I have a total of {0} widgets, so I can sell up to {0} units".format(widgets_avail))
            self.inform("           : The buyer wishes to buy {} units at this price".format(other_order.units))
            if can_sell and self._bot_type == BotType.REACTIVE and not (self._have_an_order or self._waiting_for_server):
                self.inform("           : I will sell one unit of widget at the price of {}".format(other_order.price))
                order = Order(other_order.price, 1, OrderType.LIMIT, OrderSide.SELL, self._market_id, ref="o{}".format(self._orders_ref))
                self._orders_ref += 1
                self.send_order(order)
                self._waiting_for_server = True
                self.inform("The sell order reference is: o{}".format(self._orders_ref))
            else:
                #again, is there a way to pull this out into a new method so we can just call that method each time instead?
                reason = "I do not have enough widgets"
                if self._bot_type != BotType.REACTIVE:
                    reason = "I am not a reactive trader"
                elif self._have_an_order:
                    reason = "I already have an order in the order book"
                elif self._waiting_for_server:
                    reason = "I am still waiting for the server"
                self.inform("           : I cannot sell any units because {}".format(reason))
    def received_completed_orders(self, orders, market_id=None):
        #had this comment written here from last time, delete if you think it's irrelevant
        #  must request through the get_completed_orders method
        pass

    def received_holdings(self, holdings):
        cash_holdings = holdings["cash"]
        self.inform("Total cash: " + st(cash_holdings["cash"]) + " available cash: " + st(cash_holdings["available_cash"]))
        # is this necessary since we initialised cash_info above?
        #are we meant to be using this instead of initialising ourselves above?

        for market_id, market_holding in holdings["markets"].items():
            self.inform("Total units: " + str(market_holding["units"]) + ", available units: " + str(market_holding["available_units"]))

    def received_marketplace_info(self, marketplace_info):
        session_id = marketplace_info["session_id"]
        # print(marketplace_info)
        if marketplace_info["active"]:
        # Jen's code had:
        # if marketplace_info["status"]:
        # why?
            self.inform("The marketplace is now open with session_id " + str(session_id))
        else:
            self.inform("The marketplace is now closed")
        # may want to check if your holdings have changed when the market reopens
        # managers may decide to reallocate cash/units when the marketplace is closed

    def run(self):
        self.initialise()
        self.start()


if __name__ == "__main__":
    FM_ACCOUNT = "bullish-delight"
    FM_EMAIL = "t.tian3@student.unimelb.edu.au"
    FM_PASSWORD = "830843"
    MARKETPLACE_ID = 352

    ds_bot = DSBot("bullish-delight", "t.tian3@student.unimelb.edu.au", "830843", 352)
    ds_bot.run()
