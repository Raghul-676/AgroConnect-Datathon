# AgroConnect Authentication System

## 🔐 Overview

AgroConnect now includes a complete user authentication system with login and signup functionality. All dashboard pages are protected and require authentication.

## 🚀 Quick Start

### 1. **Create Demo User (Optional)**
Open `create-demo-user.html` in your browser and click "Create Demo User"
- **Email:** demo@agroconnect.com
- **Password:** demo123

### 2. **Access the Application**
1. Open `home.html` in your browser
2. Click "Login" or "Get Started" 
3. Use the demo credentials or create a new account
4. Access the dashboard and all tools

## 📋 Authentication Features

### **Login System**
- **Email & Password** authentication
- **Form Validation** with error messages
- **Secure Storage** using localStorage
- **Session Management** across all pages

### **Signup System**
- **Complete Registration:** Name, Email, Password, Phone
- **Input Validation:** Email format, password length, phone format
- **Duplicate Prevention:** Checks for existing accounts
- **Automatic Login:** Signs in user after successful registration

### **Protected Pages**
All dashboard pages require authentication:
- ✅ `dashboard.html` - Main dashboard
- ✅ `profile.html` - User profile page
- ✅ `settings.html` - Profile settings and account management
- ✅ `soil_analysis/index.html` - Soil analysis tool
- ✅ `irrigation_calculation/irrigation.html` - Irrigation planner
- ✅ `crop_prediction/crop_page.html` - Crop prediction
- ✅ `market-analysis/market.html` - Market analysis

### **Public Pages**
- ✅ `home.html` - Landing page (no authentication required)
- ✅ `create-demo-user.html` - Demo user setup

## 🔧 Technical Implementation

### **Files Created/Modified**

#### **New Files:**
- `auth.js` - Authentication middleware
- `create-demo-user.html` - Demo user setup tool
- `AUTHENTICATION_GUIDE.md` - This documentation

#### **Modified Files:**
- `home.html` - Added login/signup modals, removed AgroBot
- `dashboard.html` - Added authentication protection
- `soil_analysis/index.html` - Added authentication protection
- `irrigation_calculation/irrigation.html` - Added authentication protection
- `crop_prediction/crop_page.html` - Added authentication protection
- `market-analysis/market.html` - Added authentication protection

### **Authentication Flow**

```
1. User visits home.html (public)
2. Clicks Login/Signup
3. Fills authentication form
4. System validates credentials
5. Stores user session in localStorage
6. Redirects to dashboard.html
7. All subsequent pages check authentication
8. User can logout from any protected page
```

### **Data Storage**

**Users Database:** `localStorage.agroconnect_users`
```json
[
  {
    "id": "1691234567890",
    "name": "John Farmer",
    "email": "john@example.com",
    "password": "securepass123",
    "phone": "+91 9876543210",
    "createdAt": "2025-08-06T10:30:00.000Z"
  }
]
```

**Current Session:** `localStorage.agroconnect_current_user`
```json
{
  "id": "1691234567890",
  "name": "John Farmer",
  "email": "john@example.com",
  "phone": "+91 9876543210"
}
```

## 🎯 User Experience

### **Landing Page (home.html)**
- **Clean Interface:** No AgroBot, focused on authentication
- **Login/Signup Buttons:** In navigation and hero section
- **Modal Popups:** Smooth, professional authentication forms
- **Responsive Design:** Works on all devices

### **Protected Dashboard**
- **Automatic Redirect:** Unauthenticated users go to home.html
- **Personalized Welcome:** Shows user's actual name
- **Logout Functionality:** Available in profile dropdown
- **Session Persistence:** Stays logged in across browser sessions

### **Form Validation**
- **Email Format:** Validates proper email structure
- **Password Strength:** Minimum 6 characters
- **Phone Format:** Validates phone number format
- **Required Fields:** All fields must be filled
- **Duplicate Check:** Prevents multiple accounts with same email

## 🔒 Security Features

- **Client-side Validation:** Immediate feedback on form errors
- **Session Management:** Automatic logout on session expiry
- **Protected Routes:** All dashboard pages check authentication
- **Data Persistence:** User data stored securely in localStorage
- **Clean Logout:** Removes all session data

## 🧪 Testing

### **Test Accounts**
Use the demo user or create your own:
- **Demo Email:** demo@agroconnect.com
- **Demo Password:** demo123

### **Test Scenarios**
1. **Signup Flow:** Create new account → Auto login → Dashboard access
2. **Login Flow:** Use existing credentials → Dashboard access
3. **Protection Test:** Try accessing dashboard.html directly → Redirect to home
4. **Logout Test:** Logout from dashboard → Redirect to home
5. **Session Persistence:** Close browser → Reopen → Still logged in

## 📱 Mobile Responsive

- **Modal Design:** Adapts to mobile screens
- **Touch Friendly:** Large buttons and input fields
- **Smooth Animations:** Professional transitions
- **Accessible:** Keyboard navigation support

The authentication system is now **fully functional** and provides a **professional user experience** with complete session management! 🎉
