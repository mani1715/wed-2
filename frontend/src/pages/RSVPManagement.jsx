import React, { useEffect, useState } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { useAuth } from '@/context/AuthContext';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import axios from 'axios';
import { ArrowLeft, Download, Filter, Users, CheckCircle, XCircle, HelpCircle } from 'lucide-react';

const API_URL = process.env.REACT_APP_BACKEND_URL || '';

const RSVPManagement = () => {
  const navigate = useNavigate();
  const { profileId } = useParams();
  const { admin } = useAuth();
  const [rsvps, setRsvps] = useState([]);
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState('all');
  const [profileInfo, setProfileInfo] = useState(null);

  useEffect(() => {
    if (!admin) {
      navigate('/admin/login');
      return;
    }
    fetchData();
  }, [admin, profileId, filter]);

  const fetchData = async () => {
    try {
      // Fetch profile info
      const profileResponse = await axios.get(`${API_URL}/api/admin/profiles/${profileId}`);
      setProfileInfo(profileResponse.data);

      // Fetch RSVPs with optional filter
      const filterParam = filter !== 'all' ? `?status=${filter}` : '';
      const rsvpsResponse = await axios.get(`${API_URL}/api/admin/profiles/${profileId}/rsvps${filterParam}`);
      setRsvps(rsvpsResponse.data);

      // Fetch stats
      const statsResponse = await axios.get(`${API_URL}/api/admin/profiles/${profileId}/rsvps/stats`);
      setStats(statsResponse.data);
    } catch (error) {
      console.error('Failed to fetch RSVP data:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleExport = async () => {
    try {
      const response = await axios.get(
        `${API_URL}/api/admin/profiles/${profileId}/rsvps/export`,
        {
          responseType: 'blob'
        }
      );

      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `rsvps_${profileId}.csv`);
      document.body.appendChild(link);
      link.click();
      link.remove();
    } catch (error) {
      console.error('Failed to export RSVPs:', error);
      alert('Failed to export RSVPs');
    }
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case 'yes':
        return <CheckCircle className="w-5 h-5 text-green-600" />;
      case 'no':
        return <XCircle className="w-5 h-5 text-red-600" />;
      case 'maybe':
        return <HelpCircle className="w-5 h-5 text-yellow-600" />;
      default:
        return null;
    }
  };

  const getStatusLabel = (status) => {
    switch (status) {
      case 'yes':
        return 'Attending';
      case 'no':
        return 'Not Attending';
      case 'maybe':
        return 'Maybe';
      default:
        return status;
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'yes':
        return 'text-green-600 bg-green-50';
      case 'no':
        return 'text-red-600 bg-red-50';
      case 'maybe':
        return 'text-yellow-600 bg-yellow-50';
      default:
        return 'text-gray-600 bg-gray-50';
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <p className="text-gray-600">Loading RSVPs...</p>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="container mx-auto px-4 py-8">
        {/* Header */}
        <div className="mb-8">
          <Button
            variant="ghost"
            onClick={() => navigate('/admin/dashboard')}
            className="mb-4"
          >
            <ArrowLeft className="w-4 h-4 mr-2" />
            Back to Dashboard
          </Button>

          <div className="flex justify-between items-start">
            <div>
              <h1 className="text-3xl font-bold text-gray-800">RSVP Management</h1>
              {profileInfo && (
                <p className="text-gray-600 mt-2">
                  {profileInfo.groom_name} & {profileInfo.bride_name} - {new Date(profileInfo.event_date).toLocaleDateString()}
                </p>
              )}
            </div>
            <Button onClick={handleExport} className="bg-rose-600 hover:bg-rose-700 text-white">
              <Download className="w-4 h-4 mr-2" />
              Export CSV
            </Button>
          </div>
        </div>

        {/* Statistics */}
        {stats && (
          <div className="grid grid-cols-1 md:grid-cols-5 gap-4 mb-8">
            <Card className="p-6 text-center">
              <div className="text-3xl font-bold text-gray-800">{stats.total_rsvps}</div>
              <div className="text-sm text-gray-600 mt-1">Total RSVPs</div>
            </Card>
            <Card className="p-6 text-center bg-green-50">
              <div className="text-3xl font-bold text-green-600">{stats.attending_count}</div>
              <div className="text-sm text-gray-600 mt-1">Attending</div>
            </Card>
            <Card className="p-6 text-center bg-red-50">
              <div className="text-3xl font-bold text-red-600">{stats.not_attending_count}</div>
              <div className="text-sm text-gray-600 mt-1">Not Attending</div>
            </Card>
            <Card className="p-6 text-center bg-yellow-50">
              <div className="text-3xl font-bold text-yellow-600">{stats.maybe_count}</div>
              <div className="text-sm text-gray-600 mt-1">Maybe</div>
            </Card>
            <Card className="p-6 text-center bg-blue-50">
              <div className="text-3xl font-bold text-blue-600">{stats.total_guest_count}</div>
              <div className="text-sm text-gray-600 mt-1">
                <Users className="w-4 h-4 inline mr-1" />
                Total Guests
              </div>
            </Card>
          </div>
        )}

        {/* Filter */}
        <div className="mb-6 flex gap-2">
          <Button
            onClick={() => setFilter('all')}
            variant={filter === 'all' ? 'default' : 'outline'}
            className={filter === 'all' ? 'bg-rose-600 text-white' : ''}
          >
            <Filter className="w-4 h-4 mr-2" />
            All ({stats?.total_rsvps || 0})
          </Button>
          <Button
            onClick={() => setFilter('yes')}
            variant={filter === 'yes' ? 'default' : 'outline'}
            className={filter === 'yes' ? 'bg-green-600 text-white' : ''}
          >
            Attending ({stats?.attending_count || 0})
          </Button>
          <Button
            onClick={() => setFilter('no')}
            variant={filter === 'no' ? 'default' : 'outline'}
            className={filter === 'no' ? 'bg-red-600 text-white' : ''}
          >
            Not Attending ({stats?.not_attending_count || 0})
          </Button>
          <Button
            onClick={() => setFilter('maybe')}
            variant={filter === 'maybe' ? 'default' : 'outline'}
            className={filter === 'maybe' ? 'bg-yellow-600 text-white' : ''}
          >
            Maybe ({stats?.maybe_count || 0})
          </Button>
        </div>

        {/* RSVP List */}
        <Card className="p-6">
          <h2 className="text-xl font-semibold text-gray-800 mb-4">
            {filter === 'all' ? 'All RSVPs' : `${getStatusLabel(filter)} RSVPs`}
          </h2>
          
          {rsvps.length === 0 ? (
            <p className="text-gray-500 text-center py-8">No RSVPs found</p>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Guest Name
                    </th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Phone
                    </th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Status
                    </th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Guests
                    </th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Message
                    </th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Submitted
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {rsvps.map((rsvp) => (
                    <tr key={rsvp.id} className="hover:bg-gray-50">
                      <td className="px-4 py-4 whitespace-nowrap">
                        <div className="text-sm font-medium text-gray-900">{rsvp.guest_name}</div>
                      </td>
                      <td className="px-4 py-4 whitespace-nowrap">
                        <div className="text-sm text-gray-500">{rsvp.guest_phone}</div>
                      </td>
                      <td className="px-4 py-4 whitespace-nowrap">
                        <span className={`inline-flex items-center px-3 py-1 rounded-full text-xs font-medium ${getStatusColor(rsvp.status)}`}>
                          {getStatusIcon(rsvp.status)}
                          <span className="ml-1">{getStatusLabel(rsvp.status)}</span>
                        </span>
                      </td>
                      <td className="px-4 py-4 whitespace-nowrap">
                        <div className="text-sm text-gray-900">
                          {rsvp.status === 'yes' ? rsvp.guest_count : '-'}
                        </div>
                      </td>
                      <td className="px-4 py-4">
                        <div className="text-sm text-gray-500 max-w-xs truncate">
                          {rsvp.message || '-'}
                        </div>
                      </td>
                      <td className="px-4 py-4 whitespace-nowrap">
                        <div className="text-sm text-gray-500">
                          {new Date(rsvp.created_at).toLocaleDateString()}
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </Card>
      </div>
    </div>
  );
};

export default RSVPManagement;
