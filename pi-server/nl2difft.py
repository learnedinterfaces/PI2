import os
import openai

openai.api_key = os.getenv("OPENAI_APIKEY")

cache = {}

def query(question):
    global cache

    if question in cache:
        return cache[question]

    knowledge = open("nl2difft_prompt.txt").read()
    prompt = knowledge + "\n" + "--" + question + "\n"
    response = openai.Completion.create(
        model="code-davinci-002",
        prompt=prompt,
        temperature=0,
        max_tokens=150,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0,
        stop=["#", ";"]
    )
    cache[question] = response["choices"][0]["text"]
    return cache[question]
