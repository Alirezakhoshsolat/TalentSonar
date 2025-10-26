import os
import sys
import time
from dotenv import load_dotenv

# Ensure project root on sys.path
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

load_dotenv()

from modules.smart_recruiter import SmartRecruiter


def main():
    rec = SmartRecruiter()

    # Ensure a job with precomputed analysis to avoid LLM latency
    rec.job_postings.insert(0, {
        'title': 'Backend Engineer (Python/React)',
        'description': 'Backend engineer position',
        'analysis': {
            'technical': ['Python', 'Django', 'FastAPI', 'React', 'PostgreSQL'],
            'experience_years': 3,
        }
    })

    start = time.time()
    candidates = rec.discover_unconventional_candidates(0, max_candidates=1)
    elapsed = time.time() - start

    print(f"Discovery finished in {elapsed:.2f}s, found {len(candidates)} candidate(s)")
    if candidates:
        c = candidates[0]
        print({
            'name': c.get('name'),
            'username': c.get('username'),
            'source': c.get('source'),
            'skills': c.get('skills')[:8],
            'location': c.get('location'),
            'profile_url': c.get('profile_url'),
            'score': c.get('discovery_score', 'n/a')
        })


if __name__ == "__main__":
    main()
