from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
	redis_host: str
	redis_port: int

	model_config = SettingsConfigDict(
		env_file = ".env",
		extra="ignore"	# Docker용 변수 무시 (위에 정의해둔 변수말고는 무시)
	)

settings = Settings()