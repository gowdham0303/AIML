from pydantic import BaseModel
from typing import Optional

class LinkProcess(BaseModel):
    link: Optional[str]