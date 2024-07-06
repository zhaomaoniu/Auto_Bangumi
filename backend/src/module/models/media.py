from pydantic import BaseModel


class BasicEpisode(BaseModel):
    title: str
    link: str
