import os
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List, Optional
from pathlib import Path
from vosk import Model

# AWS S3 Config
class S3Config(BaseSettings):
    model_config  = SettingsConfigDict(env_file= "s3.env" ) 

    AWS_ACCESS_KEY_ID:str  = Field(alias='AWS_ACCESS_KEY_ID')
    AWS_SECRET_ACCESS_KEY:str = Field(alias='AWS_SECRET_ACCESS_KEY')
    AWS_DEFAULT_REGION:str = Field(alias='AWS_DEFAULT_REGION')
    AWS_S3_ENDPOINT:str = Field(alias='AWS_S3_ENDPOINT')
    AWS_BUCKET_NAME: str = Field(alias='AWS_BUCKET_NAME')
    YA_SPEECH_ID:str  = Field(alias='YA_SPEECH_ID')
    YA_SPEECH_ACCESS_KEY:str = Field(alias='YA_SPEECH_ACCESS_KEY')
    YA_SPEECH_FOLDER_ID:str = Field(alias='YA_SPEECH_FOLDER_ID')
    LR_KEY_API:str = Field(alias='LR_KEY_API')

# JWT Config
class JWTConfig(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")
    
    JWT_SECRET_KEY: str = Field(default="supersecret", alias='JWT_SECRET_KEY')
    JWT_ALGORITHM: str = Field(default="HS256", alias='JWT_ALGORITHM')
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=30, alias='ACCESS_TOKEN_EXPIRE_MINUTES')
    REFRESH_TOKEN_EXPIRE_DAYS: int = Field(default=7, alias='REFRESH_TOKEN_EXPIRE_DAYS')

	