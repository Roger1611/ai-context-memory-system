from src.retrieval.memory_search import MemorySearch
from src.prompt_generation.prompt_builder import PromptBuilder
def main():
    search_engine = MemorySearch()
    prompt_builder = PromptBuilder()
    query = input("Ask a question about your project: ")
    memories = search_engine.search(query)
    prompt = prompt_builder.build_prompt(query, memories)
    print("\nGenerated Prompt:\n")
    print("=" * 60)
    print(prompt)
    print("=" * 60)


if __name__ == "__main__":
    main()