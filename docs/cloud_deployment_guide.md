# DevForge — Free Cloud Deployment & Ad Monetization Guide

This guide details how to deploy the **DevForge Official Landing Page & Web Portal** to fast, 100% free cloud platforms (**Vercel**, **Netlify**, **GitHub Pages**, **Render**) with global CDN acceleration and **Ad Monetization (Google AdSense / Carbon Ads)**.

---

## ☁️ Free Cloud Deployment Options

### Option 1: Deploy on Vercel (Recommended for React & Vite)

Vercel provides free instant deployment with global edge CDN acceleration.

1. Go to **[https://vercel.com](https://vercel.com)** and log in with your GitHub account.
2. Click **New Project** -> Select repository **`nihar-rajput/devforge`**.
3. Set **Root Directory**: `frontend`.
4. Framework Preset: **Vite**.
5. Click **Deploy**.
   - Your website will be live globally at **`https://devforge.vercel.app`** with free SSL HTTPS!

---

### Option 2: Deploy on Netlify

Netlify provides free drag-and-drop or continuous git deployment:

1. Go to **[https://netlify.com](https://netlify.com)** and log in with GitHub.
2. Click **Add new site** -> **Import an existing project**.
3. Select **`nihar-rajput/devforge`**.
4. Set **Base directory**: `frontend`, **Build command**: `npm run build`, **Publish directory**: `dist`.
5. Click **Deploy Site**.
   - Your website will be live at **`https://devforge.netlify.app`**!

---

### Option 3: Deploy Backend API on Render.com (Free)

Deploy the backend FastAPI engine on Render:

1. Go to **[https://render.com](https://render.com)** -> Click **New +** -> **Web Service**.
2. Connect repository **`nihar-rajput/devforge`**.
3. Environment: **Docker** (or Python 3.11).
4. Build Command: `pip install -r backend/requirements.txt`.
5. Start Command: `cd backend && python -m uvicorn src.main:app --host 0.0.0.0 --port $PORT`.
6. Select **Free Tier ($0/mo)** -> Click **Create Web Service**.

---

## 💰 How to Activate Ad Monetization (Google AdSense / Carbon Ads)

DevForge includes a pre-built `<AdBanner />` React component in `frontend/src/components/landing/AdBanner.tsx`.

### 1. Google AdSense Integration:
1. Apply for Google AdSense at **[https://adsense.google.com](https://adsense.google.com)** with your live domain (`devforge.vercel.app`).
2. Add your AdSense Publisher ID in `AdBanner.tsx`:
   ```tsx
   <AdBanner type="adsense" adClient="ca-pub-XXXXXXXXXXXXXXXX" adSlot="1234567890" />
   ```

### 2. Carbon Ads / EthicalAds Integration (Developer Focused):
- Apply at **[https://ethicalads.io](https://ethicalads.io)** or **[https://carbonads.net](https://carbonads.net)**.
- Carbon Ads are developer-centric, privacy-respecting banners tailored for open-source tools.

---

## 📄 Summary of Live Website Pages
- **Hero Download Section**: Direct `.exe`, `.dmg`, `.AppImage` download buttons pointing to GitHub Release `v1.0.0`.
- **Interactive Stack Wizard**: Web-based offline zip builder and CLI snippet generator.
- **36 Tool Catalog Grid**: Live search and category filtering across all 36 plugins.
