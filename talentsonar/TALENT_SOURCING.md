# Talent Sourcing with GitHub - Quick Start Guide

## Overview

The TalentSonar engine now includes powerful GitHub talent sourcing capabilities that:

1. **Scrape GitHub profiles** - Extract skills, experience, and expertise from user profiles and repositories
2. **Match candidates** - Compare candidates against job requirements using AI-powered matching
3. **Score and rank** - Calculate fit scores based on technical skills, experience, activity, and more
4. **Auto-search** - Automatically find candidates based on job requirements

## How It Works

```
Job Description → AI Analysis → GitHub Search → Profile Analysis → Matching → Ranking
```

### Scoring System (0-100 points)

**Component Weights:**
- 🔧 **Technical Skills** (45%): Programming languages, frameworks, tools
- 📚 **Experience** (20%): Years active, repository count, code quality
- ⚡ **Activity** (15%): Recent contributions, consistency, engagement
- 🎓 **Education** (10%): Indicators from profile, bio, company
- 🤝 **Soft Skills** (10%): Documentation, collaboration, community engagement

## Quick Start

### 1. Setup GitHub Token (Optional but Recommended)

Get a GitHub Personal Access Token for higher API rate limits:
1. Go to https://github.com/settings/tokens
2. Click "Generate new token (classic)"
3. Select scopes: `public_repo`, `read:user`
4. Copy token and add to `.env`:

```bash
GITHUB_TOKEN=your_github_token_here
```

### 2. Basic Usage

**Auto-search for candidates:**
```bash
python talent_pipeline.py --job-file examples/sample_job_description.txt --auto-search --top 10
```

**Manual search with custom query:**
```bash
python talent_pipeline.py --job-file job.txt --search "language:python location:sanfrancisco followers:>=50" --top 20
```

**Analyze specific users:**
```bash
python talent_pipeline.py --job-file job.txt --usernames torvalds gvanrossum

 guido
```

**Use pre-analyzed job requirements:**
```bash
python talent_pipeline.py --job-analysis analysis_result.json --auto-search --top 15
```

### 3. Advanced Options

**Save results to file:**
```bash
python talent_pipeline.py --job-file job.txt --auto-search --output candidates.json
```

**Verbose output with detailed scores:**
```bash
python talent_pipeline.py --job-file job.txt --auto-search --verbose
```

**Set minimum score threshold:**
```bash
python talent_pipeline.py --job-file job.txt --auto-search --min-score 70
```

## GitHub Search Query Syntax

Build powerful search queries to find the right candidates:

### By Programming Language
```
language:python
language:javascript
language:go
```

### By Location
```
location:sanfrancisco
location:newyork
location:london
location:remote
```

### By Activity
```
followers:>=100          # At least 100 followers
repos:>=10               # At least 10 public repos
created:>2020-01-01      # Account created after date
```

### Combined Queries
```
language:python location:california followers:>=50 repos:>=10
language:javascript location:remote created:>2019-01-01
language:rust followers:>=100
```

## Example Output

```
====================================================================
RANKED CANDIDATES
====================================================================

#1 - @john_doe
Overall Score: 87.5/100
Profile: https://github.com/john_doe
Location: San Francisco, CA
🟢 Hireable: Yes

Score Breakdown:
  • Technical Skills: 92.0/100
  • Experience: 85.0/100
  • Activity: 88.0/100
  • Education: 75.0/100
  • Soft Skills: 90.0/100

  ✅ Matched Skills (15):
     - Python
     - JavaScript
     - React
     - Node.js
     - Docker
     ...

  ❌ Missing Skills (2):
     - Kubernetes
     - AWS Lambda

  ⭐ Bonus Skills (8):
     - TypeScript
     - GraphQL
     - Redis
     ...
```

## Understanding the Scores

### Technical Skills Score (0-100)
- **90-100**: Perfect match, has all required skills + many preferred
- **75-89**: Strong match, has most required skills
- **60-74**: Good match, has core skills but missing some
- **40-59**: Moderate match, has some relevant skills
- **0-39**: Weak match, missing many critical skills

### Experience Score (0-100)
Based on:
- GitHub account age (proxy for years of experience)
- Number of original repositories
- Stars received (code quality indicator)
- Forks (contribution impact)

### Activity Score (0-100)
Based on:
- Recency of latest commit
- Total number of repositories
- Community engagement (followers, forks)
- Contribution frequency

### Overall Interpretation

- **85-100**: 🌟 Excellent fit - Reach out immediately
- **70-84**: ✅ Strong fit - Good candidate to interview
- **55-69**: 👍 Moderate fit - Worth considering
- **40-54**: ⚠️ Potential fit - May need training
- **0-39**: ❌ Weak fit - Probably not suitable

## Rate Limits

**Without GitHub Token:**
- 60 API requests per hour
- ~3-5 candidate analyses per hour

**With GitHub Token:**
- 5,000 API requests per hour
- ~250+ candidate analyses per hour

Get a token at: https://github.com/settings/tokens

## Programmatic Usage

```python
from src.github_scraper import GitHubScraper
from src.talent_matcher import TalentMatcher
from src.job_analyzer import create_analyzer

# Analyze job
analyzer = create_analyzer(gemini_api_key)
job_analysis = analyzer.analyze_to_json("Senior Python Developer position...")

# Setup GitHub scraper
scraper = GitHubScraper(github_token="your_token")

# Find and analyze candidates
users = scraper.search_users("language:python location:california", max_results=20)

scored_candidates = []
matcher = TalentMatcher()

for user in users:
    # Analyze candidate
    analysis = scraper.analyze_candidate_skills(user['username'])
    
    # Match against job
    score = matcher.match_candidate(analysis, job_analysis)
    scored_candidates.append(score)

# Rank candidates
ranked = matcher.rank_candidates(scored_candidates, min_score=70)

# Top candidate
best = ranked[0]
print(f"Top candidate: @{best.username} - {best.total_score}/100")
```

## Tips for Best Results

### 1. Refine Your Search Query
- Start broad, then narrow down
- Use location filters to match job location
- Require minimum followers/repos for quality

### 2. Adjust Minimum Score
- **70+**: When you need top-tier talent
- **60+**: For standard positions
- **50+**: When willing to train/develop

### 3. Analyze More Candidates
- Default is 10, try 20-30 for better selection
- More candidates = better chance of finding perfect fit
- Watch your rate limits!

### 4. Use Verbose Mode
- See exactly why candidates scored high/low
- Identify specific skill gaps
- Make informed interview decisions

### 5. Save Results
- Keep records of candidate searches
- Compare candidates across multiple searches
- Build a talent pipeline over time

## Troubleshooting

### "Rate limit exceeded"
- Add GitHub token to `.env`
- Wait for rate limit reset
- Reduce number of candidates analyzed

### "No candidates found"
- Broaden your search criteria
- Remove location restrictions
- Lower minimum followers/repos

### "Low scores for all candidates"
- Job requirements may be too specific
- Consider "preferred" vs "required" skills
- Expand search to more candidates

## Integration Ideas

1. **Automated Talent Pipeline**: Run searches weekly, build candidate database
2. **Multi-Position Matching**: Score candidates against multiple open positions
3. **Diversity Sourcing**: Use location/bio filters for diverse candidate pools
4. **Passive Recruitment**: Monitor high-scoring candidates who aren't actively searching

## Privacy & Ethics

- **Public Data Only**: Only uses publicly available GitHub information
- **No Spam**: Do not automate direct contact without consent
- **Respectful Use**: Respect candidates' privacy and time
- **Transparent**: Be clear about how you found them

## Support

- Check GitHub API status: https://www.githubstatus.com/
- Report issues or suggestions in project issues
- See main README.md for more documentation

---

**Happy Talent Hunting! 🎯**