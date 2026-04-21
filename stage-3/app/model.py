from sqlmodel import SQLModel, Field
from uuid_extensions import uuid7
from datetime import datetime, timezone


class ProfileBase(SQLModel):
    name: str = Field(index=True, unique=True)
    gender: str = Field(enum=["male", "female"])
    gender_probability: float = Field()
    age: int = Field()
    age_group: str = Field(enum=["child", "teenager", "adult", "senior"])
    country_id: str = Field(length=2)
    country_name: str = Field(length=50)
    country_probability: float = Field()


class Profile(ProfileBase, table=True):
    id: uuid7.UUID = Field(default_factory=uuid7.uuid7, primary_key=True)
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
