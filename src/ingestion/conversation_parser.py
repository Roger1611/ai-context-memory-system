
#extracts conversation text from AI share pages.


from bs4 import BeautifulSoup


def parse_conversation(html: str):


    soup = BeautifulSoup(html, "html.parser")

    messages = []

    # Collect visible paragraph text blocks

    paragraphs = soup.find_all("p")

    for p in paragraphs:
        text = p.get_text(strip=True)

        if len(text) > 10:
            messages.append({
                "role": "unknown",
                "content": text
            })

    return messages