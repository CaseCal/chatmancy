import dotenv
from chatmancy.agent import GPTAgent
from chatmancy.conversation import Conversation

dotenv.load_dotenv()

agent = GPTAgent(
    name="Poet",
    desc="A poet that can write poems about any topic.",
    model="gpt-4",
    system_prompt=(
        "You are a poet. You write poems about any topic, "
        "and always respond with concise poetry."
    ),
)

convo = Conversation(main_agent=agent)

response = convo.send_message("Hello, how are you?")
print(response)
