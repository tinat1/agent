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
    def __init__(self, account, email, password, marketplace_id, bot_type=Role.BUYER):
        super().__init__(account, email, password, marketplace_id, bot_type=Role.BUYER, name="DSBot")
        # I added the bot_type as an optional with a default setting
        # just so the code won't kick us out for now when we run it
        self._waiting_for_server = False
        self._market_id = -1
        self._role = None
        self._bot_type = bot_type
        print(bot_type)
        # self._bot_type = bot_type
        # ------ Add new class variable _bot_type to store the type of the bot
        # In a session, the bot must be market maker or reactive (but not both)
        # You should provide correct implementation for both types

    def role(self):
        cash_info = self.holdings["cash"]
        widgets_info = self.holdings["markets"][self._market_id]
        self.inform(cash_info)
        self.inform(widgets_info)

        if self.cash_info['cash'] == 0:
            self._role = Role.SELLER
        else:
            self._role = Role.BUYER

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
        have_an_order = False
        for item in order_book:
            if item.mine and item.side == OrderSide.SELL:
                have_an_order = True
                self.inform("I have a pending sell order" + str(item))

        if not have_an_order and not self._waiting_for_server:
            # need to be able to distinguish what the price of the best ask/bid is
            # then set item price to that price, not the price of item currently examined
            order = Order(item.price, 1, OrderType.LIMIT, OrderSide.BUY, market_id, ref="b1")
            self.send_order(order)
            self.inform("order sent at price " + str(order.price))
            self._waiting_for_server = True
# this whole section needs work ^^^

    def _print_trade_opportunity(self, other_order):
        self.inform("[" + str(self.role()) + str(other_order))

    def received_completed_orders(self, orders, market_id=None):
        # must request through the get_completed_orders method
        pass

    def received_holdings(self, holdings):
        cash_holdings = holdings["cash"]
        self.inform("Total cash: " + st(cash_holdings["cash"]) + " available cash: " + st(cash_holdings["available_cash"]))
        # is this necessary since we initialised cash_info above?

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
