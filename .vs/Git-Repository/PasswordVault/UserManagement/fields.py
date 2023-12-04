from typing import Any
from django.db import models
# Encrpytion Methods
from .SupportingImports.MasterKey_AES import AES_custom, FernetEncryption
import os
from encrypted_fields import fields
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.exceptions import FieldError, ImproperlyConfigured
KEY_SIZE = 128

#@ Fernet
class EncryptedField_Char(models.CharField):
    description = "Encrypted value - key must be 32 bytes in length, USE For symetric key encryption only - This implementation uses fernet and uses 128 it keys, Encrpyted using server key "
    
    def __init__(self,key = None ,*args, **kwargs):
        super().__init__(*args, **kwargs)
        if key == None:
            self.key = os.environ["Fernet"]
        else:
            self.key = key
        
    def deconstruct(self):
        name, path, args, kwargs = super().deconstruct()

        return name, path, args, kwargs
    def get_prep_value(self, value, instance=None):
        
        # convert value to byte form
        if type(value) != str:
            value = str(value).encode('utf-8')
            
        # Encrypt data 
        data = FernetEncryption(self.key).encrypt(value)

        # return string version of encrpyted data to caller
        return str(data)
    
    def from_db_value(self, value, expression, connection):
        if value is None:
            return value
        # convert string byte form into byte hex form
        value = value
        # decrypt cipher text
        result = FernetEncryption(self.key).decrypt(data = value,)
        
        # return decoded clear text
        return result
    def to_python(self, value):
       
        return value
class EncryptedField_EmailField(models.EmailField):
    description = "Encrypted value - key must be 32 bytes in length, USE For symetric key encryption only - This implementation uses fernet and uses 128 it keys, Encrpyted using server key "
    
    def __init__(self,key = None ,*args, **kwargs):
        super().__init__(*args, **kwargs)
        if key == None:
            self.key = os.environ["Fernet"]
        else:
            self.key = key
        
    def deconstruct(self):
        name, path, args, kwargs = super().deconstruct()

        return name, path, args, kwargs
    def get_prep_value(self, value, instance=None):
        
        # convert value to byte form
        if type(value) != str:
            value = str(value).encode('utf-8')
            
        # Encrypt data 
        data = FernetEncryption(self.key).encrypt(value)

        # return encrpyted data to caller
        return data
    
    def from_db_value(self, value, expression, connection):
        if value is None:
            return value
        
        # decrypt cipher text
        result = FernetEncryption(self.key).decrypt(data = value,)
        # return decoded clear text
        return result
    def to_python(self, value):
       
        return value   

class EncryptedText_Private(models.TextField):
    description = "Encrypted value - key must be 32 bytes in length, USE For symetric key encryption only - This implementation uses fernet and uses 128 it keys "
    def __init__(self,key = None ,*args, **kwargs):
        kwargs['max_length'] = 5000
        kwargs['blank'] = True
        kwargs['null'] = True
        kwargs['unique'] = False
        kwargs['default'] = ''
        self.key = key
        super().__init__(*args, **kwargs)
        
    def deconstruct(self):
        name, path, args, kwargs = super().deconstruct()
        del kwargs["max_length"]
        del kwargs["blank"]
        del kwargs["null"]
        del kwargs['default']
        

        return name, path, args, kwargs
    def get_prep_value(self, value, instance=None):
            
        # convert value to byte form
        if type(value) != str:
            value = str(value).encode('utf-8')
            
        # Encrypt data 
        data = FernetEncryption(self.key).encrypt(value)

        # return encrpyted data to caller
        return data
    
    def from_db_value(self, value, expression, connection):
        if value is None:
            return value
        value = value.hex()
        # decrypt cipher text
        result = FernetEncryption(self.key).decrypt(data = value,)
        # return decoded clear text
        return result
    def to_python(self, value):
       
        return value
    
   
#@AES
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


# Custom Encrypted Field Using Django Searchable Encrypted Fields
class PrivateEncryptedCharField(fields.EncryptedCharField):
    
    def __init__(self, *args, **kwargs):
        if type(kwargs.get("encryption_key")):
            self.user_key = kwargs.get("encryption_key")
        super().__init__(*args, **kwargs)
        
    def keys(self):
        # should be a list or tuple of hex encoded 32byte keys
        if self.user_key:
             key_list = [self.user_key]
        else:
            key_list = settings.FIELD_ENCRYPTION_KEYS
       
        if not isinstance(key_list, (list, tuple)):
            raise ImproperlyConfigured("FIELD_ENCRYPTION_KEYS should be a list.")
        return key_list
    
class PrivateEncryptedEmailField(fields.EncryptedEmailField):
    
    def __init__(self, *args, **kwargs):
        if type(kwargs.get("encryption_key")):
            self.user_key = kwargs.get("encryption_key")
        super().__init__(*args, **kwargs)
        
    def keys(self):
        # should be a list or tuple of hex encoded 32byte keys
        if self.user_key:
             key_list = [self.user_key]
        else:
            key_list = settings.FIELD_ENCRYPTION_KEYS
       
        if not isinstance(key_list, (list, tuple)):
            raise ImproperlyConfigured("FIELD_ENCRYPTION_KEYS should be a list.")
        return key_list