from langchain_community.llms.llamacpp import LlamaCpp

MODEL_PATH = "Qwen3-0.6B-Q4_K_M.guff"

llm = LlamaCpp(
    model_path=MODEL_PATH,
    temperature=0,
    max_tokens=512,
    n_ctx=2048,
    n_threads=4,
    verbose=False,
)

response = llm.invoke("Привет как тебя зоовут?")
print("Ответ модели: ", response)
