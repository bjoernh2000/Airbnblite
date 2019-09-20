import hashlib
def encrypt(password):
    """one way encryption"""
    return hashlib.sha256(password.encode('utf-8')).hexdigest()

def is_password(password,encryption):
    """check password"""
    return hashlib.sha256(password.encode('utf-8')).hexdigest() == encryption