# Requeres pycryptodome for AES - encryption mechanisms
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
from cryptography.fernet import Fernet



class AES_custom:
    """Default Object uses a 256 bit Key, must be in byte form"""
    def __init__(self, source_key = get_random_bytes(32),*args, **kwargs):
        # STORE AES cipher - data and source key for encrpytion, cipher_text and source key for decryption, tag is for verification during decyption
        self.AES = AES.new(source_key, AES.MODE_EAX)
    
    
    def encrpyt_file(self, text):
        """Encrypts current object clear_text using current object in key"""
        self.ciphertext, self.tag = self.AES.encrypt_and_digest(text)
        return {"cipher": self.cipher_text, "tag": self.tag}
    def decrypt_file(self, cipher_text, tag):
        """Decrypts current object cipher_text using current object in key, it is crucial that the key is the same used for encrpytion"""
        if cipher_text == '' or tag == '':
            print("cipher_text, and tag are both required")
            return
        clear_text = self.AES.decrypt_and_verify(cipher_text, tag)
        return clear_text
    
    def hash_file(self, clear_text):
        pass
    def compare_hash(self, data_a, data_b):
        pass
    
        
FERNET_KEY_SIZE = 128
class FernetEncrpytion:
    def __init__(self, key = None):
        self.key = key
        
    def encrypt(self, data = None, key = None):
        if data == None:
            return None
        if key == None:
            if self.key == None:
                return
            key = self.key
        
        cipher = Fernet(key)
        cipher_text = cipher.encrypt(data)
        return cipher_text
            
    def decrypt(self,data = None, key = None):
        if data == None:
            return None
        if key == None:
            if self.key == None:
                return
            key = self.key
        
        cipher = Fernet(key)
        clear_text = cipher.decrypt(data)
        return clear_text
        
    def generate_128b_key(self):
        return Fernet.generate_key()