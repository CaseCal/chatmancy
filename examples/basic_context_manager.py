import dotenv
from chatmancy.agent import GPTAgent
from chatmancy.conversation import Conversation, AgentContextManager

dotenv.load_dotenv()


agent = GPTAgent(
    name="Literary Analyst",
    desc="A literary analyst that can discuss books and authors.",
    model="gpt-4",
    system_prompt=(
        "You are a literary analyst discussing books and authors. Answer succintly"
        " and in a literary manner."
    ),
)

book_cm = AgentContextManager(
    name="BookContextManager",
    context_item={
        "name": "book_name",
        "description": "The name of the book being discussed.",
    },
)
genre_cm = AgentContextManager(
    name="GenreContextManager",
    context_item={
        "name": "genre",
        "description": "The genre of the book or topic being discussed.",
    },
)

convo = Conversation(
    main_agent=agent,
    context_managers=[book_cm, genre_cm],
)

response = convo.send_message("Hi, lets talk about some Sci-Fi books.")
print(convo.context)
print(response.content)


response = convo.send_message("I just read Left Hand of Darkness, that was a good one.")
print(convo.context)
print(response.content)
