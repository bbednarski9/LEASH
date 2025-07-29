import React, { useState, useEffect } from 'react';
import { User, Heart, Clock, Award } from 'lucide-react';
import { useAuth } from '../Auth/AuthProvider';
import type { Pet } from '../../services/api';
import { apiService } from '../../services/api';

const ProfilePanel: React.FC = () => {
  const { user } = useAuth();
  const [pets, setPets] = useState<Pet[]>([]);
  const [loading, setLoading] = useState(false);
  const [expandedPet, setExpandedPet] = useState<string | null>(null);

  useEffect(() => {
    loadPetProfiles();
  }, []);

  const loadPetProfiles = async () => {
    setLoading(true);
    try {
      const petProfiles = await apiService.getPetProfiles();
      setPets(petProfiles);
    } catch (error) {
      console.error('Error loading pet profiles:', error);
    } finally {
      setLoading(false);
    }
  };

  const togglePetExpansion = (petId: string) => {
    setExpandedPet(expandedPet === petId ? null : petId);
  };



  return (
    <div className="bg-white rounded-lg shadow-sm p-6 mb-6">
      <h2 className="text-xl font-semibold text-gray-900 mb-6 flex items-center space-x-2">
        <User className="w-5 h-5 text-blue-600" />
        <span>Profile Information</span>
      </h2>

      {/* User Information */}
      {user && (
        <div className="mb-6 p-4 bg-blue-50 rounded-lg">
          <h3 className="font-medium text-gray-900 mb-3">Owner Details</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <span className="text-sm text-gray-600">Name:</span>
              <p className="font-medium">{user.name}</p>
            </div>
            <div>
              <span className="text-sm text-gray-600">Email:</span>
              <p className="font-medium">{user.email}</p>
            </div>
            <div>
              <span className="text-sm text-gray-600">Yard Access:</span>
              <p className="font-medium">{user['yard-access'] ? 'Yes' : 'No'}</p>
            </div>
            <div>
              <span className="text-sm text-gray-600">Exercise Level:</span>
              <p className="font-medium capitalize">{user['exercise-level']}</p>
            </div>
            <div className="md:col-span-2">
              <span className="text-sm text-gray-600">Preferred Walk Times:</span>
              <p className="font-medium">{user['preferred-walk-times'].join(', ')}</p>
            </div>
          </div>
        </div>
      )}

      {/* Pet Information */}
      <div>
        <h3 className="font-medium text-gray-900 mb-4 flex items-center space-x-2">
          <Heart className="w-4 h-4 text-pink-500" />
          <span>Your Pets ({pets.length})</span>
        </h3>

        {loading ? (
          <div className="text-center py-4">
            <div className="inline-flex items-center space-x-2 text-gray-600">
              <div className="w-4 h-4 border-2 border-blue-500 border-t-transparent rounded-full animate-spin"></div>
              <span>Loading pet profiles...</span>
            </div>
          </div>
        ) : pets.length === 0 ? (
          <div className="text-center py-8 text-gray-500">
            <Heart className="w-12 h-12 mx-auto mb-3 text-gray-300" />
            <p>No pet profiles found</p>
          </div>
        ) : (
          <div className="space-y-4">
            {pets.map((pet) => (
              <div key={pet.id} className="border border-gray-200 rounded-lg p-4">
                <div 
                  className="flex items-center justify-between cursor-pointer"
                  onClick={() => togglePetExpansion(pet.id)}
                >
                  <div className="flex items-center space-x-3">
                    <div className="w-10 h-10 bg-gradient-to-br from-pink-400 to-purple-500 rounded-full flex items-center justify-center">
                      <span className="text-white font-bold text-lg">
                        {pet.name.charAt(0).toUpperCase()}
                      </span>
                    </div>
                    <div>
                      <h4 className="font-semibold text-gray-900">{pet.name}</h4>
                      <p className="text-sm text-gray-600">{pet.breed} • {pet.age}</p>
                    </div>
                  </div>
                  <div className="text-right">
                    <p className="text-sm text-gray-600">Energy: {pet['energy-level']}</p>
                    <p className="text-xs text-gray-500">{pet.weight}</p>
                  </div>
                </div>

                {expandedPet === pet.id && (
                  <div className="mt-4 pt-4 border-t border-gray-100">
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      <div>
                        <span className="text-sm text-gray-600">Gender:</span>
                        <p className="font-medium capitalize">{pet.gender}</p>
                      </div>
                      <div>
                        <span className="text-sm text-gray-600">Color:</span>
                        <p className="font-medium">{pet.color}</p>
                      </div>
                      <div>
                        <span className="text-sm text-gray-600">Training Level:</span>
                        <p className="font-medium capitalize">{pet['training-level']}</p>
                      </div>
                      <div>
                        <span className="text-sm text-gray-600 flex items-center space-x-1">
                          <Clock className="w-3 h-3" />
                          <span>Daily Walk Time:</span>
                        </span>
                        <p className="font-medium">{pet['walk-time-per-day']}</p>
                      </div>
                    </div>

                    {pet['favorite-activities'].length > 0 && (
                      <div className="mt-4">
                        <span className="text-sm text-gray-600 flex items-center space-x-1 mb-2">
                          <Award className="w-3 h-3" />
                          <span>Favorite Activities:</span>
                        </span>
                        <div className="flex flex-wrap gap-2">
                          {pet['favorite-activities'].map((activity) => (
                            <span
                              key={activity}
                              className="px-2 py-1 bg-blue-100 text-blue-800 text-xs rounded-full"
                            >
                              {activity}
                            </span>
                          ))}
                        </div>
                      </div>
                    )}

                    {pet.current_medications.length > 0 && (
                      <div className="mt-4">
                        <span className="text-sm text-gray-600 mb-2 block">Current Medications:</span>
                        <div className="space-y-2">
                          {pet.current_medications.map((med, index) => (
                            <div key={index} className="p-3 bg-yellow-50 rounded-lg border border-yellow-200">
                              <div className="flex justify-between items-start">
                                <div>
                                  <p className="font-medium text-gray-900">{med.name}</p>
                                  <p className="text-sm text-gray-600">
                                    {med['mg-per-serving']}mg, {med['count-per-day']}x daily
                                  </p>
                                  {med['give-with-food'] && (
                                    <p className="text-xs text-orange-600">Give with food</p>
                                  )}
                                </div>
                              </div>
                              {med.notes && (
                                <p className="text-xs text-gray-600 mt-2">{med.notes}</p>
                              )}
                            </div>
                          ))}
                        </div>
                      </div>
                    )}

                    {pet['behavioral-notes'] && (
                      <div className="mt-4">
                        <span className="text-sm text-gray-600 mb-2 block">Behavioral Notes:</span>
                        <p className="text-sm text-gray-800 bg-gray-50 p-3 rounded-lg">
                          {pet['behavioral-notes']}
                        </p>
                      </div>
                    )}

                    {pet['dietary-restrictions'].length > 0 && (
                      <div className="mt-4">
                        <span className="text-sm text-gray-600 mb-2 block">Dietary Restrictions:</span>
                        <div className="flex flex-wrap gap-2">
                          {pet['dietary-restrictions'].map((restriction) => (
                            <span
                              key={restriction}
                              className="px-2 py-1 bg-red-100 text-red-800 text-xs rounded-full"
                            >
                              {restriction}
                            </span>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                )}
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default ProfilePanel; 