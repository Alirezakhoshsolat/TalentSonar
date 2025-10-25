# TalentSonar - AI-Powered HR & Talent Sourcing Engine

A sophisticated Python engine that combines AI-powered job analysis with GitHub talent sourcing to help HR professionals, recruiters, and hiring managers find, analyze, and rank the best candidates.

## 🌟 Key Features

### Job Analysis Engine
- **AI-Powered Analysis**: Uses Google Gemini 2.5 Flash for intelligent job description parsing
- **Comprehensive Extraction**: Identifies technical skills, soft skills, education, experience, and more
- **Structured Output**: Returns well-organized JSON with categorized requirements
- **Requirement Classification**: Automatically categorizes as "required", "preferred", or "nice-to-have"

### GitHub Talent Sourcing (NEW! 🎯)
- **Profile Scraping**: Extract skills and experience from GitHub profiles and repositories
- **Smart Matching**: AI-powered matching of candidates against job requirements
- **Intelligent Scoring**: Multi-factor scoring system (technical skills, experience, activity, etc.)
- **Auto-Search**: Automatically find candidates based on job requirements
- **Ranking System**: Rank candidates by overall fit score (0-100)

## 🚀 Quick Start

### Installation

1. **Clone the repository:**
   ```bash
   git clone <your-repo-url>
   cd talentsonar
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure API keys:**
   ```bash
   cp .env.template .env
   # Edit .env and add your keys:
   # GEMINI_API_KEY=your_gemini_key
   # GITHUB_TOKEN=your_github_token (optional but recommended)
   ```

## 💼 Usage

### 1. Analyze Job Descriptions
   # Edit .env and add your Google Gemini API key
   ```

## Quick Start

### 1. Get Your Google Gemini API Key

1. Visit [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Create a new API key
3. Add it to your `.env` file:
   ```
   GEMINI_API_KEY=your_api_key_here
   ```

### 2. Basic Usage

**Analyze a job description file:**
```bash
python main.py --input examples/sample_job_description.txt --output analysis.json
```

**Analyze text directly:**
```bash
python main.py --text "Software Engineer position requiring Python, React, 5+ years experience..." --output result.json
```

### 2. Source and Rank GitHub Talent (NEW! 🎯)

**Auto-search for candidates matching job requirements:**
```bash
python talent_pipeline.py --job-file examples/sample_job_description.txt --auto-search --top 20
```

**Manual search with custom criteria:**
```bash
python talent_pipeline.py --job-file job.txt --search "language:python location:sanfrancisco followers:>=50" --top 15
```

**Analyze specific GitHub users:**
```bash
python talent_pipeline.py --job-file job.txt --usernames torvalds gvanrossum guido --verbose
```

**Complete pipeline with results saved:**
```bash
python talent_pipeline.py --job-file job.txt --auto-search --top 20 --min-score 70 --output top_candidates.json
```

### 3. Try the Demo

```bash
python examples/talent_sourcing_demo.py
```

## 📊 Example Output

### Job Analysis
```json
{
  "job_title": "Senior Full Stack Software Engineer",
  "company": "TechCorp Inc.",
  "salary_range": "$120,000 - $180,000",
  "technical_skills": [
    {"requirement": "Python", "importance": "required"},
    {"requirement": "React", "importance": "required"},
    {"requirement": "AWS", "importance": "preferred"}
  ],
  "experience": [
    {"requirement": "Full-stack development", "years_experience": 5}
  ]
}
```

### Talent Ranking
```
#1 - @john_developer
Overall Score: 87.5/100
Profile: https://github.com/john_developer
Location: San Francisco, CA
🟢 Hireable: Yes

Score Breakdown:
  • Technical Skills: 92.0/100
  • Experience: 85.0/100  
  • Activity: 88.0/100
  • Education: 75.0/100
  • Soft Skills: 90.0/100

✅ Matched Skills (12): Python, JavaScript, React, Docker, AWS...
❌ Missing Skills (2): Kubernetes, GraphQL
⭐ Bonus Skills (8): TypeScript, Redis, PostgreSQL...
```

## 🎯 Scoring System

Candidates are scored on a 0-100 scale across five components:

| Component | Weight | What It Measures |
|-----------|--------|------------------|
| 🔧 Technical Skills | 45% | Programming languages, frameworks, tools matching job requirements |
| 📚 Experience | 20% | Years active on GitHub, repository count, code quality (stars/forks) |
| ⚡ Activity | 15% | Recent contributions, consistency, community engagement |
| 🎓 Education | 10% | Indicators from profile, bio, and quality of work |
| 🤝 Soft Skills | 10% | Documentation quality, collaboration, professional presence |

**Score Interpretation:**
- **85-100**: 🌟 Excellent fit - Reach out immediately
- **70-84**: ✅ Strong fit - Good candidate to interview
- **55-69**: 👍 Moderate fit - Worth considering
- **40-54**: ⚠️ Potential fit - May need training
- **0-39**: ❌ Weak fit - Probably not suitable

## 📚 Documentation

- **[TALENT_SOURCING.md](TALENT_SOURCING.md)** - Complete guide to GitHub talent sourcing
- **[API Reference](#api-reference)** - Programmatic usage
- **[Examples](examples/)** - Sample scripts and demos

## 🔧 Configuration

### Environment Variables (.env)

```bash
# Required
GEMINI_API_KEY=your_gemini_api_key_here

# Optional (highly recommended for talent sourcing)
GITHUB_TOKEN=your_github_personal_access_token

# Optional
OUTPUT_DIR=output
LOG_LEVEL=INFO
MAX_RETRIES=3
```

### GitHub Token Setup (Optional but Recommended)

Get higher API rate limits (5,000/hour vs 60/hour):

1. Go to https://github.com/settings/tokens
2. Click "Generate new token (classic)"
3. Select scopes: `public_repo`, `read:user`
4. Copy token and add to `.env`

##

**Interactive mode:**
```bash
python main.py --interactive
```

### 3. Programmatic Usage

```python
from src.job_analyzer import create_analyzer
from config.settings import config

# Initialize analyzer
analyzer = create_analyzer(config.gemini_api_key)

# Analyze job description
job_description = "Your job description text here..."
result = analyzer.analyze_to_json(job_description)

# Access structured data
print(f"Job Title: {result['job_title']}")
print(f"Technical Skills: {len(result['technical_skills'])}")
print(f"Required Experience: {result['experience']}")
```

## Output Format

The engine returns a comprehensive JSON structure:

```json
{
  "job_title": "Senior Software Engineer",
  "company": "TechCorp Inc.",
  "location": "San Francisco, CA",
  "employment_type": "full-time",
  "salary_range": "$120,000 - $180,000",
  "remote_work_option": true,
  
  "technical_skills": [
    {
      "category": "technical_skills",
      "requirement": "Python programming",
      "importance": "required",
      "years_experience": 5
    }
  ],
  
  "soft_skills": [
    {
      "category": "soft_skills",
      "requirement": "Strong communication skills",
      "importance": "required",
      "years_experience": null
    }
  ],
  
  "education": [
    {
      "category": "education",
      "requirement": "Bachelor's degree in Computer Science",
      "importance": "required",
      "years_experience": null
    }
  ],
  
  "experience": [
    {
      "category": "experience",
      "requirement": "Full-stack web development",
      "importance": "required",
      "years_experience": 5
    }
  ],
  
  "certifications": [
    {
      "category": "certifications", 
      "requirement": "AWS Certified Developer",
      "importance": "preferred",
      "years_experience": null
    }
  ],
  
  "responsibilities": [
    "Design and develop web applications",
    "Collaborate with cross-functional teams",
    "Mentor junior developers"
  ],
  
  "benefits": [
    "Health insurance",
    "401(k) matching", 
    "Flexible work arrangements"
  ],
  
  "company_culture": [
    "Collaborative environment",
    "Innovation-focused",
    "Work-life balance"
  ],
  
  "analysis_timestamp": "2025-10-25T10:30:00",
  "confidence_score": 0.92
}
```

## Command Line Options

```bash
python main.py [OPTIONS]

Input Options (choose one):
  --input, -i FILE        Path to job description text file
  --text, -t TEXT         Job description as text string
  --interactive           Run in interactive mode

Output Options:
  --output, -o FILE       Save results to JSON file (default: print to stdout)

Configuration:
  --api-key KEY          Override API key from environment
```

## Examples

### Example 1: Analyze Multiple Job Descriptions

```bash
# Analyze all job descriptions in a directory
for file in job_descriptions/*.txt; do
    python main.py --input "$file" --output "results/$(basename "$file" .txt)_analysis.json"
done
```

### Example 2: Batch Processing with Python

```python
import os
from src.job_analyzer import create_analyzer
from config.settings import config

analyzer = create_analyzer(config.gemini_api_key)

job_files = ['job1.txt', 'job2.txt', 'job3.txt']
for job_file in job_files:
    with open(job_file, 'r') as f:
        job_description = f.read()
    
    result = analyzer.analyze_to_json(job_description)
    
    # Save individual analysis
    output_file = f"analysis_{os.path.basename(job_file)}.json"
    analyzer.analyze_to_json(job_description, output_file)
```

### Example 3: Filter by Requirements

```python
# Find jobs requiring specific skills
def has_required_skill(analysis, skill_name):
    for skill in analysis['technical_skills']:
        if skill_name.lower() in skill['requirement'].lower() and skill['importance'] == 'required':
            return True
    return False

# Filter job analyses
python_jobs = []
for analysis_file in analysis_files:
    with open(analysis_file, 'r') as f:
        analysis = json.load(f)
    if has_required_skill(analysis, 'python'):
        python_jobs.append(analysis)
```

## Configuration

### Environment Variables

Create a `.env` file with the following variables:

```bash
# Required
GEMINI_API_KEY=your_gemini_api_key_here

# Optional
OUTPUT_DIR=output              # Default output directory
LOG_LEVEL=INFO                # Logging level (DEBUG, INFO, WARNING, ERROR)
MAX_RETRIES=3                 # Maximum API retry attempts
```

### Advanced Configuration

You can customize the analysis by modifying the prompt in `src/job_analyzer.py` or extending the `JobAnalysisResult` model with additional fields.

## API Reference

### JobAnalyzer Class

```python
class JobAnalyzer:
    def __init__(self, api_key: str)
    def analyze_job_description(self, job_description: str) -> JobAnalysisResult
    def analyze_to_json(self, job_description: str, output_file: str = None) -> dict
```

### Configuration Class

```python  
class Config:
    @property
    def gemini_api_key(self) -> str
    @property  
    def default_output_dir(self) -> str
    def validate(self) -> bool
```

## Error Handling

The engine handles various error scenarios:

- **Missing API Key**: Clear instructions for setup
- **Invalid Job Descriptions**: Graceful failure with error messages  
- **API Rate Limits**: Automatic retry with exponential backoff
- **Network Issues**: Informative error messages
- **Invalid JSON**: Fallback parsing and error reporting

## Limitations

- Requires internet connection for Gemini API calls
- Analysis quality depends on job description clarity and completeness
- API usage costs apply based on Google Gemini pricing
- Rate limits apply per Google's API terms

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/new-feature`)
3. Make your changes
4. Add tests for new functionality
5. Commit your changes (`git commit -am 'Add new feature'`)
6. Push to the branch (`git push origin feature/new-feature`)
7. Create a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

- **Issues**: Report bugs and feature requests on GitHub Issues
- **Documentation**: Check the `examples/` directory for more usage examples
- **API Questions**: Refer to [Google Gemini API documentation](https://developers.generativeai.google/)

## Changelog

### Version 1.0.0
- Initial release
- Basic job description analysis
- Support for multiple input formats
- Comprehensive requirement extraction
- Interactive and batch processing modes

---

**Made with ❤️ for HR professionals and developers**