/**
 * AgroConnect Authentication System
 * Simple client-side authentication using localStorage
 */

// Check if user is authenticated
function checkAuthentication() {
  const currentUser = localStorage.getItem('agroconnect_current_user');
  if (!currentUser) {
    // Redirect to home page if not logged in
    window.location.href = getHomePath();
    return false;
  }
  
  // Update user name in the interface if elements exist
  const user = JSON.parse(currentUser);
  updateUserInterface(user);
  
  return true;
}

// Update user interface with current user data
function updateUserInterface(user) {
  const profileElements = document.querySelectorAll('.profile');
  const welcomeElements = document.querySelectorAll('.welcome');
  
  profileElements.forEach(el => {
    el.textContent = `${user.name} 👨‍🌾`;
  });
  
  welcomeElements.forEach(el => {
    el.textContent = `👋 Welcome back, ${user.name}!`;
  });
}

// Get current user data
function getCurrentUser() {
  const currentUser = localStorage.getItem('agroconnect_current_user');
  return currentUser ? JSON.parse(currentUser) : null;
}

// Logout functionality
function logout() {
  localStorage.removeItem('agroconnect_current_user');
  window.location.href = getHomePath();
}

// Get path to home.html based on current location
function getHomePath() {
  const currentPath = window.location.pathname;
  if (currentPath.includes('/')) {
    // If in a subdirectory, go up one level
    return '../home.html';
  }
  return 'home.html';
}

// Initialize authentication check when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
  // Only check authentication if not on home page
  if (!window.location.pathname.includes('home.html')) {
    checkAuthentication();
  }
});

// Show Profile function (can be used on any page)
function showProfile() {
  const user = getCurrentUser();
  if (user) {
    const memberSince = user.createdAt ? new Date(user.createdAt).toLocaleDateString() : 'Unknown';
    alert(`Profile Information:\n\n👤 Name: ${user.name}\n📧 Email: ${user.email}\n📱 Phone: ${user.phone}\n📅 Member Since: ${memberSince}\n🆔 User ID: ${user.id}`);
  } else {
    alert('No user profile found');
  }
}

// Export functions for global use
window.checkAuthentication = checkAuthentication;
window.getCurrentUser = getCurrentUser;
window.logout = logout;
window.updateUserInterface = updateUserInterface;
window.showProfile = showProfile;
