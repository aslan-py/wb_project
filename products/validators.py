def normalize_text(value: str) -> str:
    """Убирает пробелы по краям и делает первую букву заглавной."""
    value = value.strip()
    return value[:1].upper() + value[1:]
