import React, { useState, useEffect } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { useAuth } from '@/context/AuthContext';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import axios from 'axios';
import { ArrowLeft, Save } from 'lucide-react';

const API_URL = process.env.REACT_APP_BACKEND_URL || '';

const ProfileForm = () => {
  const navigate = useNavigate();
  const { profileId } = useParams();
  const { admin } = useAuth();
  const isEdit = !!profileId;

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const [formData, setFormData] = useState({
    groom_name: '',
    bride_name: '',
    event_type: 'marriage',
    event_date: '',
    venue: '',
    language: ['english'],
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
    }
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
        language: profile.language,
        link_expiry_type: profile.link_expiry_type,
        link_expiry_value: profile.link_expiry_value || '',
        sections_enabled: profile.sections_enabled
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

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      const submitData = {
        ...formData,
        event_date: new Date(formData.event_date).toISOString(),
        link_expiry_value: formData.link_expiry_value ? parseInt(formData.link_expiry_value) : 30
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
      <div className="container mx-auto px-4 py-8 max-w-3xl">
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

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Language *
                </label>
                <select
                  name="language"
                  value={formData.language}
                  onChange={handleChange}
                  required
                  className="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-rose-500 focus:border-rose-500"
                >
                  <option value="english">English</option>
                  <option value="telugu">Telugu</option>
                  <option value="hindi">Hindi</option>
                  <option value="tamil">Tamil</option>
                </select>
              </div>
            </div>
          </Card>

          {/* Link Expiry */}
          <Card className="p-6">
            <h2 className="text-xl font-semibold text-gray-800 mb-4">Link Expiry Settings</h2>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Expiry Type *
                </label>
                <select
                  name="link_expiry_type"
                  value={formData.link_expiry_type}
                  onChange={handleChange}
                  required
                  className="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-rose-500 focus:border-rose-500"
                >
                  <option value="permanent">Permanent</option>
                  <option value="hours">Hours</option>
                  <option value="days">Days</option>
                </select>
              </div>

              {formData.link_expiry_type !== 'permanent' && (
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Duration ({formData.link_expiry_type}) *
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
              )}
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

          {/* Error Message */}
          {error && (
            <div className="bg-red-50 border border-red-200 text-red-600 px-4 py-3 rounded-md">
              {error}
            </div>
          )}

          {/* Submit */}
          <div className="flex gap-4">
            <Button
              type="submit"
              disabled={loading}
              className="flex-1 bg-rose-500 hover:bg-rose-600 text-white py-3"
            >
              <Save className="w-4 h-4 mr-2" />
              {loading ? 'Saving...' : (isEdit ? 'Update Profile' : 'Create Profile')}
            </Button>
            <Button
              type="button"
              variant="outline"
              onClick={() => navigate('/admin/dashboard')}
              className="flex-1"
            >
              Cancel
            </Button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default ProfileForm;
