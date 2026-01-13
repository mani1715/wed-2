from pydantic import BaseModel, Field, ConfigDict, field_validator
from typing import Optional, List, Dict
from datetime import datetime, timezone
import uuid
import re


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
    language: List[str]  # telugu, hindi, tamil, english - multiple languages supported
    design_id: str = "royal_classic"  # Selected design theme
    deity_id: Optional[str] = None  # Selected deity: ganesha, venkateswara_padmavati, shiva_parvati, lakshmi_vishnu, none
    whatsapp_groom: Optional[str] = None  # Groom WhatsApp number in E.164 format
    whatsapp_bride: Optional[str] = None  # Bride WhatsApp number in E.164 format
    enabled_languages: List[str] = Field(default=["english"])  # Languages enabled for this invitation
    custom_text: Dict[str, Dict[str, str]] = Field(default_factory=dict)  # Custom text overrides {language: {section: text}}
    sections_enabled: SectionsEnabled = Field(default_factory=SectionsEnabled)
    link_expiry_type: str  # hours, days, permanent
    link_expiry_value: Optional[int] = None  # number of hours/days
    link_expiry_date: Optional[datetime] = None  # calculated expiry date
    is_active: bool = True
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    
    @field_validator('whatsapp_groom', 'whatsapp_bride')
    def validate_whatsapp_number(cls, v):
        """Validate WhatsApp number is in E.164 format"""
        if v is not None and v.strip():
            pattern = r'^\+[1-9]\d{1,14}$'
            if not re.match(pattern, v):
                raise ValueError('WhatsApp number must be in E.164 format (e.g., +919876543210)')
        return v
    
    @field_validator('design_id')
    def validate_design_id(cls, v):
        """Validate design_id is one of the allowed values"""
        allowed_designs = ['royal_classic', 'floral_soft', 'divine_temple', 'modern_minimal', 'cinematic_luxury']
        if v not in allowed_designs:
            raise ValueError(f'design_id must be one of: {", ".join(allowed_designs)}')
        return v
    
    @field_validator('deity_id')
    def validate_deity_id(cls, v):
        """Validate deity_id is one of the allowed values"""
        if v is not None:
            allowed_deities = ['ganesha', 'venkateswara_padmavati', 'shiva_parvati', 'lakshmi_vishnu', 'none']
            if v not in allowed_deities:
                raise ValueError(f'deity_id must be one of: {", ".join(allowed_deities)} or null')
        return v
    
    @field_validator('enabled_languages')
    def validate_enabled_languages(cls, v):
        """Validate at least one language is enabled"""
        if not v or len(v) == 0:
            raise ValueError('At least one language must be enabled')
        allowed_languages = ['english', 'telugu', 'hindi']
        for lang in v:
            if lang not in allowed_languages:
                raise ValueError(f'Language must be one of: {", ".join(allowed_languages)}')
        return v


class ProfileCreate(BaseModel):
    groom_name: str
    bride_name: str
    event_type: str
    event_date: datetime
    venue: str
    language: List[str] = ["english"]
    design_id: str = "royal_classic"
    deity_id: Optional[str] = None
    whatsapp_groom: Optional[str] = None
    whatsapp_bride: Optional[str] = None
    enabled_languages: List[str] = Field(default=["english"])
    custom_text: Dict[str, Dict[str, str]] = Field(default_factory=dict)
    sections_enabled: SectionsEnabled = Field(default_factory=SectionsEnabled)
    link_expiry_type: str = "days"
    link_expiry_value: Optional[int] = 30
    
    @field_validator('whatsapp_groom', 'whatsapp_bride')
    def validate_whatsapp_number(cls, v):
        """Validate WhatsApp number is in E.164 format"""
        if v is not None and v.strip():
            pattern = r'^\+[1-9]\d{1,14}$'
            if not re.match(pattern, v):
                raise ValueError('WhatsApp number must be in E.164 format (e.g., +919876543210)')
        return v
    
    @field_validator('design_id')
    def validate_design_id(cls, v):
        """Validate design_id is one of the allowed values"""
        allowed_designs = ['royal_classic', 'floral_soft', 'divine_temple', 'modern_minimal', 'cinematic_luxury']
        if v not in allowed_designs:
            raise ValueError(f'design_id must be one of: {", ".join(allowed_designs)}')
        return v
    
    @field_validator('deity_id')
    def validate_deity_id(cls, v):
        """Validate deity_id is one of the allowed values"""
        if v is not None:
            allowed_deities = ['ganesha', 'venkateswara_padmavati', 'shiva_parvati', 'lakshmi_vishnu', 'none']
            if v not in allowed_deities:
                raise ValueError(f'deity_id must be one of: {", ".join(allowed_deities)} or null')
        return v
    
    @field_validator('enabled_languages')
    def validate_enabled_languages(cls, v):
        """Validate at least one language is enabled"""
        if not v or len(v) == 0:
            raise ValueError('At least one language must be enabled')
        allowed_languages = ['english', 'telugu', 'hindi']
        for lang in v:
            if lang not in allowed_languages:
                raise ValueError(f'Language must be one of: {", ".join(allowed_languages)}')
        return v


class ProfileUpdate(BaseModel):
    groom_name: Optional[str] = None
    bride_name: Optional[str] = None
    event_type: Optional[str] = None
    event_date: Optional[datetime] = None
    venue: Optional[str] = None
    language: Optional[List[str]] = None
    design_id: Optional[str] = None
    deity_id: Optional[str] = None
    whatsapp_groom: Optional[str] = None
    whatsapp_bride: Optional[str] = None
    enabled_languages: Optional[List[str]] = None
    custom_text: Optional[Dict[str, Dict[str, str]]] = None
    sections_enabled: Optional[SectionsEnabled] = None
    link_expiry_type: Optional[str] = None
    link_expiry_value: Optional[int] = None
    is_active: Optional[bool] = None
    
    @field_validator('whatsapp_groom', 'whatsapp_bride')
    def validate_whatsapp_number(cls, v):
        """Validate WhatsApp number is in E.164 format"""
        if v is not None and v.strip():
            pattern = r'^\+[1-9]\d{1,14}$'
            if not re.match(pattern, v):
                raise ValueError('WhatsApp number must be in E.164 format (e.g., +919876543210)')
        return v
    
    @field_validator('design_id')
    def validate_design_id(cls, v):
        """Validate design_id is one of the allowed values"""
        if v is not None:
            allowed_designs = ['royal_classic', 'floral_soft', 'divine_temple', 'modern_minimal', 'cinematic_luxury']
            if v not in allowed_designs:
                raise ValueError(f'design_id must be one of: {", ".join(allowed_designs)}')
        return v
    
    @field_validator('deity_id')
    def validate_deity_id(cls, v):
        """Validate deity_id is one of the allowed values"""
        if v is not None and v != "":
            allowed_deities = ['ganesha', 'venkateswara_padmavati', 'shiva_parvati', 'lakshmi_vishnu', 'none']
            if v not in allowed_deities:
                raise ValueError(f'deity_id must be one of: {", ".join(allowed_deities)} or null')
        return v
    
    @field_validator('enabled_languages')
    def validate_enabled_languages(cls, v):
        """Validate at least one language is enabled"""
        if v is not None:
            if len(v) == 0:
                raise ValueError('At least one language must be enabled')
            allowed_languages = ['english', 'telugu', 'hindi']
            for lang in v:
                if lang not in allowed_languages:
                    raise ValueError(f'Language must be one of: {", ".join(allowed_languages)}')
        return v


class ProfileResponse(BaseModel):
    id: str
    slug: str
    groom_name: str
    bride_name: str
    event_type: str
    event_date: datetime
    venue: str
    language: List[str]
    design_id: str
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
    language: List[str]
    design_id: str
    sections_enabled: SectionsEnabled
    media: List[ProfileMedia]
    greetings: List[GreetingResponse]
