from pydantic import BaseModel

class ProjectMetadataSchema(BaseModel):
    name: str
    version: str

class ConfigurationSchema(BaseModel):
    project: ProjectMetadataSchema