import re

from bs4 import BeautifulSoup

# UI chrome strings that contaminate conversation text across platforms
_CHROME_PATTERNS = re.compile(
    r'^(copy|copy code|copied!|regenerate|edit|like|dislike|share|report|'
    r'thumbs up|thumbs down|good response|bad response|stop generating|'
    r'continue generating|send message|new chat|try again|'
    r'\d{1,2}:\d{2}\s?(am|pm)?|today|yesterday|\d+ (hour|minute|day)s? ago)$',
    re.IGNORECASE,
)

# Role label patterns used in heuristic text splitting
_ROLE_LABEL_PATTERN = re.compile(
    r'^(you|human|user|assistant|claude|gemini|chatgpt|model|ai):?\s*$',
    re.IGNORECASE,
)


def _clean(text: str) -> str:
    text = re.sub(r'\n{3,}', '\n\n', text)
    return text.strip()


def _strip_chrome(text: str) -> str:
    """Remove UI chrome lines from extracted text."""
    lines = text.splitlines()
    cleaned = [line for line in lines if not _CHROME_PATTERNS.match(line.strip())]
    return _clean("\n".join(cleaned))


def _replace_code_blocks(soup: BeautifulSoup) -> None:
    for pre in soup.find_all('pre'):
        code_text = pre.get_text()
        code_text = re.sub(r'^Copy code\n?', '', code_text, flags=re.IGNORECASE).strip()
        pre.replace_with(f"\n```\n{code_text}\n```\n")


def _remove_ui_elements(soup: BeautifulSoup) -> None:
    """Remove known non-content elements before text extraction."""
    for tag in soup.find_all(['nav', 'footer', 'header', 'button', 'svg', 'style', 'script']):
        tag.decompose()
    for tag in soup.find_all(attrs={"aria-label": True}):
        label = tag.get("aria-label", "").lower()
        if any(w in label for w in ("copy", "share", "like", "dislike", "report", "menu", "close")):
            tag.decompose()


def _heuristic_split(text: str, default_first_role: str = "user") -> list[dict]:
    """
    Split a wall of text into turns using role label patterns and large
    whitespace breaks as turn boundaries. Used when DOM parsing finds nothing.
    """
    # Try splitting on explicit role labels (e.g. "You:", "Claude:", "Assistant:")
    label_split = re.split(r'\n(?=' + _ROLE_LABEL_PATTERN.pattern[1:-1] + r'\n)', text, flags=re.IGNORECASE | re.MULTILINE)

    if len(label_split) >= 2:
        messages = []
        roles = [default_first_role, "assistant"]
        for i, block in enumerate(label_split):
            # Strip the role label line itself
            block = re.sub(_ROLE_LABEL_PATTERN, '', block, count=1, flags=re.IGNORECASE).strip()
            content = _strip_chrome(block)
            if len(content) > 50:
                role = roles[i % 2]
                messages.append({"role": role, "content": content})
        if len(messages) >= 2:
            return messages

    # Fallback: split on large whitespace gaps (3+ blank lines) and alternate roles
    blocks = re.split(r'\n{3,}', text)
    messages = []
    roles = [default_first_role, "assistant"]
    i = 0
    for block in blocks:
        content = _strip_chrome(block.strip())
        if len(content) > 100:
            messages.append({"role": roles[i % 2], "content": content})
            i += 1

    return messages


def _els_to_turns(els, role: str) -> list[tuple]:
    turns = []
    for el in els:
        content = _strip_chrome(el.get_text(separator="\n"))
        if len(content) > 30:
            turns.append((el.sourceline or 0, role, content))
    return turns


def _parse_chatgpt(soup: BeautifulSoup) -> list[dict]:
    messages = []
    for el in soup.find_all('div', {'data-message-author-role': True}):
        role = el.get('data-message-author-role')
        content = _strip_chrome(el.get_text(separator="\n"))
        if content:
            messages.append({"role": role, "content": content})
    return messages


def _parse_claude(soup: BeautifulSoup) -> list[dict]:
    # Strategy 1: semantic class selectors (current Claude share page DOM)
    selector_pairs = [
        (re.compile(r'font-claude-message'), re.compile(r'human-turn|user-message|human-message')),
        (re.compile(r'claude-message|assistant-message|bot-message'), re.compile(r'human-turn|user-turn|user-bubble')),
        (re.compile(r'response-content|model-output'), re.compile(r'prompt-content|input-content')),
    ]

    for assistant_pat, user_pat in selector_pairs:
        assistant_els = soup.find_all(class_=assistant_pat)
        user_els = soup.find_all(class_=user_pat)
        if assistant_els or user_els:
            turns = _els_to_turns(assistant_els, "assistant") + _els_to_turns(user_els, "user")
            if turns:
                turns.sort(key=lambda t: t[0])
                return [{"role": role, "content": content} for _, role, content in turns]

    # Strategy 2: look for alternating article/section/div siblings
    for container_tag in ['main', 'article', 'section']:
        container = soup.find(container_tag)
        if container:
            children = [c for c in container.children if getattr(c, 'name', None) in ('div', 'article', 'section', 'p')]
            if len(children) >= 2:
                turns = []
                roles = ["user", "assistant"]
                for i, child in enumerate(children):
                    content = _strip_chrome(child.get_text(separator="\n"))
                    if len(content) > 50:
                        turns.append({"role": roles[i % 2], "content": content})
                if len(turns) >= 2:
                    return turns

    # Strategy 3: heuristic text split
    page_text = soup.get_text(separator="\n")
    return _heuristic_split(page_text, default_first_role="user")


def _parse_gemini(soup: BeautifulSoup) -> list[dict]:
    # Strategy 1: semantic class selectors
    selector_pairs = [
        (re.compile(r'model-response|response-content|gemini-response|model-turn'),
         re.compile(r'user-query|human-turn|query-content|user-turn')),
        (re.compile(r'response-bubble|answer-content'),
         re.compile(r'query-bubble|question-content')),
    ]

    for assistant_pat, user_pat in selector_pairs:
        assistant_els = soup.find_all(class_=assistant_pat)
        user_els = soup.find_all(class_=user_pat)
        if assistant_els or user_els:
            turns = _els_to_turns(assistant_els, "assistant") + _els_to_turns(user_els, "user")
            if turns:
                turns.sort(key=lambda t: t[0])
                return [{"role": role, "content": content} for _, role, content in turns]

    # Strategy 2: heuristic text split
    page_text = soup.get_text(separator="\n")
    return _heuristic_split(page_text, default_first_role="user")


def _quality_check(messages: list[dict], raw_text_length: int) -> list[dict]:
    if raw_text_length > 2000 and len(messages) < 3:
        print(
            f"[WARN] Parsed only {len(messages)} message(s) from {raw_text_length} characters of page text. "
            "Conversation structure may have been lost — consider inspecting the raw HTML."
        )
    return messages


def parse_conversation(html_content: str, source: str = "chatgpt") -> list:
    soup = BeautifulSoup(html_content, 'html.parser')
    _remove_ui_elements(soup)
    _replace_code_blocks(soup)

    raw_text_length = len(soup.get_text())

    if source == "chatgpt":
        messages = _parse_chatgpt(soup)
    elif source == "claude":
        messages = _parse_claude(soup)
    elif source == "gemini":
        messages = _parse_gemini(soup)
    else:
        messages = _parse_chatgpt(soup)

    # Universal fallback: heuristic split on page text if all strategies returned nothing
    if not messages:
        page_text = soup.get_text(separator="\n")
        messages = _heuristic_split(page_text)

    # Last resort: at least return non-empty paragraphs rather than nothing
    if not messages:
        for tag in soup.find_all(['p', 'article', 'section']):
            content = _strip_chrome(tag.get_text(separator="\n"))
            if len(content) > 50:
                messages.append({"role": "assistant", "content": content})

    return _quality_check(messages, raw_text_length)
