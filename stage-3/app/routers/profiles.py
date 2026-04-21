from fastapi import APIRouter, status, Query
from fastapi.responses import JSONResponse
from ..dependency import SessionDep
from sqlmodel import select, col
import uuid
from ..util import CustomHTTPException, generate_profile
from ..model import (
    ProfilePublic,
    ProfilesPublic,
    ProfilePublicMessage,
    ProfileCreate,
    Profile,
)
from pydantic import BaseModel, Field
from typing import Annotated, Literal

router = APIRouter(
    prefix="/api/profiles",
    tags=["Profiles"],
)


class PaginationParams(BaseModel):
    page: int = 1
    limit: int = Field(default=10, ge=10, le=50)


class FilterParams(PaginationParams):
    gender: str | None = None
    age_group: str | None = None
    country_id: str | None = None
    min_age: int | None = None
    max_age: int | None = None
    min_gender_probability: float | None = None
    min_country_probability: float | None = None
    order: Literal["asc", "desc"] = "asc"
    sort_by: Literal["age", "created_at", "gender_probability"] = "created_at"


class SearchParams(PaginationParams):
    query: str


@router.get("/", response_model=ProfilesPublic)
async def get_profiles(
    filter_params: Annotated[FilterParams, Query()],
    session: SessionDep,
):
    statement = select(Profile)
    if filter_params.gender is not None:
        statement = statement.where(col(Profile.gender) == filter_params.gender.lower())
    if filter_params.country_id is not None:
        statement = statement.where(
            col(Profile.country_id) == filter_params.country_id.upper()
        )
    if filter_params.age_group is not None:
        statement = statement.where(
            col(Profile.age_group) == filter_params.age_group.lower()
        )
    if filter_params.min_age is not None:
        statement = statement.where(col(Profile.age) >= filter_params.min_age)
    if filter_params.max_age is not None:
        statement = statement.where(col(Profile.age) <= filter_params.max_age)
    if filter_params.min_gender_probability is not None:
        statement = statement.where(
            col(Profile.gender_probability) >= filter_params.min_gender_probability
        )
    if filter_params.min_country_probability is not None:
        statement = statement.where(
            col(Profile.country_probability) >= filter_params.min_country_probability
        )
    if filter_params.order is not None:
        statement = statement.order_by(
            col(filter_params.sort_by) * (1 if filter_params.order == "asc" else -1)
        )
    profiles = session.exec(statement).all()
    return ProfilesPublic(count=len(profiles), data=profiles)


@router.get("/search", response_model=ProfilesPublic)
async def search_profiles(
    search_params: Annotated[SearchParams, Query()], session: SessionDep
):
    statement = select(Profile).where(
        col(Profile.name).ilike(f"%{search_params.query}%")
    )
    if search_params.page is not None:
        statement = statement.offset((search_params.page - 1) * search_params.limit)
    if search_params.limit is not None:
        statement = statement.limit(search_params.limit)
    profiles = session.exec(statement).all()
    return ProfilesPublic(count=len(profiles), data=profiles)


@router.get("/{profile_id}", response_model=ProfilePublic)
async def get_profile(profile_id: uuid.UUID, session: SessionDep):
    profile = session.get(Profile, profile_id)
    if not profile:
        raise CustomHTTPException(status_code=404, message="Profile not found")
    return ProfilePublic(data=profile)


@router.post(
    "/",
)
async def create_profile(profile: ProfileCreate, session: SessionDep):
    # db_profile = ProfileCreate.model_validate(profile)
    existing_profile = session.exec(
        select(Profile).where(Profile.name == profile.name)
    ).first()
    if existing_profile:
        print("Profile already exists")
        return ProfilePublicMessage(data=existing_profile)
    profile_data = generate_profile(profile.name)
    db_profile = Profile.model_validate(profile_data)
    session.add(db_profile)
    session.commit()
    session.refresh(db_profile)
    return ProfilePublic(data=db_profile)


@router.delete(
    "/{profile_id}", status_code=status.HTTP_204_NO_CONTENT, response_model=None
)
async def delete_profile(profile_id: uuid.UUID, session: SessionDep):
    profile = session.get(Profile, profile_id)
    if not profile:
        raise CustomHTTPException(status_code=404, message="Profile not found")
    session.delete(profile)
    session.commit()
    return JSONResponse(status_code=204, content={})
