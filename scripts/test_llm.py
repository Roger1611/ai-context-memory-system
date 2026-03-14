
from src.llm import generate_response


def main():

    prompt = """
    Summarize this sentence in one line:

    Lambda 0.1 improved accuracy to 0.725 and reduced ESS.
    """

    response = generate_response(prompt)

    print("\nModel Response:\n")
    print(response)


if __name__ == "__main__":
    main()