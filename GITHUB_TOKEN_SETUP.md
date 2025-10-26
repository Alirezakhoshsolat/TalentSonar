# GitHub Token Setup Guide

## 🎯 Why You Need This

Without a GitHub token, you're limited to **60 API requests per hour**. This means you can only discover about **5-10 candidates** before hitting the rate limit.

With a GitHub token, you get **5000 requests per hour** - enough to discover **500+ candidates** without issues!

---

## 🚀 Quick Setup (5 minutes)

### Step 1: Create a GitHub Token

1. **Go to GitHub Settings:**
   - Visit: https://github.com/settings/tokens
   - Or: GitHub.com → Click your profile picture → Settings → Developer settings → Personal access tokens → Tokens (classic)

2. **Generate New Token:**
   - Click **"Generate new token (classic)"**
   - Give it a descriptive name: `TalentSonar App Token`

3. **Select Permissions (Scopes):**
   - ✅ **public_repo** - Access public repositories
   - ✅ **read:user** - Read user profile data
   - ✅ **user:email** - Access user email (optional)
   
   **Note:** You only need read permissions - no write access required!

4. **Set Expiration:**
   - Choose: 30 days, 60 days, 90 days, or No expiration
   - For development: No expiration is fine
   - For production: Use 90 days and set a reminder to renew

5. **Generate Token:**
   - Click **"Generate token"** at the bottom
   - **IMPORTANT:** Copy the token immediately - you won't be able to see it again!
   - It looks like: `ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx`

---

### Step 2: Add Token to Your Project

1. **Open your `.env` file** in the project root:
   ```
   d:\work\hackathon\.env
   ```

2. **Add this line** (replace with your actual token):
   ```env
   GITHUB_TOKEN=ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
   ```

3. **Save the file**

4. **Restart the Streamlit app:**
   - Stop the current app (Ctrl+C in terminal)
   - Run again: `streamlit run app.py`

---

### Step 3: Verify It's Working

1. **Open the app** in your browser
2. **Go to "Candidate Discovery" tab**
3. **Look for the rate limit status** at the top:
   - ❌ Without token: "X/60 requests remaining"
   - ✅ With token: "X/5000 requests remaining"

4. **Try discovering candidates:**
   - You should see a much higher limit!
   - Cache will further reduce API calls

---

## 🔒 Security Best Practices

### DO:
- ✅ Keep your token in `.env` file (already in `.gitignore`)
- ✅ Never commit `.env` to GitHub
- ✅ Use tokens with minimum required permissions
- ✅ Set expiration dates for production tokens
- ✅ Revoke old tokens you're not using

### DON'T:
- ❌ Share your token publicly
- ❌ Commit tokens to version control
- ❌ Use your personal account token for production (create a bot account instead)
- ❌ Give more permissions than needed

---

## 🛠️ Troubleshooting

### Issue: "GitHub token not configured" error

**Solution:**
1. Check if `.env` file exists in project root
2. Verify the line is: `GITHUB_TOKEN=your_token_here` (no spaces, no quotes)
3. Make sure you restarted the Streamlit app after adding the token

---

### Issue: Still getting rate limit errors

**Possible causes:**
1. **Token is invalid** - Generate a new one
2. **Token expired** - Check expiration date, create new token
3. **Token permissions wrong** - Make sure `public_repo` and `read:user` are selected
4. **Multiple apps using same token** - Each app shares the rate limit

**Solution:**
- Verify token at: https://github.com/settings/tokens
- Check if it's still active and has correct scopes
- Create a new token if needed

---

### Issue: App doesn't see the token

**Solution:**
1. Check `.env` file location - must be in project root: `d:\work\hackathon\.env`
2. Check file name - must be exactly `.env` (not `env.txt` or `.env.txt`)
3. Restart the app completely (kill terminal, restart)
4. Check for spaces in the `.env` file:
   ```env
   # ❌ WRONG (has quotes and spaces)
   GITHUB_TOKEN = "ghp_xxxx"
   
   # ✅ CORRECT (no quotes, no spaces)
   GITHUB_TOKEN=ghp_xxxx
   ```

---

## 📊 Rate Limit Comparison

| Scenario | Requests/Hour | Candidates/Discovery | Use Case |
|----------|---------------|---------------------|----------|
| **No Token** | 60 | ~5-10 | Testing, Demo |
| **With Token** | 5000 | ~500+ | Production |
| **With Token + Cache** | 2500 effective | ~1000+ | Optimal |

---

## 🔄 Token Rotation (Production)

For production deployments:

1. **Create a bot GitHub account:**
   - Email: `talentsonar-bot@yourcompany.com`
   - Username: `talentsonar-bot`

2. **Generate token from bot account:**
   - Limits won't affect your personal account
   - Easier to track usage
   - Can be shared with team

3. **Set expiration to 90 days**

4. **Set calendar reminder to renew:**
   - 7 days before expiration
   - Generate new token
   - Update `.env` or deployment secrets
   - Revoke old token

---

## 🌐 Deployment (Hugging Face, Streamlit Cloud, etc.)

When deploying to a hosting platform:

1. **Don't include `.env` in your repository** (already in `.gitignore`)

2. **Add token as a secret** in your hosting platform:

   **Hugging Face Spaces:**
   - Go to: Settings → Repository secrets
   - Add secret: Name = `GITHUB_TOKEN`, Value = your token

   **Streamlit Cloud:**
   - Go to: App settings → Secrets
   - Add to secrets.toml:
     ```toml
     GITHUB_TOKEN = "ghp_xxxx"
     ```

   **Heroku:**
   - Go to: Settings → Config Vars
   - Add: KEY = `GITHUB_TOKEN`, VALUE = your token

3. **Test the deployed app** to verify token is working

---

## ✅ Checklist

Before you start using the app in production:

- [ ] GitHub token created
- [ ] Token has `public_repo` and `read:user` permissions
- [ ] Token added to `.env` file
- [ ] App restarted after adding token
- [ ] Rate limit shows 5000/hour in app
- [ ] Successfully discovered candidates
- [ ] Token safely stored (not in git)
- [ ] Token expiration set (if using for production)
- [ ] Calendar reminder for token renewal (if applicable)

---

## 🆘 Need Help?

**GitHub Token Documentation:**
https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/creating-a-personal-access-token

**TalentSonar Support:**
Check `COMPREHENSIVE_GUIDE.md` for full documentation

**Quick Test:**
Run this in your terminal to check if token works:
```bash
curl -H "Authorization: token YOUR_TOKEN_HERE" https://api.github.com/user
```
If you get your user info back, the token works!

---

**Happy Recruiting! 🎉**
