// Centralized API configuration
// Get API URL from environment, ensure it doesn't end with a slash
const getApiUrl = () => {
  const url = import.meta.env.VITE_API_URL || 'http://localhost:8000'
  // Remove trailing slash if present
  return url.endsWith('/') ? url.slice(0, -1) : url
}

export const API_URL = getApiUrl()

// Helper function to build API paths
export const apiPath = (path: string) => {
  // Ensure path starts with /
  const cleanPath = path.startsWith('/') ? path : `/${path}`
  return `${API_URL}${cleanPath}`
}

