import secrets
import string


def generate_password(
    length: int = 16,
    include_uppercase: bool = True,
    include_lowercase: bool = True,
    include_numbers: bool = True,
    include_symbols: bool = True,
) -> str:
    character_pool = ""

    required_characters: list[str] = []

    if include_uppercase:
        character_pool += string.ascii_uppercase
        required_characters.append(
            secrets.choice(string.ascii_uppercase)
        )

    if include_lowercase:
        character_pool += string.ascii_lowercase
        required_characters.append(
            secrets.choice(string.ascii_lowercase)
        )

    if include_numbers:
        character_pool += string.digits
        required_characters.append(
            secrets.choice(string.digits)
        )

    if include_symbols:
        character_pool += string.punctuation
        required_characters.append(
            secrets.choice(string.punctuation)
        )

    if not character_pool:
        raise ValueError(
            "At least one character type must be enabled."
        )

    if length < len(required_characters):
        raise ValueError(
            "Password length is too short for the selected "
            "character requirements."
        )

    remaining_length = length - len(required_characters)

    password_characters = required_characters + [
        secrets.choice(character_pool)
        for _ in range(remaining_length)
    ]

    secrets.SystemRandom().shuffle(password_characters)

    return "".join(password_characters)