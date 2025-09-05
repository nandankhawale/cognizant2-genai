// API Configuration
export const API_CONFIG = {
  BASE_URL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8001',
  ENDPOINTS: {
    HEALTH: '/health',
    LOAN_TYPES: '/loan-types',
    CHAT_START: '/chat/start',
    CHAT_MESSAGE: '/chat/message',
    SESSION_INFO: '/session',
    ADMIN_STATS: '/admin/stats',
    ADMIN_APPLICATIONS: '/admin/applications'
  }
};

export default API_CONFIG;