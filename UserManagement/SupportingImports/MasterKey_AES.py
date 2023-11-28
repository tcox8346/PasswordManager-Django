# Requeres pycryptodome for AES - encryption mechanisms
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
from cryptography.fernet import Fernet
import binascii
import os


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
class FernetEncryption:
    """Encrpytion mechanism - default key is os.enviorment variable"""
    def __init__(self, key):
        #self.key = os.environ['FERNET']
        if key == None:
            key  = os.environ["Fernet"]
        self.key =  key
        
    def encrypt(self, data = None, key = None):
        """Takes a string or bytes form object and converts it into a url safe base 64 utf encoded cipher text - converted into hex form for storage"""
        if data == None or key == None:
            return
        # convert base form data into byte form
        data = bytes(data, "utf-8")
        
        # setup encrpytion cipher
        cipher = FernetEncryption(key)
        
        #encrpyt result into url safe base 64 utf-8 fernet cipher text
        basic_result = cipher.encrypt(data)
        
        # convert to hex format for manipulation
        hexed_result =  binascii.hexlify(basic_result)
        # return hexed form
        return hexed_result
        
        
            
    def decrypt(self,data = None):
        """Decrypt fernet token in hex form """
        if data == None or self.key == None:
            return None
          
        cipher = Fernet(self.key)
        # convert hex data back into non hex url encoded base 64 form
        print(f"the data is {type(data)}")
        data = binascii.unhexlify(data)
        # decrypt original token form
        clear_text = cipher.decrypt(data).decode()
        # return clear text
        return clear_text
        
def generate_128b_key():
    return Fernet.generate_key()