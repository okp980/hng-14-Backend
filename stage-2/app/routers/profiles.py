from fastapi import APIRouter, status
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

router = APIRouter(
    prefix="/api/profiles",
    tags=["Profiles"],
)


@router.get("/", response_model=ProfilesPublic)
async def get_profiles(
    *,
    gender: str | None = None,
    country_id: str | None = None,
    age_group: str | None = None,
    session: SessionDep,
):
    statement = select(Profile)
    if gender is not None:
        statement = statement.where(col(Profile.gender) == gender.lower())
    if country_id is not None:
        statement = statement.where(col(Profile.country_id) == country_id.upper())
    if age_group is not None:
        statement = statement.where(col(Profile.age_group) == age_group.lower())
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
