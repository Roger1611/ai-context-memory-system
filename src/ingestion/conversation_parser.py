from bs4 import BeautifulSoup
import re

def parse_conversation(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    
    for pre in soup.find_all('pre'):
        
        code_text = pre.get_text() 
        code_text = re.sub(r'^Copy code\n?', '', code_text, flags=re.IGNORECASE).strip()
        markdown_code = f"\n```\n{code_text}\n```\n"
        pre.replace_with(markdown_code)
        
    messages = []
    message_elements = soup.find_all('div', {'data-message-author-role': True})
    
    if message_elements:
        for el in message_elements:
            role = el.get('data-message-author-role')
            content = el.get_text(separator="\n").strip()
            content = re.sub(r'\n{3,}', '\n\n', content)
            if content:
                messages.append({"role": role, "content": content})
    else:
        content = soup.get_text(separator="\n").strip()
        content = re.sub(r'\n{3,}', '\n\n', content)
        if content:
            messages.append({"role": "assistant", "content": content})
            
    return messages