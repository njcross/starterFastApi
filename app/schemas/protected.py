from pydantic import BaseModel

class WhoAmIResponse(BaseModel):
    user_id: int
