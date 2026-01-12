import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '@/context/AuthContext';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import axios from 'axios';
import { Plus, LogOut, ExternalLink, Copy, Edit, Trash2, Calendar, Clock } from 'lucide-react';

const API_URL = process.env.REACT_APP_BACKEND_URL || '';

const AdminDashboard = () => {
  const navigate = useNavigate();
  const { admin, logout } = useAuth();
  const [profiles, setProfiles] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!admin) {
      navigate('/admin/login');
    } else {
      fetchProfiles();
    }
  }, [admin]);

  const fetchProfiles = async () => {
    try {
      const response = await axios.get(`${API_URL}/api/admin/profiles`);
      setProfiles(response.data);
    } catch (error) {
      console.error('Failed to fetch profiles:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleLogout = () => {
    logout();
    navigate('/admin/login');
  };

  const copyLink = (slug) => {
    const link = `${window.location.origin}/invite/${slug}`;
    navigator.clipboard.writeText(link);
    alert('Link copied to clipboard!');
  };

  const handleDelete = async (profileId) => {
    if (!window.confirm('Are you sure you want to delete this profile?')) {
      return;
    }

    try {
      await axios.delete(`${API_URL}/api/admin/profiles/${profileId}`);
      fetchProfiles();
    } catch (error) {
      console.error('Failed to delete profile:', error);
      alert('Failed to delete profile');
    }
  };

  const getEventTypeLabel = (type) => {
    const labels = {
      marriage: 'Marriage',
      engagement: 'Engagement',
      birthday: 'Birthday'
    };
    return labels[type] || type;
  };

  const getExpiryInfo = (profile) => {
    if (profile.link_expiry_type === 'permanent') {
      return 'Permanent';
    }
    if (profile.link_expiry_date) {
      const expiryDate = new Date(profile.link_expiry_date);
      const now = new Date();
      if (expiryDate < now) {
        return 'Expired';
      }
      return `Expires ${expiryDate.toLocaleDateString()}`;
    }
    return 'N/A';
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <p className="text-gray-600">Loading...</p>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white border-b border-gray-200">
        <div className="container mx-auto px-4 py-4">
          <div className="flex justify-between items-center">
            <div>
              <h1 className="text-2xl font-bold text-gray-800">Admin Dashboard</h1>
              <p className="text-sm text-gray-600">Welcome, {admin?.email}</p>
            </div>
            <Button
              variant="outline"
              onClick={handleLogout}
              className="border-rose-500 text-rose-500 hover:bg-rose-50"
            >
              <LogOut className="w-4 h-4 mr-2" />
              Logout
            </Button>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="container mx-auto px-4 py-8">
        <div className="flex justify-between items-center mb-8">
          <h2 className="text-xl font-semibold text-gray-800">
            Invitation Profiles ({profiles.length})
          </h2>
          <Button
            onClick={() => navigate('/admin/profile/new')}
            className="bg-rose-500 hover:bg-rose-600 text-white"
          >
            <Plus className="w-4 h-4 mr-2" />
            Create New Profile
          </Button>
        </div>

        {/* Profiles Grid */}
        {profiles.length === 0 ? (
          <Card className="p-12 text-center">
            <p className="text-gray-600 mb-4">No profiles created yet</p>
            <Button
              onClick={() => navigate('/admin/profile/new')}
              className="bg-rose-500 hover:bg-rose-600 text-white"
            >
              Create Your First Profile
            </Button>
          </Card>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {profiles.map((profile) => (
              <Card key={profile.id} className="p-6 hover:shadow-lg transition-shadow">
                <div className="space-y-4">
                  {/* Header */}
                  <div>
                    <div className="flex items-start justify-between mb-2">
                      <span className="inline-block px-2 py-1 text-xs font-semibold text-rose-600 bg-rose-100 rounded">
                        {getEventTypeLabel(profile.event_type)}
                      </span>
                      {!profile.is_active && (
                        <span className="text-xs text-gray-500">Inactive</span>
                      )}
                    </div>
                    <h3 className="text-lg font-bold text-gray-800">
                      {profile.groom_name} & {profile.bride_name}
                    </h3>
                  </div>

                  {/* Details */}
                  <div className="space-y-2 text-sm text-gray-600">
                    <div className="flex items-center">
                      <Calendar className="w-4 h-4 mr-2" />
                      {new Date(profile.event_date).toLocaleDateString()}
                    </div>
                    <div className="flex items-center">
                      <Clock className="w-4 h-4 mr-2" />
                      {getExpiryInfo(profile)}
                    </div>
                    <div className="text-xs text-gray-500">
                      Language: {Array.isArray(profile.language) ? profile.language.join(', ') : profile.language}
                    </div>
                  </div>

                  {/* Actions */}
                  <div className="pt-4 border-t border-gray-200 space-y-2">
                    <div className="flex gap-2">
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => window.open(`/invite/${profile.slug}`, '_blank')}
                        className="flex-1"
                      >
                        <ExternalLink className="w-4 h-4 mr-1" />
                        View
                      </Button>
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => copyLink(profile.slug)}
                        className="flex-1"
                      >
                        <Copy className="w-4 h-4 mr-1" />
                        Copy
                      </Button>
                    </div>
                    <div className="flex gap-2">
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => navigate(`/admin/profile/${profile.id}/edit`)}
                        className="flex-1"
                      >
                        <Edit className="w-4 h-4 mr-1" />
                        Edit
                      </Button>
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => handleDelete(profile.id)}
                        className="flex-1 text-red-600 hover:bg-red-50"
                      >
                        <Trash2 className="w-4 h-4 mr-1" />
                        Delete
                      </Button>
                    </div>
                  </div>
                </div>
              </Card>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default AdminDashboard;
