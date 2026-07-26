import os

from dotenv import load_dotenv


load_dotenv()


def get_required_environment_variable(
    variable_name: str,
) -> str:
    value = os.getenv(variable_name)

    if value is None or not value.strip():
        raise RuntimeError(
            f"Required environment variable "
            f"'{variable_name}' is missing."
        )

    return value


SECRET_KEY = get_required_environment_variable(
    "SECRET_KEY"
)

ENCRYPTION_KEY = get_required_environment_variable(
    "ENCRYPTION_KEY"
)

ALGORITHM = os.getenv(
    "ALGORITHM",
    "HS256",
)

ACCESS_TOKEN_EXPIRE_MINUTES = int(
    os.getenv(
        "ACCESS_TOKEN_EXPIRE_MINUTES",
        "30",
    )
)