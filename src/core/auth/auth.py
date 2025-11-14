from passlib.context import CryptContext

pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')

def verify_password(password: str, hashed_password: str):
    '''
    Verifies if the password matches the hashed_password when hashed
    '''

    return pwd_context.verify(password, hashed_password)

def hash_password(password: str):
    '''
    Returns a hash of the password
    '''

    return pwd_context.hash(password)

