import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import axios from 'axios';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Heart, Calendar, MapPin, Send } from 'lucide-react';
import { getTheme, applyThemeVariables } from '@/config/themes';

const API_URL = process.env.REACT_APP_BACKEND_URL || '';

const PublicInvitation = () => {
  const { slug } = useParams();
  const [invitation, setInvitation] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [guestName, setGuestName] = useState('');
  const [message, setMessage] = useState('');
  const [submitting, setSubmitting] = useState(false);
  const [submitSuccess, setSubmitSuccess] = useState(false);

  useEffect(() => {
    fetchInvitation();
  }, [slug]);

  // Apply theme when invitation loads
  useEffect(() => {
    if (invitation && invitation.design_id) {
      const theme = getTheme(invitation.design_id);
      applyThemeVariables(theme);
      
      // Load Google Fonts dynamically
      const link = document.createElement('link');
      link.href = 'https://fonts.googleapis.com/css2?family=Cinzel:wght@400;600;700&family=Lora:wght@400;600;700&family=Playfair+Display:wght@400;600;700&family=Libre+Baskerville:wght@400;700&family=Quicksand:wght@400;600;700&family=Nunito:wght@400;600;700&family=Cormorant+Garamond:wght@400;600;700&family=Montserrat:wght@400;600;700&family=UnifrakturMaguntia&family=Merriweather:wght@400;700&family=Raleway:wght@400;600;700&family=Inter:wght@400;600;700&family=Poppins:wght@400;600;700&family=Open+Sans:wght@400;600;700&family=Indie+Flower&family=Architects+Daughter&display=swap';
      link.rel = 'stylesheet';
      document.head.appendChild(link);
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

  return (
    <div 
      className="min-h-screen" 
      style={{ 
        background: 'var(--color-background, #FFF8E7)',
        fontFamily: 'var(--font-body, "Lora", serif)',
        color: 'var(--color-text, #4A3728)',
        paddingTop: 'var(--spacing-section, 3rem)',
        paddingBottom: 'var(--spacing-section, 3rem)'
      }}
    >
      <div className="container mx-auto px-4 max-w-4xl">
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
              {invitation.event_type === 'marriage' ? 'Wedding Invitation' : 
               invitation.event_type === 'engagement' ? 'Engagement Invitation' : 'Event Invitation'}
            </h1>
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
              With joy in our hearts, we invite you to celebrate
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
              Event Details
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
                    Date & Time
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
                    Venue
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
              Our Memories
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
              Our Story
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
              Send Your Blessings
            </h3>

            {/* Greeting Form */}
            <form onSubmit={handleSubmitGreeting} className="mb-8">
              <div className="space-y-4">
                <div>
                  <label 
                    className="block text-sm font-medium mb-2"
                    style={{ color: 'var(--color-text, #4A3728)' }}
                  >
                    Your Name
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
                    placeholder="Enter your name"
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
                    placeholder="Write your blessings..."
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
                  {submitting ? 'Sending...' : 'Send Greeting'}
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
              Your presence will make our day even more special
            </p>
          </div>
        )}
      </div>
    </div>
  );
};

export default PublicInvitation;
