"""
Project Scaffolder DTO schemas.
"""

from typing import Optional
from pydantic import BaseModel, Field


class ScaffoldProjectRequest(BaseModel):
    template: str = Field(..., description="Template type: 'python-app', 'web-react', 'rust-cli', or 'go-service'")
    project_name: str = Field(..., description="Name of the new project folder")
    target_directory: Optional[str] = Field(None, description="Parent directory path (defaults to current working dir)")
    initialize_git: bool = Field(default=True, description="Whether to run git init automatically")


class ScaffoldProjectResponse(BaseModel):
    success: bool
    project_name: str
    project_path: str
    files_created: list[str]
    message: str
