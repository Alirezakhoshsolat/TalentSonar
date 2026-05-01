# TalentSonar

![Python](https://img.shields.io/badge/python-3.8%2B-yellow)
![Gemini API](https://img.shields.io/badge/Gemini-API-blue)
![Streamlit](https://img.shields.io/badge/streamlit-deployed-red)

Recruiting platform for HR teams. Paste a job description, Gemini API extracts the required skills and experience criteria, and the system finds and assesses candidates sourced from GitHub. Supports PDF, Word, and markdown job description uploads.

## Live Demo

[TalentSonar on HuggingFace Spaces](https://huggingface.co/spaces/parhamkhoshsolat/TalentSonar)

## Team

- Parham Khosh Solat
- Amirhosein Shahdadian

## Features

**For HR teams:**
- Create and manage job postings with customizable skill requirements and priority weights
- Upload job descriptions in PDF, Word, or markdown — Gemini API parses and structures them automatically
- Discover candidates from GitHub and review their profiles
- Track active jobs, candidates, invitations, and test completions from the HR dashboard

**Candidate assessment:**
- Generate custom questionnaires covering technical skills and soft skills
- Multiple question formats: multiple choice, text responses, rating scales
- Session-based test management with resume capability
- Available in English and Italian

## Tech Stack

- Gemini API (`google-generativeai`) — job description parsing and skill extraction
- GitHub API — candidate discovery
- Streamlit — user interface
- PyPDF2, python-docx — document parsing
- Pydantic — data validation
- JSON file storage — jobs, candidates, test results

## Project Structure

```
├── app.py                 # Main Streamlit application
├── talentsonar/           # Core package
├── modules/               # Feature modules
├── pages/                 # Streamlit pages
├── scripts/               # Utility scripts
├── test_integration.py    # Integration tests
├── .env.example           # Environment variable template
├── requirements.txt
└── README.md
```

## Local Setup

```bash
git clone https://github.com/Alirezakhoshsolat/TalentSonar.git
cd TalentSonar
pip install -r requirements.txt
cp .env.example .env
# Add your Gemini API key to .env
streamlit run app.py
```

## License

MIT
