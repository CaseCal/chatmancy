import json
from typing import Dict, List
import dotenv
import logging
from functools import partial

dotenv.load_dotenv()  # Must have openai key in .env file

from pydantic import BaseModel

# flake8: noqa
from chatmancy.agent import GPTAgent
from chatmancy.conversation import (
    Conversation,
    ContextManager,
    ContextItem,
    AgentContextManager,
)
from chatmancy.message import Message, MessageQueue
from chatmancy.function import (
    FunctionRequestMessage,
    FunctionItem,
    FunctionItemGenerator,
)


# Note that pydantic models are not required; any data structre can be used as long as context vales are serializable to string
class Restaurant(BaseModel):
    name: str
    cuisine: str
    city: str
    days_open: List[str]


# Fill-in for a database or service
RESTAURANTS = {
    "Joe's Italian": Restaurant(
        name="Joe's Italian",
        cuisine="Italian",
        city="LA",
        days_open=[
            "Monday",
            "Tuesday",
            "Wednesday",
            "Thursday",
            "Friday",
            "Saturday",
        ],
    ),
    "Sappa Sushi": Restaurant(
        name="Sappa Sushi",
        cuisine="Japanese",
        city="LA",
        days_open=[
            "Monday",
            "Tuesday",
            "Wednesday",
            "Thursday",
            "Friday",
            "Saturday",
            "Sunday",
        ],
    ),
    "The French Place": Restaurant(
        name="The French Place",
        cuisine="French",
        city="LA",
        days_open=["Friday", "Saturday", "Sunday"],
    ),
    "Mama's Fish Fry": Restaurant(
        name="Mamma's Fish Fry",
        cuisine="Seafood",
        city="New York",
        days_open=[
            "Monday",
            "Tuesday",
            "Wednesday",
            "Thursday",
            "Friday",
            "Saturday",
            "Sunday",
        ],
    ),
}


def RecommenderGPTAgent() -> GPTAgent:
    return GPTAgent(
        name="Sample GPTAgent",
        desc="Sample GPTAgent description",
        model="gpt-4",
        system_prompt="You are a restaurant recomendation GPTAgent. You help the user find a restaurant that fits their questions, preferences and settings.",
    )


class UserContextManager(ContextManager):
    def __init__(self, name: str, user: dict) -> None:
        super().__init__(name, keys=["user"])

        self.user = user

    def _get_context_updates(
        self, history: MessageQueue, current_context: Dict
    ) -> Dict:
        """
        Analyzes the message history and updates the current context.

        * history: The list of past messages.
        """
        if "user" not in current_context:
            return {"user": self.user}


class RestaurantContextManager(AgentContextManager):
    def __init__(self, name: str, restaurants: Dict[str, Dict]) -> None:
        self.restaurants = restaurants
        super().__init__(
            name,
            context_item=ContextItem(
                name="restaurant",
                description="The restaurant crrently being discussed.",
                valid_values=list(restaurants.keys()),
            ),
        )

    def _get_context_updates(
        self, history: MessageQueue, current_context: Dict
    ) -> Dict:
        """
        Analyzes the message history and updates the current context. If a resturant is found, adds all that restaurants info to context
        """
        restaurant_name = (
            super()
            ._get_context_updates(history, current_context)
            .get("restaurant", None)
        )
        if restaurant_name in self.restaurants:
            return {"restaurant": self.restaurants[restaurant_name].model_dump()}
        else:
            return {}


class RestaurantFunctionGenerator(FunctionItemGenerator):
    @staticmethod
    def make_reservation(restaurant_name: str, time: str) -> str:
        return f"Reservation made at {restaurant_name} for {time}"

    def generate_functions(
        self, input_message: str, history, context: Dict
    ) -> List[FunctionItem]:
        # Get the restaurant from context
        if "restaurant" not in context:
            return []

        restaurant = context["restaurant"]
        if not isinstance(restaurant, dict):
            return []
        if restaurant is None:
            return []

        # Create a function for each piece of info
        functions = [
            FunctionItem(
                method=partial(
                    self.make_reservation, restaurant_name=restaurant["name"]
                ),
                name="make_reservation",
                description=f"Make a reservation at {restaurant['name']}",
                function=self.make_reservation,
                params={
                    "time": {
                        "type": "string",
                        "description": "The time to make the reservation",
                    },
                },
            )
        ]

        return functions


def SampleConversation() -> Conversation:
    # User context
    user = {
        "name": "Adrian",
        "city": "LA",
        "Booking Enabled": "True",
    }
    user_cm = UserContextManager(name="User Context", user=user)

    # Restaurant context
    restaurant_cm = RestaurantContextManager(
        name="Restaurant Context", restaurants=RESTAURANTS
    )

    # Functions
    restaurant_fg = RestaurantFunctionGenerator()

    return Conversation(
        main_agent=RecommenderGPTAgent(),
        context_managers=[user_cm, restaurant_cm],
        function_generators=[restaurant_fg],
    )


if __name__ == "__main__":
    # chat_logger = logging.getLogger("chatmancy")
    # chat_logger.setLevel(logging.INFO)
    # formatter = logging.Formatter("%(name)s - %(levelname)s - %(message)s")
    # handler = logging.StreamHandler()
    # handler.setFormatter(formatter)
    # chat_logger.addHandler(handler)

    # logging.getLogger("chatmancy.Conversation").setLevel(logging.DEBUG)

    conversation = SampleConversation()

    print(conversation.opening_prompt)

    while True:
        try:
            print("### User: ", end="")
            question = input()
            print("### Response: ")
            print(" Thinking...", end="\r")
            response: Message = conversation.send_message(question)
            if isinstance(response, FunctionRequestMessage):
                print(f"Function Request: {response.content} \n Allow? y/n")
                answer = input()
                if answer == "y":
                    approval = response.create_response()
                else:
                    approval = conversation.main_GPTAgent.model_handler.create_message(
                        "user",
                        f"Request to call {response.func_name} was denied",
                    )
                response = conversation.send_message(approval)

            print(f"[{response.sender}]: {response.content}" + "\n")
        # except Exception as e:
        #     print(f"Error: {e}")
        except KeyboardInterrupt:
            print("Exiting...")
            break
