import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import axios from 'axios';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Heart, Calendar, MapPin, Send, Languages, MessageCircle } from 'lucide-react';
import { getTheme, applyThemeVariables } from '@/config/themes';
import { getDeity, getDeityImage } from '@/config/religiousAssets';
import { LANGUAGES, loadLanguage, getText, getSectionText, preloadLanguages } from '@/utils/languageLoader';

const API_URL = process.env.REACT_APP_BACKEND_URL || '';

// Deity Background Component - Progressive Loading Layer
const DeityBackground = ({ deityId }) => {
  const [imageLoaded, setImageLoaded] = useState(false);
  const [currentImage, setCurrentImage] = useState(null);
  
  useEffect(() => {
    if (!deityId) return;
    
    const deity = getDeity(deityId);
    if (!deity || !deity.images) return;
    
    // Start with thumbnail
    const thumbnail = new Image();
    thumbnail.src = deity.images.thumbnail;
    thumbnail.onload = () => {
      setCurrentImage(deity.images.thumbnail);
      
      // Load mobile or desktop based on screen size
      const isMobile = window.innerWidth < 768;
      const nextImage = new Image();
      nextImage.src = isMobile ? deity.images.mobile : deity.images.desktop;
      nextImage.onload = () => {
        setCurrentImage(isMobile ? deity.images.mobile : deity.images.desktop);
        setImageLoaded(true);
      };
    };
  }, [deityId]);
  
  if (!deityId || !currentImage) {
    return null;
  }
  
  return (
    <div
      style={{
        position: 'fixed',
        top: 0,
        left: 0,
        right: 0,
        bottom: 0,
        zIndex: 0,
        pointerEvents: 'none',
        opacity: 0.2,
        overflow: 'hidden'
      }}
    >
      <img
        src={currentImage}
        alt="Religious background"
        loading="lazy"
        style={{
          width: '100%',
          height: '100%',
          objectFit: 'cover',
          objectPosition: 'center',
          filter: imageLoaded ? 'none' : 'blur(10px)',
          transition: 'filter 0.3s ease-in-out'
        }}
      />
    </div>
  );
};

const PublicInvitation = () => {
  const { slug } = useParams();
  const [invitation, setInvitation] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [selectedLanguage, setSelectedLanguage] = useState('english');
  const [languageData, setLanguageData] = useState(null);
  const [guestName, setGuestName] = useState('');
  const [message, setMessage] = useState('');
  const [submitting, setSubmitting] = useState(false);
  const [submitSuccess, setSubmitSuccess] = useState(false);
  
  // Music player state
  const [musicPlaying, setMusicPlaying] = useState(false);
  const [audioRef] = useState(new Audio());
  
  // RSVP state
  const [showRSVP, setShowRSVP] = useState(false);
  const [rsvpData, setRsvpData] = useState({
    guest_name: '',
    guest_phone: '',
    status: 'yes',
    guest_count: 1,
    message: ''
  });
  const [rsvpSubmitting, setRsvpSubmitting] = useState(false);
  const [rsvpSuccess, setRsvpSuccess] = useState(false);
  const [rsvpError, setRsvpError] = useState('');
  const [submittedRsvpStatus, setSubmittedRsvpStatus] = useState('');

  useEffect(() => {
    fetchInvitation();
  }, [slug]);

  // Apply theme and set default language when invitation loads
  useEffect(() => {
    if (invitation && invitation.design_id) {
      const theme = getTheme(invitation.design_id);
      applyThemeVariables(theme);
      
      // Load Google Fonts dynamically
      const link = document.createElement('link');
      link.href = 'https://fonts.googleapis.com/css2?family=Cinzel:wght@400;600;700&family=Lora:wght@400;600;700&family=Playfair+Display:wght@400;600;700&family=Libre+Baskerville:wght@400;700&family=Quicksand:wght@400;600;700&family=Nunito:wght@400;600;700&family=Cormorant+Garamond:wght@400;600;700&family=Montserrat:wght@400;600;700&family=UnifrakturMaguntia&family=Merriweather:wght@400;700&family=Raleway:wght@400;600;700&family=Inter:wght@400;600;700&family=Poppins:wght@400;600;700&family=Open+Sans:wght@400;600;700&family=Indie+Flower&family=Architects+Daughter&display=swap';
      link.rel = 'stylesheet';
      document.head.appendChild(link);
      
      // Set default language (first enabled language) and preload languages
      if (invitation.enabled_languages && invitation.enabled_languages.length > 0) {
        const defaultLang = invitation.enabled_languages[0];
        setSelectedLanguage(defaultLang);
        
        // Preload all enabled languages for faster switching
        preloadLanguages(invitation.enabled_languages).catch(err => {
          console.warn('Failed to preload languages:', err);
        });
        
        // Load default language immediately
        loadLanguage(defaultLang).then(setLanguageData).catch(err => {
          console.error('Failed to load language:', err);
        });
      }
    }
  }, [invitation]);
  
  // Load language data when selected language changes
  useEffect(() => {
    loadLanguage(selectedLanguage).then(setLanguageData).catch(err => {
      console.error('Failed to load language:', err);
    });
    
    // Store language preference in localStorage
    localStorage.setItem('preferredLanguage', selectedLanguage);
  }, [selectedLanguage]);

  const fetchInvitation = async () => {
    try {
      const response = await axios.get(`${API_URL}/api/invite/${slug}`);
      setInvitation(response.data);
      
      // PHASE 7: Track view after content is fetched (privacy-first)
      trackInvitationView();
    } catch (error) {
      console.error('Failed to fetch invitation:', error);
      if (error.response?.status === 410) {
        setError('This invitation link has expired.');
      } else if (error.response?.status === 404) {
        setError('Invitation not found.');
      } else {
        setError('Failed to load invitation.');
      }
    } finally {
      setLoading(false);
    }
  };

  // PHASE 9: Generate or retrieve session ID
  const getSessionId = () => {
    const SESSION_KEY = `session_id_${slug}`;
    const EXPIRY_KEY = `session_expiry_${slug}`;
    
    const now = new Date().getTime();
    const existingSessionId = localStorage.getItem(SESSION_KEY);
    const expiry = localStorage.getItem(EXPIRY_KEY);
    
    // Check if session is still valid (24 hours)
    if (existingSessionId && expiry && now < parseInt(expiry)) {
      return existingSessionId;
    }
    
    // Generate new session ID
    const newSessionId = `${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    const newExpiry = now + (24 * 60 * 60 * 1000); // 24 hours
    
    localStorage.setItem(SESSION_KEY, newSessionId);
    localStorage.setItem(EXPIRY_KEY, newExpiry.toString());
    
    return newSessionId;
  };

  // PHASE 9: Track invitation view (session-based unique tracking)
  const trackInvitationView = () => {
    try {
      // Get or generate session ID
      const sessionId = getSessionId();
      
      // Detect device type (mobile, desktop, or tablet)
      const width = window.innerWidth;
      let deviceType;
      if (width < 768) {
        deviceType = 'mobile';
      } else if (width >= 768 && width < 1024) {
        deviceType = 'tablet';
      } else {
        deviceType = 'desktop';
      }
      
      // Send view tracking request (non-blocking)
      axios.post(`${API_URL}/api/invite/${slug}/view`, {
        session_id: sessionId,
        device_type: deviceType
      }).catch(err => {
        // Silent fail - don't disrupt user experience
        console.debug('View tracking failed:', err);
      });
    } catch (error) {
      // Silent fail - don't disrupt user experience
      console.debug('View tracking error:', error);
    }
  };

  // PHASE 9: Track language selection
  const trackLanguageView = (languageCode) => {
    try {
      const sessionId = getSessionId();
      
      axios.post(`${API_URL}/api/invite/${slug}/track-language`, {
        session_id: sessionId,
        language_code: languageCode
      }).catch(err => {
        console.debug('Language tracking failed:', err);
      });
    } catch (error) {
      console.debug('Language tracking error:', error);
    }
  };

  // PHASE 9: Track interactions (map clicks, RSVP clicks, music)
  const trackInteraction = (interactionType) => {
    try {
      const sessionId = getSessionId();
      
      axios.post(`${API_URL}/api/invite/${slug}/track-interaction`, {
        session_id: sessionId,
        interaction_type: interactionType
      }).catch(err => {
        console.debug('Interaction tracking failed:', err);
      });
    } catch (error) {
      console.debug('Interaction tracking error:', error);
    }
  };

  const handleSubmitGreeting = async (e) => {
    e.preventDefault();
    setSubmitting(true);
    setSubmitSuccess(false);

    try {
      await axios.post(`${API_URL}/api/invite/${slug}/greetings`, {
        guest_name: guestName,
        message: message
      });

      setSubmitSuccess(true);
      setGuestName('');
      setMessage('');
      
      // Refresh invitation to show new greeting
      fetchInvitation();
    } catch (error) {
      console.error('Failed to submit greeting:', error);
      alert('Failed to submit greeting. Please try again.');
    } finally {
      setSubmitting(false);
    }
  };

  // Music player logic
  useEffect(() => {
    if (!invitation || !invitation.background_music || !invitation.background_music.enabled) {
      return;
    }

    // Configure audio
    audioRef.src = invitation.background_music.file_url;
    audioRef.loop = true;
    audioRef.volume = 0.5;
    audioRef.preload = 'none';

    // Pause on page blur/tab change
    const handleVisibilityChange = () => {
      if (document.hidden && musicPlaying) {
        audioRef.pause();
      }
    };

    document.addEventListener('visibilitychange', handleVisibilityChange);

    return () => {
      audioRef.pause();
      document.removeEventListener('visibilitychange', handleVisibilityChange);
    };
  }, [invitation]);

  const toggleMusic = () => {
    if (musicPlaying) {
      audioRef.pause();
      setMusicPlaying(false);
      // PHASE 9: Track music pause
      trackInteraction('music_pause');
    } else {
      audioRef.play().catch(err => {
        console.error('Failed to play audio:', err);
      });
      setMusicPlaying(true);
      // PHASE 9: Track music play
      trackInteraction('music_play');
    }
  };

  // RSVP submission
  const handleSubmitRSVP = async (e) => {
    e.preventDefault();
    
    // Check if online
    if (!navigator.onLine) {
      setRsvpError('Internet connection required to submit RSVP');
      return;
    }

    setRsvpSubmitting(true);
    setRsvpError('');

    try {
      await axios.post(`${API_URL}/api/rsvp?slug=${slug}`, rsvpData);
      setRsvpSuccess(true);
      setSubmittedRsvpStatus(rsvpData.status); // Save the status before clearing
      setRsvpData({
        guest_name: '',
        guest_phone: '',
        status: 'yes',
        guest_count: 1,
        message: ''
      });
      setShowRSVP(false);
    } catch (error) {
      console.error('Failed to submit RSVP:', error);
      if (error.response?.status === 400) {
        setRsvpError('You have already submitted an RSVP for this invitation');
      } else if (error.response?.status === 410) {
        setRsvpError('This invitation link has expired');
      } else {
        setRsvpError('Failed to submit RSVP. Please try again.');
      }
    } finally {
      setRsvpSubmitting(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center" style={{ background: 'var(--color-background, #FFF8E7)' }}>
        <p style={{ color: 'var(--color-text, #4A3728)' }}>Loading invitation...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen flex items-center justify-center p-4" style={{ background: 'var(--color-background, #FFF8E7)' }}>
        <Card className="p-8 max-w-md text-center" style={{ background: 'var(--color-card, #FFFDF7)' }}>
          <p className="text-red-600 text-lg mb-4">{error}</p>
          <p style={{ color: 'var(--color-text, #4A3728)' }}>Please contact the event organizer for assistance.</p>
        </Card>
      </div>
    );
  }

  const eventDate = new Date(invitation.event_date);
  
  // Get available languages for this invitation
  const availableLanguages = invitation.enabled_languages || ['english'];
  
  // Get text helper functions with custom text and fallback
  const customText = invitation.custom_text || {};
  
  const getT = (section, key) => {
    // Check custom text first
    if (customText[selectedLanguage]?.[`${section}.${key}`]) {
      return customText[selectedLanguage][`${section}.${key}`];
    }
    
    // Get from loaded language data
    if (languageData?.[section]?.[key]) {
      return languageData[section][key];
    }
    
    // Fallback to key
    return key;
  };
  
  const getSectionT = (section) => {
    const sectionData = languageData?.[section] || {};
    
    // Merge with custom text
    const result = { ...sectionData };
    
    if (customText[selectedLanguage]) {
      Object.keys(customText[selectedLanguage]).forEach(customKey => {
        if (customKey.startsWith(`${section}.`)) {
          const key = customKey.replace(`${section}.`, '');
          result[key] = customText[selectedLanguage][customKey];
        }
      });
    }
    
    return result;
  };

  // Generate WhatsApp URL with pre-filled message
  const generateWhatsAppURL = (phoneNumber) => {
    if (!phoneNumber) return null;
    
    // Get default message in selected language
    const defaultMessage = getT('whatsapp', 'defaultMessage');
    
    // Encode message for URL
    const encodedMessage = encodeURIComponent(defaultMessage);
    
    // Generate wa.me URL
    return `https://wa.me/${phoneNumber.replace(/[^0-9]/g, '')}?text=${encodedMessage}`;
  };
  
  // Show loading if language data not loaded yet
  if (!languageData && !error) {
    return (
      <div className="min-h-screen flex items-center justify-center" style={{ background: 'var(--color-background, #FFF8E7)' }}>
        <p style={{ color: 'var(--color-text, #4A3728)' }}>Loading...</p>
      </div>
    );
  }

  return (
    <>
      {/* Deity Background Layer - Optional, behind all content */}
      <DeityBackground deityId={invitation.deity_id} />
      
      {/* Main Content - Positioned above deity background */}
      <div 
        className="min-h-screen" 
        style={{ 
          position: 'relative',
          zIndex: 1,
          background: 'var(--color-background, #FFF8E7)',
          fontFamily: 'var(--font-body, "Lora", serif)',
          color: 'var(--color-text, #4A3728)',
          paddingTop: 'var(--spacing-section, 3rem)',
          paddingBottom: 'var(--spacing-section, 3rem)'
        }}
      >
        <div className="container mx-auto px-4 max-w-4xl">
        
        {/* Cover Photo Hero Section */}
        {invitation.cover_photo_id && (() => {
          const coverPhoto = invitation.media.find(m => m.id === invitation.cover_photo_id);
          return coverPhoto ? (
            <div 
              className="relative w-full mb-8 rounded-lg overflow-hidden shadow-2xl"
              style={{
                height: '60vh',
                minHeight: '400px',
                maxHeight: '600px'
              }}
            >
              <img
                src={`${API_URL}${coverPhoto.media_url}`}
                alt="Cover"
                className="w-full h-full object-cover"
              />
              {/* Overlay with couple names */}
              <div 
                className="absolute inset-0 flex flex-col items-center justify-center"
                style={{
                  background: 'linear-gradient(to bottom, rgba(0,0,0,0.3), rgba(0,0,0,0.5))'
                }}
              >
                <h1 
                  className="text-4xl md:text-6xl font-bold mb-4 text-white text-center px-4"
                  style={{ 
                    fontFamily: 'var(--font-heading, "Cinzel", serif)',
                    textShadow: '2px 2px 8px rgba(0,0,0,0.5)'
                  }}
                >
                  {invitation.groom_name} & {invitation.bride_name}
                </h1>
                {invitation.invitation_message && (
                  <p 
                    className="text-lg md:text-xl text-white text-center px-6 max-w-2xl"
                    style={{ 
                      textShadow: '1px 1px 4px rgba(0,0,0,0.5)',
                      fontFamily: 'var(--font-body, "Lora", serif)'
                    }}
                  >
                    {invitation.invitation_message}
                  </p>
                )}
              </div>
            </div>
          ) : null;
        })()}

        {/* Music Player Icon - Fixed Position */}
        {invitation.background_music && invitation.background_music.enabled && invitation.background_music.file_url && (
          <button
            onClick={toggleMusic}
            className="fixed top-4 left-4 z-50 w-12 h-12 rounded-full shadow-lg flex items-center justify-center transition-all hover:scale-110"
            style={{
              background: 'var(--color-primary, #8B7355)',
              color: 'white'
            }}
            aria-label={musicPlaying ? 'Pause music' : 'Play music'}
          >
            {musicPlaying ? (
              <svg xmlns="http://www.w3.org/2000/svg" className="w-6 h-6" fill="currentColor" viewBox="0 0 24 24">
                <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-1 14H9V8h2v8zm4 0h-2V8h2v8z"/>
              </svg>
            ) : (
              <svg xmlns="http://www.w3.org/2000/svg" className="w-6 h-6" fill="currentColor" viewBox="0 0 24 24">
                <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 14.5v-9l6 4.5-6 4.5z"/>
              </svg>
            )}
          </button>
        )}
        
        {/* Language Switcher - Only show if multiple languages available */}
        {availableLanguages.length > 1 && (
          <div className="flex justify-end mb-6">
            <div className="flex gap-2 bg-white/80 backdrop-blur-sm rounded-lg p-2 shadow-sm">
              {availableLanguages.map((langCode) => {
                const lang = LANGUAGES.find(l => l.code === langCode);
                if (!lang) return null;
                
                return (
                  <button
                    key={langCode}
                    onClick={() => {
                      setSelectedLanguage(langCode);
                      // PHASE 9: Track language change
                      trackLanguageView(langCode);
                    }}
                    className="px-4 py-2 rounded-md text-sm font-medium transition-all"
                    style={{
                      background: selectedLanguage === langCode 
                        ? 'var(--color-primary, #8B7355)' 
                        : 'transparent',
                      color: selectedLanguage === langCode 
                        ? 'white' 
                        : 'var(--color-text, #4A3728)',
                      border: selectedLanguage === langCode 
                        ? 'none' 
                        : '1px solid var(--color-accent, #C9A961)'
                    }}
                  >
                    {lang.nativeName}
                  </button>
                );
              })}
            </div>
          </div>
        )}
        
        {/* Opening Section */}
        {invitation.sections_enabled.opening && (
          <div className="text-center" style={{ marginBottom: 'var(--spacing-section, 3rem)' }}>
            <Heart 
              className="w-16 h-16 mx-auto mb-6" 
              style={{ color: 'var(--color-secondary, #D4AF37)' }} 
            />
            <h1 
              className="text-4xl md:text-5xl font-bold mb-4"
              style={{ 
                fontFamily: 'var(--font-heading, "Cinzel", serif)',
                color: 'var(--color-primary, #8B7355)'
              }}
            >
              {getT('opening', 'title')}
            </h1>
            <p 
              className="text-lg"
              style={{ color: 'var(--color-text, #4A3728)' }}
            >
              {getT('opening', 'subtitle')}
            </p>
          </div>
        )}

        {/* Welcome Section */}
        {invitation.sections_enabled.welcome && (
          <Card 
            className="p-8 mb-8 text-center"
            style={{
              background: 'var(--color-card, #FFFDF7)',
              boxShadow: 'var(--card-shadow, 0 4px 12px rgba(139, 115, 85, 0.15))',
              border: 'var(--card-border, 1px solid #E8D9C5)',
              borderRadius: 'var(--card-radius, 12px)',
              marginBottom: 'var(--spacing-card, 1.5rem)'
            }}
          >
            <p className="text-xl" style={{ color: 'var(--color-text, #4A3728)' }}>
              {getT('welcome', 'message')}
            </p>
          </Card>
        )}

        {/* Couple Names Section */}
        {invitation.sections_enabled.couple && (
          <Card 
            className="p-12 mb-8 text-center"
            style={{
              background: 'var(--color-card, #FFFDF7)',
              boxShadow: 'var(--card-shadow, 0 4px 12px rgba(139, 115, 85, 0.15))',
              border: 'var(--card-border, 1px solid #E8D9C5)',
              borderRadius: 'var(--card-radius, 12px)',
              marginBottom: 'var(--spacing-card, 1.5rem)'
            }}
          >
            <div className="space-y-6">
              <h2 
                className="text-3xl md:text-4xl font-bold"
                style={{ 
                  fontFamily: 'var(--font-heading, "Cinzel", serif)',
                  color: 'var(--color-primary, #8B7355)'
                }}
              >
                {invitation.groom_name}
              </h2>
              <Heart 
                className="w-8 h-8 mx-auto" 
                style={{ color: 'var(--color-secondary, #D4AF37)' }} 
              />
              <h2 
                className="text-3xl md:text-4xl font-bold"
                style={{ 
                  fontFamily: 'var(--font-heading, "Cinzel", serif)',
                  color: 'var(--color-primary, #8B7355)'
                }}
              >
                {invitation.bride_name}
              </h2>
            </div>
          </Card>
        )}

        {/* About Couple Section */}
        {invitation.sections_enabled.about && invitation.about_couple && (
          <Card 
            className="p-8 mb-8"
            style={{
              background: 'var(--color-card, #FFFDF7)',
              boxShadow: 'var(--card-shadow, 0 4px 12px rgba(139, 115, 85, 0.15))',
              border: 'var(--card-border, 1px solid #E8D9C5)',
              borderRadius: 'var(--card-radius, 12px)',
              marginBottom: 'var(--spacing-card, 1.5rem)'
            }}
          >
            <h3 
              className="text-2xl font-semibold mb-6 text-center"
              style={{ 
                fontFamily: 'var(--font-heading, "Cinzel", serif)',
                color: 'var(--color-primary, #8B7355)'
              }}
            >
              About Us
            </h3>
            <div 
              dangerouslySetInnerHTML={{ __html: invitation.about_couple }}
              className="prose prose-lg max-w-none"
              style={{ 
                color: 'var(--color-text, #4A3728)',
                fontFamily: 'var(--font-body, "Lora", serif)'
              }}
            />
          </Card>
        )}

        {/* Family Details Section */}
        {invitation.sections_enabled.family && invitation.family_details && (
          <Card 
            className="p-8 mb-8"
            style={{
              background: 'var(--color-card, #FFFDF7)',
              boxShadow: 'var(--card-shadow, 0 4px 12px rgba(139, 115, 85, 0.15))',
              border: 'var(--card-border, 1px solid #E8D9C5)',
              borderRadius: 'var(--card-radius, 12px)',
              marginBottom: 'var(--spacing-card, 1.5rem)'
            }}
          >
            <h3 
              className="text-2xl font-semibold mb-6 text-center"
              style={{ 
                fontFamily: 'var(--font-heading, "Cinzel", serif)',
                color: 'var(--color-primary, #8B7355)'
              }}
            >
              Our Families
            </h3>
            <div 
              dangerouslySetInnerHTML={{ __html: invitation.family_details }}
              className="prose prose-lg max-w-none"
              style={{ 
                color: 'var(--color-text, #4A3728)',
                fontFamily: 'var(--font-body, "Lora", serif)'
              }}
            />
          </Card>
        )}

        {/* Love Story Section */}
        {invitation.sections_enabled.love_story && invitation.love_story && (
          <Card 
            className="p-8 mb-8"
            style={{
              background: 'var(--color-card, #FFFDF7)',
              boxShadow: 'var(--card-shadow, 0 4px 12px rgba(139, 115, 85, 0.15))',
              border: 'var(--card-border, 1px solid #E8D9C5)',
              borderRadius: 'var(--card-radius, 12px)',
              marginBottom: 'var(--spacing-card, 1.5rem)'
            }}
          >
            <h3 
              className="text-2xl font-semibold mb-6 text-center"
              style={{ 
                fontFamily: 'var(--font-heading, "Cinzel", serif)',
                color: 'var(--color-primary, #8B7355)'
              }}
            >
              Our Story
            </h3>
            <div 
              dangerouslySetInnerHTML={{ __html: invitation.love_story }}
              className="prose prose-lg max-w-none"
              style={{ 
                color: 'var(--color-text, #4A3728)',
                fontFamily: 'var(--font-body, "Lora", serif)'
              }}
            />
          </Card>
        )}

        {/* Event Schedule Section */}
        {invitation.sections_enabled.events && invitation.events && invitation.events.length > 0 && (
          <Card 
            className="p-8 mb-8"
            style={{
              background: 'var(--color-card, #FFFDF7)',
              boxShadow: 'var(--card-shadow, 0 4px 12px rgba(139, 115, 85, 0.15))',
              border: 'var(--card-border, 1px solid #E8D9C5)',
              borderRadius: 'var(--card-radius, 12px)',
              marginBottom: 'var(--spacing-card, 1.5rem)'
            }}
          >
            <h3 
              className="text-2xl font-semibold mb-6 text-center"
              style={{ 
                fontFamily: 'var(--font-heading, "Cinzel", serif)',
                color: 'var(--color-primary, #8B7355)'
              }}
            >
              Event Schedule
            </h3>
            
            <div className="space-y-6">
              {invitation.events
                .filter(event => event.visible)
                .sort((a, b) => {
                  const dateCompare = new Date(a.date).getTime() - new Date(b.date).getTime();
                  if (dateCompare !== 0) return dateCompare;
                  return a.start_time.localeCompare(b.start_time);
                })
                .map((event) => (
                  <div 
                    key={event.event_id}
                    className="border-l-4 pl-4 py-2"
                    style={{ 
                      borderLeftColor: 'var(--color-secondary, #D4AF37)',
                      borderRadius: '2px'
                    }}
                  >
                    <h4 
                      className="text-lg font-semibold mb-2"
                      style={{ color: 'var(--color-primary, #8B7355)' }}
                    >
                      {event.name}
                    </h4>
                    
                    <div className="space-y-2 text-sm">
                      <div className="flex items-start">
                        <Calendar 
                          className="w-4 h-4 mr-2 mt-0.5 flex-shrink-0" 
                          style={{ color: 'var(--color-secondary, #D4AF37)' }} 
                        />
                        <div style={{ color: 'var(--color-text, #4A3728)' }}>
                          {new Date(event.date).toLocaleDateString('en-US', {
                            weekday: 'long',
                            year: 'numeric',
                            month: 'long',
                            day: 'numeric'
                          })}
                        </div>
                      </div>

                      <div className="flex items-start">
                        <span className="w-4 h-4 mr-2 mt-0.5 flex-shrink-0 text-center" style={{ color: 'var(--color-secondary, #D4AF37)' }}>⏰</span>
                        <div style={{ color: 'var(--color-text, #4A3728)' }}>
                          {event.start_time}
                          {event.end_time && ` - ${event.end_time}`}
                        </div>
                      </div>

                      <div className="flex items-start">
                        <MapPin 
                          className="w-4 h-4 mr-2 mt-0.5 flex-shrink-0" 
                          style={{ color: 'var(--color-secondary, #D4AF37)' }} 
                        />
                        <div>
                          <div 
                            className="font-medium"
                            style={{ color: 'var(--color-primary, #8B7355)' }}
                          >
                            {event.venue_name}
                          </div>
                          <div 
                            className="text-xs mt-1"
                            style={{ color: 'var(--color-text, #4A3728)' }}
                          >
                            {event.venue_address}
                          </div>
                        </div>
                      </div>

                      {event.description && (
                        <div className="mt-2 italic text-xs" style={{ color: 'var(--color-text-light, #6B5A47)' }}>
                          {event.description}
                        </div>
                      )}

                      {event.map_link && (
                        <div className="mt-3 space-y-3">
                          <a
                            href={event.map_link}
                            target="_blank"
                            rel="noopener noreferrer"
                            onClick={() => trackInteraction('map_click')}
                            className="inline-flex items-center px-4 py-2 text-sm font-medium rounded-md"
                            style={{
                              background: 'var(--color-secondary, #D4AF37)',
                              color: 'white',
                              textDecoration: 'none'
                            }}
                          >
                            📍 Get Directions
                          </a>
                          
                          {/* Map Embed - Desktop Only, if enabled */}
                          {invitation.map_settings?.embed_enabled && (
                            <div className="hidden md:block mt-3 w-full h-64 rounded-lg overflow-hidden border border-gray-300">
                              <iframe
                                src={(() => {
                                  // Convert regular Google Maps link to embed format
                                  const url = event.map_link;
                                  if (url.includes('google.com/maps')) {
                                    // Extract coordinates or place info
                                    if (url.includes('@')) {
                                      // Has coordinates: extract them
                                      const match = url.match(/@(-?\d+\.\d+),(-?\d+\.\d+)/);
                                      if (match) {
                                        return `https://maps.google.com/maps?q=${match[1]},${match[2]}&output=embed`;
                                      }
                                    }
                                    // Try to use the full URL as query
                                    return `https://maps.google.com/maps?q=${encodeURIComponent(event.venue_name + ' ' + event.venue_address)}&output=embed`;
                                  }
                                  return url;
                                })()}
                                width="100%"
                                height="100%"
                                style={{ border: 0 }}
                                allowFullScreen=""
                                loading="lazy"
                                referrerPolicy="no-referrer-when-downgrade"
                                title={`Map for ${event.venue_name}`}
                              ></iframe>
                            </div>
                          )}
                        </div>
                      )}
                    </div>
                  </div>
                ))}
            </div>
          </Card>
        )}

        {/* Fallback: Show old event details if no events array */}
        {invitation.sections_enabled.events && (!invitation.events || invitation.events.length === 0) && (
          <Card 
            className="p-8 mb-8"
            style={{
              background: 'var(--color-card, #FFFDF7)',
              boxShadow: 'var(--card-shadow, 0 4px 12px rgba(139, 115, 85, 0.15))',
              border: 'var(--card-border, 1px solid #E8D9C5)',
              borderRadius: 'var(--card-radius, 12px)',
              marginBottom: 'var(--spacing-card, 1.5rem)'
            }}
          >
            <h3 
              className="text-2xl font-semibold mb-6 text-center"
              style={{ 
                fontFamily: 'var(--font-heading, "Cinzel", serif)',
                color: 'var(--color-primary, #8B7355)'
              }}
            >
              {getT('events', 'title')}
            </h3>
            <div className="space-y-4">
              <div className="flex items-start">
                <Calendar 
                  className="w-6 h-6 mr-4 mt-1" 
                  style={{ color: 'var(--color-secondary, #D4AF37)' }} 
                />
                <div>
                  <p 
                    className="font-semibold"
                    style={{ color: 'var(--color-primary, #8B7355)' }}
                  >
                    {getT('events', 'dateLabel')}
                  </p>
                  <p style={{ color: 'var(--color-text, #4A3728)' }}>
                    {eventDate.toLocaleDateString('en-US', {
                      weekday: 'long',
                      year: 'numeric',
                      month: 'long',
                      day: 'numeric'
                    })}
                  </p>
                </div>
              </div>
              <div className="flex items-start">
                <MapPin 
                  className="w-6 h-6 mr-4 mt-1" 
                  style={{ color: 'var(--color-secondary, #D4AF37)' }} 
                />
                <div>
                  <p 
                    className="font-semibold"
                    style={{ color: 'var(--color-primary, #8B7355)' }}
                  >
                    {getT('events', 'venueLabel')}
                  </p>
                  <p 
                    className="whitespace-pre-line"
                    style={{ color: 'var(--color-text, #4A3728)' }}
                  >
                    {invitation.venue}
                  </p>
                </div>
              </div>
            </div>
          </Card>
        )}

        {/* WhatsApp Greeting Section */}
        {(invitation.whatsapp_groom || invitation.whatsapp_bride) && (
          <Card 
            className="p-8 mb-8"
            style={{
              background: 'var(--color-card, #FFFDF7)',
              boxShadow: 'var(--card-shadow, 0 4px 12px rgba(139, 115, 85, 0.15))',
              border: 'var(--card-border, 1px solid #E8D9C5)',
              borderRadius: 'var(--card-radius, 12px)',
              marginBottom: 'var(--spacing-card, 1.5rem)'
            }}
          >
            <h3 
              className="text-2xl font-semibold mb-6 text-center"
              style={{ 
                fontFamily: 'var(--font-heading, "Cinzel", serif)',
                color: 'var(--color-primary, #8B7355)'
              }}
            >
              {getT('greetings', 'title')}
            </h3>
            <p 
              className="text-center mb-6"
              style={{ color: 'var(--color-text, #4A3728)' }}
            >
              Send your wishes directly via WhatsApp
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              {invitation.whatsapp_groom && (
                <Button
                  onClick={() => window.open(generateWhatsAppURL(invitation.whatsapp_groom), '_blank')}
                  className="flex items-center justify-center gap-2 px-6 py-3 bg-[#25D366] hover:bg-[#20BA5A] text-white"
                >
                  <MessageCircle className="w-5 h-5" />
                  {getT('whatsapp', 'groomButton')}
                </Button>
              )}
              {invitation.whatsapp_bride && (
                <Button
                  onClick={() => window.open(generateWhatsAppURL(invitation.whatsapp_bride), '_blank')}
                  className="flex items-center justify-center gap-2 px-6 py-3 bg-[#25D366] hover:bg-[#20BA5A] text-white"
                >
                  <MessageCircle className="w-5 h-5" />
                  {getT('whatsapp', 'brideButton')}
                </Button>
              )}
            </div>
          </Card>
        )}

        {/* Photos Section */}
        {invitation.sections_enabled.photos && invitation.media.length > 0 && (
          <Card 
            className="p-8 mb-8"
            style={{
              background: 'var(--color-card, #FFFDF7)',
              boxShadow: 'var(--card-shadow, 0 4px 12px rgba(139, 115, 85, 0.15))',
              border: 'var(--card-border, 1px solid #E8D9C5)',
              borderRadius: 'var(--card-radius, 12px)',
              marginBottom: 'var(--spacing-card, 1.5rem)'
            }}
          >
            <h3 
              className="text-2xl font-semibold mb-6 text-center"
              style={{ 
                fontFamily: 'var(--font-heading, "Cinzel", serif)',
                color: 'var(--color-primary, #8B7355)'
              }}
            >
              {getT('photos', 'title')}
            </h3>
            <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
              {invitation.media
                .filter(m => m.media_type === 'photo')
                .map((media) => (
                  <div 
                    key={media.id} 
                    className="aspect-square overflow-hidden"
                    style={{
                      border: 'var(--image-border, 4px solid #D4AF37)',
                      borderRadius: 'var(--image-radius, 8px)'
                    }}
                  >
                    <img
                      src={media.media_url}
                      alt={media.caption || 'Wedding photo'}
                      className="w-full h-full object-cover"
                    />
                  </div>
                ))}
            </div>
          </Card>
        )}

        {/* Video Section */}
        {invitation.sections_enabled.video && invitation.media.some(m => m.media_type === 'video') && (
          <Card 
            className="p-8 mb-8"
            style={{
              background: 'var(--color-card, #FFFDF7)',
              boxShadow: 'var(--card-shadow, 0 4px 12px rgba(139, 115, 85, 0.15))',
              border: 'var(--card-border, 1px solid #E8D9C5)',
              borderRadius: 'var(--card-radius, 12px)',
              marginBottom: 'var(--spacing-card, 1.5rem)'
            }}
          >
            <h3 
              className="text-2xl font-semibold mb-6 text-center"
              style={{ 
                fontFamily: 'var(--font-heading, "Cinzel", serif)',
                color: 'var(--color-primary, #8B7355)'
              }}
            >
              {getT('video', 'title')}
            </h3>
            <div 
              className="aspect-video overflow-hidden bg-gray-100"
              style={{
                border: 'var(--image-border, 4px solid #D4AF37)',
                borderRadius: 'var(--image-radius, 8px)'
              }}
            >
              {invitation.media
                .filter(m => m.media_type === 'video')
                .map((media) => (
                  <video
                    key={media.id}
                    src={media.media_url}
                    controls
                    className="w-full h-full"
                  />
                ))}
            </div>
          </Card>
        )}

        {/* Greetings Section */}
        {invitation.sections_enabled.greetings && (
          <Card 
            className="p-8 mb-8"
            style={{
              background: 'var(--color-card, #FFFDF7)',
              boxShadow: 'var(--card-shadow, 0 4px 12px rgba(139, 115, 85, 0.15))',
              border: 'var(--card-border, 1px solid #E8D9C5)',
              borderRadius: 'var(--card-radius, 12px)',
              marginBottom: 'var(--spacing-card, 1.5rem)'
            }}
          >
            <h3 
              className="text-2xl font-semibold mb-6 text-center"
              style={{ 
                fontFamily: 'var(--font-heading, "Cinzel", serif)',
                color: 'var(--color-primary, #8B7355)'
              }}
            >
              {getT('greetings', 'title')}
            </h3>

            {/* Greeting Form */}
            <form onSubmit={handleSubmitGreeting} className="mb-8">
              <div className="space-y-4">
                <div>
                  <label 
                    className="block text-sm font-medium mb-2"
                    style={{ color: 'var(--color-text, #4A3728)' }}
                  >
                    {getT('greetings', 'nameLabel')}
                  </label>
                  <input
                    type="text"
                    value={guestName}
                    onChange={(e) => setGuestName(e.target.value)}
                    required
                    className="w-full px-4 py-2 border rounded-md"
                    style={{
                      borderColor: 'var(--color-accent, #C9A961)',
                      background: 'var(--color-background, #FFF8E7)',
                      color: 'var(--color-text, #4A3728)'
                    }}
                    placeholder={getT('greetings', 'messagePlaceholder')}
                  />
                </div>
                <div>
                  <label 
                    className="block text-sm font-medium mb-2"
                    style={{ color: 'var(--color-text, #4A3728)' }}
                  >
                    Your Message (max 250 characters)
                  </label>
                  <textarea
                    value={message}
                    onChange={(e) => {
                      if (e.target.value.length <= 250) {
                        setMessage(e.target.value);
                      }
                    }}
                    required
                    maxLength={250}
                    rows="4"
                    className="w-full px-4 py-2 border rounded-md"
                    style={{
                      borderColor: 'var(--color-accent, #C9A961)',
                      background: 'var(--color-background, #FFF8E7)',
                      color: 'var(--color-text, #4A3728)'
                    }}
                    placeholder={getT('greetings', 'messagePlaceholder')}
                  />
                  <p className="text-xs text-gray-500 mt-1 text-right">
                    {message.length}/250 characters
                  </p>
                </div>
                {!navigator.onLine && (
                  <p className="text-red-600 text-sm text-center">
                    Internet connection required to submit greeting
                  </p>
                )}
                <Button
                  type="submit"
                  disabled={submitting || !navigator.onLine}
                  className="w-full text-white"
                  style={{
                    background: 'var(--color-primary, #8B7355)',
                    opacity: (submitting || !navigator.onLine) ? 0.6 : 1
                  }}
                >
                  <Send className="w-4 h-4 mr-2" />
                  {submitting ? 'Sending...' : getT('greetings', 'submitButton')}
                </Button>
                {submitSuccess && (
                  <p className="text-green-600 text-sm text-center">
                    Thank you! Your greeting has been submitted.
                  </p>
                )}
              </div>
            </form>

            {/* Display Greetings */}
            {invitation.greetings.length > 0 && (
              <div>
                <h4 
                  className="text-lg font-semibold mb-4"
                  style={{ color: 'var(--color-primary, #8B7355)' }}
                >
                  Wishes from Loved Ones ({invitation.greetings.length})
                </h4>
                <div className="space-y-4 max-h-96 overflow-y-auto">
                  {invitation.greetings.map((greeting) => (
                    <div 
                      key={greeting.id} 
                      className="rounded-lg p-4"
                      style={{
                        background: 'var(--color-background, #FFF8E7)',
                        border: 'var(--card-border, 1px solid #E8D9C5)'
                      }}
                    >
                      <p 
                        className="font-semibold mb-1"
                        style={{ color: 'var(--color-primary, #8B7355)' }}
                      >
                        {greeting.guest_name}
                      </p>
                      <p 
                        className="text-sm mb-2"
                        style={{ color: 'var(--color-text, #4A3728)' }}
                      >
                        {greeting.message}
                      </p>
                      <p 
                        className="text-xs"
                        style={{ color: 'var(--color-accent, #C9A961)' }}
                      >
                        {new Date(greeting.created_at).toLocaleDateString()}
                      </p>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </Card>
        )}

        {/* RSVP Section - Conditional based on sections_enabled */}
        {invitation.sections_enabled.rsvp && (
          <Card 
            className="mb-8 p-8"
            style={{
              background: 'var(--color-card, #FFFDF7)',
              border: 'var(--card-border, 1px solid #E8D9C5)',
              boxShadow: 'var(--card-shadow, 0 4px 6px rgba(0,0,0,0.1))',
              borderRadius: 'var(--card-radius, 8px)'
            }}
          >
          <h3 
            className="text-2xl font-semibold mb-4 text-center"
            style={{ 
              color: 'var(--color-primary, #8B7355)',
              fontFamily: 'var(--font-heading, "Playfair Display", serif)'
            }}
          >
            RSVP
          </h3>
          <p className="text-center mb-6" style={{ color: 'var(--color-text, #4A3728)' }}>
            Please let us know if you can join us for this special occasion
          </p>

          {!rsvpSuccess ? (
            <form onSubmit={handleSubmitRSVP} className="space-y-4">
              <div>
                <label className="block text-sm font-medium mb-2" style={{ color: 'var(--color-text, #4A3728)' }}>
                  Your Name *
                </label>
                <input
                  type="text"
                  value={rsvpData.guest_name}
                  onChange={(e) => setRsvpData(prev => ({ ...prev, guest_name: e.target.value }))}
                  required
                  className="w-full px-4 py-2 border rounded-md"
                  style={{
                    borderColor: 'var(--color-accent, #C9A961)',
                    background: 'var(--color-background, #FFF8E7)',
                    color: 'var(--color-text, #4A3728)'
                  }}
                />
              </div>

              <div>
                <label className="block text-sm font-medium mb-2" style={{ color: 'var(--color-text, #4A3728)' }}>
                  Phone Number (with country code) *
                </label>
                <input
                  type="tel"
                  value={rsvpData.guest_phone}
                  onChange={(e) => setRsvpData(prev => ({ ...prev, guest_phone: e.target.value }))}
                  required
                  placeholder="+91 98765 43210"
                  className="w-full px-4 py-2 border rounded-md"
                  style={{
                    borderColor: 'var(--color-accent, #C9A961)',
                    background: 'var(--color-background, #FFF8E7)',
                    color: 'var(--color-text, #4A3728)'
                  }}
                />
                <p className="text-xs mt-1" style={{ color: 'var(--color-accent, #C9A961)' }}>
                  Format: +[country code][number]
                </p>
              </div>

              <div>
                <label className="block text-sm font-medium mb-2" style={{ color: 'var(--color-text, #4A3728)' }}>
                  Will you attend? *
                </label>
                <div className="grid grid-cols-3 gap-3">
                  {[
                    { value: 'yes', label: 'Attending', emoji: '✓' },
                    { value: 'no', label: 'Not Attending', emoji: '✗' },
                    { value: 'maybe', label: 'Maybe', emoji: '?' }
                  ].map((option) => (
                    <button
                      key={option.value}
                      type="button"
                      onClick={() => {
                        setRsvpData(prev => ({ ...prev, status: option.value }));
                        // PHASE 9: Track RSVP button click
                        trackInteraction('rsvp_click');
                      }}
                      className="px-4 py-3 rounded-md text-sm font-medium transition-all"
                      style={{
                        background: rsvpData.status === option.value 
                          ? 'var(--color-primary, #8B7355)' 
                          : 'var(--color-background, #FFF8E7)',
                        color: rsvpData.status === option.value 
                          ? 'white' 
                          : 'var(--color-text, #4A3728)',
                        border: '2px solid var(--color-accent, #C9A961)'
                      }}
                    >
                      <div className="text-lg mb-1">{option.emoji}</div>
                      {option.label}
                    </button>
                  ))}
                </div>
              </div>

              {rsvpData.status === 'yes' && (
                <div>
                  <label className="block text-sm font-medium mb-2" style={{ color: 'var(--color-text, #4A3728)' }}>
                    Number of Guests
                  </label>
                  <input
                    type="number"
                    min="1"
                    max="10"
                    value={rsvpData.guest_count}
                    onChange={(e) => setRsvpData(prev => ({ ...prev, guest_count: parseInt(e.target.value) || 1 }))}
                    className="w-full px-4 py-2 border rounded-md"
                    style={{
                      borderColor: 'var(--color-accent, #C9A961)',
                      background: 'var(--color-background, #FFF8E7)',
                      color: 'var(--color-text, #4A3728)'
                    }}
                  />
                </div>
              )}

              <div>
                <label className="block text-sm font-medium mb-2" style={{ color: 'var(--color-text, #4A3728)' }}>
                  Message / Blessings (Optional, max 250 characters)
                </label>
                <textarea
                  value={rsvpData.message}
                  onChange={(e) => setRsvpData(prev => ({ ...prev, message: e.target.value.slice(0, 250) }))}
                  maxLength={250}
                  rows="3"
                  className="w-full px-4 py-2 border rounded-md"
                  style={{
                    borderColor: 'var(--color-accent, #C9A961)',
                    background: 'var(--color-background, #FFF8E7)',
                    color: 'var(--color-text, #4A3728)'
                  }}
                  placeholder="Your message..."
                />
                <p className="text-xs text-right mt-1" style={{ color: 'var(--color-accent, #C9A961)' }}>
                  {rsvpData.message.length}/250
                </p>
              </div>

              {rsvpError && (
                <p className="text-red-600 text-sm text-center">
                  {rsvpError}
                </p>
              )}

              {!navigator.onLine && (
                <p className="text-orange-600 text-sm text-center">
                  Internet connection required to submit RSVP
                </p>
              )}

              <Button
                type="submit"
                disabled={rsvpSubmitting || !navigator.onLine}
                className="w-full text-white"
                style={{
                  background: 'var(--color-primary, #8B7355)',
                  opacity: (rsvpSubmitting || !navigator.onLine) ? 0.6 : 1
                }}
              >
                {rsvpSubmitting ? 'Submitting...' : 'Submit RSVP'}
              </Button>
            </form>
          ) : (
            <div className="text-center py-8">
              <div className="text-6xl mb-4">
                {submittedRsvpStatus === 'yes' && '✓'}
                {submittedRsvpStatus === 'no' && '✗'}
                {submittedRsvpStatus === 'maybe' && '?'}
              </div>
              <h4 
                className="text-xl font-semibold mb-2"
                style={{ color: 'var(--color-primary, #8B7355)' }}
              >
                Thank You!
              </h4>
              <p style={{ color: 'var(--color-text, #4A3728)' }} className="mb-2">
                Your RSVP has been submitted successfully.
              </p>
              <p style={{ color: 'var(--color-primary, #8B7355)' }} className="font-semibold">
                {submittedRsvpStatus === 'yes' && '✓ Attending'}
                {submittedRsvpStatus === 'no' && 'Not Attending'}
                {submittedRsvpStatus === 'maybe' && 'Maybe'}
              </p>
            </div>
          )}
        </Card>
        )}

        {/* Footer Section */}
        {invitation.sections_enabled.footer && (
          <div className="text-center py-8">
            <Heart 
              className="w-12 h-12 mx-auto mb-4" 
              style={{ color: 'var(--color-secondary, #D4AF37)' }}
            />
            <p 
              className="text-lg"
              style={{ color: 'var(--color-text, #4A3728)' }}
            >
              {getT('footer', 'thankyou')}
            </p>
          </div>
        )}
      </div>
    </div>
    </>
  );
};

export default PublicInvitation;
