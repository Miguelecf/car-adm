from datetime import datetime, date


class InvalidDateInput(ValueError):
    pass


def parse_latam_date(value: str, field_label: str = "Fecha", required: bool = True) -> date | None:
    normalized = (value or "").strip()
    if not normalized:
        if required:
            raise InvalidDateInput(f"{field_label}: completá la fecha en formato dd/mm/yyyy.")
        return None

    try:
        return datetime.strptime(normalized, "%d/%m/%Y").date()
    except ValueError as exc:
        raise InvalidDateInput(f"{field_label}: fecha inválida. Usá formato dd/mm/yyyy.") from exc
