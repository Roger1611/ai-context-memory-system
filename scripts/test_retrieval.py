from src.retrieval.memory_search import MemorySearch


def main():
    search_engine = MemorySearch()
    query = input("Ask a question about your project: ")
    results = search_engine.search(query)
    print("\nRelevant Memory:\n")
    for r in results:
        print(f"Topic: {r['topic']}")
        print(f"Content: {r['content']}")
        print("-" * 40)

if __name__ == "__main__":
    main()