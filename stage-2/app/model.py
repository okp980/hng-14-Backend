from sqlmodel import SQLModel, Field
import uuid
from datetime import datetime, timezone


class ProfileBase(SQLModel):
    name: str = Field(index=True)
    gender: str = Field()
    gender_probability: float = Field()
    sample_size: int = Field()
    age: int = Field()
    age_group: str = Field()
    country_id: str = Field()
    country_probability: float = Field()


class Profile(ProfileBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class ProfilePublic(SQLModel):
    status: str = "success"
    data: Profile


class ProfilePublicMessage(ProfilePublic):
    message: str | None = "Profile already exists"


class ProfilesPublic(SQLModel):
    status: str = "success"
    count: int
    data: list[Profile]


class ProfileCreate(SQLModel):
    name: str = Field()
