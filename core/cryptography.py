from Crypto.Cipher import AES
from base64 import b64encode, b64decode

# Function > AES 256 GCM Encryption
def AES_256_GCM_Encrypt(secret_key: str, secret_message: str) -> tuple[str, str, str]:
    # encode the key and message to utf-8
    secret_key = secret_key.encode('utf8')
    secret_message = secret_message.encode('utf8')

    # create cipher mode
    cipher = AES.new(secret_key, AES.MODE_GCM)

    # encrypt and digest
    secret_message, auth_tag = cipher.encrypt_and_digest(secret_message)

    # convert to Base64 and decode by UTF-8
    secret_message = b64encode(secret_message).decode('utf8')
    auth_tag = b64encode(auth_tag).decode('utf8')
    cipher_nonce = b64encode(cipher.nonce).decode('utf8')

    # return secrets as a tuple of strings
    return secret_message, auth_tag, cipher_nonce


# Function > AES 256 GCM Decryption
def AES_256_GCM_Decrypt(secret_key: str, secret_message: str, auth_tag: str, cipher_nonce: str) -> str:
    # encode the key and message to utf-8
    secret_key = secret_key.encode('utf8')

    # base 64 decode the message, tag and nonce
    secret_message = b64decode(secret_message)
    auth_tag = b64decode(auth_tag)
    cipher_nonce = b64decode(cipher_nonce)

    # create cipher mode
    with AES.new(secret_key, AES.MODE_GCM, cipher_nonce) as cipher:
        # decrypt secret message and verify
        secret_message = cipher.decrypt_and_verify(secret_message, auth_tag)

    # return the decoded secret message
    return secret_message.decode('utf8')
