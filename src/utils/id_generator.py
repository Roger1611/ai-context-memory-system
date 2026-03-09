

#This module generates unique IDs for conversations.

import uuid

def generate_conversation_id():

    return "conv_" + str(uuid.uuid4())[:8]