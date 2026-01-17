import React, { useState, useEffect } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { useAuth } from '@/context/AuthContext';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import axios from 'axios';
import { ArrowLeft, Save, Eye, ChevronDown, ChevronUp, Check } from 'lucide-react';
import { DESIGN_THEMES } from '@/config/designThemes';
import { DEITY_OPTIONS } from '@/config/religiousAssets';
import { LANGUAGES } from '@/utils/languageLoader';

const API_URL = process.env.REACT_APP_BACKEND_URL || '';

const ProfileForm = () => {
  const navigate = useNavigate();
  const { profileId } = useParams();
  const { admin } = useAuth();
  const isEdit = !!profileId;

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [showCustomText, setShowCustomText] = useState(false);
  const [whatsappErrors, setWhatsappErrors] = useState({
    groom: '',
    bride: ''
  });

  const [formData, setFormData] = useState({
    groom_name: '',
    bride_name: '',
    event_type: 'marriage',
    event_date: '',
    venue: '',
    language: ['english'],
    design_id: 'royal_classic',
    deity_id: null,
    whatsapp_groom: '',
    whatsapp_bride: '',
    enabled_languages: ['english'],
    custom_text: {},
    link_expiry_type: 'days',
    link_expiry_value: '30',
    sections_enabled: {
      opening: true,
      welcome: true,
      couple: true,
      photos: true,
      video: false,
      events: true,
      greetings: true,
      footer: true
    },
    background_music: {
      enabled: false,
      file_url: null
    },
    events: []
  });

  const [savedProfile, setSavedProfile] = useState(null);

  useEffect(() => {
    if (!admin) {
      navigate('/admin/login');
      return;
    }

    if (isEdit) {
      fetchProfile();
    }
  }, [admin, profileId]);

  const fetchProfile = async () => {
    try {
      const response = await axios.get(`${API_URL}/api/admin/profiles/${profileId}`);
      const profile = response.data;
      
      setFormData({
        groom_name: profile.groom_name,
        bride_name: profile.bride_name,
        event_type: profile.event_type,
        event_date: new Date(profile.event_date).toISOString().split('T')[0],
        venue: profile.venue,
        language: Array.isArray(profile.language) ? profile.language : [profile.language],
        design_id: profile.design_id || 'royal_classic',
        deity_id: profile.deity_id || null,
        whatsapp_groom: profile.whatsapp_groom || '',
        whatsapp_bride: profile.whatsapp_bride || '',
        enabled_languages: profile.enabled_languages || ['english'],
        custom_text: profile.custom_text || {},
        link_expiry_type: profile.link_expiry_type,
        link_expiry_value: profile.link_expiry_value || '30',
        sections_enabled: profile.sections_enabled,
        background_music: profile.background_music || { enabled: false, file_url: null },
        events: profile.events || [],
        slug: profile.slug
      });
    } catch (error) {
      console.error('Failed to fetch profile:', error);
      setError('Failed to load profile');
    }
  };

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleLanguageToggle = (lang) => {
    setFormData(prev => {
      const currentLangs = prev.language;
      const newLangs = currentLangs.includes(lang)
        ? currentLangs.filter(l => l !== lang)
        : [...currentLangs, lang];
      
      // Ensure at least one language is selected
      return {
        ...prev,
        language: newLangs.length > 0 ? newLangs : currentLangs
      };
    });
  };

  const handleEnabledLanguageToggle = (lang) => {
    setFormData(prev => {
      const currentLangs = prev.enabled_languages;
      
      // Prevent removing English (mandatory language)
      if (lang === 'english' && currentLangs.includes('english')) {
        return prev; // Cannot remove English
      }
      
      const newLangs = currentLangs.includes(lang)
        ? currentLangs.filter(l => l !== lang)
        : [...currentLangs, lang];
      
      // Ensure at least one language is enabled
      return {
        ...prev,
        enabled_languages: newLangs.length > 0 ? newLangs : currentLangs
      };
    });
  };

  const validateWhatsAppNumber = (number) => {
    if (!number || number.trim() === '') return true; // Optional field
    const e164Pattern = /^\+[1-9]\d{1,14}$/;
    return e164Pattern.test(number);
  };

  const handleWhatsAppChange = (field, value) => {
    setFormData(prev => ({
      ...prev,
      [field]: value
    }));

    // Validate
    if (value && !validateWhatsAppNumber(value)) {
      setWhatsappErrors(prev => ({
        ...prev,
        [field === 'whatsapp_groom' ? 'groom' : 'bride']: 'Must be in E.164 format (e.g., +919876543210)'
      }));
    } else {
      setWhatsappErrors(prev => ({
        ...prev,
        [field === 'whatsapp_groom' ? 'groom' : 'bride']: ''
      }));
    }
  };

  const handleCustomTextChange = (language, section, value) => {
    setFormData(prev => ({
      ...prev,
      custom_text: {
        ...prev.custom_text,
        [language]: {
          ...(prev.custom_text[language] || {}),
          [section]: value
        }
      }
    }));
  };

  const handleExpiryPresetChange = (e) => {
    const preset = e.target.value;
    if (preset === 'custom') {
      setFormData(prev => ({
        ...prev,
        link_expiry_type: 'days',
        link_expiry_value: ''
      }));
    } else if (preset === '1day') {
      setFormData(prev => ({
        ...prev,
        link_expiry_type: 'days',
        link_expiry_value: '1'
      }));
    } else if (preset === '7days') {
      setFormData(prev => ({
        ...prev,
        link_expiry_type: 'days',
        link_expiry_value: '7'
      }));
    } else if (preset === '30days') {
      setFormData(prev => ({
        ...prev,
        link_expiry_type: 'days',
        link_expiry_value: '30'
      }));
    }
  };

  const getExpiryPreset = () => {
    if (formData.link_expiry_type === 'days') {
      if (formData.link_expiry_value === '1' || formData.link_expiry_value === 1) return '1day';
      if (formData.link_expiry_value === '7' || formData.link_expiry_value === 7) return '7days';
      if (formData.link_expiry_value === '30' || formData.link_expiry_value === 30) return '30days';
    }
    return 'custom';
  };

  const handleSectionToggle = (section) => {
    setFormData(prev => ({
      ...prev,
      sections_enabled: {
        ...prev.sections_enabled,
        [section]: !prev.sections_enabled[section]
      }
    }));
  };

  // Event Handlers
  const generateEventId = () => {
    return `evt_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  };

  const addDefaultEvents = () => {
    const defaultEvents = [
      { name: 'Mehendi', visible: true },
      { name: 'Sangeet', visible: true },
      { name: 'Wedding', visible: true },
      { name: 'Reception', visible: true }
    ];

    const newEvents = defaultEvents.map((evt, index) => ({
      event_id: generateEventId(),
      name: evt.name,
      date: '',
      start_time: '',
      end_time: '',
      venue_name: '',
      venue_address: '',
      map_link: '',
      description: '',
      visible: evt.visible,
      order: index
    }));

    setFormData(prev => ({
      ...prev,
      events: newEvents
    }));
  };

  const addEvent = () => {
    if (formData.events.length >= 7) {
      alert('Maximum 7 events allowed');
      return;
    }

    const newEvent = {
      event_id: generateEventId(),
      name: '',
      date: '',
      start_time: '',
      end_time: '',
      venue_name: '',
      venue_address: '',
      map_link: '',
      description: '',
      visible: true,
      order: formData.events.length
    };

    setFormData(prev => ({
      ...prev,
      events: [...prev.events, newEvent]
    }));
  };

  const updateEvent = (eventId, field, value) => {
    setFormData(prev => ({
      ...prev,
      events: prev.events.map(evt =>
        evt.event_id === eventId ? { ...evt, [field]: value } : evt
      )
    }));
  };

  const deleteEvent = (eventId) => {
    const visibleEvents = formData.events.filter(e => e.visible && e.event_id !== eventId);
    const eventToDelete = formData.events.find(e => e.event_id === eventId);
    
    if (visibleEvents.length === 0 && eventToDelete?.visible) {
      alert('At least one event must be visible');
      return;
    }

    setFormData(prev => ({
      ...prev,
      events: prev.events.filter(evt => evt.event_id !== eventId)
    }));
  };

  const toggleEventVisibility = (eventId) => {
    const event = formData.events.find(e => e.event_id === eventId);
    if (!event) return;

    const visibleCount = formData.events.filter(e => e.visible).length;
    
    if (event.visible && visibleCount === 1) {
      alert('At least one event must be visible');
      return;
    }

    setFormData(prev => ({
      ...prev,
      events: prev.events.map(evt =>
        evt.event_id === eventId ? { ...evt, visible: !evt.visible } : evt
      )
    }));
  };

  const moveEvent = (eventId, direction) => {
    const index = formData.events.findIndex(e => e.event_id === eventId);
    if (index === -1) return;

    const newEvents = [...formData.events];
    
    if (direction === 'up' && index > 0) {
      [newEvents[index], newEvents[index - 1]] = [newEvents[index - 1], newEvents[index]];
    } else if (direction === 'down' && index < newEvents.length - 1) {
      [newEvents[index], newEvents[index + 1]] = [newEvents[index + 1], newEvents[index]];
    }

    // Update order numbers
    newEvents.forEach((evt, idx) => {
      evt.order = idx;
    });

    setFormData(prev => ({
      ...prev,
      events: newEvents
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');

    // Validate WhatsApp numbers
    if (formData.whatsapp_groom && !validateWhatsAppNumber(formData.whatsapp_groom)) {
      setError('Groom WhatsApp number must be in E.164 format');
      return;
    }
    if (formData.whatsapp_bride && !validateWhatsAppNumber(formData.whatsapp_bride)) {
      setError('Bride WhatsApp number must be in E.164 format');
      return;
    }

    // Validate events if any exist
    if (formData.events.length > 0) {
      const visibleEvents = formData.events.filter(e => e.visible);
      if (visibleEvents.length === 0) {
        setError('At least one event must be visible');
        return;
      }

      // Validate required fields for all events
      for (const evt of formData.events) {
        if (!evt.name || !evt.date || !evt.start_time || !evt.venue_name || !evt.venue_address || !evt.map_link) {
          setError(`Please fill all required fields for event: ${evt.name || 'Unnamed'}`);
          return;
        }
      }
    }

    setLoading(true);

    try {
      const submitData = {
        ...formData,
        event_date: new Date(formData.event_date).toISOString(),
        link_expiry_value: formData.link_expiry_value ? parseInt(formData.link_expiry_value) : 30,
        whatsapp_groom: formData.whatsapp_groom || null,
        whatsapp_bride: formData.whatsapp_bride || null,
        deity_id: formData.deity_id || null
      };

      let response;
      if (isEdit) {
        response = await axios.put(`${API_URL}/api/admin/profiles/${profileId}`, submitData);
      } else {
        response = await axios.post(`${API_URL}/api/admin/profiles`, submitData);
      }

      setSavedProfile(response.data);
      
      // Don't navigate immediately, show the generated link
      if (!isEdit) {
        alert('Profile created successfully! You can now preview the invitation or copy the link.');
      } else {
        alert('Profile updated successfully!');
        navigate('/admin/dashboard');
      }
    } catch (error) {
      console.error('Failed to save profile:', error);
      setError(error.response?.data?.detail || 'Failed to save profile');
    } finally {
      setLoading(false);
    }
  };

  const handlePreview = () => {
    const slug = savedProfile?.slug || (isEdit && formData.slug);
    if (slug) {
      window.open(`/invite/${slug}`, '_blank');
    } else {
      alert('Please save the profile first to generate a preview link.');
    }
  };

  const handleCopyLink = () => {
    const link = savedProfile?.invitation_link;
    if (link) {
      const fullLink = window.location.origin + link;
      navigator.clipboard.writeText(fullLink);
      alert('Link copied to clipboard!');
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white border-b border-gray-200">
        <div className="container mx-auto px-4 py-4">
          <Button
            variant="ghost"
            onClick={() => navigate('/admin/dashboard')}
          >
            <ArrowLeft className="w-4 h-4 mr-2" />
            Back to Dashboard
          </Button>
        </div>
      </div>

      {/* Form */}
      <div className="container mx-auto px-4 py-8 max-w-4xl">
        <h1 className="text-3xl font-bold text-gray-800 mb-8">
          {isEdit ? 'Edit Profile' : 'Create New Profile'}
        </h1>

        <form onSubmit={handleSubmit} className="space-y-6">
          {/* Basic Information */}
          <Card className="p-6">
            <h2 className="text-xl font-semibold text-gray-800 mb-4">Basic Information</h2>
            <div className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Groom Name *
                  </label>
                  <input
                    type="text"
                    name="groom_name"
                    value={formData.groom_name}
                    onChange={handleChange}
                    required
                    className="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-rose-500 focus:border-rose-500"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Bride Name *
                  </label>
                  <input
                    type="text"
                    name="bride_name"
                    value={formData.bride_name}
                    onChange={handleChange}
                    required
                    className="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-rose-500 focus:border-rose-500"
                  />
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Event Type *
                  </label>
                  <select
                    name="event_type"
                    value={formData.event_type}
                    onChange={handleChange}
                    required
                    className="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-rose-500 focus:border-rose-500"
                  >
                    <option value="marriage">Marriage</option>
                    <option value="engagement">Engagement</option>
                    <option value="birthday">Birthday</option>
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Event Date *
                  </label>
                  <input
                    type="date"
                    name="event_date"
                    value={formData.event_date}
                    onChange={handleChange}
                    required
                    className="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-rose-500 focus:border-rose-500"
                  />
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Venue *
                </label>
                <textarea
                  name="venue"
                  value={formData.venue}
                  onChange={handleChange}
                  required
                  rows="3"
                  className="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-rose-500 focus:border-rose-500"
                />
              </div>
            </div>
          </Card>

          {/* Design Theme Selection */}
          <Card className="p-6">
            <h2 className="text-xl font-semibold text-gray-800 mb-4">Select Design Theme *</h2>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              {DESIGN_THEMES.map((design) => (
                <div
                  key={design.id}
                  onClick={() => setFormData(prev => ({ ...prev, design_id: design.id }))}
                  className={`cursor-pointer p-4 border-2 rounded-lg transition-all hover:shadow-md ${
                    formData.design_id === design.id
                      ? 'border-rose-500 bg-rose-50 shadow-lg'
                      : 'border-gray-200 hover:border-gray-400'
                  }`}
                >
                  <div className="aspect-video bg-gradient-to-br rounded-md mb-3 overflow-hidden" 
                       style={{
                         backgroundImage: `linear-gradient(to bottom right, ${design.colors.primary}, ${design.colors.secondary})`
                       }}>
                  </div>
                  <div className="text-sm font-semibold text-gray-800 mb-1">{design.name}</div>
                  <div className="text-xs text-gray-600 mb-2">{design.description}</div>
                  {formData.design_id === design.id && (
                    <div className="flex items-center text-rose-600 text-xs font-semibold">
                      <Check className="w-3 h-3 mr-1" />
                      Selected
                    </div>
                  )}
                </div>
              ))}
            </div>
          </Card>

          {/* Deity/Religious Background Selection */}
          <Card className="p-6">
            <h2 className="text-xl font-semibold text-gray-800 mb-4">Religious Background (Optional)</h2>
            <p className="text-sm text-gray-600 mb-4">
              Select a deity theme for your invitation, or choose "No Religious Theme" for a secular invitation
            </p>
            <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-4">
              {DEITY_OPTIONS.map((deity) => (
                <div
                  key={deity.id}
                  onClick={() => setFormData(prev => ({ ...prev, deity_id: deity.id === 'none' ? null : deity.id }))}
                  className={`cursor-pointer p-4 border-2 rounded-lg transition-all hover:shadow-md ${
                    (formData.deity_id === deity.id || (deity.id === 'none' && !formData.deity_id))
                      ? 'border-rose-500 bg-rose-50 shadow-lg'
                      : 'border-gray-200 hover:border-gray-400'
                  }`}
                >
                  <div className="aspect-square bg-gray-100 rounded-md mb-3 flex items-center justify-center">
                    <img 
                      src={deity.thumbnail} 
                      alt={deity.name}
                      className="w-full h-full object-contain rounded-md"
                      onError={(e) => {
                        e.target.style.display = 'none';
                        e.target.nextSibling.style.display = 'flex';
                      }}
                    />
                    <div className="w-full h-full items-center justify-center text-gray-400 text-xs" style={{display: 'none'}}>
                      {deity.name}
                    </div>
                  </div>
                  <div className="text-xs font-semibold text-gray-800 mb-1 text-center">{deity.name}</div>
                  <div className="text-xs text-gray-600 mb-2 text-center line-clamp-2">{deity.description}</div>
                  {(formData.deity_id === deity.id || (deity.id === 'none' && !formData.deity_id)) && (
                    <div className="flex items-center justify-center text-rose-600 text-xs font-semibold">
                      <Check className="w-3 h-3 mr-1" />
                      Selected
                    </div>
                  )}
                </div>
              ))}
            </div>
          </Card>

          {/* Language Configuration */}
          <Card className="p-6">
            <h2 className="text-xl font-semibold text-gray-800 mb-4">Language Configuration *</h2>
            <p className="text-sm text-gray-600 mb-4">
              Select which languages guests can view the invitation in. English is mandatory and always enabled.
            </p>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
              {LANGUAGES.map((lang) => {
                const isEnglish = lang.code === 'english';
                const isChecked = formData.enabled_languages.includes(lang.code);
                
                return (
                  <label 
                    key={lang.code} 
                    className={`flex items-center space-x-3 p-4 border-2 rounded-lg transition-all ${
                      isChecked
                        ? 'border-rose-500 bg-rose-50'
                        : 'border-gray-200'
                    } ${isEnglish ? 'opacity-75' : 'cursor-pointer hover:border-gray-400'}`}
                  >
                    <input
                      type="checkbox"
                      checked={isChecked}
                      onChange={() => !isEnglish && handleEnabledLanguageToggle(lang.code)}
                      disabled={isEnglish}
                      className="w-5 h-5 text-rose-600 border-gray-300 rounded focus:ring-rose-500 disabled:opacity-50"
                    />
                    <div className="flex-1">
                      <div className="text-sm font-medium text-gray-800">
                        {lang.name}
                        {isEnglish && <span className="ml-2 text-xs text-gray-500">(Required)</span>}
                      </div>
                      <div className="text-xs text-gray-600">{lang.nativeName}</div>
                    </div>
                    {isChecked && (
                      <Check className="w-4 h-4 text-rose-600" />
                    )}
                  </label>
                );
              })}
            </div>
          </Card>

          {/* WhatsApp Numbers */}
          <Card className="p-6">
            <h2 className="text-xl font-semibold text-gray-800 mb-4">WhatsApp Contact Numbers (Optional)</h2>
            <p className="text-sm text-gray-600 mb-4">
              Allow guests to send WhatsApp wishes directly. Include country code (e.g., +91 for India)
            </p>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Groom's WhatsApp Number
                </label>
                <input
                  type="tel"
                  value={formData.whatsapp_groom}
                  onChange={(e) => handleWhatsAppChange('whatsapp_groom', e.target.value)}
                  placeholder="+91 98765 43210"
                  className={`w-full px-4 py-2 border rounded-md focus:ring-2 focus:ring-rose-500 ${
                    whatsappErrors.groom ? 'border-red-500' : 'border-gray-300'
                  }`}
                />
                {whatsappErrors.groom && (
                  <p className="text-xs text-red-600 mt-1">{whatsappErrors.groom}</p>
                )}
                <p className="text-xs text-gray-500 mt-1">Format: +[country code][number]</p>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Bride's WhatsApp Number
                </label>
                <input
                  type="tel"
                  value={formData.whatsapp_bride}
                  onChange={(e) => handleWhatsAppChange('whatsapp_bride', e.target.value)}
                  placeholder="+91 98765 43210"
                  className={`w-full px-4 py-2 border rounded-md focus:ring-2 focus:ring-rose-500 ${
                    whatsappErrors.bride ? 'border-red-500' : 'border-gray-300'
                  }`}
                />
                {whatsappErrors.bride && (
                  <p className="text-xs text-red-600 mt-1">{whatsappErrors.bride}</p>
                )}
                <p className="text-xs text-gray-500 mt-1">Format: +[country code][number]</p>
              </div>
            </div>
          </Card>

          {/* Sections Enabled */}
          <Card className="p-6">
            <h2 className="text-xl font-semibold text-gray-800 mb-4">Enable/Disable Sections</h2>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              {Object.keys(formData.sections_enabled).map((section) => (
                <label key={section} className="flex items-center space-x-2 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={formData.sections_enabled[section]}
                    onChange={() => handleSectionToggle(section)}
                    className="w-4 h-4 text-rose-600 border-gray-300 rounded focus:ring-rose-500"
                  />
                  <span className="text-sm text-gray-700 capitalize">{section}</span>
                </label>
              ))}
            </div>
          </Card>

          {/* Background Music (Optional) */}
          <Card className="p-6">
            <h2 className="text-xl font-semibold text-gray-800 mb-4">Background Music (Optional)</h2>
            <p className="text-sm text-gray-600 mb-4">
              Add background music to your invitation. Music will NOT autoplay and guests can control playback.
            </p>
            
            {/* Enable/Disable Toggle */}
            <label className="flex items-center space-x-3 mb-4 cursor-pointer">
              <input
                type="checkbox"
                checked={formData.background_music.enabled}
                onChange={(e) => setFormData(prev => ({
                  ...prev,
                  background_music: {
                    ...prev.background_music,
                    enabled: e.target.checked,
                    file_url: e.target.checked ? prev.background_music.file_url : null
                  }
                }))}
                className="w-5 h-5 text-rose-600 border-gray-300 rounded focus:ring-rose-500"
              />
              <span className="text-sm font-medium text-gray-700">Enable Background Music</span>
            </label>

            {/* Music Upload Field */}
            {formData.background_music.enabled && (
              <div className="mt-4 space-y-3">
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Music File URL *
                </label>
                <input
                  type="url"
                  value={formData.background_music.file_url || ''}
                  onChange={(e) => setFormData(prev => ({
                    ...prev,
                    background_music: {
                      ...prev.background_music,
                      file_url: e.target.value
                    }
                  }))}
                  placeholder="https://example.com/wedding-music.mp3"
                  className="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-rose-500"
                  required={formData.background_music.enabled}
                />
                <div className="text-xs text-gray-600 space-y-1">
                  <p>• Supported format: MP3 only</p>
                  <p>• Maximum file size: 5MB recommended</p>
                  <p>• Music will play in a loop at 50% volume</p>
                  <p>• Guests can toggle music ON/OFF anytime</p>
                </div>
              </div>
            )}
          </Card>

          {/* Wedding Events Schedule */}
          <Card className="p-6">
            <div className="flex items-center justify-between mb-4">
              <div>
                <h2 className="text-xl font-semibold text-gray-800">Wedding Events Schedule</h2>
                <p className="text-sm text-gray-600 mt-1">Add multiple events (max 7). At least one event must be visible.</p>
              </div>
              {formData.events.length === 0 && (
                <Button
                  type="button"
                  onClick={addDefaultEvents}
                  variant="outline"
                  className="border-rose-500 text-rose-600 hover:bg-rose-50"
                >
                  Add Default Events
                </Button>
              )}
            </div>

            {formData.events.length > 0 && (
              <div className="space-y-4 mb-4">
                {formData.events.map((event, index) => (
                  <div key={event.event_id} className={`border rounded-lg p-4 ${!event.visible ? 'bg-gray-50 opacity-60' : 'bg-white'}`}>
                    <div className="flex items-center justify-between mb-3">
                      <div className="flex items-center space-x-2">
                        <span className="text-sm font-medium text-gray-700">Event {index + 1}</span>
                        <label className="flex items-center space-x-1 text-xs">
                          <input
                            type="checkbox"
                            checked={event.visible}
                            onChange={() => toggleEventVisibility(event.event_id)}
                            className="w-3 h-3"
                          />
                          <span>Visible</span>
                        </label>
                      </div>
                      <div className="flex items-center space-x-2">
                        <Button
                          type="button"
                          onClick={() => moveEvent(event.event_id, 'up')}
                          disabled={index === 0}
                          variant="ghost"
                          size="sm"
                          className="h-7 w-7 p-0"
                        >
                          <ChevronUp className="w-4 h-4" />
                        </Button>
                        <Button
                          type="button"
                          onClick={() => moveEvent(event.event_id, 'down')}
                          disabled={index === formData.events.length - 1}
                          variant="ghost"
                          size="sm"
                          className="h-7 w-7 p-0"
                        >
                          <ChevronDown className="w-4 h-4" />
                        </Button>
                        <Button
                          type="button"
                          onClick={() => deleteEvent(event.event_id)}
                          variant="ghost"
                          size="sm"
                          className="h-7 text-red-600 hover:bg-red-50"
                        >
                          Delete
                        </Button>
                      </div>
                    </div>

                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">
                          Event Name *
                        </label>
                        <input
                          type="text"
                          value={event.name}
                          onChange={(e) => updateEvent(event.event_id, 'name', e.target.value)}
                          placeholder="e.g., Mehendi Ceremony"
                          className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm"
                          required
                        />
                      </div>

                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">
                          Event Date *
                        </label>
                        <input
                          type="date"
                          value={event.date}
                          onChange={(e) => updateEvent(event.event_id, 'date', e.target.value)}
                          className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm"
                          required
                        />
                      </div>

                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">
                          Start Time *
                        </label>
                        <input
                          type="time"
                          value={event.start_time}
                          onChange={(e) => updateEvent(event.event_id, 'start_time', e.target.value)}
                          className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm"
                          required
                        />
                      </div>

                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">
                          End Time
                        </label>
                        <input
                          type="time"
                          value={event.end_time}
                          onChange={(e) => updateEvent(event.event_id, 'end_time', e.target.value)}
                          className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm"
                        />
                      </div>

                      <div className="md:col-span-2">
                        <label className="block text-sm font-medium text-gray-700 mb-1">
                          Venue Name *
                        </label>
                        <input
                          type="text"
                          value={event.venue_name}
                          onChange={(e) => updateEvent(event.event_id, 'venue_name', e.target.value)}
                          placeholder="e.g., Grand Ballroom, Hotel Name"
                          className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm"
                          required
                        />
                      </div>

                      <div className="md:col-span-2">
                        <label className="block text-sm font-medium text-gray-700 mb-1">
                          Venue Address *
                        </label>
                        <input
                          type="text"
                          value={event.venue_address}
                          onChange={(e) => updateEvent(event.event_id, 'venue_address', e.target.value)}
                          placeholder="Full address"
                          className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm"
                          required
                        />
                      </div>

                      <div className="md:col-span-2">
                        <label className="block text-sm font-medium text-gray-700 mb-1">
                          Google Maps Link *
                        </label>
                        <input
                          type="url"
                          value={event.map_link}
                          onChange={(e) => updateEvent(event.event_id, 'map_link', e.target.value)}
                          placeholder="https://maps.google.com/..."
                          className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm"
                          required
                        />
                      </div>

                      <div className="md:col-span-2">
                        <label className="block text-sm font-medium text-gray-700 mb-1">
                          Description (max 200 chars)
                        </label>
                        <textarea
                          value={event.description}
                          onChange={(e) => updateEvent(event.event_id, 'description', e.target.value)}
                          maxLength={200}
                          rows={2}
                          placeholder="Optional description of the event"
                          className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm"
                        />
                        <p className="text-xs text-gray-500 mt-1">{event.description?.length || 0}/200</p>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}

            <Button
              type="button"
              onClick={addEvent}
              disabled={formData.events.length >= 7}
              variant="outline"
              className="w-full border-gray-300 hover:bg-gray-50"
            >
              + Add Event {formData.events.length > 0 && `(${formData.events.length}/7)`}
            </Button>
          </Card>

          {/* Custom Text Overrides (Collapsible) */}
          <Card className="p-6">
            <div 
              onClick={() => setShowCustomText(!showCustomText)}
              className="flex items-center justify-between cursor-pointer"
            >
              <div>
                <h2 className="text-xl font-semibold text-gray-800">Customize Text (Optional)</h2>
                <p className="text-sm text-gray-600 mt-1">Override default text templates for enabled languages</p>
              </div>
              {showCustomText ? <ChevronUp className="w-5 h-5" /> : <ChevronDown className="w-5 h-5" />}
            </div>
            
            {showCustomText && (
              <div className="mt-6 space-y-6">
                {formData.enabled_languages.map((lang) => {
                  const langConfig = LANGUAGES.find(l => l.code === lang);
                  return (
                    <div key={lang} className="border-t pt-4">
                      <h3 className="text-lg font-semibold text-gray-800 mb-3">
                        {langConfig?.name} ({langConfig?.nativeName})
                      </h3>
                      <div className="space-y-3">
                        <div>
                          <label className="block text-sm font-medium text-gray-700 mb-1">
                            Opening Title
                          </label>
                          <input
                            type="text"
                            value={formData.custom_text[lang]?.opening_title || ''}
                            onChange={(e) => handleCustomTextChange(lang, 'opening_title', e.target.value)}
                            placeholder="Leave empty to use default"
                            className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm focus:ring-2 focus:ring-rose-500"
                          />
                        </div>
                        <div>
                          <label className="block text-sm font-medium text-gray-700 mb-1">
                            Welcome Message
                          </label>
                          <textarea
                            value={formData.custom_text[lang]?.welcome_message || ''}
                            onChange={(e) => handleCustomTextChange(lang, 'welcome_message', e.target.value)}
                            placeholder="Leave empty to use default"
                            rows="2"
                            className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm focus:ring-2 focus:ring-rose-500"
                          />
                        </div>
                        <div>
                          <label className="block text-sm font-medium text-gray-700 mb-1">
                            Footer Thank You Message
                          </label>
                          <input
                            type="text"
                            value={formData.custom_text[lang]?.footer_thankyou || ''}
                            onChange={(e) => handleCustomTextChange(lang, 'footer_thankyou', e.target.value)}
                            placeholder="Leave empty to use default"
                            className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm focus:ring-2 focus:ring-rose-500"
                          />
                        </div>
                      </div>
                    </div>
                  );
                })}
              </div>
            )}
          </Card>

          {/* Link Expiry */}
          <Card className="p-6">
            <h2 className="text-xl font-semibold text-gray-800 mb-4">Link Expiry Settings</h2>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Expiry Duration *
                </label>
                <select
                  value={getExpiryPreset()}
                  onChange={handleExpiryPresetChange}
                  required
                  className="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-rose-500 focus:border-rose-500"
                >
                  <option value="1day">1 Day</option>
                  <option value="7days">7 Days</option>
                  <option value="30days">30 Days (Default)</option>
                  <option value="custom">Custom</option>
                </select>
              </div>

              {getExpiryPreset() === 'custom' && (
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Type *
                    </label>
                    <select
                      name="link_expiry_type"
                      value={formData.link_expiry_type}
                      onChange={handleChange}
                      required
                      className="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-rose-500 focus:border-rose-500"
                    >
                      <option value="hours">Hours</option>
                      <option value="days">Days</option>
                    </select>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Duration *
                    </label>
                    <input
                      type="number"
                      name="link_expiry_value"
                      value={formData.link_expiry_value}
                      onChange={handleChange}
                      required
                      min="1"
                      className="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-rose-500 focus:border-rose-500"
                    />
                  </div>
                </div>
              )}
            </div>
          </Card>

          {/* Error Message */}
          {error && (
            <div className="bg-red-50 border border-red-200 text-red-600 px-4 py-3 rounded-md">
              {error}
            </div>
          )}

          {/* Generated Link Display */}
          {savedProfile && (
            <Card className="p-6 bg-green-50 border-green-200">
              <h3 className="text-lg font-semibold text-green-800 mb-2">✓ Profile Saved Successfully!</h3>
              <p className="text-sm text-gray-700 mb-3">Your invitation link:</p>
              <div className="flex gap-2">
                <input
                  type="text"
                  readOnly
                  value={window.location.origin + savedProfile.invitation_link}
                  className="flex-1 px-4 py-2 bg-white border border-gray-300 rounded-md text-sm"
                />
                <Button
                  type="button"
                  onClick={handleCopyLink}
                  variant="outline"
                  className="whitespace-nowrap"
                >
                  Copy Link
                </Button>
              </div>
            </Card>
          )}

          {/* Submit */}
          <div className="flex gap-4">
            <Button
              type="submit"
              disabled={loading}
              className="flex-1 bg-rose-500 hover:bg-rose-600 text-white py-3"
            >
              <Save className="w-4 h-4 mr-2" />
              {loading ? 'Saving...' : (isEdit ? 'Update Profile' : 'Save Profile')}
            </Button>
            {(savedProfile || isEdit) && (
              <Button
                type="button"
                onClick={handlePreview}
                className="flex-1 bg-purple-500 hover:bg-purple-600 text-white py-3"
              >
                <Eye className="w-4 h-4 mr-2" />
                Preview Invitation
              </Button>
            )}
            <Button
              type="button"
              variant="outline"
              onClick={() => navigate('/admin/dashboard')}
              className="flex-1"
            >
              {savedProfile ? 'Back to Dashboard' : 'Cancel'}
            </Button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default ProfileForm;
