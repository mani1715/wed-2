from fastapi import FastAPI, APIRouter, HTTPException, Depends, status, UploadFile, File, Form
from fastapi.responses import StreamingResponse
from fastapi.staticfiles import StaticFiles
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from typing import List, Optional
from datetime import datetime, timedelta, timezone
import re
import random
import string
import io
import shutil
import bleach
import uuid
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import inch
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image as RLImage
from reportlab.lib import colors as rl_colors
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
import urllib.request
from PIL import Image as PILImage
import qrcode
from icalendar import Calendar, Event as ICalEvent
from io import BytesIO

from models import (
    Admin, AdminLogin, AdminResponse,
    Profile, ProfileCreate, ProfileUpdate, ProfileResponse,
    ProfileMedia, ProfileMediaCreate,
    Greeting, GreetingCreate, GreetingResponse,
    InvitationPublicView, SectionsEnabled, BackgroundMusic, MapSettings, ContactInfo,
    WeddingEvent,
    RSVP, RSVPCreate, RSVPResponse, RSVPStats,
    Analytics, ViewSession, DailyView, ViewTrackingRequest, InteractionTrackingRequest, 
    LanguageTrackingRequest, AnalyticsResponse, AnalyticsSummary,
    # PHASE 12 Models
    InvitationTemplate, InvitationTemplateCreate, InvitationTemplateResponse,
    AuditLog, AuditLogResponse,
    RateLimitTracker, SetExpiryRequest
)
from auth import (
    get_password_hash, verify_password, 
    create_access_token, get_current_admin
)


ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Create the main app without a prefix
app = FastAPI()

# Create uploads directory
UPLOADS_DIR = Path("/app/uploads/photos")
UPLOADS_DIR.mkdir(parents=True, exist_ok=True)

# Mount static files for serving uploaded photos
app.mount("/uploads", StaticFiles(directory="/app/uploads"), name="uploads")

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")


# Helper Functions
def generate_slug(groom_name: str, bride_name: str) -> str:
    """Generate unique URL slug from names"""
    # Take first names only and clean
    groom = re.sub(r'[^a-zA-Z]', '', groom_name.split()[0].lower())
    bride = re.sub(r'[^a-zA-Z]', '', bride_name.split()[0].lower())
    
    # Add random suffix
    suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))
    
    return f"{groom}-{bride}-{suffix}"


def calculate_expiry_date(expiry_type: str, expiry_value: Optional[int]) -> Optional[datetime]:
    """Calculate link expiry date"""
    now = datetime.now(timezone.utc)
    
    # Default to 30 days if not specified
    if not expiry_type or expiry_type == "days":
        days = expiry_value if expiry_value else 30
        return now + timedelta(days=days)
    elif expiry_type == "hours" and expiry_value:
        return now + timedelta(hours=expiry_value)
    
    return None


async def check_profile_active(profile: dict) -> bool:
    """Check if profile is active and not expired"""
    if not profile.get('is_active', True):
        return False
    
    expiry_date = profile.get('link_expiry_date')
    if expiry_date:
        if isinstance(expiry_date, str):
            expiry_date = datetime.fromisoformat(expiry_date)
        
        # Ensure expiry_date is timezone-aware
        if expiry_date.tzinfo is None:
            expiry_date = expiry_date.replace(tzinfo=timezone.utc)
        
        if datetime.now(timezone.utc) > expiry_date:
            return False
    
    return True



# HTML Sanitization
ALLOWED_TAGS = ['p', 'br', 'strong', 'em', 'u', 'ul', 'ol', 'li', 'a', 'h3', 'h4']
ALLOWED_ATTRIBUTES = {'a': ['href', 'title']}

def sanitize_html(html: str) -> str:
    """Sanitize HTML to prevent XSS attacks"""
    if not html:
        return html
    return bleach.clean(
        html,
        tags=ALLOWED_TAGS,
        attributes=ALLOWED_ATTRIBUTES,
        strip=True
    )


# File Upload Validation
ALLOWED_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.webp', '.gif'}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB

def validate_image_file(file: UploadFile) -> tuple[bool, str]:
    """Validate image file"""
    # Check extension
    ext = Path(file.filename).suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        return False, "Invalid file type. Allowed: JPG, PNG, WebP, GIF"
    
    # Check file size
    file.file.seek(0, 2)
    size = file.file.tell()
    file.file.seek(0)
    if size > MAX_FILE_SIZE:
        return False, f"File too large. Maximum size: 5MB"
    
    return True, ""


async def convert_to_webp(file: UploadFile, quality: int = 85) -> tuple[bytes, int]:
    """Convert image to WebP format and return bytes with size"""
    try:
        # Read image
        image_data = await file.read()
        img = PILImage.open(io.BytesIO(image_data))
        
        # Convert RGBA to RGB if necessary
        if img.mode in ('RGBA', 'LA', 'P'):
            background = PILImage.new('RGB', img.size, (255, 255, 255))
            if img.mode == 'P':
                img = img.convert('RGBA')
            background.paste(img, mask=img.split()[-1] if img.mode in ('RGBA', 'LA') else None)
            img = background
        
        # Resize if too large (max 1920px width)
        max_width = 1920
        if img.width > max_width:
            ratio = max_width / img.width
            new_height = int(img.height * ratio)
            img = img.resize((max_width, new_height), PILImage.Resampling.LANCZOS)
        
        # Convert to WebP
        output = io.BytesIO()
        img.save(output, format='WebP', quality=quality, optimize=True)
        webp_data = output.getvalue()
        
        return webp_data, len(webp_data)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid image file: {str(e)}")


# ==================== AUTH ROUTES ====================

@api_router.post("/auth/login")
async def login(login_data: AdminLogin):
    """Admin login endpoint"""
    admin = await db.admins.find_one({"email": login_data.email}, {"_id": 0})
    
    if not admin or not verify_password(login_data.password, admin['password_hash']):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    
    access_token = create_access_token(data={"sub": admin['id']})
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "admin": {
            "id": admin['id'],
            "email": admin['email']
        }
    }


@api_router.get("/auth/me", response_model=AdminResponse)
async def get_current_admin_info(admin_id: str = Depends(get_current_admin)):
    """Get current admin info"""
    admin = await db.admins.find_one({"id": admin_id}, {"_id": 0})
    
    if not admin:
        raise HTTPException(status_code=404, detail="Admin not found")
    
    return AdminResponse(**admin)


# ==================== ADMIN - PROFILE ROUTES ====================

@api_router.get("/admin/profiles", response_model=List[ProfileResponse])
async def get_all_profiles(admin_id: str = Depends(get_current_admin)):
    """Get all profiles"""
    profiles = await db.profiles.find({}, {"_id": 0}).sort("created_at", -1).to_list(1000)
    
    # Convert date strings back to datetime
    for profile in profiles:
        if isinstance(profile.get('event_date'), str):
            profile['event_date'] = datetime.fromisoformat(profile['event_date'])
        if isinstance(profile.get('created_at'), str):
            profile['created_at'] = datetime.fromisoformat(profile['created_at'])
        if isinstance(profile.get('updated_at'), str):
            profile['updated_at'] = datetime.fromisoformat(profile['updated_at'])
        if profile.get('link_expiry_date') and isinstance(profile['link_expiry_date'], str):
            profile['link_expiry_date'] = datetime.fromisoformat(profile['link_expiry_date'])
        
        # Add invitation link
        profile['invitation_link'] = f"/invite/{profile['slug']}"
    
    return profiles


@api_router.post("/admin/profiles", response_model=ProfileResponse)
async def create_profile(profile_data: ProfileCreate, admin: dict = Depends(get_current_admin)):
    """Create new profile"""
    # Generate unique slug
    slug = generate_slug(profile_data.groom_name, profile_data.bride_name)
    
    # Check if slug exists (rare but possible)
    while await db.profiles.find_one({"slug": slug}):
        slug = generate_slug(profile_data.groom_name, profile_data.bride_name)
    
    # Calculate expiry date
    expiry_date = calculate_expiry_date(
        profile_data.link_expiry_type,
        profile_data.link_expiry_value
    )
    
    # PHASE 12: Calculate default expires_at (wedding date + 7 days)
    default_expires_at = profile_data.expires_at if profile_data.expires_at else profile_data.event_date + timedelta(days=7)
    
    # Sanitize HTML fields
    about_couple = sanitize_html(profile_data.about_couple) if profile_data.about_couple else None
    family_details = sanitize_html(profile_data.family_details) if profile_data.family_details else None
    love_story = sanitize_html(profile_data.love_story) if profile_data.love_story else None
    
    # Create profile object
    profile = Profile(
        slug=slug,
        groom_name=profile_data.groom_name,
        bride_name=profile_data.bride_name,
        event_type=profile_data.event_type,
        event_date=profile_data.event_date,
        venue=profile_data.venue,
        city=profile_data.city,
        invitation_message=profile_data.invitation_message,
        language=profile_data.language,
        design_id=profile_data.design_id,
        deity_id=profile_data.deity_id,
        whatsapp_groom=profile_data.whatsapp_groom,
        whatsapp_bride=profile_data.whatsapp_bride,
        enabled_languages=profile_data.enabled_languages,
        custom_text=profile_data.custom_text,
        about_couple=about_couple,
        family_details=family_details,
        love_story=love_story,
        cover_photo_id=profile_data.cover_photo_id,
        sections_enabled=profile_data.sections_enabled,
        background_music=profile_data.background_music,
        map_settings=profile_data.map_settings,
        contact_info=profile_data.contact_info,  # PHASE 11: Contact information
        events=profile_data.events,
        link_expiry_type=profile_data.link_expiry_type,
        link_expiry_value=profile_data.link_expiry_value,
        link_expiry_date=expiry_date,
        # PHASE 12: New fields
        is_template=profile_data.is_template,
        template_name=profile_data.template_name,
        cloned_from=None,  # Set by duplication endpoint only
        expires_at=default_expires_at
    )
    
    # Convert to dict and serialize dates
    doc = profile.model_dump()
    doc['event_date'] = doc['event_date'].isoformat()
    doc['created_at'] = doc['created_at'].isoformat()
    doc['updated_at'] = doc['updated_at'].isoformat()
    if doc['link_expiry_date']:
        doc['link_expiry_date'] = doc['link_expiry_date'].isoformat()
    if doc.get('expires_at'):
        doc['expires_at'] = doc['expires_at'].isoformat()
    
    await db.profiles.insert_one(doc)
    
    # PHASE 12: Create audit log
    await create_audit_log(
        admin_id=admin['id'],
        action="profile_created",
        target_id=profile.id,
        details={"slug": slug, "groom": profile_data.groom_name, "bride": profile_data.bride_name}
    )
    
    # Prepare response
    response_data = profile.model_dump()
    response_data['invitation_link'] = f"/invite/{profile.slug}"
    
    return ProfileResponse(**response_data)


@api_router.get("/admin/profiles/{profile_id}", response_model=ProfileResponse)
async def get_profile(profile_id: str, admin_id: str = Depends(get_current_admin)):
    """Get single profile"""
    profile = await db.profiles.find_one({"id": profile_id}, {"_id": 0})
    
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    
    # Convert date strings
    if isinstance(profile.get('event_date'), str):
        profile['event_date'] = datetime.fromisoformat(profile['event_date'])
    if isinstance(profile.get('created_at'), str):
        profile['created_at'] = datetime.fromisoformat(profile['created_at'])
    if isinstance(profile.get('updated_at'), str):
        profile['updated_at'] = datetime.fromisoformat(profile['updated_at'])
    if profile.get('link_expiry_date') and isinstance(profile['link_expiry_date'], str):
        profile['link_expiry_date'] = datetime.fromisoformat(profile['link_expiry_date'])
    
    profile['invitation_link'] = f"/invite/{profile['slug']}"
    
    return ProfileResponse(**profile)


@api_router.put("/admin/profiles/{profile_id}", response_model=ProfileResponse)
async def update_profile(
    profile_id: str,
    update_data: ProfileUpdate,
    admin: dict = Depends(get_current_admin)
):
    """Update profile"""
    existing_profile = await db.profiles.find_one({"id": profile_id}, {"_id": 0})
    
    if not existing_profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    
    # Prepare update
    update_dict = update_data.model_dump(exclude_unset=True)
    
    # Sanitize HTML fields if present
    if 'about_couple' in update_dict and update_dict['about_couple']:
        update_dict['about_couple'] = sanitize_html(update_dict['about_couple'])
    if 'family_details' in update_dict and update_dict['family_details']:
        update_dict['family_details'] = sanitize_html(update_dict['family_details'])
    if 'love_story' in update_dict and update_dict['love_story']:
        update_dict['love_story'] = sanitize_html(update_dict['love_story'])
    
    # Recalculate expiry if changed
    if 'link_expiry_type' in update_dict or 'link_expiry_value' in update_dict:
        expiry_type = update_dict.get('link_expiry_type', existing_profile['link_expiry_type'])
        expiry_value = update_dict.get('link_expiry_value', existing_profile.get('link_expiry_value'))
        update_dict['link_expiry_date'] = calculate_expiry_date(expiry_type, expiry_value)
    
    # Update timestamp
    update_dict['updated_at'] = datetime.now(timezone.utc)
    
    # Serialize dates
    if 'event_date' in update_dict:
        update_dict['event_date'] = update_dict['event_date'].isoformat()
    if 'expires_at' in update_dict and update_dict['expires_at']:
        update_dict['expires_at'] = update_dict['expires_at'].isoformat()
    update_dict['updated_at'] = update_dict['updated_at'].isoformat()
    if 'link_expiry_date' in update_dict and update_dict['link_expiry_date']:
        update_dict['link_expiry_date'] = update_dict['link_expiry_date'].isoformat()
    
    await db.profiles.update_one(
        {"id": profile_id},
        {"$set": update_dict}
    )
    
    # PHASE 12: Create audit log
    await create_audit_log(
        admin_id=admin['id'],
        action="profile_updated",
        target_id=profile_id,
        details={"fields_updated": list(update_dict.keys())}
    )
    
    # Get updated profile
    updated_profile = await db.profiles.find_one({"id": profile_id}, {"_id": 0})
    
    # Convert dates back
    if isinstance(updated_profile.get('event_date'), str):
        updated_profile['event_date'] = datetime.fromisoformat(updated_profile['event_date'])
    if isinstance(updated_profile.get('created_at'), str):
        updated_profile['created_at'] = datetime.fromisoformat(updated_profile['created_at'])
    if isinstance(updated_profile.get('updated_at'), str):
        updated_profile['updated_at'] = datetime.fromisoformat(updated_profile['updated_at'])
    if updated_profile.get('link_expiry_date') and isinstance(updated_profile['link_expiry_date'], str):
        updated_profile['link_expiry_date'] = datetime.fromisoformat(updated_profile['link_expiry_date'])
    if updated_profile.get('expires_at') and isinstance(updated_profile['expires_at'], str):
        updated_profile['expires_at'] = datetime.fromisoformat(updated_profile['expires_at'])
    
    updated_profile['invitation_link'] = f"/invite/{updated_profile['slug']}"
    
    return ProfileResponse(**updated_profile)


@api_router.delete("/admin/profiles/{profile_id}")
async def delete_profile(profile_id: str, admin_id: str = Depends(get_current_admin)):
    """Delete profile (soft delete)"""
    result = await db.profiles.update_one(
        {"id": profile_id},
        {"$set": {"is_active": False}}
    )
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Profile not found")
    
    return {"message": "Profile deleted successfully"}


# ==================== ADMIN - MEDIA ROUTES ====================

@api_router.post("/admin/profiles/{profile_id}/media", response_model=ProfileMedia)
async def add_profile_media(
    profile_id: str,
    media_data: ProfileMediaCreate,
    admin_id: str = Depends(get_current_admin)
):
    """Add media to profile"""
    # Check if profile exists
    profile = await db.profiles.find_one({"id": profile_id})
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    
    media = ProfileMedia(
        profile_id=profile_id,
        media_type=media_data.media_type,
        media_url=media_data.media_url,
        caption=media_data.caption,
        order=media_data.order
    )
    
    doc = media.model_dump()
    doc['created_at'] = doc['created_at'].isoformat()
    
    await db.profile_media.insert_one(doc)
    
    return media


@api_router.delete("/admin/media/{media_id}")
async def delete_media(media_id: str, admin_id: str = Depends(get_current_admin)):
    """Delete media"""
    result = await db.profile_media.delete_one({"id": media_id})
    
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Media not found")
    
    return {"message": "Media deleted successfully"}


@api_router.get("/admin/profiles/{profile_id}/media", response_model=List[ProfileMedia])
async def get_profile_media(profile_id: str, admin_id: str = Depends(get_current_admin)):
    """Get all media for a profile"""
    media_list = await db.profile_media.find(
        {"profile_id": profile_id},
        {"_id": 0}
    ).sort("order", 1).to_list(1000)
    
    for media in media_list:
        if isinstance(media.get('created_at'), str):
            media['created_at'] = datetime.fromisoformat(media['created_at'])
    
    return media_list



@api_router.post("/admin/profiles/{profile_id}/upload-photo", response_model=ProfileMedia)
async def upload_photo(
    profile_id: str,
    file: UploadFile = File(...),
    caption: str = Form(""),
    admin_id: str = Depends(get_current_admin)
):
    """Upload a photo for a profile with WebP conversion"""
    # Check if profile exists
    profile = await db.profiles.find_one({"id": profile_id})
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    
    # Validate max 20 photos per profile
    media_count = await db.profile_media.count_documents({
        "profile_id": profile_id,
        "media_type": "photo"
    })
    if media_count >= 20:
        raise HTTPException(status_code=400, detail="Maximum 20 photos allowed per profile")
    
    # Validate image file
    is_valid, error_msg = validate_image_file(file)
    if not is_valid:
        raise HTTPException(status_code=400, detail=error_msg)
    
    # Convert to WebP
    webp_data, file_size = await convert_to_webp(file, quality=85)
    
    # Generate unique filename
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    random_suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))
    filename = f"{profile_id}_{timestamp}_{random_suffix}.webp"
    file_path = UPLOADS_DIR / filename
    
    # Save file
    with open(file_path, 'wb') as f:
        f.write(webp_data)
    
    # Get next order number
    max_order = await db.profile_media.find_one(
        {"profile_id": profile_id},
        sort=[("order", -1)]
    )
    next_order = (max_order.get('order', 0) + 1) if max_order else 0
    
    # Create media record
    media = ProfileMedia(
        profile_id=profile_id,
        media_type="photo",
        media_url=f"/uploads/photos/{filename}",
        caption=caption if caption else None,
        order=next_order,
        is_cover=False,
        file_size=file_size,
        original_filename=file.filename
    )
    
    doc = media.model_dump()
    doc['created_at'] = doc['created_at'].isoformat()
    
    await db.profile_media.insert_one(doc)
    
    return media


@api_router.put("/admin/media/{media_id}/set-cover")
async def set_cover_photo(
    media_id: str,
    admin_id: str = Depends(get_current_admin)
):
    """Set a photo as the cover photo"""
    # Find the media
    media = await db.profile_media.find_one({"id": media_id})
    if not media:
        raise HTTPException(status_code=404, detail="Media not found")
    
    if media['media_type'] != 'photo':
        raise HTTPException(status_code=400, detail="Only photos can be set as cover")
    
    profile_id = media['profile_id']
    
    # Unset all other covers for this profile
    await db.profile_media.update_many(
        {"profile_id": profile_id},
        {"$set": {"is_cover": False}}
    )
    
    # Set this media as cover
    await db.profile_media.update_one(
        {"id": media_id},
        {"$set": {"is_cover": True}}
    )
    
    # Update profile cover_photo_id
    await db.profiles.update_one(
        {"id": profile_id},
        {"$set": {"cover_photo_id": media_id}}
    )
    
    return {"message": "Cover photo updated successfully"}


@api_router.post("/admin/profiles/{profile_id}/reorder-media")
async def reorder_media(
    profile_id: str,
    media_ids: List[str],
    admin_id: str = Depends(get_current_admin)
):
    """Reorder media items"""
    # Check if profile exists
    profile = await db.profiles.find_one({"id": profile_id})
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    
    # Update order for each media
    for index, media_id in enumerate(media_ids):
        await db.profile_media.update_one(
            {"id": media_id, "profile_id": profile_id},
            {"$set": {"order": index}}
        )
    
    return {"message": "Media reordered successfully"}


@api_router.put("/admin/media/{media_id}/caption")
async def update_media_caption(
    media_id: str,
    caption: str = Form(""),
    admin_id: str = Depends(get_current_admin)
):
    """Update media caption"""
    result = await db.profile_media.update_one(
        {"id": media_id},
        {"$set": {"caption": caption if caption else None}}
    )
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Media not found")
    
    return {"message": "Caption updated successfully"}


# ==================== PUBLIC INVITATION ROUTES ====================

@api_router.get("/invite/{slug}", response_model=InvitationPublicView)
async def get_invitation(slug: str):
    """Get public invitation by slug"""
    profile = await db.profiles.find_one({"slug": slug}, {"_id": 0})
    
    if not profile:
        raise HTTPException(status_code=404, detail="Invitation not found")
    
    # Check if active and not expired
    if not await check_profile_active(profile):
        raise HTTPException(status_code=410, detail="This invitation link has expired")
    
    # Get media
    media_list = await db.profile_media.find(
        {"profile_id": profile['id']},
        {"_id": 0}
    ).sort("order", 1).to_list(1000)
    
    # Get greetings - PHASE 11: Only return approved greetings for public view (last 20)
    greetings_list = await db.greetings.find(
        {"profile_id": profile['id'], "approval_status": "approved"},
        {"_id": 0}
    ).sort("created_at", -1).limit(20).to_list(20)
    
    # Convert date strings
    if isinstance(profile.get('event_date'), str):
        profile['event_date'] = datetime.fromisoformat(profile['event_date'])
    
    for media in media_list:
        if isinstance(media.get('created_at'), str):
            media['created_at'] = datetime.fromisoformat(media['created_at'])
    
    for greeting in greetings_list:
        if isinstance(greeting.get('created_at'), str):
            greeting['created_at'] = datetime.fromisoformat(greeting['created_at'])
    
    return InvitationPublicView(
        slug=profile['slug'],
        groom_name=profile['groom_name'],
        bride_name=profile['bride_name'],
        event_type=profile['event_type'],
        event_date=profile['event_date'],
        venue=profile['venue'],
        city=profile.get('city'),
        invitation_message=profile.get('invitation_message'),
        language=profile['language'],
        design_id=profile['design_id'],
        deity_id=profile.get('deity_id'),
        whatsapp_groom=profile.get('whatsapp_groom'),
        whatsapp_bride=profile.get('whatsapp_bride'),
        enabled_languages=profile.get('enabled_languages', ['english']),
        custom_text=profile.get('custom_text', {}),
        about_couple=profile.get('about_couple'),
        family_details=profile.get('family_details'),
        love_story=profile.get('love_story'),
        cover_photo_id=profile.get('cover_photo_id'),
        sections_enabled=SectionsEnabled(**profile['sections_enabled']),
        background_music=BackgroundMusic(**profile.get('background_music', {'enabled': False, 'file_url': None})),
        map_settings=MapSettings(**profile.get('map_settings', {'embed_enabled': False})),
        contact_info=ContactInfo(**profile.get('contact_info', {})),  # PHASE 11: Contact information
        events=[WeddingEvent(**e) for e in profile.get('events', [])],
        media=[ProfileMedia(**m) for m in media_list],
        greetings=[GreetingResponse(**g) for g in greetings_list]
    )


@api_router.post("/invite/{slug}/greetings", response_model=GreetingResponse)
async def submit_greeting(slug: str, greeting_data: GreetingCreate):
    """Submit greeting for invitation - PHASE 11: Default status is 'pending' for moderation"""
    profile = await db.profiles.find_one({"slug": slug}, {"_id": 0})
    
    if not profile:
        raise HTTPException(status_code=404, detail="Invitation not found")
    
    if not await check_profile_active(profile):
        raise HTTPException(status_code=410, detail="This invitation link has expired")
    
    # Sanitize input using bleach
    import bleach
    sanitized_name = bleach.clean(greeting_data.guest_name, tags=[], strip=True)
    sanitized_message = bleach.clean(greeting_data.message, tags=[], strip=True)
    
    greeting = Greeting(
        profile_id=profile['id'],
        guest_name=sanitized_name,
        message=sanitized_message,
        approval_status="pending"  # PHASE 11: Default to pending for moderation
    )
    
    doc = greeting.model_dump()
    doc['created_at'] = doc['created_at'].isoformat()
    
    await db.greetings.insert_one(doc)
    
    return GreetingResponse(
        id=greeting.id,
        guest_name=greeting.guest_name,
        message=greeting.message,
        approval_status=greeting.approval_status,
        created_at=greeting.created_at
    )


@api_router.get("/admin/profiles/{profile_id}/greetings", response_model=List[GreetingResponse])
async def get_profile_greetings(
    profile_id: str, 
    status: Optional[str] = None,
    admin_id: str = Depends(get_current_admin)
):
    """PHASE 11: Get all greetings for a profile with optional status filter"""
    # Build query filter
    query_filter = {"profile_id": profile_id}
    if status and status in ['pending', 'approved', 'rejected']:
        query_filter["approval_status"] = status
    
    greetings = await db.greetings.find(
        query_filter,
        {"_id": 0}
    ).sort("created_at", -1).to_list(1000)
    
    for greeting in greetings:
        if isinstance(greeting.get('created_at'), str):
            greeting['created_at'] = datetime.fromisoformat(greeting['created_at'])
        # Set default approval_status for old greetings without this field
        if 'approval_status' not in greeting:
            greeting['approval_status'] = 'approved'
    
    return [GreetingResponse(**g) for g in greetings]


# ==================== PHASE 11: GREETING MODERATION ROUTES ====================

@api_router.put("/admin/greetings/{greeting_id}/approve")
async def approve_greeting(greeting_id: str, admin_id: str = Depends(get_current_admin)):
    """PHASE 11: Approve a greeting"""
    result = await db.greetings.update_one(
        {"id": greeting_id},
        {"$set": {"approval_status": "approved"}}
    )
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Greeting not found")
    
    return {"message": "Greeting approved successfully"}


@api_router.put("/admin/greetings/{greeting_id}/reject")
async def reject_greeting(greeting_id: str, admin_id: str = Depends(get_current_admin)):
    """PHASE 11: Reject a greeting"""
    result = await db.greetings.update_one(
        {"id": greeting_id},
        {"$set": {"approval_status": "rejected"}}
    )
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Greeting not found")
    
    return {"message": "Greeting rejected successfully"}


@api_router.delete("/admin/greetings/{greeting_id}")
async def delete_greeting(greeting_id: str, admin_id: str = Depends(get_current_admin)):
    """PHASE 11: Delete a greeting"""
    result = await db.greetings.delete_one({"id": greeting_id})
    
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Greeting not found")
    
    return {"message": "Greeting deleted successfully"}


# ==================== RSVP ROUTES ====================

@api_router.post("/rsvp", response_model=RSVPResponse)
async def submit_rsvp(slug: str, rsvp_data: RSVPCreate):
    """Submit RSVP for invitation (public endpoint)"""
    # Find profile by slug
    profile = await db.profiles.find_one({"slug": slug}, {"_id": 0})
    
    if not profile:
        raise HTTPException(status_code=404, detail="Invitation not found")
    
    # Check if profile is active and not expired
    if not await check_profile_active(profile):
        raise HTTPException(status_code=410, detail="This invitation link has expired")
    
    # Check for duplicate RSVP (profile_id + guest_phone)
    existing_rsvp = await db.rsvps.find_one({
        "profile_id": profile['id'],
        "guest_phone": rsvp_data.guest_phone
    }, {"_id": 0})
    
    if existing_rsvp:
        # PHASE 11: Check if within 48 hours - allow update instead
        if isinstance(existing_rsvp.get('created_at'), str):
            created_at = datetime.fromisoformat(existing_rsvp['created_at'])
        else:
            created_at = existing_rsvp['created_at']
        
        time_since_creation = datetime.now(timezone.utc) - created_at
        if time_since_creation <= timedelta(hours=48):
            # Update existing RSVP
            update_doc = {
                "guest_name": rsvp_data.guest_name,
                "status": rsvp_data.status,
                "guest_count": rsvp_data.guest_count,
                "message": rsvp_data.message
            }
            
            await db.rsvps.update_one(
                {"id": existing_rsvp['id']},
                {"$set": update_doc}
            )
            
            # Fetch updated RSVP
            updated_rsvp = await db.rsvps.find_one({"id": existing_rsvp['id']}, {"_id": 0})
            if isinstance(updated_rsvp.get('created_at'), str):
                updated_rsvp['created_at'] = datetime.fromisoformat(updated_rsvp['created_at'])
            
            return RSVPResponse(**updated_rsvp)
        else:
            raise HTTPException(
                status_code=400,
                detail="You have already submitted an RSVP. Edits are only allowed within 48 hours of submission."
            )
    
    # Create RSVP
    rsvp = RSVP(
        profile_id=profile['id'],
        guest_name=rsvp_data.guest_name,
        guest_phone=rsvp_data.guest_phone,
        status=rsvp_data.status,
        guest_count=rsvp_data.guest_count,
        message=rsvp_data.message
    )
    
    doc = rsvp.model_dump()
    doc['created_at'] = doc['created_at'].isoformat()
    
    await db.rsvps.insert_one(doc)
    
    return RSVPResponse(
        id=rsvp.id,
        guest_name=rsvp.guest_name,
        guest_phone=rsvp.guest_phone,
        status=rsvp.status,
        guest_count=rsvp.guest_count,
        message=rsvp.message,
        created_at=rsvp.created_at
    )


@api_router.get("/invite/{slug}/rsvp/check")
async def check_rsvp_status(slug: str, phone: str):
    """PHASE 11: Check if RSVP exists and if it can be edited"""
    # Find profile by slug
    profile = await db.profiles.find_one({"slug": slug}, {"_id": 0})
    
    if not profile:
        raise HTTPException(status_code=404, detail="Invitation not found")
    
    # Find RSVP by phone
    existing_rsvp = await db.rsvps.find_one({
        "profile_id": profile['id'],
        "guest_phone": phone
    }, {"_id": 0})
    
    if not existing_rsvp:
        return {
            "exists": False,
            "can_edit": False,
            "rsvp": None
        }
    
    # Convert created_at if string
    if isinstance(existing_rsvp.get('created_at'), str):
        created_at = datetime.fromisoformat(existing_rsvp['created_at'])
    else:
        created_at = existing_rsvp['created_at']
    
    # Check if within 48 hours
    time_since_creation = datetime.now(timezone.utc) - created_at
    can_edit = time_since_creation <= timedelta(hours=48)
    
    # Convert dates for response
    if isinstance(existing_rsvp.get('created_at'), str):
        existing_rsvp['created_at'] = datetime.fromisoformat(existing_rsvp['created_at'])
    
    return {
        "exists": True,
        "can_edit": can_edit,
        "hours_remaining": max(0, 48 - (time_since_creation.total_seconds() / 3600)) if can_edit else 0,
        "rsvp": RSVPResponse(**existing_rsvp)
    }


@api_router.put("/rsvp/{rsvp_id}", response_model=RSVPResponse)
async def update_rsvp(rsvp_id: str, rsvp_data: RSVPCreate):
    """PHASE 11: Update RSVP within 48 hours of creation"""
    # Find existing RSVP
    existing_rsvp = await db.rsvps.find_one({"id": rsvp_id}, {"_id": 0})
    
    if not existing_rsvp:
        raise HTTPException(status_code=404, detail="RSVP not found")
    
    # Convert created_at if string
    if isinstance(existing_rsvp.get('created_at'), str):
        created_at = datetime.fromisoformat(existing_rsvp['created_at'])
    else:
        created_at = existing_rsvp['created_at']
    
    # Check if within 48 hours
    time_since_creation = datetime.now(timezone.utc) - created_at
    if time_since_creation > timedelta(hours=48):
        raise HTTPException(
            status_code=403,
            detail="Cannot edit RSVP after 48 hours of submission"
        )
    
    # Verify phone number matches (security check)
    if existing_rsvp['guest_phone'] != rsvp_data.guest_phone:
        raise HTTPException(
            status_code=403,
            detail="Phone number does not match original RSVP"
        )
    
    # Update RSVP
    update_doc = {
        "guest_name": rsvp_data.guest_name,
        "status": rsvp_data.status,
        "guest_count": rsvp_data.guest_count,
        "message": rsvp_data.message
    }
    
    result = await db.rsvps.update_one(
        {"id": rsvp_id},
        {"$set": update_doc}
    )
    
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="RSVP not found or no changes made")
    
    # Fetch updated RSVP
    updated_rsvp = await db.rsvps.find_one({"id": rsvp_id}, {"_id": 0})
    
    # Convert date strings
    if isinstance(updated_rsvp.get('created_at'), str):
        updated_rsvp['created_at'] = datetime.fromisoformat(updated_rsvp['created_at'])
    
    return RSVPResponse(**updated_rsvp)


@api_router.get("/admin/profiles/{profile_id}/rsvps", response_model=List[RSVPResponse])
async def get_profile_rsvps(
    profile_id: str,
    status: Optional[str] = None,
    admin_id: str = Depends(get_current_admin)
):
    """Get all RSVPs for a profile with optional status filter"""
    # Build query
    query = {"profile_id": profile_id}
    if status and status in ['yes', 'no', 'maybe']:
        query['status'] = status
    
    # Fetch RSVPs (limit 500)
    rsvps = await db.rsvps.find(
        query,
        {"_id": 0}
    ).sort("created_at", -1).limit(500).to_list(500)
    
    # Convert date strings
    for rsvp in rsvps:
        if isinstance(rsvp.get('created_at'), str):
            rsvp['created_at'] = datetime.fromisoformat(rsvp['created_at'])
    
    return [RSVPResponse(**r) for r in rsvps]


@api_router.get("/admin/profiles/{profile_id}/rsvps/stats", response_model=RSVPStats)
async def get_rsvp_stats(profile_id: str, admin_id: str = Depends(get_current_admin)):
    """Get RSVP statistics for a profile"""
    # Get all RSVPs for the profile
    rsvps = await db.rsvps.find(
        {"profile_id": profile_id},
        {"_id": 0}
    ).to_list(500)
    
    # Calculate statistics
    total_rsvps = len(rsvps)
    attending_count = sum(1 for r in rsvps if r['status'] == 'yes')
    not_attending_count = sum(1 for r in rsvps if r['status'] == 'no')
    maybe_count = sum(1 for r in rsvps if r['status'] == 'maybe')
    total_guest_count = sum(r.get('guest_count', 1) for r in rsvps if r['status'] == 'yes')
    
    return RSVPStats(
        total_rsvps=total_rsvps,
        attending_count=attending_count,
        not_attending_count=not_attending_count,
        maybe_count=maybe_count,
        total_guest_count=total_guest_count
    )


@api_router.get("/admin/profiles/{profile_id}/rsvps/export")
async def export_rsvps_csv(profile_id: str, admin_id: str = Depends(get_current_admin)):
    """Export RSVPs as CSV"""
    from fastapi.responses import StreamingResponse
    import io
    import csv
    
    # Fetch all RSVPs
    rsvps = await db.rsvps.find(
        {"profile_id": profile_id},
        {"_id": 0}
    ).sort("created_at", -1).to_list(500)
    
    # Convert to CSV
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Write header
    writer.writerow(['Guest Name', 'Phone', 'Status', 'Guest Count', 'Message', 'Submitted At'])
    
    # Write data
    for rsvp in rsvps:
        created_at = rsvp.get('created_at')
        if isinstance(created_at, str):
            created_at = datetime.fromisoformat(created_at)
        
        writer.writerow([
            rsvp.get('guest_name', ''),
            rsvp.get('guest_phone', ''),
            rsvp.get('status', ''),
            rsvp.get('guest_count', 1),
            rsvp.get('message', ''),
            created_at.strftime('%Y-%m-%d %H:%M:%S') if created_at else ''
        ])
    
    # Prepare response
    output.seek(0)
    
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={
            "Content-Disposition": f"attachment; filename=rsvps_{profile_id}.csv"
        }
    )


# ==================== ANALYTICS ROUTES (PHASE 9 - ENHANCED) ====================

@api_router.post("/invite/{slug}/view", status_code=204)
async def track_invitation_view(slug: str, view_data: ViewTrackingRequest):
    """Track invitation view with session-based unique visitor tracking (Phase 9)"""
    # Find profile by slug
    profile = await db.profiles.find_one({"slug": slug}, {"_id": 0})
    
    if not profile:
        raise HTTPException(status_code=404, detail="Invitation not found")
    
    profile_id = profile['id']
    now = datetime.now(timezone.utc)
    current_date = now.date().isoformat()
    current_hour = str(now.hour)
    
    # Check if session exists and is valid (24-hour window)
    existing_session = await db.view_sessions.find_one({
        "session_id": view_data.session_id,
        "profile_id": profile_id,
        "expires_at": {"$gt": now.isoformat()}
    })
    
    is_unique_view = existing_session is None
    
    # If no valid session exists, create one
    if is_unique_view:
        session = ViewSession(
            session_id=view_data.session_id,
            profile_id=profile_id,
            device_type=view_data.device_type,
            created_at=now,
            expires_at=now + timedelta(hours=24)
        )
        
        session_doc = session.model_dump()
        session_doc['created_at'] = session_doc['created_at'].isoformat()
        session_doc['expires_at'] = session_doc['expires_at'].isoformat()
        
        await db.view_sessions.insert_one(session_doc)
    
    # Find or create analytics document
    analytics_doc = await db.analytics.find_one({"profile_id": profile_id}, {"_id": 0})
    
    if analytics_doc:
        # Update existing analytics
        update_data = {
            "total_views": analytics_doc.get('total_views', 0) + 1,
            "last_viewed_at": now.isoformat()
        }
        
        # Update unique views if new session
        if is_unique_view:
            update_data["unique_views"] = analytics_doc.get('unique_views', 0) + 1
            
            # Set first_viewed_at if not set
            if not analytics_doc.get('first_viewed_at'):
                update_data["first_viewed_at"] = now.isoformat()
        
        # Increment device-specific counter
        if view_data.device_type == "mobile":
            update_data["mobile_views"] = analytics_doc.get('mobile_views', 0) + 1
        elif view_data.device_type == "desktop":
            update_data["desktop_views"] = analytics_doc.get('desktop_views', 0) + 1
        elif view_data.device_type == "tablet":
            update_data["tablet_views"] = analytics_doc.get('tablet_views', 0) + 1
        
        # Update hourly distribution
        hourly_dist = analytics_doc.get('hourly_distribution', {})
        hourly_dist[current_hour] = hourly_dist.get(current_hour, 0) + 1
        update_data["hourly_distribution"] = hourly_dist
        
        # Update daily views (keep last 30 days)
        daily_views = analytics_doc.get('daily_views', [])
        today_entry = next((dv for dv in daily_views if dv['date'] == current_date), None)
        
        if today_entry:
            today_entry['count'] += 1
        else:
            daily_views.append({"date": current_date, "count": 1})
        
        # Keep only last 30 days
        if len(daily_views) > 30:
            daily_views = sorted(daily_views, key=lambda x: x['date'], reverse=True)[:30]
        
        update_data["daily_views"] = daily_views
        
        await db.analytics.update_one(
            {"profile_id": profile_id},
            {"$set": update_data}
        )
    else:
        # Create new analytics document
        analytics = Analytics(
            profile_id=profile_id,
            total_views=1,
            unique_views=1 if is_unique_view else 0,
            mobile_views=1 if view_data.device_type == "mobile" else 0,
            desktop_views=1 if view_data.device_type == "desktop" else 0,
            tablet_views=1 if view_data.device_type == "tablet" else 0,
            first_viewed_at=now,
            last_viewed_at=now,
            daily_views=[{"date": current_date, "count": 1}],
            hourly_distribution={current_hour: 1},
            language_views={},
            map_clicks=0,
            rsvp_clicks=0,
            music_plays=0,
            music_pauses=0
        )
        
        doc = analytics.model_dump()
        doc['created_at'] = doc['created_at'].isoformat()
        doc['first_viewed_at'] = doc['first_viewed_at'].isoformat()
        doc['last_viewed_at'] = doc['last_viewed_at'].isoformat()
        
        await db.analytics.insert_one(doc)
    
    # Return 204 No Content for fast response
    return None


@api_router.post("/invite/{slug}/track-language", status_code=204)
async def track_language_view(slug: str, language_data: LanguageTrackingRequest):
    """Track language selection (public endpoint, Phase 9)"""
    # Find profile by slug
    profile = await db.profiles.find_one({"slug": slug}, {"_id": 0})
    
    if not profile:
        raise HTTPException(status_code=404, detail="Invitation not found")
    
    profile_id = profile['id']
    
    # Update analytics with language view
    analytics_doc = await db.analytics.find_one({"profile_id": profile_id}, {"_id": 0})
    
    if analytics_doc:
        language_views = analytics_doc.get('language_views', {})
        language_views[language_data.language_code] = language_views.get(language_data.language_code, 0) + 1
        
        await db.analytics.update_one(
            {"profile_id": profile_id},
            {"$set": {"language_views": language_views}}
        )
    
    return None


@api_router.post("/invite/{slug}/track-interaction", status_code=204)
async def track_interaction(slug: str, interaction_data: InteractionTrackingRequest):
    """Track user interactions (public endpoint, Phase 9)"""
    # Find profile by slug
    profile = await db.profiles.find_one({"slug": slug}, {"_id": 0})
    
    if not profile:
        raise HTTPException(status_code=404, detail="Invitation not found")
    
    profile_id = profile['id']
    
    # Update analytics with interaction
    analytics_doc = await db.analytics.find_one({"profile_id": profile_id}, {"_id": 0})
    
    if analytics_doc:
        update_data = {}
        
        if interaction_data.interaction_type == "map_click":
            update_data["map_clicks"] = analytics_doc.get('map_clicks', 0) + 1
        elif interaction_data.interaction_type == "rsvp_click":
            update_data["rsvp_clicks"] = analytics_doc.get('rsvp_clicks', 0) + 1
        elif interaction_data.interaction_type == "music_play":
            update_data["music_plays"] = analytics_doc.get('music_plays', 0) + 1
        elif interaction_data.interaction_type == "music_pause":
            update_data["music_pauses"] = analytics_doc.get('music_pauses', 0) + 1
        
        if update_data:
            await db.analytics.update_one(
                {"profile_id": profile_id},
                {"$set": update_data}
            )
    
    return None


@api_router.get("/admin/profiles/{profile_id}/analytics", response_model=AnalyticsResponse)
async def get_profile_analytics(profile_id: str, admin_id: str = Depends(get_current_admin)):
    """Get detailed analytics for a specific profile (admin only, Phase 9)"""
    # Verify profile exists
    profile = await db.profiles.find_one({"id": profile_id}, {"_id": 0})
    
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    
    # Get analytics
    analytics_doc = await db.analytics.find_one({"profile_id": profile_id}, {"_id": 0})
    
    if not analytics_doc:
        # Return zero stats if no views yet
        return AnalyticsResponse(
            profile_id=profile_id,
            total_views=0,
            unique_views=0,
            mobile_views=0,
            desktop_views=0,
            tablet_views=0,
            first_viewed_at=None,
            last_viewed_at=None,
            daily_views=[],
            hourly_distribution={},
            language_views={},
            map_clicks=0,
            rsvp_clicks=0,
            music_plays=0,
            music_pauses=0
        )
    
    # Convert datetime strings if needed
    first_viewed = analytics_doc.get('first_viewed_at')
    if isinstance(first_viewed, str):
        first_viewed = datetime.fromisoformat(first_viewed)
    
    last_viewed = analytics_doc.get('last_viewed_at')
    if isinstance(last_viewed, str):
        last_viewed = datetime.fromisoformat(last_viewed)
    
    # Convert daily_views to DailyView objects
    daily_views_data = analytics_doc.get('daily_views', [])
    daily_views = [DailyView(**dv) if isinstance(dv, dict) else dv for dv in daily_views_data]
    
    return AnalyticsResponse(
        profile_id=analytics_doc['profile_id'],
        total_views=analytics_doc.get('total_views', 0),
        unique_views=analytics_doc.get('unique_views', 0),
        mobile_views=analytics_doc.get('mobile_views', 0),
        desktop_views=analytics_doc.get('desktop_views', 0),
        tablet_views=analytics_doc.get('tablet_views', 0),
        first_viewed_at=first_viewed,
        last_viewed_at=last_viewed,
        daily_views=daily_views,
        hourly_distribution=analytics_doc.get('hourly_distribution', {}),
        language_views=analytics_doc.get('language_views', {}),
        map_clicks=analytics_doc.get('map_clicks', 0),
        rsvp_clicks=analytics_doc.get('rsvp_clicks', 0),
        music_plays=analytics_doc.get('music_plays', 0),
        music_pauses=analytics_doc.get('music_pauses', 0)
    )


@api_router.get("/admin/profiles/{profile_id}/analytics/summary", response_model=AnalyticsSummary)
async def get_analytics_summary(profile_id: str, date_range: str = "7d", admin_id: str = Depends(get_current_admin)):
    """Get analytics summary with date range filter (admin only, Phase 9)
    
    Args:
        date_range: "7d" (last 7 days), "30d" (last 30 days), or "all" (all time)
    """
    # Verify profile exists
    profile = await db.profiles.find_one({"id": profile_id}, {"_id": 0})
    
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    
    # Get analytics
    analytics_doc = await db.analytics.find_one({"profile_id": profile_id}, {"_id": 0})
    
    if not analytics_doc:
        return AnalyticsSummary(
            total_views=0,
            unique_visitors=0,
            most_viewed_language=None,
            peak_hour=None,
            device_breakdown={"mobile": 0, "desktop": 0, "tablet": 0}
        )
    
    # Apply date range filter for daily views
    daily_views = analytics_doc.get('daily_views', [])
    if date_range != "all" and daily_views:
        cutoff_date = (datetime.now(timezone.utc) - timedelta(days=int(date_range[:-1]))).date().isoformat()
        daily_views = [dv for dv in daily_views if dv['date'] >= cutoff_date]
    
    # Calculate filtered total views
    if date_range == "all":
        filtered_total_views = analytics_doc.get('total_views', 0)
    else:
        filtered_total_views = sum(dv['count'] for dv in daily_views)
    
    # Find most viewed language
    language_views = analytics_doc.get('language_views', {})
    most_viewed_language = max(language_views.items(), key=lambda x: x[1])[0] if language_views else None
    
    # Find peak hour
    hourly_dist = analytics_doc.get('hourly_distribution', {})
    peak_hour = int(max(hourly_dist.items(), key=lambda x: x[1])[0]) if hourly_dist else None
    
    return AnalyticsSummary(
        total_views=filtered_total_views,
        unique_visitors=analytics_doc.get('unique_views', 0),
        most_viewed_language=most_viewed_language,
        peak_hour=peak_hour,
        device_breakdown={
            "mobile": analytics_doc.get('mobile_views', 0),
            "desktop": analytics_doc.get('desktop_views', 0),
            "tablet": analytics_doc.get('tablet_views', 0)
        }
    )


# ==================== PDF GENERATION ====================

# Design theme color mappings for PDF
THEME_COLORS = {
    'temple_divine': {'primary': (139, 115, 85), 'secondary': (212, 175, 55), 'text': (74, 55, 40), 'bg': (255, 248, 231)},
    'royal_classic': {'primary': (139, 0, 0), 'secondary': (255, 215, 0), 'text': (74, 26, 26), 'bg': (255, 245, 230)},
    'floral_soft': {'primary': (255, 182, 193), 'secondary': (255, 218, 185), 'text': (107, 78, 113), 'bg': (255, 240, 245)},
    'cinematic_luxury': {'primary': (26, 26, 26), 'secondary': (212, 175, 55), 'text': (245, 245, 245), 'bg': (44, 44, 44)},
    'heritage_scroll': {'primary': (139, 90, 43), 'secondary': (205, 133, 63), 'text': (74, 48, 23), 'bg': (250, 240, 230)},
    'minimal_elegant': {'primary': (128, 128, 128), 'secondary': (169, 169, 169), 'text': (64, 64, 64), 'bg': (255, 255, 255)},
    'modern_premium': {'primary': (47, 79, 79), 'secondary': (72, 209, 204), 'text': (245, 245, 245), 'bg': (32, 32, 32)},
    'artistic_handcrafted': {'primary': (160, 82, 45), 'secondary': (210, 180, 140), 'text': (101, 67, 33), 'bg': (255, 250, 240)}
}

# Language templates for PDF
LANGUAGE_TEMPLATES = {
    'english': {
        'opening_title': 'Wedding Invitation',
        'couple_label': 'Join us in celebrating the union of',
        'events_title': 'Event Schedule',
        'date_label': 'Date',
        'time_label': 'Time',
        'venue_label': 'Venue',
        'contact_title': 'Contact Information',
        'groom_label': 'Groom',
        'bride_label': 'Bride'
    },
    'telugu': {
        'opening_title': 'వివాహ ఆహ్వానం',
        'couple_label': 'మా వివాహ వేడుకలో పాల్గొనండి',
        'events_title': 'కార్యక్రమ షెడ్యూల్',
        'date_label': 'తేదీ',
        'time_label': 'సమయం',
        'venue_label': 'స్థలం',
        'contact_title': 'సంప్రదించండి',
        'groom_label': 'వరుడు',
        'bride_label': 'వధువు'
    },
    'hindi': {
        'opening_title': 'विवाह निमंत्रण',
        'couple_label': 'हमारे विवाह समारोह में शामिल हों',
        'events_title': 'कार्यक्रम कार्यक्रम',
        'date_label': 'तारीख',
        'time_label': 'समय',
        'venue_label': 'स्थान',
        'contact_title': 'संपर्क जानकारी',
        'groom_label': 'वर',
        'bride_label': 'वधू'
    },
    'tamil': {
        'opening_title': 'திருமண அழைப்பிதழ்',
        'couple_label': 'எங்கள் திருமண நிகழ்வில் சேரவும்',
        'events_title': 'நிகழ்வு அட்டவணை',
        'date_label': 'தேதி',
        'time_label': 'நேரம்',
        'venue_label': 'இடம்',
        'contact_title': 'தொடர்பு தகவல்',
        'groom_label': 'மணமகன்',
        'bride_label': 'மணமகள்'
    },
    'kannada': {
        'opening_title': 'ಮದುವೆ ಆಮಂತ್ರಣ',
        'couple_label': 'ನಮ್ಮ ಮದುವೆ ಸಮಾರಂಭದಲ್ಲಿ ಸೇರಿ',
        'events_title': 'ಕಾರ್ಯಕ್ರಮದ ವೇಳಾಪಟ್ಟಿ',
        'date_label': 'ದಿನಾಂಕ',
        'time_label': 'ಸಮಯ',
        'venue_label': 'ಸ್ಥಳ',
        'contact_title': 'ಸಂಪರ್ಕ ಮಾಹಿತಿ',
        'groom_label': 'ವರ',
        'bride_label': 'ವಧು'
    },
    'malayalam': {
        'opening_title': 'വിവാഹ ക്ഷണം',
        'couple_label': 'ഞങ്ങളുടെ വിവാഹ ചടങ്ങിൽ പങ്കെടുക്കൂ',
        'events_title': 'പരിപാടി ഷെഡ്യൂൾ',
        'date_label': 'തീയതി',
        'time_label': 'സമയം',
        'venue_label': 'സ്ഥലം',
        'contact_title': 'ബന്ധപ്പെടുക',
        'groom_label': 'വരൻ',
        'bride_label': 'വധു'
    }
}


def get_theme_colors(design_id: str):
    """Get theme colors for PDF generation"""
    return THEME_COLORS.get(design_id, THEME_COLORS['royal_classic'])


def get_language_text(language: str):
    """Get language-specific text for PDF"""
    return LANGUAGE_TEMPLATES.get(language, LANGUAGE_TEMPLATES['english'])


def rgb_to_reportlab_color(rgb_tuple):
    """Convert RGB tuple to ReportLab color"""
    r, g, b = rgb_tuple
    return rl_colors.Color(r/255.0, g/255.0, b/255.0)


async def generate_invitation_pdf(profile: dict, language: str = 'english'):
    """Generate PDF invitation from profile data"""
    buffer = io.BytesIO()
    
    # Get theme colors and language text
    theme = get_theme_colors(profile.get('design_id', 'royal_classic'))
    lang_text = get_language_text(language)
    
    # Convert colors
    primary_color = rgb_to_reportlab_color(theme['primary'])
    secondary_color = rgb_to_reportlab_color(theme['secondary'])
    text_color = rgb_to_reportlab_color(theme['text'])
    bg_color = rgb_to_reportlab_color(theme['bg'])
    
    # Get deity background path if present
    deity_id = profile.get('deity_id')
    deity_bg_path = None
    if deity_id and deity_id != 'none':
        # Map deity IDs to local file paths
        deity_file_map = {
            'ganesha': '/app/frontend/public/assets/deities/ganesha_desktop.jpg',
            'venkateswara_padmavati': '/app/frontend/public/assets/deities/venkateswara_padmavati_desktop.jpg',
            'shiva_parvati': '/app/frontend/public/assets/deities/shiva_parvati_desktop.jpg',
            'lakshmi_vishnu': '/app/frontend/public/assets/deities/lakshmi_vishnu_desktop.jpg'
        }
        deity_bg_path = deity_file_map.get(deity_id)
    
    # Create PDF document
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=0.75*inch,
        leftMargin=0.75*inch,
        topMargin=0.75*inch,
        bottomMargin=0.75*inch
    )
    
    # Container for PDF elements
    story = []
    
    # Define styles
    styles = getSampleStyleSheet()
    
    # Title style
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=28,
        textColor=primary_color,
        spaceAfter=20,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    )
    
    # Heading style
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=18,
        textColor=secondary_color,
        spaceAfter=12,
        spaceBefore=20,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    )
    
    # Subheading style
    subheading_style = ParagraphStyle(
        'CustomSubHeading',
        parent=styles['Heading3'],
        fontSize=14,
        textColor=primary_color,
        spaceAfter=8,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    )
    
    # Body style
    body_style = ParagraphStyle(
        'CustomBody',
        parent=styles['Normal'],
        fontSize=11,
        textColor=text_color,
        spaceAfter=6,
        alignment=TA_LEFT,
        fontName='Helvetica'
    )
    
    # Center body style
    center_body_style = ParagraphStyle(
        'CustomCenterBody',
        parent=body_style,
        alignment=TA_CENTER
    )
    
    # Add title
    story.append(Paragraph(lang_text['opening_title'], title_style))
    story.append(Spacer(1, 0.3*inch))
    
    # Add couple names
    story.append(Paragraph(lang_text['couple_label'], center_body_style))
    story.append(Spacer(1, 0.2*inch))
    
    couple_text = f"<b>{profile['groom_name']}</b> & <b>{profile['bride_name']}</b>"
    story.append(Paragraph(couple_text, heading_style))
    story.append(Spacer(1, 0.4*inch))
    
    # Add events section
    events = profile.get('events', [])
    visible_events = [e for e in events if e.get('visible', True)]
    
    if visible_events:
        story.append(Paragraph(lang_text['events_title'], heading_style))
        story.append(Spacer(1, 0.2*inch))
        
        # Sort events by date
        sorted_events = sorted(visible_events, key=lambda x: x.get('date', ''))
        
        for event in sorted_events:
            # Event name
            event_name_style = ParagraphStyle(
                'EventName',
                parent=subheading_style,
                fontSize=14,
                textColor=primary_color,
                alignment=TA_LEFT
            )
            story.append(Paragraph(f"<b>{event['name']}</b>", event_name_style))
            story.append(Spacer(1, 0.1*inch))
            
            # Event details
            date_str = event.get('date', '')
            time_str = event.get('start_time', '')
            if event.get('end_time'):
                time_str += f" - {event['end_time']}"
            
            story.append(Paragraph(f"<b>{lang_text['date_label']}:</b> {date_str}", body_style))
            story.append(Paragraph(f"<b>{lang_text['time_label']}:</b> {time_str}", body_style))
            story.append(Paragraph(f"<b>{lang_text['venue_label']}:</b> {event.get('venue_name', '')}", body_style))
            story.append(Paragraph(f"{event.get('venue_address', '')}", body_style))
            
            if event.get('description'):
                story.append(Spacer(1, 0.05*inch))
                story.append(Paragraph(event['description'], body_style))
            
            story.append(Spacer(1, 0.25*inch))
    
    # Add contact information
    if profile.get('whatsapp_groom') or profile.get('whatsapp_bride'):
        story.append(Spacer(1, 0.3*inch))
        story.append(Paragraph(lang_text['contact_title'], heading_style))
        story.append(Spacer(1, 0.15*inch))
        
        if profile.get('whatsapp_groom'):
            story.append(Paragraph(
                f"<b>{lang_text['groom_label']}:</b> {profile['whatsapp_groom']}", 
                body_style
            ))
        
        if profile.get('whatsapp_bride'):
            story.append(Paragraph(
                f"<b>{lang_text['bride_label']}:</b> {profile['whatsapp_bride']}", 
                body_style
            ))
    
    # Build PDF with deity background if present
    if deity_bg_path and os.path.exists(deity_bg_path):
        def add_deity_background(canvas_obj, doc_obj):
            """Add deity background with very light opacity"""
            canvas_obj.saveState()
            try:
                # Load and compress deity image
                img = PILImage.open(deity_bg_path)
                
                # Resize to optimize file size (max 800px width)
                max_width = 800
                if img.width > max_width:
                    ratio = max_width / img.width
                    new_height = int(img.height * ratio)
                    img = img.resize((max_width, new_height), PILImage.Resampling.LANCZOS)
                
                # Convert to RGB if needed
                if img.mode != 'RGB':
                    img = img.convert('RGB')
                
                # Save compressed image to buffer
                img_buffer = io.BytesIO()
                img.save(img_buffer, format='JPEG', quality=70, optimize=True)
                img_buffer.seek(0)
                
                # Create ReportLab Image
                img_reader = ImageReader(img_buffer)
                
                # Calculate centered position
                page_width, page_height = A4
                img_width, img_height = img.size
                
                # Scale to fit page while maintaining aspect ratio
                scale = min(page_width / img_width, page_height / img_height)
                scaled_width = img_width * scale
                scaled_height = img_height * scale
                
                # Center on page
                x = (page_width - scaled_width) / 2
                y = (page_height - scaled_height) / 2
                
                # Draw with very light opacity (0.12)
                canvas_obj.setFillAlpha(0.12)
                canvas_obj.drawImage(
                    img_reader, 
                    x, y, 
                    width=scaled_width, 
                    height=scaled_height,
                    preserveAspectRatio=True,
                    mask='auto'
                )
            except Exception as e:
                # If deity image fails, continue without it
                logging.warning(f"Failed to add deity background: {e}")
            finally:
                canvas_obj.restoreState()
        
        doc.build(story, onFirstPage=add_deity_background, onLaterPages=add_deity_background)
    else:
        doc.build(story)
    
    # Get PDF data
    buffer.seek(0)
    return buffer


@api_router.get("/admin/profiles/{profile_id}/download-pdf")
async def download_invitation_pdf(
    profile_id: str, 
    language: str = 'english',
    admin_id: str = Depends(get_current_admin)
):
    """Generate and download PDF invitation (admin only)"""
    # Fetch profile
    profile = await db.profiles.find_one({"id": profile_id}, {"_id": 0})
    
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    
    # Generate PDF
    pdf_buffer = await generate_invitation_pdf(profile, language)
    
    # Create filename
    groom_name = re.sub(r'[^a-zA-Z]', '', profile['groom_name'].split()[0].lower())
    bride_name = re.sub(r'[^a-zA-Z]', '', profile['bride_name'].split()[0].lower())
    filename = f"wedding-invitation-{groom_name}-{bride_name}.pdf"
    
    # Return PDF as download
    return StreamingResponse(
        pdf_buffer,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f"attachment; filename={filename}"
        }
    )


# ==================== CONFIGURATION ROUTES ====================

@api_router.get("/config/designs")
async def get_designs():
    """Get all available design themes"""
    designs = [
        {
            "id": "royal_classic",
            "name": "Royal Classic",
            "description": "Elegant maroon and gold with traditional motifs",
            "thumbnail": "/assets/designs/royal_classic_thumb.webp",
            "preview": "/assets/designs/royal_classic_preview.webp"
        },
        {
            "id": "floral_soft",
            "name": "Floral Soft",
            "description": "Pastel pink with delicate floral patterns",
            "thumbnail": "/assets/designs/floral_soft_thumb.webp",
            "preview": "/assets/designs/floral_soft_preview.webp"
        },
        {
            "id": "divine_temple",
            "name": "Divine Temple",
            "description": "Warm ivory and gold with sacred temple aesthetics",
            "thumbnail": "/assets/designs/divine_temple_thumb.webp",
            "preview": "/assets/designs/divine_temple_preview.webp"
        },
        {
            "id": "modern_minimal",
            "name": "Modern Minimal",
            "description": "Clean white and gray with contemporary design",
            "thumbnail": "/assets/designs/modern_minimal_thumb.webp",
            "preview": "/assets/designs/modern_minimal_preview.webp"
        },
        {
            "id": "cinematic_luxury",
            "name": "Cinematic Luxury",
            "description": "Dark gradient with gold accents and premium feel",
            "thumbnail": "/assets/designs/cinematic_luxury_thumb.webp",
            "preview": "/assets/designs/cinematic_luxury_preview.webp"
        }
    ]
    return designs


@api_router.get("/config/deities")
async def get_deities():
    """Get all available deity options"""
    deities = [
        {
            "id": "none",
            "name": "No Religious Theme",
            "description": "Secular invitation without deity imagery",
            "thumbnail": "/assets/deities/none.svg"
        },
        {
            "id": "ganesha",
            "name": "Lord Ganesha",
            "description": "Remover of obstacles, auspicious beginning",
            "thumbnail": "/assets/deities/ganesha_thumb.webp",
            "languages": ["english", "telugu", "hindi"]
        },
        {
            "id": "venkateswara_padmavati",
            "name": "Lord Venkateswara & Padmavati",
            "description": "Divine couple symbolizing eternal love",
            "thumbnail": "/assets/deities/venkateswara_padmavati_thumb.webp",
            "languages": ["english", "telugu", "hindi"]
        },
        {
            "id": "shiva_parvati",
            "name": "Lord Shiva & Parvati",
            "description": "Perfect union of masculine and feminine energy",
            "thumbnail": "/assets/deities/shiva_parvati_thumb.webp",
            "languages": ["english", "telugu", "hindi"]
        },
        {
            "id": "lakshmi_vishnu",
            "name": "Lakshmi & Vishnu",
            "description": "Wealth, prosperity, and harmony",
            "thumbnail": "/assets/deities/lakshmi_vishnu_thumb.webp",
            "languages": ["english", "telugu", "hindi"]
        }
    ]
    return deities


@api_router.get("/config/languages")
async def get_languages():
    """Get available language configuration"""
    languages = [
        {
            "code": "english",
            "name": "English",
            "nativeName": "English",
            "rtl": False
        },
        {
            "code": "telugu",
            "name": "Telugu",
            "nativeName": "తెలుగు",
            "rtl": False
        },
        {
            "code": "hindi",
            "name": "Hindi",
            "nativeName": "हिन्दी",
            "rtl": False
        }
    ]
    return languages



# ==================== PHASE 11: QR CODE & CALENDAR ROUTES ====================

@api_router.get("/invite/{slug}/qr")
async def generate_qr_code(slug: str):
    """PHASE 11: Generate QR code for invitation link"""
    profile = await db.profiles.find_one({"slug": slug}, {"_id": 0})
    
    if not profile:
        raise HTTPException(status_code=404, detail="Invitation not found")
    
    # Generate QR code using qrcode library
    import qrcode
    from io import BytesIO
    
    # Build invitation URL
    invitation_url = f"https://vows-organizer.preview.emergentagent.com/invite/{slug}"
    
    # Create QR code
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(invitation_url)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    
    # Convert to bytes
    img_bytes = BytesIO()
    img.save(img_bytes, format='PNG')
    img_bytes.seek(0)
    
    return StreamingResponse(img_bytes, media_type="image/png")


@api_router.get("/invite/{slug}/calendar")
async def download_calendar(slug: str):
    """PHASE 11: Generate .ics calendar file for wedding events"""
    profile = await db.profiles.find_one({"slug": slug}, {"_id": 0})
    
    if not profile:
        raise HTTPException(status_code=404, detail="Invitation not found")
    
    if not await check_profile_active(profile):
        raise HTTPException(status_code=410, detail="This invitation link has expired")
    
    # Convert date string if needed
    if isinstance(profile.get('event_date'), str):
        profile['event_date'] = datetime.fromisoformat(profile['event_date'])
    
    # Get events
    events = profile.get('events', [])
    
    # Build .ics file content
    ics_lines = [
        "BEGIN:VCALENDAR",
        "VERSION:2.0",
        "PRODID:-//Wedding Invitation//EN",
        "CALSCALE:GREGORIAN",
        "METHOD:PUBLISH"
    ]
    
    # If events exist, use those; otherwise use main event_date
    if events and len(events) > 0:
        for event in events:
            if not event.get('visible', True):
                continue
            
            # Parse event date and time
            event_date = datetime.strptime(event['date'], '%Y-%m-%d')
            start_time_parts = event['start_time'].split(':')
            event_datetime = event_date.replace(
                hour=int(start_time_parts[0]),
                minute=int(start_time_parts[1])
            )
            
            # End time (default to 2 hours later if not specified)
            if event.get('end_time'):
                end_time_parts = event['end_time'].split(':')
                end_datetime = event_date.replace(
                    hour=int(end_time_parts[0]),
                    minute=int(end_time_parts[1])
                )
            else:
                end_datetime = event_datetime + timedelta(hours=2)
            
            # Format dates for .ics
            dtstart = event_datetime.strftime('%Y%m%dT%H%M%S')
            dtend = end_datetime.strftime('%Y%m%dT%H%M%S')
            
            ics_lines.extend([
                "BEGIN:VEVENT",
                f"UID:{event.get('event_id', str(uuid.uuid4()))}@wedding-invitation",
                f"DTSTAMP:{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}",
                f"DTSTART:{dtstart}",
                f"DTEND:{dtend}",
                f"SUMMARY:{event['name']} - {profile['groom_name']} & {profile['bride_name']}",
                f"LOCATION:{event['venue_name']}, {event['venue_address']}",
                f"DESCRIPTION:{event.get('description', '')}",
                "STATUS:CONFIRMED",
                "END:VEVENT"
            ])
    else:
        # Use main event_date
        event_datetime = profile['event_date']
        end_datetime = event_datetime + timedelta(hours=4)
        
        dtstart = event_datetime.strftime('%Y%m%dT%H%M%S')
        dtend = end_datetime.strftime('%Y%m%dT%H%M%S')
        
        ics_lines.extend([
            "BEGIN:VEVENT",
            f"UID:{profile['id']}@wedding-invitation",
            f"DTSTAMP:{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}",
            f"DTSTART:{dtstart}",
            f"DTEND:{dtend}",
            f"SUMMARY:{profile['event_type'].title()} - {profile['groom_name']} & {profile['bride_name']}",
            f"LOCATION:{profile['venue']}, {profile.get('city', '')}",
            f"DESCRIPTION:Join us for our {profile['event_type']}",
            "STATUS:CONFIRMED",
            "END:VEVENT"
        ])
    
    ics_lines.append("END:VCALENDAR")
    ics_content = "\r\n".join(ics_lines)
    
    # Return as downloadable file
    from fastapi.responses import Response
    filename = f"wedding-{profile['groom_name']}-{profile['bride_name']}.ics".replace(" ", "-").lower()
    
    return Response(
        content=ics_content,
        media_type="text/calendar",
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"'
        }
    )


# ==========================================
# PHASE 12 - SCALABILITY & PRODUCTION ENDPOINTS
# ==========================================

# Helper function for audit logging
async def create_audit_log(admin_id: str, action: str, target_id: Optional[str] = None, details: Optional[dict] = None):
    """Create audit log entry"""
    audit_log = {
        "id": str(uuid.uuid4()),
        "admin_id": admin_id,
        "action": action,
        "target_id": target_id,
        "details": details,
        "timestamp": datetime.now(timezone.utc)
    }
    await db.audit_logs.insert_one(audit_log)


# Helper function for rate limiting
async def check_rate_limit(ip_address: str, action_type: str, max_count: int) -> bool:
    """Check if IP has exceeded rate limit for the day"""
    today = datetime.now(timezone.utc).strftime('%Y-%m-%d')
    
    tracker = await db.rate_limits.find_one({
        "ip_address": ip_address,
        "action_type": action_type,
        "date": today
    })
    
    if tracker and tracker['count'] >= max_count:
        return False  # Rate limit exceeded
    
    # Update or create tracker
    if tracker:
        await db.rate_limits.update_one(
            {"_id": tracker['_id']},
            {
                "$inc": {"count": 1},
                "$set": {"last_action_at": datetime.now(timezone.utc)}
            }
        )
    else:
        await db.rate_limits.insert_one({
            "id": str(uuid.uuid4()),
            "ip_address": ip_address,
            "action_type": action_type,
            "count": 1,
            "date": today,
            "last_action_at": datetime.now(timezone.utc)
        })
    
    return True  # Within rate limit


@api_router.post("/admin/profiles/{profile_id}/save-as-template", response_model=InvitationTemplateResponse)
async def save_profile_as_template(
    profile_id: str,
    template_data: InvitationTemplateCreate,
    admin: dict = Depends(get_current_admin)
):
    """
    Save an existing profile as a reusable template.
    Strips all personal data (names, dates, photos, RSVPs, wishes, analytics).
    """
    # Get the profile
    profile = await db.profiles.find_one({"id": profile_id})
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    
    # Extract only configuration (NO personal data)
    events_structure = []
    if profile.get('events'):
        for event in profile['events']:
            events_structure.append({
                "name": event['name'],  # Keep event type (Mehendi, Sangeet, etc.)
                "venue_name": "",  # Empty - admin fills
                "venue_address": "",  # Empty - admin fills
                "map_link": "",  # Empty - admin fills
                "description": event.get('description', ''),
                "visible": event['visible'],
                "order": event['order']
            })
    
    # Create template
    template = {
        "id": str(uuid.uuid4()),
        "template_name": template_data.template_name,
        "description": template_data.description,
        "design_id": profile['design_id'],
        "deity_id": profile.get('deity_id'),
        "enabled_languages": profile['enabled_languages'],
        "sections_enabled": profile['sections_enabled'],
        "background_music": {
            "enabled": profile.get('background_music', {}).get('enabled', False),
            "file_url": None  # Don't save personal music file
        },
        "map_settings": profile.get('map_settings', {"embed_enabled": False}),
        "contact_info": {
            "groom_phone": None,  # Empty - admin fills
            "bride_phone": None,
            "emergency_phone": None,
            "email": None
        },
        "events_structure": events_structure,
        "created_by": admin['id'],
        "created_at": datetime.now(timezone.utc),
        "usage_count": 0
    }
    
    await db.templates.insert_one(template)
    
    # Create audit log
    await create_audit_log(
        admin_id=admin['id'],
        action="template_saved",
        target_id=template['id'],
        details={"profile_id": profile_id, "template_name": template_data.template_name}
    )
    
    return InvitationTemplateResponse(**template)


@api_router.get("/admin/templates", response_model=List[InvitationTemplateResponse])
async def list_templates(admin: dict = Depends(get_current_admin)):
    """List all saved templates"""
    templates = await db.templates.find().sort("created_at", -1).to_list(100)
    return [InvitationTemplateResponse(**t) for t in templates]


@api_router.post("/admin/profiles/create-from-template/{template_id}")
async def get_template_for_profile_creation(
    template_id: str,
    admin: dict = Depends(get_current_admin)
):
    """
    Get template data for creating a new profile.
    Returns template configuration that can be used to prefill the profile form.
    """
    template = await db.templates.find_one({"id": template_id})
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    
    # Increment usage count
    await db.templates.update_one(
        {"id": template_id},
        {"$inc": {"usage_count": 1}}
    )
    
    # Return template data for frontend to use
    return {
        "design_id": template['design_id'],
        "deity_id": template.get('deity_id'),
        "enabled_languages": template['enabled_languages'],
        "sections_enabled": template['sections_enabled'],
        "background_music": template['background_music'],
        "map_settings": template['map_settings'],
        "events_structure": template['events_structure']
    }


@api_router.delete("/admin/templates/{template_id}")
async def delete_template(
    template_id: str,
    admin: dict = Depends(get_current_admin)
):
    """Delete a template"""
    template = await db.templates.find_one({"id": template_id})
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    
    await db.templates.delete_one({"id": template_id})
    
    # Create audit log
    await create_audit_log(
        admin_id=admin['id'],
        action="template_deleted",
        target_id=template_id,
        details={"template_name": template.get('template_name')}
    )
    
    return {"message": "Template deleted successfully"}


@api_router.post("/admin/profiles/{profile_id}/duplicate", response_model=ProfileResponse)
async def duplicate_profile(
    profile_id: str,
    admin: dict = Depends(get_current_admin)
):
    """
    Duplicate an existing profile.
    Copies: design, sections, languages, event structure.
    Resets: RSVP, wishes, analytics, generates new slug.
    """
    # Get the original profile
    original = await db.profiles.find_one({"id": profile_id})
    if not original:
        raise HTTPException(status_code=404, detail="Profile not found")
    
    # Generate new slug
    new_slug = generate_slug(original['groom_name'], original['bride_name'])
    
    # Calculate default expiry (wedding date + 7 days)
    default_expiry = original['event_date'] + timedelta(days=7)
    
    # Create duplicated profile
    new_profile = {
        "id": str(uuid.uuid4()),
        "slug": new_slug,
        "groom_name": original['groom_name'],
        "bride_name": original['bride_name'],
        "event_type": original['event_type'],
        "event_date": original['event_date'],
        "venue": original['venue'],
        "city": original.get('city'),
        "invitation_message": original.get('invitation_message'),
        "language": original['language'],
        "design_id": original['design_id'],
        "deity_id": original.get('deity_id'),
        "whatsapp_groom": original.get('whatsapp_groom'),
        "whatsapp_bride": original.get('whatsapp_bride'),
        "enabled_languages": original['enabled_languages'],
        "custom_text": original.get('custom_text', {}),
        "about_couple": original.get('about_couple'),
        "family_details": original.get('family_details'),
        "love_story": original.get('love_story'),
        "cover_photo_id": None,  # Reset cover photo
        "sections_enabled": original['sections_enabled'],
        "background_music": original.get('background_music', {"enabled": False, "file_url": None}),
        "map_settings": original.get('map_settings', {"embed_enabled": False}),
        "contact_info": original.get('contact_info', {}),
        "events": original.get('events', []),
        "link_expiry_type": original.get('link_expiry_type', 'days'),
        "link_expiry_value": original.get('link_expiry_value', 30),
        "link_expiry_date": calculate_expiry_date(
            original.get('link_expiry_type', 'days'),
            original.get('link_expiry_value', 30)
        ),
        "is_active": True,
        "is_template": False,
        "template_name": None,
        "cloned_from": profile_id,  # Track original profile
        "expires_at": default_expiry,  # Auto-set expiry
        "created_at": datetime.now(timezone.utc),
        "updated_at": datetime.now(timezone.utc)
    }
    
    await db.profiles.insert_one(new_profile)
    
    # Create audit log
    await create_audit_log(
        admin_id=admin['id'],
        action="profile_duplicated",
        target_id=new_profile['id'],
        details={"original_profile_id": profile_id, "new_slug": new_slug}
    )
    
    # Return response
    new_profile['invitation_link'] = f"/invite/{new_slug}"
    return ProfileResponse(**new_profile)


@api_router.put("/admin/profiles/{profile_id}/set-expiry")
async def set_profile_expiry(
    profile_id: str,
    expiry_data: SetExpiryRequest,
    admin: dict = Depends(get_current_admin)
):
    """Set custom expiry date for a profile"""
    profile = await db.profiles.find_one({"id": profile_id})
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    
    # Update expiry date
    await db.profiles.update_one(
        {"id": profile_id},
        {
            "$set": {
                "expires_at": expiry_data.expires_at,
                "updated_at": datetime.now(timezone.utc)
            }
        }
    )
    
    # Create audit log
    await create_audit_log(
        admin_id=admin['id'],
        action="expiry_set",
        target_id=profile_id,
        details={"expires_at": expiry_data.expires_at.isoformat()}
    )
    
    return {"message": "Expiry date set successfully", "expires_at": expiry_data.expires_at}


@api_router.get("/admin/audit-logs", response_model=List[AuditLogResponse])
async def get_audit_logs(
    limit: int = 1000,
    admin: dict = Depends(get_current_admin)
):
    """Get audit logs (last 1000 entries)"""
    logs = await db.audit_logs.find().sort("timestamp", -1).limit(limit).to_list(limit)
    return [AuditLogResponse(**log) for log in logs]


# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()