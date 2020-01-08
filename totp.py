import base64
import hashlib
import hmac
import secrets
import time


class TOTP:
    def __init__(self, secret: str):
        self.secret = secret

    def now(self) -> str:
        return self.at(int(time.time() / 30))

    def at(self, for_time: int) -> str:
        secret = base64.b32decode(self.secret.upper())
        hmac_hash = hmac.digest(secret, for_time.to_bytes(8, 'big'), hashlib.sha1)
        offset = hmac_hash[-1] & 0xf
        code = ((hmac_hash[offset] & 0x7f) << 24 |
                (hmac_hash[offset + 1] & 0xff) << 16 |
                (hmac_hash[offset + 2] & 0xff) << 8 |
                (hmac_hash[offset + 3] & 0xff))
        out = str(code % 10 ** 6)
        return "0" * (6 - len(out)) + out

    def verify(self, code: str, valid_window: int = 0) -> bool:
        for_time = int(time.time() / 30)
        for i in range(-valid_window, valid_window + 1):
            if self.at(for_time + i) == code.replace(" ", ""):
                return True
        return False

    def generate_uri(self, user: str, issuer: str) -> str:
        return f"otpauth://totp/{user}?secret={self.secret.lower()}&issuer={issuer}"

    def show_qrcode(self, user: str, issuer: str):
        from qrcode import console_scripts
        
        console_scripts.main([self.generate_uri(user, issuer)])

    @staticmethod
    def generate_random(nbytes=20) -> 'TOTP':
        return TOTP(base64.b32encode(secrets.token_bytes(nbytes)).decode())
