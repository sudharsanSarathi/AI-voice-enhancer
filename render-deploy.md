# 🚀 Deploy Voice Enhancer AI to Render.com - Step by Step Guide

This guide will walk you through deploying your Voice Enhancer AI application to Render.com for free cloud hosting.

## 📋 Prerequisites

- ✅ Render.com account (free tier available)
- ✅ GitHub account with your AI-voice-enhancer repository
- ✅ Your project is already pushed to GitHub

## 🎯 Step-by-Step Deployment Process

### Step 1: Access Render Dashboard

1. **Go to Render.com**
   - Open your web browser
   - Navigate to: https://render.com
   - Click **"Sign In"** (top right corner)
   - Log in with your existing account

2. **Access Dashboard**
   - After logging in, you'll see your Render Dashboard
   - Click **"New +"** button (usually blue, top right)

### Step 2: Create New Web Service

1. **Select Service Type**
   - From the dropdown menu, select **"Web Service"**
   - You'll see a page titled "Create a new Web Service"

2. **Connect GitHub Repository**
   - Look for **"Connect a repository"** section
   - Click **"Connect GitHub"** (if not already connected)
   - Authorize Render to access your GitHub repositories
   - Search for your repository: `AI-voice-enhancer`
   - Click **"Connect"** next to your repository

### Step 3: Configure Your Web Service

Fill out the following fields exactly as shown:

#### Basic Settings:
- **Name**: `voice-enhancer-ai` (or any name you prefer)
- **Region**: Choose closest to your location (e.g., `Oregon (US West)`)
- **Branch**: `main` (should be auto-selected)
- **Root Directory**: Leave empty (blank)

#### Build & Deploy Settings:
- **Runtime**: `Python 3` (should be auto-detected)
- **Build Command**: 
  ```
  pip install -r requirements.txt
  ```
- **Start Command**: 
  ```
  python run.py
  ```

#### Advanced Settings (Click "Advanced" to expand):
- **Auto-Deploy**: `Yes` (recommended - deploys automatically when you push to GitHub)

### Step 4: Environment Variables (Important!)

1. **Scroll down to "Environment Variables" section**
2. **Click "Add Environment Variable"**
3. **Add these variables one by one:**

   **Variable 1:**
   - Key: `PORT`
   - Value: `10000`

   **Variable 2:**
   - Key: `DEBUG`
   - Value: `false`

   **Variable 3:**
   - Key: `LOG_LEVEL`
   - Value: `INFO`

   **Variable 4:**
   - Key: `PYTHON_VERSION`
   - Value: `3.9.18`

### Step 5: Choose Your Plan

1. **Select Plan Type**
   - **Free Tier**: $0/month (recommended for testing)
     - 512 MB RAM
     - Shared CPU
     - Sleeps after 15 minutes of inactivity
     - 750 hours/month free
   
   - **Starter Plan**: $7/month (recommended for production)
     - 512 MB RAM
     - Shared CPU
     - No sleeping
     - Custom domains

2. **Click "Create Web Service"**

### Step 6: Monitor Deployment

1. **Watch the Build Process**
   - Render will start building your application
   - You'll see real-time logs in the "Logs" tab
   - Build process typically takes 3-5 minutes

2. **Build Steps You'll See:**
   ```
   ==> Cloning from GitHub repository...
   ==> Installing Python dependencies...
   ==> Starting application...
   ==> Your service is live at https://your-app-name.onrender.com
   ```

3. **Wait for "Deploy succeeded" message**

### Step 7: Access Your Live Application

1. **Get Your App URL**
   - Once deployment succeeds, you'll see your app URL
   - Format: `https://voice-enhancer-ai-xxxx.onrender.com`
   - Click the URL to open your live application

2. **Test Your Application**
   - Upload an audio file
   - Adjust the intensity slider
   - Process the audio
   - Download the enhanced result

## 🔧 Troubleshooting Common Issues

### Issue 1: Build Fails - "Requirements not found"
**Solution:**
- Check that `requirements.txt` is in your repository root
- Ensure the file is properly committed to GitHub

### Issue 2: Application Won't Start
**Solution:**
- Verify your Start Command is: `python run.py`
- Check that `PORT` environment variable is set to `10000`

### Issue 3: "Module not found" Errors
**Solution:**
- Check your `requirements.txt` includes all dependencies
- Rebuild by clicking "Manual Deploy" → "Deploy latest commit"

### Issue 4: App Sleeps on Free Tier
**Solution:**
- This is normal for free tier (sleeps after 15 min inactivity)
- First request after sleep takes 30-60 seconds to wake up
- Upgrade to Starter plan ($7/month) to prevent sleeping

### Issue 5: Large File Upload Fails
**Solution:**
- Free tier has limited resources
- Consider upgrading to Starter plan for better performance
- Ensure files are under 50MB limit

## 📊 Monitoring Your Application

### View Logs:
1. Go to your Render dashboard
2. Click on your service name
3. Click "Logs" tab to see real-time application logs

### Check Performance:
1. Click "Metrics" tab to see:
   - CPU usage
   - Memory usage
   - Request count
   - Response times

### Update Your App:
1. Push changes to your GitHub repository
2. Render will automatically redeploy (if Auto-Deploy is enabled)
3. Or manually deploy by clicking "Manual Deploy"

## 🎉 Success! Your App is Live

Once deployed successfully, you can:

- **Share your app**: Send the Render URL to anyone
- **Use it anywhere**: Access from any device with internet
- **Scale up**: Upgrade plans as your usage grows
- **Custom domain**: Add your own domain name (paid plans)

## 💡 Pro Tips

1. **Keep Free Tier Active**: Visit your app occasionally to prevent extended sleeping
2. **Monitor Usage**: Check Render dashboard for usage statistics
3. **Backup Important**: Keep your GitHub repository as backup
4. **Environment Variables**: Never commit sensitive data to GitHub, use environment variables
5. **Logs are Your Friend**: Always check logs if something isn't working

## 🆘 Need Help?

If you encounter issues:
1. Check the troubleshooting section above
2. Review Render's logs for error messages
3. Ensure your GitHub repository has all necessary files
4. Contact Render support (they have excellent free support)

---

**🎵 Congratulations! Your Voice Enhancer AI is now live on the internet! 🎉**