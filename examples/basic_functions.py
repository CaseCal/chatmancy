import dotenv
from chatmancy.agent import GPTAgent
from chatmancy.conversation import Conversation
from chatmancy.function import FunctionItem, StaticFunctionItemGenerator

dotenv.load_dotenv()

agent = GPTAgent(
    name="Stock Brocker",
    desc="An professional Stock broker that can buy and sell stocks for you",
    model="gpt-4",
    system_prompt=(
        "You are a stock broker. You can buy and sell stocks for your clients. "
    ),
)

functions = [
    FunctionItem(
        method=lambda amount, ticker: f"Bought {amount} shares of {ticker} stock!",
        name="buy_stock",
        description="Buy an amount of a stock",
        params={
            "amount": {
                "type": "number",
                "description": "The amount of stock to buy",
            },
            "ticker": {
                "type": "string",
                "description": "The ticker of the stock to buy",
                "enum": ["AAPL", "GOOG", "MSFT", "AMZN", "FB"],
            },
        },
    )
]
func_generator = StaticFunctionItemGenerator(functions=functions)

convo = Conversation(main_agent=agent, function_generators=[func_generator])

response = convo.send_message("Please buy 100 shares of AAPL stock")
print(response)
