
from chatbot import Chatbot


def main():

    print("Loading chatbot...")

    try:
        bot = Chatbot()
    except FileNotFoundError:
        print("No trained model found!")
        print("Run train.py first.")
        return

    print("\nChatbot ready!")
    print("Type 'exit' to quit.\n")

    while True:

        message = input("You: ").strip()

        if message.lower() == "exit":
            print("Program: Goodbye!")
            break

        if not message:
            continue

        response = bot.generate(message)

        print("Bot:", response)


if __name__ == "__main__":
    main()
