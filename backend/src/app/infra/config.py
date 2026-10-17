from pathlib import Path

from dynaconf import Dynaconf

BASE_DIR = Path(__file__).resolve().parents[3]
CONFIG_FILE = BASE_DIR / "configs" / "config.yaml"
ENV_FILE = BASE_DIR / ".env"


settings = Dynaconf(
    envvar_prefix=False,
    settings_files=[CONFIG_FILE],
    load_dotenv=True,
    dotenv_path=ENV_FILE,
    environments=False,
    merge_enabled=True,
    lowercase_read=True,
)


def build_postgres_url() -> str:
    return (
        f"{settings.db.driver}://"
        f"{settings.db_user}:"
        f"{settings.db_password}@"
        f"{settings.db_host}:"
        f"{settings.db_port}/"
        f"{settings.db_name}"
    )


settings.set("POSTGRES_URL", build_postgres_url())


def get_media_dir() -> Path:
    raw = settings.get("APP_MEDIA_DIR", "")
    text = str(raw).strip() if raw else ""
    if not text:
        return BASE_DIR / "media"
    path = Path(text)
    if not path.is_absolute():
        return BASE_DIR / path
    return path
