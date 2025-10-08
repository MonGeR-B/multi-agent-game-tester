# test_llm_provider.py
from agents.llm_provider import LLMProvider

def main():
    p = LLMProvider()
    print("Provider selected:", p.provider)
    resp = p.generate("Say hi and list 3 short, concrete test cases for a number-input puzzle web game.", temperature=0.2, max_tokens=200)
    print("\nLLM response:\n", resp)

if __name__ == "__main__":
    main()
