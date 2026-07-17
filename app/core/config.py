from pydantic_settings import BaseSettings,SettingsConfigDict
from typing import Literal

class Settings(BaseSettings):

    ENVIRONMENT: Literal["dev", "staging", "prod"] = "dev"

    DB_HOST: str
    DB_PORT: str
    DB_USER: str
    DB_PASS: str
    DB_NAME: str

    REDIS_URL: str

    SECRET_KEY: str
    ALGORITHM: str 
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    REFRESH_TOKEN_EXPIRE_MINUTES: int



    @property
    def DATABASE_URL(self) ->str:
        url = f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASS}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

        if self.DB_HOST in ["localhost", "127.0.0.1"]:
            return url + "?ssl=disable"

        return url

    model_config = SettingsConfigDict(env_file='.env',env_file_encoding='utf-8')


settings = Settings()