from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    DB_HOST: str
    DB_PORT: int
    DB_USER: str
    DB_PASSWORD: str
    DB_NAME: str
    # 意思是：我这个项目需要从 .env 里读取这 5 个配置
    # 那 Settings() 就会自动把它们读进来。
    OPENAI_API_KEY: str

    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    # 默认值的作用是：算法和过期时间即使没配置也有默认值；但 JWT_SECRET_KEY 没有默认值，强制项目必须提供密钥，避免误用固定密钥。

    # 意思是：告诉 Pydantic，去项目根目录找 .env 文件。
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
    )

    # 意思是：把数据库配置拼成一个完整连接地址。给后面 create_async_engine() 用来连接 MySQL 的。
    @property
    def async_database_url(self) -> str:
        return (
            f"mysql+aiomysql://{self.DB_USER}:{self.DB_PASSWORD}"
            f"@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}?charset=utf8mb4"
        )

settings = Settings()