import bcrypt


def hash_password(password: str) -> str:
    """
    Convert a plain-text password into a secure bcrypt hash.
    """

    password_bytes = password.encode("utf-8")

    salt = bcrypt.gensalt()

    hashed_password = bcrypt.hashpw(
        password_bytes,
        salt
    )

    return hashed_password.decode("utf-8")


def verify_password(
    password: str,
    hashed_password: str
) -> bool:
    """
    Check whether the entered password
    matches the stored bcrypt hash.
    """

    password_bytes = password.encode("utf-8")

    hashed_password_bytes = hashed_password.encode("utf-8")

    return bcrypt.checkpw(
        password_bytes,
        hashed_password_bytes
    )