from dataclasses import dataclass
from typing import Optional

@dataclass
class FacebookConfig:
    APP_SECRET: str = '850a30f1853fc82acb62c6ec9c875a0b'
    VERIFY_TOKEN: str = 'arf'
    PAGE_ACCESS_TOKEN: str = 'EAFzlgpi4cQMBO6CzRRZAx9LPxBDlRAZC45VTtgMaZBpP3OTp8ZBlFV1uSr33jVo7jTzPespILOMPXWkAHZC5kEMIfoL3Rkz5ZBbtTCxu4eZCNXtZBVCL8yi1hZCFztmWKcRZC4KZCvZCXdwJnuTfnU9jMN5Mw76VXQkPhZCtYzfATATgXySuWqZBIcVzqwoPlDObtn9UkZD'
    API_VERSION: str = 'v20.0'
    DEFAULT_PAGE_ID: str = '143528668844641'

@dataclass
class Config:
    DEBUG: bool = False
    TESTING: bool = False
    MAX_HISTORY_SIZE: int = 100
    facebook: FacebookConfig = FacebookConfig()

config = Config() 