import openai


openai.api_key = "" 

messages = [
     {"role": "system", "content": "You are an helpful assistant."}
]

while True:

    prompt = input()

    message_str = {"role": "user", "content": prompt}
    messages.append(message_str)

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo-0301",
        messages=messages
    )

    print(response['choices'][0]['message']['content'])

    assistant_str = {"role": "assistant", "content":response['choices'][0]['message']['content']}
    messages.append(assistant_str)
    