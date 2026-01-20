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
    about: bool = False  # About couple section
    family: bool = False  # Family details section
    love_story: bool = False  # Love story section
    photos: bool = True
    video: bool = False
    events: bool = True
    rsvp: bool = False  # RSVP section (default DISABLED)
    greetings: bool = True  # Greetings/Wishes wall (default ENABLED)
    footer: bool = True
    contact: bool = False  # PHASE 11: Contact information section
    calendar: bool = False  # PHASE 11: Add to calendar feature
    countdown: bool = False  # PHASE 11: Event countdown
    qr: bool = False  # PHASE 11: QR code display


class BackgroundMusic(BaseModel):
    enabled: bool = False
    file_url: Optional[str] = None


class MapSettings(BaseModel):
    embed_enabled: bool = False  # Default OFF (safe default)


class ContactInfo(BaseModel):
    """PHASE 11: Contact information for the wedding"""
    groom_phone: Optional[str] = None  # Groom family phone
    bride_phone: Optional[str] = None  # Bride family phone
    emergency_phone: Optional[str] = None  # Emergency contact
    email: Optional[str] = None  # Contact email
    
    @field_validator('groom_phone', 'bride_phone', 'emergency_phone')
    def validate_phone(cls, v):
        """Validate phone number is in E.164 format"""
        if v is not None and v.strip():
            pattern = r'^\+[1-9]\d{1,14}$'
            if not re.match(pattern, v):
                raise ValueError('Phone number must be in E.164 format (e.g., +919876543210)')
        return v


class Profile(BaseModel):
    model_config = ConfigDict(extra="ignore")
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    slug: str  # Unique link identifier
    groom_name: str
    bride_name: str
    event_type: str  # marriage, engagement, birthday
    event_date: datetime
    venue: str
    city: Optional[str] = None  # City/location
    invitation_message: Optional[str] = None  # Short welcome message (max 200 chars)
    language: List[str]  # telugu, hindi, tamil, english - multiple languages supported
    design_id: str = "royal_classic"  # Selected design theme
    deity_id: Optional[str] = None  # Selected deity: ganesha, venkateswara_padmavati, shiva_parvati, lakshmi_vishnu, none
    whatsapp_groom: Optional[str] = None  # Groom WhatsApp number in E.164 format
    whatsapp_bride: Optional[str] = None  # Bride WhatsApp number in E.164 format
    enabled_languages: List[str] = Field(default=["english"])  # Languages enabled for this invitation
    custom_text: Dict[str, Dict[str, str]] = Field(default_factory=dict)  # Custom text overrides {language: {section: text}}
    about_couple: Optional[str] = None  # Rich text HTML for about couple section
    family_details: Optional[str] = None  # Rich text HTML for family details
    love_story: Optional[str] = None  # Rich text HTML for love story
    cover_photo_id: Optional[str] = None  # ID of media item to use as cover photo
    sections_enabled: SectionsEnabled = Field(default_factory=SectionsEnabled)
    background_music: BackgroundMusic = Field(default_factory=BackgroundMusic)  # Optional background music
    map_settings: MapSettings = Field(default_factory=MapSettings)  # Map embed settings
    contact_info: ContactInfo = Field(default_factory=ContactInfo)  # PHASE 11: Contact information
    events: List[WeddingEvent] = Field(default_factory=list)  # Wedding events schedule
    link_expiry_type: str  # hours, days, permanent
    link_expiry_value: Optional[int] = None  # number of hours/days
    link_expiry_date: Optional[datetime] = None  # calculated expiry date
    is_active: bool = True
    # PHASE 12: Template & Duplication Support
    is_template: bool = False  # Mark if this is a saved template
    template_name: Optional[str] = None  # Name of the template (for admin reference)
    cloned_from: Optional[str] = None  # Profile ID if this was duplicated
    expires_at: Optional[datetime] = None  # Auto-expiry date (default: wedding_date + 7 days)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    
    @field_validator('invitation_message')
    def validate_invitation_message(cls, v):
        """Validate invitation message max length"""
        if v and len(v) > 200:
            raise ValueError('Invitation message must be 200 characters or less')
        return v
    
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
    city: Optional[str] = None
    invitation_message: Optional[str] = None
    language: List[str] = ["english"]
    design_id: str = "royal_classic"
    deity_id: Optional[str] = None
    whatsapp_groom: Optional[str] = None
    whatsapp_bride: Optional[str] = None
    enabled_languages: List[str] = Field(default=["english"])
    custom_text: Dict[str, Dict[str, str]] = Field(default_factory=dict)
    about_couple: Optional[str] = None
    family_details: Optional[str] = None
    love_story: Optional[str] = None
    cover_photo_id: Optional[str] = None
    sections_enabled: SectionsEnabled = Field(default_factory=SectionsEnabled)
    background_music: BackgroundMusic = Field(default_factory=BackgroundMusic)
    map_settings: MapSettings = Field(default_factory=MapSettings)
    contact_info: ContactInfo = Field(default_factory=ContactInfo)  # PHASE 11: Contact information
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
    city: Optional[str] = None
    invitation_message: Optional[str] = None
    language: Optional[List[str]] = None
    design_id: Optional[str] = None
    deity_id: Optional[str] = None
    whatsapp_groom: Optional[str] = None
    whatsapp_bride: Optional[str] = None
    enabled_languages: Optional[List[str]] = None
    custom_text: Optional[Dict[str, Dict[str, str]]] = None
    about_couple: Optional[str] = None
    family_details: Optional[str] = None
    love_story: Optional[str] = None
    cover_photo_id: Optional[str] = None
    sections_enabled: Optional[SectionsEnabled] = None
    background_music: Optional[BackgroundMusic] = None
    map_settings: Optional[MapSettings] = None
    contact_info: Optional[ContactInfo] = None  # PHASE 11: Contact information
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
    city: Optional[str]
    invitation_message: Optional[str]
    language: List[str]
    design_id: str
    deity_id: Optional[str]
    whatsapp_groom: Optional[str]
    whatsapp_bride: Optional[str]
    enabled_languages: List[str]
    custom_text: Dict[str, Dict[str, str]]
    about_couple: Optional[str]
    family_details: Optional[str]
    love_story: Optional[str]
    cover_photo_id: Optional[str]
    sections_enabled: SectionsEnabled
    background_music: BackgroundMusic
    map_settings: MapSettings
    contact_info: ContactInfo  # PHASE 11: Contact information
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
    is_cover: bool = False  # Mark as cover photo
    file_size: Optional[int] = None  # Size in bytes
    original_filename: Optional[str] = None  # Original upload name
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class ProfileMediaCreate(BaseModel):
    media_type: str
    media_url: str
    caption: Optional[str] = None
    order: int = 0
    is_cover: bool = False
    file_size: Optional[int] = None
    original_filename: Optional[str] = None


class Greeting(BaseModel):
    model_config = ConfigDict(extra="ignore")
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    profile_id: str
    guest_name: str
    message: str
    approval_status: str = "pending"  # PHASE 11: pending, approved, rejected
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    
    @field_validator('approval_status')
    def validate_approval_status(cls, v):
        """Validate approval status"""
        if v not in ['pending', 'approved', 'rejected']:
            raise ValueError('Approval status must be one of: pending, approved, rejected')
        return v
    
    @field_validator('message')
    def validate_message(cls, v):
        """Validate message length and sanitize emoji spam"""
        if len(v) > 250:
            raise ValueError('Message must be 250 characters or less')
        # Check for excessive emoji spam (more than 10 emojis)
        emoji_count = sum(1 for char in v if ord(char) > 0x1F300)
        if emoji_count > 10:
            raise ValueError('Too many emojis in message')
        return v


class GreetingCreate(BaseModel):
    guest_name: str
    message: str
    
    @field_validator('message')
    def validate_message(cls, v):
        """Validate message length and sanitize emoji spam"""
        if len(v) > 250:
            raise ValueError('Message must be 250 characters or less')
        # Check for excessive emoji spam (more than 10 emojis)
        emoji_count = sum(1 for char in v if ord(char) > 0x1F300)
        if emoji_count > 10:
            raise ValueError('Too many emojis in message')
        return v


class GreetingResponse(BaseModel):
    id: str
    guest_name: str
    message: str
    approval_status: str  # PHASE 11: Include approval status
    created_at: datetime


class InvitationPublicView(BaseModel):
    slug: str
    groom_name: str
    bride_name: str
    event_type: str
    event_date: datetime
    venue: str
    city: Optional[str]
    invitation_message: Optional[str]
    language: List[str]
    design_id: str
    deity_id: Optional[str]
    whatsapp_groom: Optional[str]
    whatsapp_bride: Optional[str]
    enabled_languages: List[str]
    custom_text: Dict[str, Dict[str, str]]
    about_couple: Optional[str]
    family_details: Optional[str]
    love_story: Optional[str]
    cover_photo_id: Optional[str]
    sections_enabled: SectionsEnabled
    background_music: BackgroundMusic
    map_settings: MapSettings
    contact_info: ContactInfo  # PHASE 11: Contact information
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



# PHASE 7 - Analytics Models (Enhanced in Phase 9)
class DailyView(BaseModel):
    """Model for daily view count"""
    date: str  # yyyy-mm-dd format
    count: int = 0

class Analytics(BaseModel):
    """Model for invitation view tracking with enhanced insights (Phase 9)"""
    model_config = ConfigDict(extra="ignore")
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    profile_id: str  # Reference to Profile
    
    # View counts
    total_views: int = 0  # Total page opens (including repeats)
    unique_views: int = 0  # Unique visitors (session-based, 24-hour window)
    
    # Device breakdown
    mobile_views: int = 0
    desktop_views: int = 0
    tablet_views: int = 0
    
    # Time tracking
    first_viewed_at: Optional[datetime] = None
    last_viewed_at: Optional[datetime] = None
    
    # Daily views (last 30 days)
    daily_views: List[DailyView] = Field(default_factory=list)
    
    # Hourly distribution (0-23)
    hourly_distribution: Dict[str, int] = Field(default_factory=dict)  # {"0": 5, "13": 12, ...}
    
    # Language usage
    language_views: Dict[str, int] = Field(default_factory=dict)  # {"english": 10, "telugu": 5, ...}
    
    # Interaction tracking
    map_clicks: int = 0
    rsvp_clicks: int = 0
    music_plays: int = 0
    music_pauses: int = 0
    
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class ViewSession(BaseModel):
    """Model for tracking unique visitor sessions (24-hour window)"""
    model_config = ConfigDict(extra="ignore")
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    session_id: str  # Client-generated session identifier
    profile_id: str  # Reference to Profile
    device_type: str  # mobile, desktop, or tablet
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    expires_at: datetime  # Session expires after 24 hours


class ViewTrackingRequest(BaseModel):
    """Request model for tracking a view"""
    session_id: str  # Client-generated session identifier
    device_type: str  # mobile, desktop, or tablet
    
    @field_validator('device_type')
    def validate_device_type(cls, v):
        """Validate device type"""
        if v not in ['mobile', 'desktop', 'tablet']:
            raise ValueError('device_type must be either "mobile", "desktop", or "tablet"')
        return v


class InteractionTrackingRequest(BaseModel):
    """Request model for tracking interactions"""
    session_id: str  # Client-generated session identifier
    interaction_type: str  # map_click, rsvp_click, music_play, music_pause
    
    @field_validator('interaction_type')
    def validate_interaction_type(cls, v):
        """Validate interaction type"""
        if v not in ['map_click', 'rsvp_click', 'music_play', 'music_pause']:
            raise ValueError('interaction_type must be one of: map_click, rsvp_click, music_play, music_pause')
        return v


class LanguageTrackingRequest(BaseModel):
    """Request model for tracking language switches"""
    session_id: str  # Client-generated session identifier
    language_code: str  # english, telugu, tamil, kannada, malayalam
    
    @field_validator('language_code')
    def validate_language_code(cls, v):
        """Validate language code"""
        if v not in ['english', 'telugu', 'tamil', 'kannada', 'malayalam']:
            raise ValueError('language_code must be one of: english, telugu, tamil, kannada, malayalam')
        return v


class AnalyticsResponse(BaseModel):
    """Response model for analytics data"""
    profile_id: str
    total_views: int
    unique_views: int
    mobile_views: int
    desktop_views: int
    tablet_views: int
    first_viewed_at: Optional[datetime]
    last_viewed_at: Optional[datetime]
    daily_views: List[DailyView]
    hourly_distribution: Dict[str, int]
    language_views: Dict[str, int]
    map_clicks: int
    rsvp_clicks: int
    music_plays: int
    music_pauses: int


class AnalyticsSummary(BaseModel):
    """Summary analytics for admin dashboard"""
    total_views: int
    unique_visitors: int
    most_viewed_language: Optional[str]
    peak_hour: Optional[int]  # Hour of day (0-23)
    device_breakdown: Dict[str, int]  # {"mobile": 10, "desktop": 5, "tablet": 2}
