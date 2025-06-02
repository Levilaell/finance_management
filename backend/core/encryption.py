"""
Encryption utilities for sensitive data storage
"""
import base64
import os
from cryptography.fernet import Fernet
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured


class FieldEncryption:
    """
    Field-level encryption for sensitive data like OAuth tokens
    """
    
    def __init__(self):
        self._key = None
        
    @property
    def key(self):
        if self._key is None:
            # Get encryption key from environment
            key_string = getattr(settings, 'FIELD_ENCRYPTION_KEY', None)
            if not key_string:
                raise ImproperlyConfigured(
                    "FIELD_ENCRYPTION_KEY must be set in settings"
                )
            self._key = key_string.encode()
        return self._key
    
    def encrypt(self, data: str) -> str:
        """Encrypt sensitive data"""
        if not data:
            return data
            
        fernet = Fernet(self.key)
        encrypted = fernet.encrypt(data.encode())
        return base64.urlsafe_b64encode(encrypted).decode()
    
    def decrypt(self, encrypted_data: str) -> str:
        """Decrypt sensitive data"""
        if not encrypted_data:
            return encrypted_data
            
        try:
            fernet = Fernet(self.key)
            decoded = base64.urlsafe_b64decode(encrypted_data.encode())
            decrypted = fernet.decrypt(decoded)
            return decrypted.decode()
        except Exception:
            # If decryption fails, assume data is not encrypted (migration case)
            return encrypted_data


# Global encryption instance
field_encryption = FieldEncryption()


def generate_encryption_key():
    """Generate a new encryption key"""
    return Fernet.generate_key().decode()


class EncryptedTextField:
    """
    Custom field descriptor for encrypted text fields
    """
    
    def __init__(self, field_name):
        self.field_name = field_name
        self.encrypted_field_name = f"_{field_name}_encrypted"
        
    def __get__(self, instance, owner):
        if instance is None:
            return self
            
        encrypted_value = getattr(instance, self.encrypted_field_name, None)
        if encrypted_value:
            return field_encryption.decrypt(encrypted_value)
        return None
        
    def __set__(self, instance, value):
        if value:
            encrypted_value = field_encryption.encrypt(value)
            setattr(instance, self.encrypted_field_name, encrypted_value)
        else:
            setattr(instance, self.encrypted_field_name, None)