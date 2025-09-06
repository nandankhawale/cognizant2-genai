"use client";

import { useState, useEffect } from 'react';
import AdminStats from '@/components/admin/AdminStats';
import AdminApplications from '@/components/admin/AdminApplications';
import AdminExports from '@/components/admin/AdminExports';

export default function AdminPage() {
  const [activeTab, setActiveTab] = useState('stats');
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    // Simulate loading
    setTimeout(() => setIsLoading(false), 1000);
  }, []);

  const tabs = [
    { id: 'stats', name: 'Statistics', icon: '📊' },
    { id: 'applications', name: 'Applications', icon: '📋' },
    { id: 'exports', name: 'Reports', icon: '📄' }
  ];

  if (isLoading) {
    return (
      <div className="min-h-screen bg-[#000049] flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-white"></div>
          <p className="text-white mt-4">Loading Admin Dashboard...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-[#000049]">
      {/* Header */}
      <div className="bg-[#000066] shadow-lg">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-6">
            <div>
              <h1 className="text-3xl font-bold text-white">🏦 Loan Admin Dashboard</h1>
              <p className="text-blue-200 mt-1">Manage and monitor loan applications</p>
            </div>
            <div className="text-right">
              <p className="text-blue-200 text-sm">Last updated: {new Date().toLocaleString()}</p>
            </div>
          </div>
        </div>
      </div>

      {/* Navigation Tabs */}
      <div className="bg-[#000055]">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <nav className="flex space-x-8">
            {tabs.map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`py-4 px-1 border-b-2 font-medium text-sm ${
                  activeTab === tab.id
                    ? 'border-blue-400 text-blue-400'
                    : 'border-transparent text-gray-300 hover:text-white hover:border-gray-300'
                }`}
              >
                <span className="mr-2">{tab.icon}</span>
                {tab.name}
              </button>
            ))}
          </nav>
        </div>
      </div>

      {/* Content */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {activeTab === 'stats' && <AdminStats />}
        {activeTab === 'applications' && <AdminApplications />}
        {activeTab === 'exports' && <AdminExports />}
      </div>
    </div>
  );
}