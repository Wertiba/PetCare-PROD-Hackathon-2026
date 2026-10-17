from pydantic import BaseModel, ConfigDict


def strip_required_text(value: object) -> object:
    if value is None:
        raise ValueError("value cannot be null")
    if isinstance(value, str):
        return value.strip()
    return value


def strip_optional_text(value: object) -> object:
    if isinstance(value, str):
        stripped = value.strip()
        return stripped or None
    return value


class PyModel(BaseModel):
    model_config = ConfigDict(from_attributes=True, allow_inf_nan=False)
