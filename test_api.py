from ai71 import AI71 

AI71_API_KEY = "api71-api-cbdf95af-ec38-4f97-8d7e-cb2ec3823f46"

for chunk in AI71(AI71_API_KEY).chat.completions.create(
    model="tiiuae/falcon-180b-chat",
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Hello!"},
    ],
    stream=True,
):
    if chunk.choices[0].delta.content:
        print(chunk.choices[0].delta.content, sep="", end="", flush=True)