# Google Analytics 4 Setup for Daily Dossier

## Steps to Create GA4 Property:

1. Go to: https://analytics.google.com/
2. Log in with Pool Hall Pros Google account (drew@poolhallpros.com)
3. Click "Admin" (bottom left)
4. Click "+ Create Property"
5. Property name: "Daily Business Dossier"
6. Time zone: Pacific Time (US)
7. Currency: USD
8. Click "Next"
9. Industry: "News & Media" or "Business Services"
10. Business size: "Small"
11. Click "Create"
12. Data stream: "Web"
13. Website URL: https://diamonddeals.github.io
14. Stream name: "Daily Dossier"
15. Copy the Measurement ID (format: G-XXXXXXXXXX)

## After Getting Measurement ID:

Run: `python3 add_google_analytics.py G-XXXXXXXXXX`
