# MetaFlex Dashboard - Authentication Guide

## Overview
The MetaFlex Dashboard now has a fully functional login/logout system using `streamlit-authenticator`.

## Login Credentials

### Pre-configured Users:

1. **Téa Phillips (Admin)**
   - Email: `tea@metaflexglove.com`
   - Password: `met1`
   - Role: Administrator (full access)

2. **Jess Lewis**
   - Email: `jess@metaflexglove.com`
   - Password: `met4`
   - Role: Team member with view-all-tasks permission

3. **Megan Cole**
   - Email: `megan@metaflexglove.com`
   - Password: `met2`
   - Role: Marketing team member

4. **Justin Stehr**
   - Email: `justin@metaflexglove.com`
   - Password: `met3`
   - Role: Team member

## How It Works

### Login Process
1. When you access the dashboard, you'll see a login form
2. Enter your email and password
3. Upon successful authentication, you'll gain access to the dashboard
4. Your session is stored in a secure cookie (valid for 30 days)

### Logout Process
1. Click the **"Logout"** button in the top-right corner of the navigation bar
2. The `authenticator.logout()` method will:
   - Clear your authentication session
   - Delete the authentication cookie
   - Redirect you back to the login screen

### Session Management
- Sessions are stored securely using encrypted cookies
- Cookie expiration: 30 days
- Cookie name: `metaflex_auth`
- Cookie key (secret): `7eb707cb9ec9120e9f9ef0edb40dbb3b`

## Technical Details

### Files Modified
- **[dashboard.py](dashboard.py)** - Added authentication logic and functional logout button
  - Lines 7-9: Imported authentication modules (`yaml`, `streamlit_authenticator`)
  - Lines 18-43: Authentication setup and login form
  - Lines 151-154: Functional logout button using `authenticator.logout()`

### Configuration File
- **[config.yaml](config.yaml)** - Stores user credentials and cookie settings
  - User passwords are hashed using bcrypt
  - Never store plain text passwords

### Dependencies Installed
- `streamlit-authenticator==0.4.2`
- `bcrypt>=3.1.7` (password hashing)
- `PyJWT>=2.3.0` (JSON Web Tokens)
- `cryptography>=42.0.5` (encryption)

## Adding New Users

To add a new user, you need to:

1. Generate a hashed password using bcrypt:
```python
import bcrypt
password = "your_password_here"
hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
print(hashed.decode())
```

2. Add the user to `config.yaml`:
```yaml
credentials:
  usernames:
    newemail@metaflexglove.com:
      email: newemail@metaflexglove.com
      name: New User Name
      password: "$2b$12$HASHED_PASSWORD_HERE"
      admin: false
```

3. Add the email to the preauthorized list:
```yaml
preauthorized:
  emails:
    - newemail@metaflexglove.com
```

## Security Notes

- All passwords are hashed using bcrypt (cannot be reversed)
- Sessions use encrypted cookies
- Authentication state is stored in Streamlit's session state
- The app prevents access to protected pages without authentication

## Testing the System

1. **Start the app:**
   ```bash
   streamlit run dashboard.py
   ```

2. **Login:**
   - Use any of the credentials listed above
   - Example: `tea@metaflexglove.com` / `met1`

3. **Test logout:**
   - Click the coral-colored "LOGOUT" button in the top-right
   - Verify you're redirected to the login screen
   - Verify you cannot access the dashboard without logging in again

## Troubleshooting

### "Module not found: streamlit_authenticator"
```bash
pip3 install streamlit-authenticator
```

### "File not found: config.yaml"
- Ensure `config.yaml` is in the same directory as `dashboard.py`

### Login not working
- Check that the email and password match exactly what's in `config.yaml`
- Passwords are case-sensitive
- Email addresses must match exactly (including the domain)

### Logout button not clearing session
- This has been fixed by using `authenticator.logout()` instead of manual session clearing
- The authenticator properly handles cookie deletion and session state reset

## What Changed

### Before:
```python
if st.button("Logout", key="nav_logout", use_container_width=True):
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.rerun()
```
❌ **Problem:** This only cleared session state but didn't handle authentication cookies properly

### After:
```python
if st.button("Logout", key="nav_logout", use_container_width=True):
    # Use authenticator's logout method to properly clear authentication
    authenticator.logout()
    st.rerun()
```
✅ **Solution:** Uses the official `authenticator.logout()` method which properly clears both session state AND authentication cookies

## Access Control

User access is controlled through the `ACCESS_SCOPE` variable in [pages/dashboard_page.py](pages/dashboard_page.py):

```python
ACCESS_SCOPE = {
    "Téa Phillips": "all",  # Full access
    "Jess Lewis": {"exclude": ["Finance"]},  # All except Finance
    "Megan Cole": ["Marketing"],  # Only Marketing
    "Justin Stehr": ["Marketing", "Products"],  # Only Marketing & Products
}
```

This controls what data each user can see once logged in.
