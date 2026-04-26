from langchain_ollama.llms import OllamaLLM

if __name__ == "__main__":
    model = OllamaLLM(model="qwen2:1.5b")
    resp = model.invoke("你是谁?")
    print(resp)
