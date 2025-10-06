# 🚀 Deployment Guide - Vercel (Frontend + Backend)

## Overview
This guide shows you how to deploy your No-Code Federated Learning application to Vercel completely free.

## ✅ What's Ready
- ✅ Files stored in Neon PostgreSQL (no local storage)
- ✅ Authentication working
- ✅ Federated learning (multiple users, project codes)
- ✅ Feature importance normalized
- ✅ All redundant files removed

---

## 📋 Prerequisites
1. GitHub account
2. Vercel account (sign up at https://vercel.com)
3. Your Neon database connection string (already in `config.py`)

---

## Step 1: Push to GitHub

### 1.1 Create GitHub Repository
1. Go to https://github.com/new
2. Name it: `nocode-federated-learning` (or your choice)
3. **DON'T** initialize with README
4. Click "Create repository"

### 1.2 Push Your Code
```bash
cd "C:\Users\User\Desktop\No code builder"

# Initialize git (if not done)
git init

# Add all files
git add .

# Commit
git commit -m "Initial commit - No-Code Federated Learning MVP"

# Add remote (replace YOUR_USERNAME with your GitHub username)
git remote add origin https://github.com/YOUR_USERNAME/nocode-federated-learning.git

# Push
git push -u origin main
```

**If `main` branch doesn't exist, try:**
```bash
git branch -M main
git push -u origin main
```

---

## Step 2: Deploy Backend to Vercel

### 2.1 Create Backend Deployment

1. Go to https://vercel.com/new
2. Click "Import Project"
3. Select your GitHub repository
4. **IMPORTANT:** Configure as follows:

**Project Settings:**
- **Framework Preset:** Other
- **Build Command:** Leave empty
- **Output Directory:** Leave empty
- **Install Command:** `pip install -r requirements.txt`
- **Root Directory:** ./ (root)

### 2.2 Add Environment Variables

Click "Environment Variables" and add these:

```
DATABASE_URL = postgresql://neondb_owner:npg_bHR7VTgl5eKv@ep-broad-brook-a13kxylc-pooler.ap-southeast-1.aws.neon.tech/neondb?sslmode=require

SECRET_KEY = your-new-secret-key-generate-a-random-string-here

GEMINI_API_KEY = AIzaSyAUsSQuwbnlOxyj7kXCF8AgaIYi36H5X0g
```

**To generate SECRET_KEY:**
```python
import secrets
print(secrets.token_hex(32))
```

### 2.3 Deploy!
- Click "Deploy"
- Wait 2-3 minutes
- Your backend URL will be: `https://your-project-name.vercel.app`

---

## Step 3: Configure Frontend

### 3.1 Update Frontend API URL

**Edit `src/lib/api.ts`:**
```typescript
// Change this line:
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:5000';

// To:
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'https://your-backend.vercel.app';
```

**Or better, add environment variable in Vercel:**

1. In Vercel dashboard, go to your project
2. Settings → Environment Variables
3. Add:
   ```
   NEXT_PUBLIC_API_URL = https://your-backend.vercel.app
   ```

### 3.2 Redeploy
```bash
git add src/lib/api.ts
git commit -m "Update API URL for production"
git push
```

Vercel will auto-deploy!

---

## Step 4: Test Your Deployment

### 4.1 Access Your App
- Frontend: `https://your-project.vercel.app`
- Backend API: `https://your-backend.vercel.app/api/projects`

### 4.2 Test Functionality
1. **Signup:** Create a new account
2. **Create Project:** Make a new project, note the code
3. **Upload Dataset:** Upload housing.csv (<1 MB)
4. **Configure:** Set target variable
5. **Generate Pipeline:** Should work!
6. **Train Models:** Should complete in 3-5 seconds
7. **View Results:** Check feature importance is normalized

### 4.3 Test Federated Learning
1. **User 2:** Create another account
2. **Join Project:** Use the project code from User 1
3. **Upload Dataset:** User 2 uploads their own dataset
4. **Train:** User 2 trains their own models
5. **Verify:** Both users see their own results separately

---

## 🔧 Troubleshooting

### Issue: "Module not found" error
**Solution:** Make sure `requirements.txt` is complete:
```bash
# Check if all imports are listed
cat requirements.txt
```

### Issue: "Database connection failed"
**Solution:** 
1. Check `DATABASE_URL` is correct in Vercel env vars
2. Make sure Neon database is running
3. Test connection from Neon dashboard

### Issue: "CORS error" in browser
**Solution:** Update `app.py`:
```python
# Change CORS config
ALLOWED_ORIGINS = [
    'http://localhost:3000',
    'https://your-frontend.vercel.app'
]
CORS(app, origins=ALLOWED_ORIGINS)
```

### Issue: Files not persisting
**Solution:** Already fixed! Files are stored in Neon database now.

### Issue: "504 Gateway Timeout" during training
**Solution:** Vercel free tier has 10-second timeout for serverless functions.
For model training, consider:
1. Use Railway instead (no timeout)
2. Or optimize model training to complete faster

---

## Alternative: Deploy Backend to Railway

If Vercel timeout is an issue, use Railway for backend:

### Railway Deployment
1. Go to https://railway.app/
2. "New Project" → "Deploy from GitHub"
3. Select your repository
4. Add same environment variables
5. Railway will auto-detect Python and deploy!
6. Update frontend `NEXT_PUBLIC_API_URL` to Railway URL

**Railway Advantages:**
- No timeout (trains models fine)
- Better for compute-heavy operations
- Still free tier available

---

## 📊 Final Architecture

```
User Browser
    ↓
Vercel (Frontend)
https://your-app.vercel.app
    ↓ API calls
Vercel (Backend) or Railway
https://your-backend.vercel.app
    ↓ Store/Retrieve
Neon PostgreSQL
(Files stored in database)
```

---

## ✅ Post-Deployment Checklist

- [ ] Backend deployed and accessible
- [ ] Frontend deployed and accessible
- [ ] Environment variables set correctly
- [ ] Database connection working
- [ ] User signup/login working
- [ ] Project creation working
- [ ] File upload working (stored in Neon)
- [ ] Model training working
- [ ] Feature importance showing correctly
- [ ] Federated learning working (multiple users)

---

## 🎉 You're Live!

Your application is now online and accessible to anyone!

Share your project:
- Frontend URL: `https://your-app.vercel.app`
- Users can signup, create projects, and train models
- Completely serverless and scalable!

---

## 💰 Cost

**Current Setup:**
- Neon PostgreSQL: FREE (0.5 GB)
- Vercel Frontend: FREE (unlimited)
- Vercel Backend: FREE (100GB bandwidth)
- **Total: $0/month** 🎉

**When to Upgrade:**
- Neon: When you exceed 0.5 GB → $19/month
- Vercel: Stays free for most use cases

---

## 🔒 Security Notes

1. **Never commit `.env` files** to GitHub
2. **Rotate SECRET_KEY** in production
3. **Monitor API usage** (Gemini free tier limits)
4. **Add rate limiting** if you get many users

---

## 📞 Need Help?

- Vercel Docs: https://vercel.com/docs
- Railway Docs: https://docs.railway.app/
- Neon Docs: https://neon.tech/docs

---

## 🚀 Next Steps (Optional)

1. **Custom Domain:** Add your own domain in Vercel settings
2. **Analytics:** Add Vercel Analytics
3. **Monitoring:** Set up Sentry for error tracking
4. **Scaling:** Upgrade Neon if needed

Good luck with your deployment! 🎉

