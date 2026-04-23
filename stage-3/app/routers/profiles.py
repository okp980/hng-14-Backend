from fastapi import APIRouter, Query
from ..dependency import SessionDep
import uuid
from ..util import CustomHTTPException, filter_profiles, filter_search_profiles
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
    try:
        profiles_result = filter_search_profiles(
            session=session, search_params=search_params
        )
        return ProfilesPublic(
            page=search_params.page,
            limit=search_params.limit,
            total=profiles_result["count"],
            data=profiles_result["data"],
        )
    except Exception:
        raise CustomHTTPException(status_code=502, message="Sever error")


@router.get("/{profile_id}", response_model=ProfilePublic)
async def get_profile(profile_id: uuid.UUID, session: SessionDep):
    profile = session.get(Profile, profile_id)
    if not profile:
        raise CustomHTTPException(status_code=404, message="Profile not found")
    return ProfilePublic(data=profile)
