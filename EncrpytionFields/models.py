from typing import Any
from django.db import models
from cryptography.fernet import Fernet


#
# TODO - This is field should automatically request-use a user key present in user Cookie or Session to attempt to decrypt that users data.
    # A Hash of the expected cleartext is compared to the hash of the clear text generated from user provided key

#Note: This class will retrieve a user cleartext key from their cookie
class SolutionEncryption(models.CharField):
    def __init__(self, *args, **kwargs):
        self.description = "A AES encrypted field that uses a credentials owners key/password as a syncrhonous key, the model must have a owner foreignkey that has a 256 length password"
        kwargs['max_length'] = 256
        kwargs['unique'] = False
        
        #if user session has a key variable set automatically use that key as users key
            
        super().__init__(*args, **kwargs)
    
    def deconstruct(self):
        name, path, args, kwargs = super().deconstruct()
        del kwargs["max_length"]
        del kwargs['unique']
        return name, path, args, kwargs
    
    def save_form_data(self, key):
        super().save_form_data()
        
    def get_prep_value(self, value, key):
        return self._encrypt(value, key)
    
    def from_db_value(self,value, expression, connection):
        if value is None:
          return value
        # decrypt data with your own function
        
        return self._decrypt(value)
    
    def to_python(self, value):
        if value is None:
            return value
        # decrypt data with your own function
        return self._decrypt(value)
    
    def _encrypt(self, data, key):
        #Get Key from user cookie
        #placeholder - User password 

        f = Fernet(key)
        ciphertext = f.encrypt(b'{data}')
        #Use Fernet to encrypt data
        
        #return ciphertext
        return ciphertext
    def _decrypt(self,data, key):
        #create fernet 256 instance using key
        f = Fernet(key)
        #decrypt provided data
        cleartext = f.decrypt(data)
        #return cleartext
        return cleartext
