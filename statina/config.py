from pathlib import Path
from typing import Optional

from pydantic import BaseSettings
from pymongo import MongoClient

from statina.adapter.plugin import StatinaAdapter

NIPT_PACKAGE = Path(__file__).parent
PACKAGE_ROOT: Path = NIPT_PACKAGE.parent
ENV_FILE: Path = PACKAGE_ROOT / ".env"


class Settings(BaseSettings):
    """Settings for serving the statina app and connect to the mongo database"""

    db_uri: str = "mongodb://localhost:27017/statina-demo"
    db_name: str = "statina-demo"
    secret_key: str = "dummy"
    algorithm: str = "ABC"
    host: str = "localhost"
    access_token_expire_minutes: int = 15
    port: int = 8000
    admin_email: Optional[str]
    sender_prefix: Optional[str]
    mail_uri: Optional[str]
    website_uri: Optional[str]
    email_server_alias: Optional[str]

    class Config:
        env_file = str(ENV_FILE)


class BaseDatasetThresholds(BaseSettings):
    name: str = "default"
    fetal_fraction_preface: float = 4
    fetal_fraction_y_for_trisomy: float = 4
    fetal_fraction_y_max: float = 3
    fetal_fraction_y_min: float = 0.6
    fetal_fraction_XXX: float = -1
    fetal_fraction_X0: float = 3.4
    y_axis_min: float = -1
    y_axis_max: float = 20
    k_upper: float = 0.9809
    k_lower: float = 0.9799
    m_lower: float = -4.3987
    m_upper: float = 6.5958

    trisomy_soft_max: float = 3
    trisomy_hard_max: float = 4
    trisomy_hard_min: float = -8

    class Config:
        env_file = str(ENV_FILE)


settings = Settings()
base_dataset_thresholds = BaseDatasetThresholds()


def get_nipt_adapter():
    client = MongoClient(settings.db_uri)
    return StatinaAdapter(client, db_name=settings.db_name)
