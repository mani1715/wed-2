from fastapi import FastAPI, APIRouter, HTTPException, Depends, status
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

from models import (
    Admin, AdminLogin, AdminResponse,
    Profile, ProfileCreate, ProfileUpdate, ProfileResponse,
    ProfileMedia, ProfileMediaCreate,
    Greeting, GreetingCreate, GreetingResponse,
    InvitationPublicView, SectionsEnabled, BackgroundMusic,
    RSVP, RSVPCreate, RSVPResponse, RSVPStats
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
async def create_profile(profile_data: ProfileCreate, admin_id: str = Depends(get_current_admin)):
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
    
    # Create profile object
    profile = Profile(
        slug=slug,
        groom_name=profile_data.groom_name,
        bride_name=profile_data.bride_name,
        event_type=profile_data.event_type,
        event_date=profile_data.event_date,
        venue=profile_data.venue,
        language=profile_data.language,
        design_id=profile_data.design_id,
        deity_id=profile_data.deity_id,
        whatsapp_groom=profile_data.whatsapp_groom,
        whatsapp_bride=profile_data.whatsapp_bride,
        enabled_languages=profile_data.enabled_languages,
        custom_text=profile_data.custom_text,
        sections_enabled=profile_data.sections_enabled,
        background_music=profile_data.background_music,
        events=profile_data.events,
        link_expiry_type=profile_data.link_expiry_type,
        link_expiry_value=profile_data.link_expiry_value,
        link_expiry_date=expiry_date
    )
    
    # Convert to dict and serialize dates
    doc = profile.model_dump()
    doc['event_date'] = doc['event_date'].isoformat()
    doc['created_at'] = doc['created_at'].isoformat()
    doc['updated_at'] = doc['updated_at'].isoformat()
    if doc['link_expiry_date']:
        doc['link_expiry_date'] = doc['link_expiry_date'].isoformat()
    
    await db.profiles.insert_one(doc)
    
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
    admin_id: str = Depends(get_current_admin)
):
    """Update profile"""
    existing_profile = await db.profiles.find_one({"id": profile_id}, {"_id": 0})
    
    if not existing_profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    
    # Prepare update
    update_dict = update_data.model_dump(exclude_unset=True)
    
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
    update_dict['updated_at'] = update_dict['updated_at'].isoformat()
    if 'link_expiry_date' in update_dict and update_dict['link_expiry_date']:
        update_dict['link_expiry_date'] = update_dict['link_expiry_date'].isoformat()
    
    await db.profiles.update_one(
        {"id": profile_id},
        {"$set": update_dict}
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
    
    # Get greetings
    greetings_list = await db.greetings.find(
        {"profile_id": profile['id']},
        {"_id": 0}
    ).sort("created_at", -1).to_list(100)
    
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
        language=profile['language'],
        design_id=profile['design_id'],
        deity_id=profile.get('deity_id'),
        whatsapp_groom=profile.get('whatsapp_groom'),
        whatsapp_bride=profile.get('whatsapp_bride'),
        enabled_languages=profile.get('enabled_languages', ['english']),
        custom_text=profile.get('custom_text', {}),
        sections_enabled=SectionsEnabled(**profile['sections_enabled']),
        background_music=BackgroundMusic(**profile.get('background_music', {'enabled': False, 'file_url': None})),
        media=[ProfileMedia(**m) for m in media_list],
        greetings=[GreetingResponse(**g) for g in greetings_list]
    )


@api_router.post("/invite/{slug}/greetings", response_model=GreetingResponse)
async def submit_greeting(slug: str, greeting_data: GreetingCreate):
    """Submit greeting for invitation"""
    profile = await db.profiles.find_one({"slug": slug}, {"_id": 0})
    
    if not profile:
        raise HTTPException(status_code=404, detail="Invitation not found")
    
    if not await check_profile_active(profile):
        raise HTTPException(status_code=410, detail="This invitation link has expired")
    
    greeting = Greeting(
        profile_id=profile['id'],
        guest_name=greeting_data.guest_name,
        message=greeting_data.message
    )
    
    doc = greeting.model_dump()
    doc['created_at'] = doc['created_at'].isoformat()
    
    await db.greetings.insert_one(doc)
    
    return GreetingResponse(
        id=greeting.id,
        guest_name=greeting.guest_name,
        message=greeting.message,
        created_at=greeting.created_at
    )


@api_router.get("/admin/profiles/{profile_id}/greetings", response_model=List[GreetingResponse])
async def get_profile_greetings(profile_id: str, admin_id: str = Depends(get_current_admin)):
    """Get all greetings for a profile"""
    greetings = await db.greetings.find(
        {"profile_id": profile_id},
        {"_id": 0}
    ).sort("created_at", -1).to_list(1000)
    
    for greeting in greetings:
        if isinstance(greeting.get('created_at'), str):
            greeting['created_at'] = datetime.fromisoformat(greeting['created_at'])
    
    return [GreetingResponse(**g) for g in greetings]


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
    })
    
    if existing_rsvp:
        raise HTTPException(
            status_code=400,
            detail="You have already submitted an RSVP for this invitation"
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