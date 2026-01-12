from pydantic import BaseModel, Field, ConfigDict, field_validator
from typing import Optional, List, Dict
from datetime import datetime, timezone
import uuid


class Admin(BaseModel):
    model_config = ConfigDict(extra="ignore")
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    email: str
    password_hash: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class AdminLogin(BaseModel):
    email: str
    password: str


class AdminResponse(BaseModel):
    id: str
    email: str
    created_at: datetime


class SectionsEnabled(BaseModel):
    opening: bool = True
    welcome: bool = True
    couple: bool = True
    photos: bool = True
    video: bool = False
    events: bool = True
    greetings: bool = True
    footer: bool = True


class Profile(BaseModel):
    model_config = ConfigDict(extra="ignore")
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    slug: str  # Unique link identifier
    groom_name: str
    bride_name: str
    event_type: str  # marriage, engagement, birthday
    event_date: datetime
    venue: str
    language: str  # telugu, hindi, tamil, english
    sections_enabled: SectionsEnabled = Field(default_factory=SectionsEnabled)
    link_expiry_type: str  # hours, days, permanent
    link_expiry_value: Optional[int] = None  # number of hours/days
    link_expiry_date: Optional[datetime] = None  # calculated expiry date
    is_active: bool = True
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class ProfileCreate(BaseModel):
    groom_name: str
    bride_name: str
    event_type: str
    event_date: datetime
    venue: str
    language: str = "english"
    sections_enabled: SectionsEnabled = Field(default_factory=SectionsEnabled)
    link_expiry_type: str = "permanent"
    link_expiry_value: Optional[int] = None


class ProfileUpdate(BaseModel):
    groom_name: Optional[str] = None
    bride_name: Optional[str] = None
    event_type: Optional[str] = None
    event_date: Optional[datetime] = None
    venue: Optional[str] = None
    language: Optional[str] = None
    sections_enabled: Optional[SectionsEnabled] = None
    link_expiry_type: Optional[str] = None
    link_expiry_value: Optional[int] = None
    is_active: Optional[bool] = None


class ProfileResponse(BaseModel):
    id: str
    slug: str
    groom_name: str
    bride_name: str
    event_type: str
    event_date: datetime
    venue: str
    language: str
    sections_enabled: SectionsEnabled
    link_expiry_type: str
    link_expiry_value: Optional[int]
    link_expiry_date: Optional[datetime]
    is_active: bool
    created_at: datetime
    updated_at: datetime
    invitation_link: str


class ProfileMedia(BaseModel):
    model_config = ConfigDict(extra="ignore")
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    profile_id: str
    media_type: str  # photo, video
    media_url: str
    caption: Optional[str] = None
    order: int = 0
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class ProfileMediaCreate(BaseModel):
    media_type: str
    media_url: str
    caption: Optional[str] = None
    order: int = 0


class Greeting(BaseModel):
    model_config = ConfigDict(extra="ignore")
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    profile_id: str
    guest_name: str
    message: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class GreetingCreate(BaseModel):
    guest_name: str
    message: str


class GreetingResponse(BaseModel):
    id: str
    guest_name: str
    message: str
    created_at: datetime


class InvitationPublicView(BaseModel):
    slug: str
    groom_name: str
    bride_name: str
    event_type: str
    event_date: datetime
    venue: str
    language: str
    sections_enabled: SectionsEnabled
    media: List[ProfileMedia]
    greetings: List[GreetingResponse]
