import os
import time
import openai
from dotenv import load_dotenv
from colorama import Fore, Style

# Define what each assistant is supposed to do
symptom_tracking_assistant_data = {
    "name": "Coach DataDog",
    "model": "gpt-4-1106-preview",
    "tools": [{"type": "code_interpreter"}],
    "instructions": "Help the user track their symptoms over time and prepare for a doctor's visit. Help users to document their symptoms for professional review."
}

wellness_assistant_data = {
    "name": "Coach Nut",
    "model": "gpt-4-1106-preview",
    "tools": [],  # Potential addition of tools for retrieving general wellness information
    "instructions": "Provide general wellness tips and advice for a healthy lifestyle. Offer general guidance on nutrition, exercise, and mental health."
}

emotional_support_assistant_data = {
    "name": "Coach Emo",
    "model": "gpt-4-1106-preview",
    "tools": [],  # Could be extended with sentiment analysis tools or similar
    "instructions": "Offer emotional support and prompts for better mental health. Provide a listening ear and empathetic responses."
}


# Function to check run status
def check_run(client, thread_id, run_id):
    while True:
        run = client.beta.threads.runs.retrieve(
            thread_id=thread_id,
            run_id=run_id
        )
        if run.status == "completed":
            print(f"{Fore.GREEN}Run is completed.{Style.RESET_ALL}")
            return run
        elif run.status == "expired":
            print(f"{Fore.RED}Run is expired.{Style.RESET_ALL}")
            return None
        print(f"{Fore.YELLOW}OpenAI: Run is not yet completed. Waiting...{run.status}{Style.RESET_ALL}")
        time.sleep(1)

# Function to interact with the assistant
def chat_loop(client, assistant, thread, user_input):
    while True:
        message = client.beta.threads.messages.create(
          thread_id=thread.id,
          role="user",
          content=user_input
        )
        run = client.beta.threads.runs.create(
          thread_id=thread.id,
          assistant_id=assistant.id
        )


        # Checking the run's status and waiting for completion
        completed_run = check_run(client, thread.id, run.id)
        if not completed_run:
            print(f"{Fore.RED}Failed to get a response from the assistant.{Style.RESET_ALL}")
            continue

        # Retrieve the latest messages from the assistant
        messages = client.beta.threads.messages.list(thread_id=thread.id)
        for message in messages.data[::-1]:
            if message.role == "assistant":
                print(f"{Fore.BLUE}Assistant: {message.content[0].text.value}{Style.RESET_ALL}")
                break

        user_input = input(f"{Fore.CYAN}User: {Style.RESET_ALL}")

def main():
    load_dotenv()  # Load environment variables from .env file (or from system environment).
    openai.api_key = os.getenv("OPENAI_API_KEY")  # Set the OpenAI API key

    # Initialize the OpenAI client with the API key
    client = openai.OpenAI(api_key=openai.api_key)

    symptom_tracking_assistant = client.beta.assistants.create(
      **symptom_tracking_assistant_data
    )
    wellness_assistant = client.beta.assistants.create(
      **wellness_assistant_data
    )
    emotional_support_assistant = client.beta.assistants.create(
      **emotional_support_assistant_data
    )

    print("Welcome to the Chronic Illness Support System.")
    print("1: Document Symptoms")
    print("2: Wellness Advice")
    print("3: Emotional Support")

    choice = int(input("How can we assist you today (1-3)? "))

    assistant = None
    # Based on user selection, call the appropriate assistant
    if choice == 1:
        assistant = symptom_tracking_assistant
    elif choice == 2:
        assistant = wellness_assistant
    elif choice == 3:
        assistant = emotional_support_assistant

    thread = client.beta.threads.create()

    # Start the interaction loop with the assistant
    print(f"{Fore.MAGENTA}Alright let's get started...{Style.RESET_ALL}\n")
    chat_loop(client, assistant, thread, "let's get started. don't confirm, just start with a relevant quote or deep thought or joke")

if __name__ == "__main__":
    main()
