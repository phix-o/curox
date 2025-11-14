import string
import random

def generate_token() -> str:
    '''
    Generates a random 6-character token
    '''

    character_pool = string.ascii_uppercase + string.digits
    token = ''.join(random.choice(character_pool) for _ in range(2))

    # This ensures we can't have above 2 consecetive letters which may form "interesting" unintentional words
    token += ''.join(random.choice(string.digits) for _ in range(2))

    token += ''.join(random.choice(character_pool) for _ in range(2))
    return token
