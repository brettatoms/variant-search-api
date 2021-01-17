from pydantic import BaseSettings


class Settings(BaseSettings):
    data_url: str = "https://raw.githubusercontent.com/invitae/variant-search-coding-assignment/master/data/variants.tsv.zip"  # noqa: E501
    data_path: str = "./variants.tsv.zip"


settings = Settings()
