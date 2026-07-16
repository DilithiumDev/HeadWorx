from pydantic import BaseModel
from app.src.core.config.schemas import ConfigurationSchema

class AppContext(BaseModel):
    config: ConfigurationSchema

class ContextBuilder:
    @staticmethod
    def build(config:ConfigurationSchema) -> AppContext:
        return AppContext(
            config=config,
        )