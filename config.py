from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    ORACLE_HOST: str
    ORACLE_USERNAME: str
    ORACLE_PASSWORD: str
    ORACLE_APP: str
    API_VERSION: str = "v3"
    INTEROP_VERSION: str = "11.1.2.3.600"

    @property
    def planning_base_url(self) -> str:
        return f"https://{self.ORACLE_HOST}/HyperionPlanning/rest/{self.API_VERSION}"

    @property
    def interop_base_url(self) -> str:
        return f"https://{self.ORACLE_HOST}/interop/rest/{self.INTEROP_VERSION}"

    @property
    def auth(self) -> tuple[str, str]:
        return (self.ORACLE_USERNAME, self.ORACLE_PASSWORD)

    model_config = {"env_file": ".env"}


@lru_cache
def get_settings() -> Settings:
    return Settings()
