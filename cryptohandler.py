"""
#!/usr/bin/env python3
backend data encryption and decryption handler
progression_tracker_OOP_V2/cryptohandler.py
"""
from Crypto.Protocol.KDF import PBKDF2
from Crypto.Random import get_random_bytes

from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad

from python_datalogger import DataLogger


class CryptoHandler:
    """
    Handles all the processes related to cryptography.
    """

    def __init__(self, availability: bool = False, password: str = "root", key: bytes = None,
                 logger_name: str = "CryptoHandleLogger"):
        self.__availability = availability
        self.__password = password
        self.salt = None
        self.key = key
        self.cipher = None
        self.iv = None
        self.logger = DataLogger(name=logger_name, propagate=False)

    @property
    def password(self) -> str:
        """makes the password read only"""
        return self.__password

    @property
    def availability(self) -> bool:
        """makes availability option read only"""
        return self.__availability

    def assign_salt(self, salt=None) -> None:
        """
        assigns salt if availability is False and param salt is None
        :param salt: byte array of length 32
        """
        if not self.__availability:
            self.salt = get_random_bytes(32)
        else:
            self.salt = salt

    def get_salt(self, path: str):
        """
        reads a given bin file and assign salt
        :param path: name/path of the salt bin file
        """
        with open(path, 'rb') as file:
            self.salt = file.read()

    def generate_key(self) -> None:
        """Generates a unique 32byte key using salt and password"""
        if self.key is None and self.salt is not None:

            self.key = PBKDF2(self.__password, self.salt, dkLen=32)
            self.logger.log_info("Key generated")

    def get_encrypting_cipher(self):
        """assigns the cipher for encryption"""
        self.cipher = AES.new(self.key, AES.MODE_CBC)

    def get_decrypting_cipher(self):
        """assigns the cipher for decryption"""
        self.cipher = AES.new(self.key, AES.MODE_CBC, iv=self.iv)

    def get_iv(self):
        """assigns iv prior to decryption"""
        self.iv = self.cipher.iv

    def encrypt(self, data: str) -> bytes:
        """
        encrypts the given set of data.
        :param data: A string of information that needs to be encrypted
        :return: encrypted bytes
        """
        self.get_encrypting_cipher()

        if not isinstance(data, bytes):
            data = data.encode()

        self.get_iv()
        return self.cipher.encrypt(pad(data, AES.block_size))

    def decrypt(self, data: bytes) -> bytes:
        """
        decrypts a given set of data.
        :param data: A bytearray that needs to be decrypted
        :return: decrypted bytes
        """
        self.get_decrypting_cipher()

        if isinstance(data, str):
            data = data.encode()

        return unpad(self.cipher.decrypt(data), AES.block_size)

    def salt_to_bin(self, path) -> None:
        """creates a bin file containing the salt bytes"""
        with open(path, 'wb') as file:
            file.write(self.salt)
        self.logger.log_info("salt bin created.")

    def write_to_bin(self, file_name: str, data: bytes):
        """
        creates or overwrites a bin file with iv and encrypted bytes.
        :param file_name: name/path of the bin file
        :param data: encrypted bytes
        """
        if isinstance(data, str):
            data = data.encode()
        with open(file_name, 'wb') as file:
            file.write(self.iv)
            file.write(data)
        self.logger.log_info("Data bin created.")

    def read_from_bin(self, file_name: str) -> bytes:
        """
        retrieves iv and encrypted byte data from a bin file.
        :param file_name: name/path of the bin file
        :return: bytes read from the bin file
        """
        with open(file_name, 'rb') as file:
            self.iv = file.read(16)
            data = file.read()
        self.logger.log_info("Data retrieved from bin.")
        return data
