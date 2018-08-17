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
class Role(Enum):
    BUYER = 0,
    SELLER = 1

# for role in Role:
#     if Role(role).name == "SELLER":
#         print(role.value)


# Let us define another enumeration to deal with the type of bot
class BotType(Enum):
    MARKET_MAKER = 0,
    REACTIVE = 1

print(BotType.MARKET_MAKER.value)


class DSBot(Agent):

    # ------ Add an extra argument bot_type to the constructor -----
    def __init__(self, account, email, password, marketplace_id, bot_type):
        super().__init__(account, email, password, marketplace_id, name="DSBot")
        self._market_id = -1
        self._role = None
        # ------ Add new class variable _bot_type to store the type of the bot
        self._bot_type = bot_type

    def role(self):
        print("yes")
        return self._role

    def initialised(self):
        print(self.markets)
        for market_id in self.markets.keys():
            self._market_id = market_id
            self.inform(self._market_id)

        # If the bot initially has positive cash, it is a buyer, otherwise, it is a seller
        if self.holdings["cash"]["available_cash"] > 0:
            self._role = Role.BUYER
        else:
            self._role = Role.SELLER

    def order_accepted(self, order):
        print("test")
        self.inform("My order got accepted")

    def order_rejected(self, info, order):
        self.inform("My order got rejected because" + str(info))

    def received_order_book(self, order_book, market_id):
        for order in order_book:
            if order.mine:
                self.inform("I have a pending order" + str(order))
            else:
                if order.side == OrderSide.SELL and order.price < 800:
                    print("yes")
                    order = Order(order.price, 1, OrderType.LIMIT, OrderSide.BUY,
                                  self._market_id, ref="b1")
                    print("order received at price " + str(order.price))
                    self.send_order(order)
                # if order.side == OrderSide.BUY and order.price > 100:
                #     order = Order(order.price, 1, OrderType.LIMIT, OrderSide.SELL,
                #                   self._market_id, ref="s1")
                #     print("order received at price " + str(order.price))
                #     self.send_order(order)

    def _print_trade_opportunity(self, other_order):
        self.inform("[" + str(self.role()) + str(other_order))

    def received_completed_orders(self, orders, market_id=None):
        pass

    def received_holdings(self, holdings):
        cash_holdings = self.holdings["cash"]
        print("Total cash: " + str(cash_holdings["cash"]) +
              ", available cash: " + str(cash_holdings["available_cash"]))
        for market_id, market_holding in self.holdings["markets"].items():
            print("Total units: " + str(market_holding["units"]) +
                  ", available units: " + str(market_holding["available_units"]))

    def received_marketplace_info(self, marketplace_info):
        session_id = marketplace_info["session_id"]
        if marketplace_info["status"]:
            print("Marketplace is now open with session id: " + str(session_id))
            # may want to check if holdings has changed when a marketplace re-opens
            # market manager may decide to reallocate cash/units when the marketplace is closed
        else:
            print("Marketplace is now closed.")

    def run(self):
        self.initialise()
        self.start()


if __name__ == "__main__":
    FM_ACCOUNT = "bullish-delight"
    FM_EMAIL = "j.tobagus1@student.unimelb.edu.au"
    FM_PASSWORD = "790373"
    MARKETPLACE_ID = 352  # replace this with the marketplace id

    ds_bot = DSBot(FM_ACCOUNT, FM_EMAIL, FM_PASSWORD, MARKETPLACE_ID, BotType(1).name)
    ds_bot.run()
