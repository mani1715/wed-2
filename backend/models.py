from pydantic import BaseModel, Field, ConfigDict, field_validator
from typing import Optional, List, Dict
from datetime import datetime, timezone, time
import uuid
import re


class WeddingEvent(BaseModel):
    """Model for individual wedding event"""
    event_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    date: str  # yyyy-mm-dd format
    start_time: str  # hh:mm format
    end_time: Optional[str] = None  # hh:mm format
    venue_name: str
    venue_address: str
    map_link: str
    description: Optional[str] = Field(None, max_length=200)
    visible: bool = True
    order: int = 0
    
    @field_validator('description')
    def validate_description(cls, v):
        """Validate description max length"""
        if v and len(v) > 200:
            raise ValueError('Description must be 200 characters or less')
        return v


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


class BackgroundMusic(BaseModel):
    enabled: bool = False
    file_url: Optional[str] = None


class MapSettings(BaseModel):
    embed_enabled: bool = False  # Default OFF (safe default)


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
    background_music: BackgroundMusic = Field(default_factory=BackgroundMusic)  # Optional background music
    map_settings: MapSettings = Field(default_factory=MapSettings)  # Map embed settings
    events: List[WeddingEvent] = Field(default_factory=list)  # Wedding events schedule
    link_expiry_type: str  # hours, days, permanent
    link_expiry_value: Optional[int] = None  # number of hours/days
    link_expiry_date: Optional[datetime] = None  # calculated expiry date
    is_active: bool = True
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    
    @field_validator('events')
    def validate_events(cls, v):
        """Validate events list"""
        if v is not None:
            if len(v) > 7:
                raise ValueError('Maximum 7 events allowed')
            
            # Check at least one visible event
            visible_events = [e for e in v if e.visible]
            if len(v) > 0 and len(visible_events) == 0:
                raise ValueError('At least one event must be visible')
        return v
    
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
        allowed_designs = ['royal_classic', 'floral_soft', 'divine_temple', 'modern_minimal', 'cinematic_luxury', 'temple_divine', 'modern_premium', 'artistic_handcrafted', 'heritage_scroll', 'minimal_elegant']
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
        """Validate at least one language is enabled and English is always included"""
        if not v or len(v) == 0:
            raise ValueError('At least one language must be enabled')
        
        # English is mandatory
        if 'english' not in v:
            raise ValueError('English is mandatory and must be included in enabled languages')
        
        allowed_languages = ['english', 'telugu', 'tamil', 'kannada', 'malayalam']
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
    background_music: BackgroundMusic = Field(default_factory=BackgroundMusic)
    map_settings: MapSettings = Field(default_factory=MapSettings)
    events: List[WeddingEvent] = Field(default_factory=list)
    link_expiry_type: str = "days"
    link_expiry_value: Optional[int] = 30
    
    @field_validator('events')
    def validate_events(cls, v):
        """Validate events list"""
        if v is not None:
            if len(v) > 7:
                raise ValueError('Maximum 7 events allowed')
            
            # Check at least one visible event if events exist
            if len(v) > 0:
                visible_events = [e for e in v if e.visible]
                if len(visible_events) == 0:
                    raise ValueError('At least one event must be visible')
        return v
    
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
        allowed_designs = ['royal_classic', 'floral_soft', 'divine_temple', 'modern_minimal', 'cinematic_luxury', 'temple_divine', 'modern_premium', 'artistic_handcrafted', 'heritage_scroll', 'minimal_elegant']
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
        """Validate at least one language is enabled and English is always included"""
        if not v or len(v) == 0:
            raise ValueError('At least one language must be enabled')
        
        # English is mandatory
        if 'english' not in v:
            raise ValueError('English is mandatory and must be included in enabled languages')
        
        allowed_languages = ['english', 'telugu', 'tamil', 'kannada', 'malayalam']
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
    background_music: Optional[BackgroundMusic] = None
    map_settings: Optional[MapSettings] = None
    events: Optional[List[WeddingEvent]] = None
    link_expiry_type: Optional[str] = None
    link_expiry_value: Optional[int] = None
    is_active: Optional[bool] = None
    
    @field_validator('events')
    def validate_events(cls, v):
        """Validate events list"""
        if v is not None:
            if len(v) > 7:
                raise ValueError('Maximum 7 events allowed')
            
            # Check at least one visible event if events exist
            if len(v) > 0:
                visible_events = [e for e in v if e.visible]
                if len(visible_events) == 0:
                    raise ValueError('At least one event must be visible')
        return v
    
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
            allowed_designs = ['royal_classic', 'floral_soft', 'divine_temple', 'modern_minimal', 'cinematic_luxury', 'temple_divine', 'modern_premium', 'artistic_handcrafted', 'heritage_scroll', 'minimal_elegant']
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
        """Validate at least one language is enabled and English is always included"""
        if v is not None:
            if len(v) == 0:
                raise ValueError('At least one language must be enabled')
            
            # English is mandatory
            if 'english' not in v:
                raise ValueError('English is mandatory and must be included in enabled languages')
            
            allowed_languages = ['english', 'telugu', 'tamil', 'kannada', 'malayalam']
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
    deity_id: Optional[str]
    whatsapp_groom: Optional[str]
    whatsapp_bride: Optional[str]
    enabled_languages: List[str]
    custom_text: Dict[str, Dict[str, str]]
    sections_enabled: SectionsEnabled
    background_music: BackgroundMusic
    map_settings: MapSettings
    events: List[WeddingEvent]
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
    deity_id: Optional[str]
    whatsapp_groom: Optional[str]
    whatsapp_bride: Optional[str]
    enabled_languages: List[str]
    custom_text: Dict[str, Dict[str, str]]
    sections_enabled: SectionsEnabled
    background_music: BackgroundMusic
    map_settings: MapSettings
    events: List[WeddingEvent]
    media: List[ProfileMedia]
    greetings: List[GreetingResponse]


class RSVP(BaseModel):
    model_config = ConfigDict(extra="ignore")
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    profile_id: str
    guest_name: str
    guest_phone: str
    status: str  # yes, no, maybe
    guest_count: int = 1
    message: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    
    @field_validator('guest_phone')
    def validate_phone(cls, v):
        """Validate phone number is in E.164 format"""
        pattern = r'^\+[1-9]\d{1,14}$'
        if not re.match(pattern, v):
            raise ValueError('Phone number must be in E.164 format (e.g., +919876543210)')
        return v
    
    @field_validator('status')
    def validate_status(cls, v):
        """Validate RSVP status"""
        if v not in ['yes', 'no', 'maybe']:
            raise ValueError('Status must be one of: yes, no, maybe')
        return v
    
    @field_validator('guest_count')
    def validate_guest_count(cls, v):
        """Validate guest count is between 1 and 10"""
        if v < 1 or v > 10:
            raise ValueError('Guest count must be between 1 and 10')
        return v
    
    @field_validator('message')
    def validate_message(cls, v):
        """Validate message length"""
        if v is not None and len(v) > 250:
            raise ValueError('Message must be 250 characters or less')
        return v


class RSVPCreate(BaseModel):
    guest_name: str
    guest_phone: str
    status: str
    guest_count: int = 1
    message: Optional[str] = None
    
    @field_validator('guest_phone')
    def validate_phone(cls, v):
        """Validate phone number is in E.164 format"""
        pattern = r'^\+[1-9]\d{1,14}$'
        if not re.match(pattern, v):
            raise ValueError('Phone number must be in E.164 format (e.g., +919876543210)')
        return v
    
    @field_validator('status')
    def validate_status(cls, v):
        """Validate RSVP status"""
        if v not in ['yes', 'no', 'maybe']:
            raise ValueError('Status must be one of: yes, no, maybe')
        return v
    
    @field_validator('guest_count')
    def validate_guest_count(cls, v):
        """Validate guest count is between 1 and 10"""
        if v < 1 or v > 10:
            raise ValueError('Guest count must be between 1 and 10')
        return v
    
    @field_validator('message')
    def validate_message(cls, v):
        """Validate message length"""
        if v is not None and len(v) > 250:
            raise ValueError('Message must be 250 characters or less')
        return v


class RSVPResponse(BaseModel):
    id: str
    guest_name: str
    guest_phone: str
    status: str
    guest_count: int
    message: Optional[str]
    created_at: datetime


class RSVPStats(BaseModel):
    total_rsvps: int
    attending_count: int
    not_attending_count: int
    maybe_count: int
    total_guest_count: int



# PHASE 7 - Analytics Models
class Analytics(BaseModel):
    """Model for invitation view tracking"""
    model_config = ConfigDict(extra="ignore")
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    profile_id: str  # Reference to Profile
    total_views: int = 0
    mobile_views: int = 0
    desktop_views: int = 0
    last_viewed_at: Optional[datetime] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class ViewTrackingRequest(BaseModel):
    """Request model for tracking a view"""
    device_type: str  # mobile or desktop
    
    @field_validator('device_type')
    def validate_device_type(cls, v):
        """Validate device type is mobile or desktop"""
        if v not in ['mobile', 'desktop']:
            raise ValueError('device_type must be either "mobile" or "desktop"')
        return v


class AnalyticsResponse(BaseModel):
    """Response model for analytics data"""
    profile_id: str
    total_views: int
    mobile_views: int
    desktop_views: int
    last_viewed_at: Optional[datetime]
