import hashlib
import json
import os
from Crypto.Cipher import AES


def encryptData(configData):
    curPwd = configData["oldPassword"]
    salt = os.urandom(13)
    iv = os.urandom(13)
    configData["salt"] = salt.hex()
    configData["iv"] = iv.hex()
    key = hashlib.pbkdf2_hmac(
        "sha256", curPwd.encode("utf8"), salt, iterations=1000, dklen=128 // 8
    )

    blob = encrypt(
        key,
        json.dumps(configData),
        iv,
    )
    encryptedConfigData = {
        "encryptedBlob": blob,
        "salt": salt.hex(),
        "iv": iv.hex(),
        "authData": "encryptData",
    }
    return encryptedConfigData


def encrypt(
    derivedKey,
    plainText,
    initVector,
):
    plainText = plainText.encode("ascii")

    cipher = AES.new(derivedKey, AES.MODE_CCM, initVector)
    cipher.update("encryptData".encode("utf8"))
    encrypted_data = cipher.encrypt(plainText)
    encrypted_data += cipher.digest()

    return encrypted_data.hex()
