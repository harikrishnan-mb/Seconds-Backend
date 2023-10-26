import random


def generate_otp():
    otp = random.randint(1000, 9999)  # Generate a random 4-digit OTP
    return otp
