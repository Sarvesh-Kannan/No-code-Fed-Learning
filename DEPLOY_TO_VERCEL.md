# 🚀 Deploy to Vercel & Railway - Quick Guide

Your code is now on GitHub! Follow these steps to deploy your application.

---

## ✅ What's Already Done

- ✅ Code pushed to GitHub: https://github.com/Sarvesh-Kannan/No-code-Fed-Learning.git
- ✅ Database migration script ready
- ✅ Environment variables configured for production
- ✅ Frontend configured to use environment-based API URL
- ✅ `.gitignore` properly configured
- ✅ All deployment configuration files ready

---

## 📋 Deployment Steps

### Step 1: Deploy Backend to Railway

1. **Go to Railway**
   - Visit: https://railway.app/
   - Sign in with GitHub

2. **Create New Project**
   - Click "New Project"
   - Select "Deploy from GitHub repo"
   - Choose: `Sarvesh-Kannan/No-code-Fed-Learning`
   - Railway will auto-detect it's a Python Flask app

3. **Add Environment Variables**
   
   Go to your Railway project → Variables → Add these:
   
   ```
   DATABASE_URL=postgresql://neondb_owner:npg_EBNGrL9gFSh8@ep-wandering-rice-a1g88vgs-pooler.ap-southeast-1.aws.neon.tech/neondb?sslmode=require
   
   GEMINI_API_KEY=AIzaSyAUsSQuwbnlOxyj7kXCF8AgaIYi36H5X0g
   
   JWT_SECRET_KEY=super-secret-jwt-key-change-in-production-12345
   
   FLASK_ENV=production
   ```

4. **Deploy**
   - Railway will automatically build and deploy
   - Wait for deployment to complete (~2-3 minutes)

5. **Run Database Migration**
   - Go to your Railway project
   - Click on the service
   - Go to "Settings" → "Deploy" 
   - After first deployment, run this command in Railway's terminal (if available) or via the Railway CLI:
   ```bash
   python migrate_database.py
   ```
   
   **OR** you can manually run the SQL migration:
   - Go to your Neon database dashboard
   - Open the SQL Editor
   - Run these commands:
   ```sql
   ALTER TABLE datasets ADD COLUMN IF NOT EXISTS file_data BYTEA;
   ALTER TABLE datasets ADD COLUMN IF NOT EXISTS file_size INTEGER;
   ALTER TABLE datasets ALTER COLUMN file_path DROP NOT NULL;
   ```

6. **Get Your Backend URL**
   - Railway will provide a URL like: `https://your-app.railway.app`
   - **COPY THIS URL** - you'll need it for Step 2

---

### Step 2: Deploy Frontend to Vercel

1. **Go to Vercel**
   - Visit: https://vercel.com/
   - Sign in with GitHub

2. **Import Project**
   - Click "Add New..." → "Project"
   - Select: `Sarvesh-Kannan/No-code-Fed-Learning`
   - Click "Import"

3. **Configure Project**
   
   **Framework Preset:** Next.js (auto-detected)
   
   **Environment Variables:** Add this ONE variable:
   ```
   NEXT_PUBLIC_API_URL=https://your-app.railway.app/api
   ```
   
   ⚠️ **IMPORTANT:** Replace `https://your-app.railway.app` with YOUR actual Railway URL from Step 1!

4. **Deploy**
   - Click "Deploy"
   - Vercel will build and deploy (~2-3 minutes)
   - You'll get a URL like: `https://your-app.vercel.app`

---

### Step 3: Update CORS Settings

After getting your Vercel URL, you need to allow it in the backend:

1. **Edit `app.py` on GitHub**
   - Go to: https://github.com/Sarvesh-Kannan/No-code-Fed-Learning
   - Navigate to `app.py`
   - Click the pencil icon to edit
   - Find line 29-30 (the CORS configuration)
   
   **Change from:**
   ```python
   CORS(app, resources={r"/api/*": {
       "origins": ["http://localhost:3000"],
   ```
   
   **To:**
   ```python
   CORS(app, resources={r"/api/*": {
       "origins": ["http://localhost:3000", "https://your-app.vercel.app"],
   ```
   
   ⚠️ Replace `https://your-app.vercel.app` with YOUR actual Vercel URL!

2. **Commit Changes**
   - Add commit message: "Update CORS for production"
   - Click "Commit changes"
   - Railway will auto-redeploy with new settings

---

### Step 4: Test Your Application

1. **Test Backend Health**
   - Visit: `https://your-app.railway.app/health`
   - Should show: `{"status": "healthy"}`

2. **Test Frontend**
   - Visit your Vercel URL
   - Create a new account
   - Create a project
   - Upload a dataset (use a small CSV file)
   - Configure target variable
   - Generate pipeline
   - Train model
   - View results

---

## 🎯 Quick Checklist

- [ ] Backend deployed to Railway
- [ ] Environment variables added to Railway
- [ ] Database migration completed
- [ ] Backend health check passes
- [ ] Frontend deployed to Vercel
- [ ] `NEXT_PUBLIC_API_URL` environment variable added to Vercel
- [ ] CORS updated in `app.py` with Vercel URL
- [ ] Full workflow tested (signup → upload → train → results)

---

## 🐛 Troubleshooting

### Backend Issues

**Problem:** Database connection failed
- **Fix:** Check `DATABASE_URL` in Railway environment variables
- **Fix:** Ensure Neon database is active and accessible

**Problem:** Gemini API errors
- **Fix:** Verify `GEMINI_API_KEY` is correct in Railway
- **Fix:** Check Gemini API quotas and rate limits

**Problem:** Health check returns 404
- **Fix:** Ensure Railway deployment completed successfully
- **Fix:** Check Railway logs for errors

### Frontend Issues

**Problem:** Can't connect to backend
- **Fix:** Verify `NEXT_PUBLIC_API_URL` in Vercel includes `/api` at the end
- **Fix:** Check that CORS is updated with your Vercel URL

**Problem:** 403 CORS errors in browser console
- **Fix:** Update `app.py` CORS settings with your Vercel URL
- **Fix:** Ensure Railway redeployed after CORS update

**Problem:** Build failed on Vercel
- **Fix:** Check Vercel build logs
- **Fix:** Ensure `package.json` has all dependencies
- **Fix:** Try redeploying

---

## 📊 Your URLs (Fill these in after deployment)

**Backend (Railway):**
```
https://_____________________.railway.app
```

**Frontend (Vercel):**
```
https://_____________________.vercel.app
```

**Health Check:**
```
https://_____________________.railway.app/health
```

---

## 🎉 You're Live!

Once all steps are complete, your No-Code Federated Learning application is live and accessible worldwide!

Share your Vercel URL with users to get started.

---

## 💡 Next Steps

1. **Test with real users** - Share your application
2. **Monitor performance** - Check Railway and Vercel dashboards
3. **Watch costs** - Monitor your free tier usage
4. **Update as needed** - Push changes to GitHub, both platforms auto-deploy

---

## 📞 Support Links

- [Railway Docs](https://docs.railway.app/)
- [Vercel Docs](https://vercel.com/docs)
- [Next.js Docs](https://nextjs.org/docs)
- [Neon Docs](https://neon.tech/docs)

Good luck with your deployment! 🚀

