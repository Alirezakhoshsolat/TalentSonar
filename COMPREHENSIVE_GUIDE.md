# 🎯 TalentSonar - Comprehensive Smart Recruiting Platform

**AI-Powered Talent Discovery & Assessment System**

A complete recruiting platform that combines AI job analysis, GitHub talent sourcing, intelligent matching, and candidate assessment with anti-cheat features.

---

## ✨ Features

### 📊 HR Dashboard
- **At-a-Glance Metrics**: Total jobs, candidates, invitations, completions
- **Job-Specific Statistics**: Track candidates per job posting
- **Application Status Tracking**: See who applied, who took tests, who completed
- **Recent Activity Timeline**: Monitor platform activity in real-time

### 📝 Job Postings
- **Multiple Input Methods**:
  - Type or paste job descriptions
  - Upload files (PDF, TXT, Markdown, Word DOCX)
- **AI-Powered Analysis** (Google Gemini 2.5 Flash):
  - Automatic skill extraction
  - Experience level detection
  - Location identification
- **Editable Requirements**:
  - Review and modify extracted skills before saving
  - Adjust experience requirements
  - Set custom priority weights for matching
- **Job Management**:
  - View all jobs in thumbnail cards
  - Edit existing job requirements
  - Delete job postings
  - See candidate count per job

### 👥 Candidate Discovery
- **GitHub-Based Sourcing**:
  - Automatic candidate discovery from GitHub
  - Smart search query generation from job requirements
  - Profile and repository analysis
- **Detailed Candidate Profiles**:
  - GitHub username and profile URL
  - Location and contact info (email, LinkedIn)
  - Programming languages and technologies
  - Years of experience estimation
  - GitHub statistics (stars, repos, contributions)
  - Portfolio projects
- **Advanced Scoring System** (0-100 scale):
  - **Technical Skills** (45%): Language/framework matches
  - **Experience** (20%): Account age, repo count, stars
  - **Activity** (15%): Recent contributions, consistency
  - **Education** (10%): Profile indicators, code quality
  - **Soft Skills** (10%): Documentation, collaboration
- **Detailed Score Breakdown**:
  - Individual component scores
  - Matched skills
  - Missing skills
  - Bonus skills
- **Filtering & Extraction**:
  - Filter by minimum match score
  - Extract top N candidates
  - Send invitations directly

### 📋 Candidate Testing & Assessment
- **Dual Interface**:
  - **HR View**: Monitor all test results and candidate progress
  - **Candidate View**: Take assessments via unique invitation links

- **Personal Information Collection**:
  - Full name, email, phone
  - LinkedIn and GitHub profiles

- **Soft Skills Assessment**:
  - Standard HR-approved questions
  - Multiple choice and text responses
  - Self-rating scales
  - Customizable by HR manager

- **Technical Skills Assessment**:
  - Job-specific technical questions
  - Language-specific questions (Python, JavaScript, etc.)
  - General programming questions
  - Detailed text responses required

- **Anti-Cheat Measures**:
  - Active monitoring indicator
  - Tab/window change detection
  - Copy-paste restrictions
  - Time constraints with penalties
  - Integrity flag system

- **Automated Scoring**:
  - Soft skills score (0-100)
  - Technical skills score (0-100)
  - Overall score (average)
  - Time penalty calculation
  - Cheating penalty application

- **Results & Analytics**:
  - Identified strengths
  - Identified weaknesses
  - Detailed score breakdown
  - Test completion timestamp
  - Integrity flags

---

## 🏗️ Architecture

### Tech Stack
- **Frontend**: Streamlit (Python web framework)
- **AI Engine**: Google Gemini 2.5 Flash API
- **Data Source**: GitHub REST API
- **Document Parsing**: PyPDF2, python-docx
- **Data Validation**: Pydantic
- **Backend**: TalentSonar Engine (custom modules)

### Core Modules

#### 1. **Job Analyzer** (`talentsonar/src/job_analyzer.py`)
- AI-powered job description analysis
- Requirement extraction (skills, experience, location)
- Importance classification (required/preferred/nice-to-have)

#### 2. **GitHub Scraper** (`talentsonar/src/github_scraper.py`)
- User profile fetching
- Repository analysis
- Language proficiency calculation
- Technology stack identification
- Advanced user search

#### 3. **Talent Matcher** (`talentsonar/src/talent_matcher.py`)
- Multi-factor scoring algorithm
- Skill normalization and synonym handling
- Candidate ranking
- Detailed match reports

#### 4. **Document Parser** (`talentsonar/src/document_parser.py`)
- PDF parsing (PyPDF2)
- Word document parsing (python-docx)
- Plain text and Markdown support

#### 5. **Candidate Testing System** (`talentsonar/src/candidate_tests.py`)
- Test session management
- Question bank (soft skills + technical)
- Anti-cheat mechanisms
- Automated scoring
- Strength/weakness identification

#### 6. **Smart Recruiter** (`modules/smart_recruiter.py`)
- Integration layer between UI and core engine
- Data persistence management
- Candidate discovery orchestration

---

## 🚀 Getting Started

### Prerequisites
- Python 3.10+
- Google Gemini API Key ([Get one here](https://makersuite.google.com/app/apikey))
- GitHub Personal Access Token ([Create one here](https://github.com/settings/tokens))

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/Alirezakhoshsolat/TalentSonar.git
cd TalentSonar
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Configure environment variables**
```bash
# Copy the template
copy .env.template .env

# Edit .env and add your API keys
GEMINI_API_KEY=your_gemini_api_key_here
GITHUB_TOKEN=your_github_token_here
```

4. **Run the application**
```bash
streamlit run app.py
```

5. **Open in browser**
```
http://localhost:8501
```

---

## 📖 User Guide

### For HR/Recruiters

#### Step 1: Create a Job Posting
1. Go to **📝 Job Postings** tab
2. Click **➕ Create New Job**
3. Enter job title and company name
4. Either:
   - Type/paste the job description, OR
   - Upload a file (PDF, DOCX, TXT, MD)
5. Click **🔍 Analyze & Save Job**
6. Review extracted requirements
7. Edit skills, experience, location as needed
8. Optionally set custom priority weights
9. Click **💾 Save Job Posting**

#### Step 2: Discover Candidates
1. Go to **👥 Candidate Discovery** tab
2. Select the job posting
3. Set number of candidates to discover (5-30)
4. Click **🚀 Discover Candidates**
5. Wait for AI analysis (may take a few minutes)
6. Review discovered candidates with detailed scores

#### Step 3: Send Invitations
1. In the candidate list, click **✉️ Send Invitation**
2. Share the generated link with the candidate
3. Monitor test progress in **📋 Candidate Tests** tab

#### Step 4: Review Test Results
1. Go to **📋 Candidate Tests** tab
2. View all invited and completed tests
3. Review scores, strengths, and weaknesses
4. Check for integrity flags
5. Make hiring decisions

### For Candidates

#### Taking the Assessment
1. Click the invitation link from HR
2. Fill in personal information form
3. Complete **Soft Skills Test**:
   - Answer all questions thoughtfully
   - Provide detailed text responses (meet minimum word counts)
   - Rate yourself honestly on scales
4. Complete **Technical Test**:
   - Answer technical questions specific to the role
   - Provide detailed explanations
   - Demonstrate your knowledge
5. Submit your assessment
6. View your scores

**Important Notes:**
- ⏱️ Time limit: 45 minutes total
- 🔒 Anti-cheat is active (don't switch tabs/apps)
- 📝 Provide detailed answers (quality over speed)
- ✅ Complete at least 70% of questions to submit

---

## 🎯 Key Features Explained

### Sticky Top Navigation
- Tabs remain visible when scrolling
- Easy navigation between sections
- No data loss when switching tabs

### Complete Data Persistence
- All data stored in Streamlit session state
- Job postings persist across tabs
- Candidates remain discovered
- Test sessions are maintained
- No data loss on page refresh (within session)

### AI-Powered Analysis
- **Job Analysis**: Extracts 15+ requirement categories
- **Candidate Matching**: Multi-factor scoring (5 components)
- **Smart Search**: Automatic GitHub query generation
- **Skill Normalization**: Handles synonyms (e.g., JS = JavaScript)

### GitHub Integration
- **Profile Analysis**: Bio, location, followers, hireable status
- **Repository Analysis**: Languages, topics, stars, forks
- **Activity Metrics**: Latest commits, consistency
- **Technology Detection**: Automatic tech stack identification

### Testing System
- **Standard Questions**: HR-approved soft skill questions
- **Custom Technical**: Job-specific technical questions
- **Anti-Cheat**: Tab monitoring, copy-paste blocking, time tracking
- **Automated Scoring**: Objective, consistent evaluation
- **Detailed Feedback**: Strengths, weaknesses, score breakdown

---

## 🔧 Configuration

### Environment Variables
```bash
# Required
GEMINI_API_KEY=your_gemini_key        # Google Gemini API
GITHUB_TOKEN=your_github_token        # GitHub Personal Access Token

# Optional
OUTPUT_DIR=output                     # Default output directory
LOG_LEVEL=INFO                        # Logging level
MAX_RETRIES=3                         # API retry attempts
```

### Custom Scoring Weights
Edit in Job Posting creation:
- Technical Skills: 0-100%
- Experience: 0-100%
- GitHub Activity: 0-100%
(Must sum to 100%)

### Test Questions
Edit in `talentsonar/src/candidate_tests.py`:
- `SOFT_SKILL_QUESTIONS`: Soft skill question bank
- `TECHNICAL_QUESTIONS_POOL`: Technical question bank by language

---

## 📊 Scoring Algorithm

### Overall Candidate Score (0-100)
```
Overall = (Technical × 0.45) + (Experience × 0.20) + 
          (Activity × 0.15) + (Education × 0.10) + (Soft Skills × 0.10)
```

### Component Breakdown

**Technical Skills (45%)**
- Required skills matched
- Preferred skills matched
- Nice-to-have skills matched
- Skill synonyms recognized
- Bonus skills identified

**Experience (20%)**
- GitHub account age vs. required years
- Number of original repositories
- Total stars received

**Activity (15%)**
- Days since last activity
- Repository count
- Follower count
- Fork count

**Education (10%)**
- Profile indicators
- High-quality contributions
- Code quality metrics

**Soft Skills (10%)**
- Documentation quality
- Collaboration indicators
- Profile completeness
- Community engagement

---

## 🛠️ Extending Functionality

### Adding New Test Questions
Edit `talentsonar/src/candidate_tests.py`:

```python
SOFT_SKILL_QUESTIONS.append({
    "id": "ss_new",
    "question": "Your question here?",
    "type": "multiple_choice",  # or "text" or "scale"
    "options": ["Option 1", "Option 2"],
    "correct_answer": 0,
    "weight": 1.0
})
```

### Customizing Scoring Weights
Edit `talentsonar/src/talent_matcher.py`:

```python
self.component_weights = {
    "technical_skills": 0.50,  # Adjust these
    "experience": 0.25,
    "activity": 0.15,
    "education": 0.05,
    "soft_skills": 0.05
}
```

### Adding File Format Support
Edit `talentsonar/src/document_parser.py`:

```python
def _parse_new_format(self, file_path: str) -> str:
    # Your parsing logic
    return extracted_text
```

---

## 🐛 Troubleshooting

### "API Key not found"
- Check your `.env` file exists
- Verify `GEMINI_API_KEY` is set correctly
- Ensure no extra spaces around the key

### "GitHub token not configured"
- Add `GITHUB_TOKEN` to `.env`
- Generate a token at https://github.com/settings/tokens
- Needs `public_repo` and `read:user` scopes

### "No candidates found"
- GitHub token may have rate limits
- Try broader search criteria
- Check job requirements aren't too restrictive

### "PDF/Word parsing failed"
- Ensure PyPDF2 and python-docx are installed:
  ```bash
  pip install PyPDF2 python-docx
  ```

### "Session expired"
- Streamlit sessions expire on browser refresh
- Redeploy to Hugging Face for persistent hosting

---

## 🚀 Deployment

### Hugging Face Spaces
1. Push code to GitHub
2. Connect to Hugging Face Spaces
3. Add secrets:
   - `GEMINI_API_KEY`
   - `GITHUB_TOKEN`
4. Auto-deploys on push

### Heroku
```bash
# Create Procfile
web: sh setup.sh && streamlit run app.py

# Create setup.sh
mkdir -p ~/.streamlit/
echo "[server]
headless = true
port = $PORT
enableCORS = false
" > ~/.streamlit/config.toml

# Deploy
heroku create
git push heroku main
```

---

## 📈 Future Enhancements

- [ ] LinkedIn integration
- [ ] Automated email invitations
- [ ] Calendar integration for interviews
- [ ] Multi-language support
- [ ] Advanced analytics dashboard
- [ ] Export candidates to CSV/PDF
- [ ] Bulk candidate upload
- [ ] Interview scheduling
- [ ] Offer letter generation
- [ ] ATS integration

---

## 🤝 Contributing

We welcome contributions! Please:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

---

## 📄 License

MIT License - See LICENSE file

---

## 🙏 Acknowledgments

- **Google Gemini AI** for job analysis
- **GitHub API** for talent sourcing
- **Streamlit** for the amazing framework
- **TalentSonar Team** for the core engine

---

## 📞 Support

- 📧 Email: support@talentsonar.com
- 🐛 Issues: GitHub Issues
- 💬 Discussions: GitHub Discussions
- 📚 Docs: This README

---

**Made with ❤️ for HR professionals and developers**

*Making talent acquisition intelligent, efficient, and data-driven.*

---

## 🎯 Quick Links

- 🌐 [Live Demo](https://huggingface.co/spaces/Alirezakhs/TalentSonar)
- 📖 [Full Documentation](README.md)
- 🔧 [API Reference](talentsonar/PROJECT_SUMMARY.md)
- 🎓 [Tutorial Videos](#) (Coming Soon)
- 💼 [Enterprise Version](#) (Coming Soon)
