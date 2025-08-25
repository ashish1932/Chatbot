from llama_cpp import Llama

model_path = "F:/Bot/model/mistral-7b-instruct-v0.2.Q5_K_M.gguf"

llm = Llama(
    model_path=model_path,
    n_ctx=2048,
    n_threads=6,
    n_batch=128,
    use_mmap=True,
    use_mlock=True
)

print("Welcome to Cube AI Chatbot! Type 'exit' to quit.\n")

while True:
    user_input = input("You: ")
    if user_input.lower() in ['exit', 'quit']:
        break

    response = llm.create_chat_completion(
        messages=[{"role": "user", "content": user_input}],
        max_tokens=256,
        temperature=0.7,
        stream=False
    )

    print(f"Bot: {response['choices'][0]['message']['content']}\n")
