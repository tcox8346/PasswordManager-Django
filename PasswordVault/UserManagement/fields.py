from django.db import models
# Encrpytion Methods
from .SupportingImports.MasterKey_AES import AES_custom, FernetEncrpytion

KEY_SIZE = 128

class EncryptedText_Private(models.TextField):
    description = "Encrypted value - key must be 32 bytes in length, USE For Private key encryption only - This implementation uses fernet and uses 128 it keys "
    def __init__(self, owning_class, user_class, user_class_instance,tag=None, *args, **kwargs):
        kwargs['max_length'] = KEY_SIZE
        kwargs['blank'] = True
        kwargs['null'] = True
    
        self.tag = tag
        self.owner = user_class.objects.filter(user = user_class_instance)
        self.key = self.owner.get_key()
        self.owning_class = owning_class
        
        super().__init__(*args, **kwargs)
    def deconstruct(self):
        name, path, args, kwargs = super().deconstruct()
        del kwargs["max_length"]
        del kwargs["blank"]
        del kwargs["null"]
        del self.key
        del self.tag
        return name, path, args, kwargs
    def get_prep_value(self, value):
        
        # convert value to byte form
        if type(value) != str:
            value = str(value).encode('utf-8')
        # encrypt data with your own function
        data = FernetEncrpytion(self.key).encrypt(value)
        if self.owner == None:
            print("No owner present, canceling operation")
            return

        # return encrpyted data to caller
        return data
    
    def from_db_value(self, value, expression, connection):
        if value is None or self.tag is None or self.owner is None:
            return value
        # decrypt data with your own function

        
        # decrypt cipher text
        result = FernetEncrpytion(self.key).decrypt(data = value,)
        
        # decode cipher text
        decoded:bytearray = str(result)
        decoded = decoded.decode("utf-8")
        # return decoded clear text
        return decoded
    def to_python(self, value):
        if isinstance(value, self.owning_class):
            return value

        if value is None:
            return value
        
        # decrypt data with your own function
        result = FernetEncrpytion(self.key).decrypt(data = value)
        # convert result into string form - expected to be byte array
        decoded:bytearray = str(result)
        # decode result into normalized form
        decoded = decoded.decode("utf-8")
        return decoded
class EncryptedChar(models.CharField):
    description = "Encrypted value - key must be 32 bytes in length"
    def __init__(self, key,  instance_class, tag = '', *args, **kwargs):
        kwargs['max_length'] = KEY_SIZE
        kwargs['blank'] = True
        kwargs['null'] = True
        self.key = key
        self.tag = tag
        self.instance_class = instance_class
        super().__init__(*args, **kwargs)
    def deconstruct(self):
        name, path, args, kwargs = super().deconstruct()
        del kwargs["max_length"]
        del kwargs["blank"]
        del kwargs["null"]
        return name, path, args, kwargs
    def get_prep_value(self, value):
        # encrypt data with your own function
        data, self.tag = AES_custom(source_key=self.key).encrpyt_file(value)
        return data
    
    def from_db_value(self, value, expression, connection):
        if value is None:
            return value
        # decrypt data with your own function
        return AES_custom(source_key=self.key).decrypt_file(value, self.tag)
    def to_python(self, value):
        if isinstance(value, self.instance_class):
            return value

        if value is None:
            return value
        # decrypt data with your own function
        return  AES_custom(source_key=self.key).decrypt_file(value, self.tag)
    
    # Update save method to save tag after encrpytion so value can be decrypted and authenticated later
