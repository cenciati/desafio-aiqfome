from re import sub


def slugify(text: str) -> str:
    return sub(r"\W", "", sub(r"[ -]", "_", text.strip().lower()))
