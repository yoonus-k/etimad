# Browser Automation Configuration
# This will automatically login to Etimad and get cookies

# Set to True to enable automatic browser login
USE_BROWSER_AUTOMATION = False

# Your Etimad credentials (store securely - see security note below)
ETIMAD_USERNAME = "1026234748"  # Your email or username
ETIMAD_PASSWORD = "Mm1406M@@@"  # Your password

# Browser settings
HEADLESS_BROWSER = False  # Set True to hide browser window
BROWSER_TYPE = "chrome"  # Options: "chrome", "firefox", "edge"

# SECURITY NOTE:
# For production, use environment variables instead:
# import os
# ETIMAD_USERNAME = os.getenv('ETIMAD_USERNAME')
# ETIMAD_PASSWORD = os.getenv('ETIMAD_PASSWORD')
