import os
import openai
from dotenv import load_dotenv
import json

# Load environment variables from the .env file
load_dotenv()

# Access the API key
openai.api_key = os.getenv("OPENAI_API_KEY")

# Load the saved context
def load_context():
    with open("context.json", "r") as f:
        data = json.load(f)
    return data["context"]

# Function to generate GPT-4 response using the saved context and a user question
def generate_gpt_response(user_question):
    context = load_context()
    
    prompt = context + f"\n\nStudent: {user_question}\n\nTutor:"
    
    try:
        response = openai.chat.completions.create(
            model="gpt-4o", 
            messages=[
                {"role": "system", "content": context},
                {"role": "user", "content": user_question},
            ],
            max_tokens=500,
            temperature=0.7,
        )
        return response['choices'][0]['message']['content'].strip()
    except Exception as e:
        return f"An error occurred: {str(e)}"

if __name__ == "__main__":
    user_question = input("Enter your question for the AI tutor: ")
    output = generate_gpt_response(user_question)
    print(f"Tutor's Response: {output}")
