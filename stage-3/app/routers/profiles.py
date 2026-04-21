from fastapi import APIRouter, Query
from ..dependency import SessionDep
from sqlmodel import select, col
import uuid
from ..util import CustomHTTPException, filter_profiles
from ..model import (
    ProfilePublic,
    ProfilesPublic,
    Profile,
)

from typing import Annotated
from ..util import FilterParams, SearchParams

router = APIRouter(
    prefix="/api/profiles",
    tags=["Profiles"],
)


@router.get("/", response_model=ProfilesPublic)
async def get_profiles(
    filter_params: Annotated[FilterParams, Query()],
    session: SessionDep,
):
    profiles_result = filter_profiles(session=session, filter_params=filter_params)
    return ProfilesPublic(
        page=filter_params.page,
        limit=filter_params.limit,
        total=profiles_result["count"],
        data=profiles_result["data"],
    )


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
