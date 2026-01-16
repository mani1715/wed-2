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
  const [guestName, setGuestName] = useState('');
  const [message, setMessage] = useState('');
  const [submitting, setSubmitting] = useState(false);
  const [submitSuccess, setSubmitSuccess] = useState(false);

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
      
      // Set default language (first enabled language)
      if (invitation.enabled_languages && invitation.enabled_languages.length > 0) {
        setSelectedLanguage(invitation.enabled_languages[0]);
      }
    }
  }, [invitation]);

  const fetchInvitation = async () => {
    try {
      const response = await axios.get(`${API_URL}/api/invite/${slug}`);
      setInvitation(response.data);
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
  
  // Get text helper functions with custom text
  const customText = invitation.custom_text || {};
  const getT = (section, key) => getText(selectedLanguage, section, key, customText);
  const getSectionT = (section) => getSectionText(selectedLanguage, section, customText);

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
        
        {/* Language Switcher - Only show if multiple languages available */}
        {availableLanguages.length > 1 && (
          <div className="flex justify-end mb-6">
            <div className="flex gap-2 bg-white/80 backdrop-blur-sm rounded-lg p-2 shadow-sm">
              {availableLanguages.map((langCode) => {
                const lang = getLanguage(langCode);
                if (!lang) return null;
                
                return (
                  <button
                    key={langCode}
                    onClick={() => setSelectedLanguage(langCode)}
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

        {/* Event Details Section */}
        {invitation.sections_enabled.events && (
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
                    Your Message
                  </label>
                  <textarea
                    value={message}
                    onChange={(e) => setMessage(e.target.value)}
                    required
                    rows="4"
                    className="w-full px-4 py-2 border rounded-md"
                    style={{
                      borderColor: 'var(--color-accent, #C9A961)',
                      background: 'var(--color-background, #FFF8E7)',
                      color: 'var(--color-text, #4A3728)'
                    }}
                    placeholder={getT('greetings', 'messagePlaceholder')}
                  />
                </div>
                <Button
                  type="submit"
                  disabled={submitting}
                  className="w-full text-white"
                  style={{
                    background: 'var(--color-primary, #8B7355)',
                    opacity: submitting ? 0.6 : 1
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
