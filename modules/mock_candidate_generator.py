"""
Mock Candidate Generator
Alternative to GitHub scraping when rate limits are hit
Generates realistic candidate profiles for testing and demo purposes
"""

import random
from datetime import datetime, timedelta


class MockCandidateGenerator:
    """Generate realistic mock candidates based on job requirements"""
    
    def __init__(self):
        self.first_names = [
            "Sarah", "Michael", "Emily", "David", "Jessica", "James", "Linda", "Robert",
            "Maria", "William", "Jennifer", "John", "Patricia", "Richard", "Lisa", "Thomas",
            "Nancy", "Christopher", "Karen", "Daniel", "Betty", "Matthew", "Sandra", "Anthony",
            "Ashley", "Mark", "Donna", "Donald", "Carol", "Steven", "Michelle", "Paul"
        ]
        
        self.last_names = [
            "Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis",
            "Rodriguez", "Martinez", "Hernandez", "Lopez", "Gonzalez", "Wilson", "Anderson",
            "Thomas", "Taylor", "Moore", "Jackson", "Martin", "Lee", "Thompson", "White",
            "Harris", "Sanchez", "Clark", "Ramirez", "Lewis", "Robinson", "Walker", "Young"
        ]
        
        self.tech_skills = {
            "python": ["Django", "Flask", "FastAPI", "Pandas", "NumPy", "TensorFlow", "PyTorch"],
            "javascript": ["React", "Vue", "Angular", "Node.js", "Express", "Next.js", "TypeScript"],
            "java": ["Spring", "Hibernate", "Maven", "Android", "Spring Boot"],
            "c#": [".NET", "ASP.NET", "Unity", "Xamarin"],
            "go": ["Gin", "Echo", "gRPC", "Docker"],
            "rust": ["Actix", "Rocket", "Tokio"],
            "ruby": ["Rails", "Sinatra"],
            "php": ["Laravel", "Symfony", "WordPress"],
            "swift": ["iOS", "SwiftUI", "UIKit"],
            "kotlin": ["Android", "Spring"],
        }
        
        self.cloud_platforms = ["AWS", "Azure", "GCP", "DigitalOcean", "Heroku"]
        self.databases = ["PostgreSQL", "MySQL", "MongoDB", "Redis", "Elasticsearch", "DynamoDB"]
        self.devops_tools = ["Docker", "Kubernetes", "Jenkins", "GitLab CI", "GitHub Actions", "Terraform"]
        self.soft_skills = ["Leadership", "Communication", "Problem Solving", "Team Collaboration", "Time Management"]
        
        self.locations = [
            "San Francisco, CA", "New York, NY", "Seattle, WA", "Austin, TX", "Boston, MA",
            "Los Angeles, CA", "Chicago, IL", "Denver, CO", "Portland, OR", "Atlanta, GA",
            "Remote", "Remote (US)", "Remote (Worldwide)"
        ]
        
        self.companies = [
            "Tech Startup Inc", "Innovation Labs", "Cloud Solutions Co", "Data Analytics Group",
            "AI Research Institute", "Mobile App Studio", "Enterprise Software Corp", "Open Source Foundation",
            "Freelance", "Independent Consultant", "E-commerce Platform", "FinTech Solutions"
        ]
        
        self.project_templates = [
            "E-commerce Platform with {tech}",
            "Real-time Chat Application using {tech}",
            "Machine Learning Model for {domain}",
            "RESTful API with {tech}",
            "Mobile App for {domain}",
            "Data Pipeline using {tech}",
            "Cloud Infrastructure on {cloud}",
            "Analytics Dashboard with {tech}",
            "Authentication System using {tech}",
            "Microservices Architecture with {tech}"
        ]
        
        self.domains = [
            "Healthcare", "Finance", "Education", "E-commerce", "Social Media",
            "IoT", "Gaming", "Transportation", "Real Estate", "Travel"
        ]
    
    def generate_candidates(self, job_requirements, num_candidates=10):
        """
        Generate mock candidates based on job requirements
        
        Args:
            job_requirements (dict): Job analysis with technical skills, experience, etc.
            num_candidates (int): Number of candidates to generate
            
        Returns:
            List of candidate dictionaries
        """
        candidates = []
        required_skills = job_requirements.get('technical', [])
        required_experience = job_requirements.get('experience_years', 3)
        
        for i in range(num_candidates):
            candidate = self._generate_single_candidate(required_skills, required_experience, i)
            candidates.append(candidate)
        
        return candidates
    
    def _generate_single_candidate(self, required_skills, required_experience, index):
        """Generate a single realistic candidate profile"""
        
        # Basic info
        first_name = random.choice(self.first_names)
        last_name = random.choice(self.last_names)
        name = f"{first_name} {last_name}"
        username = f"{first_name.lower()}{last_name.lower()}{random.randint(1, 999)}"
        
        # Experience (varied around requirement)
        experience_variance = random.randint(-1, 3)
        years_experience = max(1, required_experience + experience_variance)
        
        # Skills - include some required skills plus random others
        candidate_skills = []
        
        # Add some required skills (60-100% match)
        if required_skills:
            num_matching = random.randint(
                max(1, int(len(required_skills) * 0.6)),
                len(required_skills)
            )
            candidate_skills.extend(random.sample(required_skills, num_matching))
        
        # Add related framework/library skills
        for skill in candidate_skills[:3]:
            skill_lower = skill.lower()
            for lang, frameworks in self.tech_skills.items():
                if lang in skill_lower:
                    candidate_skills.extend(random.sample(frameworks, random.randint(1, 3)))
                    break
        
        # Add cloud/database/devops skills
        candidate_skills.append(random.choice(self.cloud_platforms))
        candidate_skills.extend(random.sample(self.databases, random.randint(1, 2)))
        candidate_skills.extend(random.sample(self.devops_tools, random.randint(1, 2)))
        
        # Remove duplicates and limit
        candidate_skills = list(set(candidate_skills))[:12]
        
        # Generate projects
        num_projects = random.randint(3, 8)
        projects = []
        for _ in range(num_projects):
            template = random.choice(self.project_templates)
            project_name = template.format(
                tech=random.choice(candidate_skills),
                cloud=random.choice(self.cloud_platforms),
                domain=random.choice(self.domains)
            )
            projects.append(project_name)
        
        # GitHub-style metrics
        github_stars = random.randint(10, 500)
        github_repos = random.randint(5, 50)
        github_contributions = random.randint(50, 2000)
        
        # Bio
        bios = [
            f"Full-stack developer with {years_experience}+ years of experience",
            f"Passionate {random.choice(candidate_skills)} developer",
            f"Building scalable solutions at {random.choice(self.companies)}",
            f"Open source contributor | {random.choice(candidate_skills)} enthusiast",
            f"Senior engineer specializing in {', '.join(random.sample(candidate_skills, 2))}"
        ]
        
        # Create candidate profile
        candidate = {
            'id': 1000 + index,  # Start from 1000 to avoid conflicts
            'name': name,
            'username': username,
            'skills': candidate_skills,
            'years_experience': years_experience,
            'github_contributions': github_contributions,
            'portfolio_projects': projects[:5],
            'recent_certifications': random.randint(0, 3),
            'status': 'Not Invited',
            'source': 'Mock Data (Demo)',
            'profile_url': f'https://github.com/{username}',
            'avatar_url': f'https://i.pravatar.cc/150?u={username}',
            'location': random.choice(self.locations),
            'company': random.choice(self.companies),
            'bio': random.choice(bios),
            'email': f'{username}@example.com',
            'hireable': random.choice([True, False]),
            'created_at': (datetime.now() - timedelta(days=random.randint(365*2, 365*10))).isoformat(),
            'github_stats': {
                'repos': github_repos,
                'stars': github_stars,
                'followers': random.randint(10, 500),
                'following': random.randint(10, 300)
            },
            'soft_skills_score': random.randint(65, 95),
            'activity_level': random.choice(['Very Active', 'Active', 'Moderate']),
            'last_active': (datetime.now() - timedelta(days=random.randint(1, 30))).isoformat(),
        }
        
        # Generate mock GitHub analysis for TalentMatcher
        candidate['github_analysis'] = {
            'username': username,
            'profile': {
                'name': name,
                'bio': candidate['bio'],
                'company': candidate['company'],
                'location': candidate['location'],
                'email': candidate['email'],
                'public_repos': github_repos,
                'followers': candidate['github_stats']['followers'],
                'hireable': candidate['hireable'],
                'profile_url': candidate['profile_url']
            },
            'statistics': {
                'total_repos': github_repos,
                'original_repos': int(github_repos * 0.7),
                'total_stars': github_stars,
                'total_code_bytes': random.randint(100000, 5000000)
            },
            'languages': {
                skill: {
                    'bytes': random.randint(10000, 500000),
                    'percentage': random.uniform(5, 40)
                }
                for skill in candidate_skills[:5]
            },
            'technologies': candidate_skills,
            'repositories': [
                {
                    'name': proj,
                    'description': f'A project built with {random.choice(candidate_skills)}',
                    'language': random.choice(candidate_skills),
                    'stars': random.randint(0, 100),
                    'forks': random.randint(0, 20)
                }
                for proj in projects[:10]
            ]
        }
        
        return candidate
    
    def generate_diverse_pool(self, num_candidates=20):
        """Generate a diverse pool of candidates without specific job requirements"""
        
        # Create varied "job requirements" to generate diverse candidates
        common_tech = ["Python", "JavaScript", "Java", "TypeScript", "React", "Node.js", "AWS"]
        
        candidates = []
        for i in range(num_candidates):
            # Random requirements for each candidate
            random_skills = random.sample(common_tech, random.randint(2, 4))
            random_exp = random.randint(1, 8)
            
            fake_requirements = {
                'technical': random_skills,
                'experience_years': random_exp
            }
            
            candidate = self._generate_single_candidate(random_skills, random_exp, i)
            candidates.append(candidate)
        
        return candidates


# Singleton instance
mock_generator = MockCandidateGenerator()
