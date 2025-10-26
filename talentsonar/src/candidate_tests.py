"""
Candidate Testing System

Manages soft skill and technical skill assessments for candidates.
Includes anti-cheat mechanisms and scoring.
"""

import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import random


class CandidateTestSystem:
    """System for managing candidate assessments."""
    
    # Standard soft skill questions (customizable by HR)
    SOFT_SKILL_QUESTIONS = [
        {
            "id": "ss_q1",
            "question": "How do you prioritize tasks when faced with multiple deadlines?",
            "type": "multiple_choice",
            "options": [
                "I create a detailed schedule and stick to it strictly",
                "I assess urgency and importance, then prioritize accordingly",
                "I work on whatever seems most interesting first",
                "I ask my manager to prioritize for me"
            ],
            "correct_answer": 1,
            "weight": 1.0
        },
        {
            "id": "ss_q2",
            "question": "Describe a time when you had to work with a difficult team member.",
            "type": "text",
            "min_words": 50,
            "weight": 1.5
        },
        {
            "id": "ss_q3",
            "question": "How do you handle constructive criticism?",
            "type": "multiple_choice",
            "options": [
                "I take it personally and feel discouraged",
                "I listen carefully, ask questions, and use it to improve",
                "I ignore it if I disagree",
                "I defend my position aggressively"
            ],
            "correct_answer": 1,
            "weight": 1.0
        },
        {
            "id": "ss_q4",
            "question": "Rate your communication skills (1-10)",
            "type": "scale",
            "min": 1,
            "max": 10,
            "weight": 0.8
        },
        {
            "id": "ss_q5",
            "question": "How do you approach learning new technologies?",
            "type": "text",
            "min_words": 30,
            "weight": 1.2
        },
        {
            "id": "ss_q6",
            "question": "What motivates you most in your work?",
            "type": "multiple_choice",
            "options": [
                "Financial compensation and benefits",
                "Challenging problems and continuous learning",
                "Recognition and praise from colleagues",
                "Work-life balance and flexibility"
            ],
            "correct_answer": -1,  # No single correct answer
            "weight": 1.0
        },
        {
            "id": "ss_q7",
            "question": "Describe a situation where you had to adapt quickly to change.",
            "type": "text",
            "min_words": 40,
            "weight": 1.5
        },
        {
            "id": "ss_q8",
            "question": "How do you handle stress and pressure in the workplace?",
            "type": "multiple_choice",
            "options": [
                "I tend to get overwhelmed and struggle to focus",
                "I break tasks into smaller steps and stay organized",
                "I avoid stressful situations when possible",
                "I thrive under pressure and work best with tight deadlines"
            ],
            "correct_answer": 1,
            "weight": 1.0
        },
        {
            "id": "ss_q9",
            "question": "Rate your ability to work independently without supervision (1-10)",
            "type": "scale",
            "min": 1,
            "max": 10,
            "weight": 0.8
        },
        {
            "id": "ss_q10",
            "question": "Describe your approach to collaborating with team members on a complex project.",
            "type": "text",
            "min_words": 50,
            "weight": 1.5
        }
    ]
    
    # Standard technical questions (can be customized based on job)
    TECHNICAL_QUESTIONS_POOL = {
        "python": [
            {
                "id": "tech_py1",
                "question": "What is the difference between a list and a tuple in Python?",
                "type": "text",
                "min_words": 20,
                "weight": 1.0
            },
            {
                "id": "tech_py2",
                "question": "Explain the concept of decorators in Python.",
                "type": "text",
                "min_words": 30,
                "weight": 1.5
            }
        ],
        "javascript": [
            {
                "id": "tech_js1",
                "question": "Explain the difference between '==' and '===' in JavaScript.",
                "type": "text",
                "min_words": 20,
                "weight": 1.0
            },
            {
                "id": "tech_js2",
                "question": "What is a closure and give an example.",
                "type": "text",
                "min_words": 30,
                "weight": 1.5
            }
        ],
        "general": [
            {
                "id": "tech_gen1",
                "question": "Describe the difference between SQL and NoSQL databases.",
                "type": "text",
                "min_words": 30,
                "weight": 1.0
            },
            {
                "id": "tech_gen2",
                "question": "What is version control and why is it important?",
                "type": "text",
                "min_words": 25,
                "weight": 1.0
            },
            {
                "id": "tech_gen3",
                "question": "Rate your experience with cloud platforms (AWS, Azure, GCP) on a scale of 1-10",
                "type": "scale",
                "min": 1,
                "max": 10,
                "weight": 0.8
            }
        ]
    }
    
    def __init__(self):
        """Initialize the testing system."""
        self.logger = self._setup_logging()
        self.test_sessions = {}  # Store active test sessions
        self.test_results = {}  # Store completed test results
    
    def _setup_logging(self) -> logging.Logger:
        """Setup logging for the testing system."""
        logger = logging.getLogger(__name__)
        if not logger.handlers:
            handler = logging.StreamHandler()
            handler.setFormatter(logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            ))
            logger.addHandler(handler)
            logger.setLevel(logging.INFO)
        return logger
    
    def create_test_session(self, candidate_id: int, job_requirements: Dict[str, Any]) -> str:
        """
        Create a new test session for a candidate.
        
        Args:
            candidate_id (int): Candidate ID
            job_requirements (dict): Job requirements to customize technical questions
            
        Returns:
            str: Session ID
        """
        session_id = f"test_{candidate_id}_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        # Only use soft skills questions (no technical questions)
        
        session_data = {
            "session_id": session_id,
            "candidate_id": candidate_id,
            "start_time": datetime.now().isoformat(),
            "soft_skill_questions": self.SOFT_SKILL_QUESTIONS.copy(),
            "technical_questions": [],  # No technical questions
            "answers": {},
            "cheating_flags": [],
            "status": "in_progress",
            "time_limit_minutes": 45  # 45 minutes total
        }
        
        self.test_sessions[session_id] = session_data
        self.logger.info(f"Created test session {session_id} for candidate {candidate_id}")
        
        return session_id
    
    def _select_technical_questions(self, job_requirements: Dict[str, Any]) -> List[Dict]:
        """Select relevant technical questions based on job requirements."""
        selected_questions = []
        
        # Extract required skills from job
        technical_skills = job_requirements.get('technical', [])
        
        # Add language-specific questions
        for skill in technical_skills[:2]:  # Top 2 skills
            skill_lower = skill.lower()
            if 'python' in skill_lower and 'python' in self.TECHNICAL_QUESTIONS_POOL:
                selected_questions.extend(self.TECHNICAL_QUESTIONS_POOL['python'])
            elif 'javascript' in skill_lower or 'js' in skill_lower:
                if 'javascript' in self.TECHNICAL_QUESTIONS_POOL:
                    selected_questions.extend(self.TECHNICAL_QUESTIONS_POOL['javascript'])
        
        # Add general questions
        selected_questions.extend(self.TECHNICAL_QUESTIONS_POOL['general'])
        
        # Ensure we have at least 3 technical questions
        if len(selected_questions) < 3:
            selected_questions.extend(self.TECHNICAL_QUESTIONS_POOL['general'])
        
        return selected_questions[:5]  # Limit to 5 technical questions
    
    def submit_answer(
        self, 
        session_id: str, 
        question_id: str, 
        answer: Any,
        time_taken_seconds: Optional[int] = None
    ) -> bool:
        """
        Submit an answer for a question.
        
        Args:
            session_id (str): Test session ID
            question_id (str): Question ID
            answer: The answer (type depends on question type)
            time_taken_seconds (int, optional): Time taken to answer
            
        Returns:
            bool: True if submission successful
        """
        if session_id not in self.test_sessions:
            self.logger.error(f"Session {session_id} not found")
            return False
        
        session = self.test_sessions[session_id]
        
        if session['status'] != 'in_progress':
            self.logger.error(f"Session {session_id} is not active")
            return False
        
        # Store answer
        session['answers'][question_id] = {
            "answer": answer,
            "submitted_at": datetime.now().isoformat(),
            "time_taken_seconds": time_taken_seconds
        }
        
        self.logger.info(f"Answer submitted for question {question_id} in session {session_id}")
        return True
    
    def flag_cheating_attempt(self, session_id: str, reason: str):
        """
        Flag a potential cheating attempt.
        
        Args:
            session_id (str): Test session ID
            reason (str): Reason for flagging
        """
        if session_id in self.test_sessions:
            flag = {
                "timestamp": datetime.now().isoformat(),
                "reason": reason
            }
            self.test_sessions[session_id]['cheating_flags'].append(flag)
            self.logger.warning(f"Cheating flag added to session {session_id}: {reason}")
    
    def complete_test(self, session_id: str) -> Dict[str, Any]:
        """
        Complete a test session and calculate scores.
        
        Args:
            session_id (str): Test session ID
            
        Returns:
            dict: Test results with scores
        """
        if session_id not in self.test_sessions:
            raise ValueError(f"Session {session_id} not found")
        
        session = self.test_sessions[session_id]
        
        # Calculate scores
        soft_skill_score = self._score_soft_skills(session)
        technical_score = self._score_technical(session)
        
        # Calculate time bonus/penalty
        start_time = datetime.fromisoformat(session['start_time'])
        time_taken = (datetime.now() - start_time).total_seconds() / 60  # minutes
        time_penalty = 0
        
        if time_taken > session['time_limit_minutes']:
            time_penalty = min((time_taken - session['time_limit_minutes']) * 2, 20)  # Max 20% penalty
        
        # Cheating penalty
        cheating_penalty = min(len(session['cheating_flags']) * 10, 30)  # Max 30% penalty
        
        # Final scores
        final_soft_skill_score = max(0, soft_skill_score - time_penalty - cheating_penalty)
        final_technical_score = max(0, technical_score - time_penalty - cheating_penalty)
        overall_score = (final_soft_skill_score + final_technical_score) / 2
        
        results = {
            "session_id": session_id,
            "candidate_id": session['candidate_id'],
            "soft_skill_score": round(final_soft_skill_score, 2),
            "technical_score": round(final_technical_score, 2),
            "overall_score": round(overall_score, 2),
            "time_taken_minutes": round(time_taken, 2),
            "time_penalty": round(time_penalty, 2),
            "cheating_flags": len(session['cheating_flags']),
            "cheating_penalty": round(cheating_penalty, 2),
            "completed_at": datetime.now().isoformat(),
            "strengths": self._identify_strengths(session),
            "weaknesses": self._identify_weaknesses(session)
        }
        
        # Mark session as completed
        session['status'] = 'completed'
        session['results'] = results
        
        # Store results
        self.test_results[session_id] = results
        
        self.logger.info(f"Test completed for session {session_id}. Overall score: {overall_score:.2f}")
        
        return results
    
    def _score_soft_skills(self, session: Dict) -> float:
        """Score soft skill answers."""
        total_score = 0
        total_weight = 0
        
        for question in session['soft_skill_questions']:
            q_id = question['id']
            if q_id in session['answers']:
                answer_data = session['answers'][q_id]
                answer = answer_data['answer']
                weight = question['weight']
                total_weight += weight
                
                if question['type'] == 'multiple_choice':
                    if answer == question['correct_answer']:
                        total_score += 100 * weight
                    else:
                        total_score += 40 * weight  # Partial credit
                
                elif question['type'] == 'text':
                    # Simple scoring based on length and keyword presence
                    text = str(answer).strip()
                    word_count = len(text.split())
                    min_words = question.get('min_words', 20)
                    
                    if word_count >= min_words:
                        score = min(100, 60 + (word_count - min_words) * 2)
                    else:
                        score = (word_count / min_words) * 60
                    
                    total_score += score * weight
                
                elif question['type'] == 'scale':
                    # Normalize scale to 0-100
                    try:
                        value = int(answer) if isinstance(answer, (int, float, str)) and str(answer).strip().isdigit() else int(question['min'])
                    except (ValueError, TypeError):
                        # Default to minimum value if conversion fails
                        value = int(question['min'])
                    max_val = question['max']
                    score = (value / max_val) * 100
                    total_score += score * weight
        
        return (total_score / total_weight) if total_weight > 0 else 0
    
    def _score_technical(self, session: Dict) -> float:
        """Score technical answers."""
        total_score = 0
        total_weight = 0
        
        for question in session['technical_questions']:
            q_id = question['id']
            if q_id in session['answers']:
                answer_data = session['answers'][q_id]
                answer = answer_data['answer']
                weight = question['weight']
                total_weight += weight
                
                if question['type'] == 'text':
                    # Score based on answer quality
                    text = str(answer).strip()
                    word_count = len(text.split())
                    min_words = question.get('min_words', 20)
                    
                    # Base score on length
                    if word_count >= min_words:
                        base_score = 70
                        # Bonus for detailed answers
                        bonus = min((word_count - min_words) * 1.5, 30)
                        score = base_score + bonus
                    else:
                        score = (word_count / min_words) * 60
                    
                    total_score += min(score, 100) * weight
                
                elif question['type'] == 'scale':
                    try:
                        value = int(answer) if isinstance(answer, (int, float, str)) and str(answer).strip().isdigit() else int(question['min'])
                    except (ValueError, TypeError):
                        # Default to minimum value if conversion fails
                        value = int(question['min'])
                    max_val = question['max']
                    score = (value / max_val) * 100
                    total_score += score * weight
        
        return (total_score / total_weight) if total_weight > 0 else 0
    
    def _identify_strengths(self, session: Dict) -> List[str]:
        """Identify candidate strengths based on answers."""
        strengths = []
        
        # Check soft skills
        for question in session['soft_skill_questions']:
            q_id = question['id']
            if q_id in session['answers']:
                if question['type'] == 'multiple_choice':
                    if session['answers'][q_id]['answer'] == question.get('correct_answer'):
                        if 'priorit' in question['question'].lower():
                            strengths.append("Strong prioritization skills")
                        elif 'criticism' in question['question'].lower():
                            strengths.append("Receptive to feedback")
        
        # Check technical answers
        for question in session['technical_questions']:
            q_id = question['id']
            if q_id in session['answers']:
                answer = str(session['answers'][q_id]['answer'])
                if len(answer.split()) > question.get('min_words', 20) + 20:
                    strengths.append("Detailed technical knowledge")
                    break
        
        return strengths if strengths else ["Completed all sections"]
    
    def _identify_weaknesses(self, session: Dict) -> List[str]:
        """Identify candidate weaknesses based on answers."""
        weaknesses = []
        
        # Check for missing answers
        total_questions = len(session['soft_skill_questions']) + len(session['technical_questions'])
        answered_questions = len(session['answers'])
        
        if answered_questions < total_questions:
            weaknesses.append(f"Incomplete ({total_questions - answered_questions} questions unanswered)")
        
        # Check for short answers
        short_answer_count = 0
        for question in session['soft_skill_questions'] + session['technical_questions']:
            if question['type'] == 'text':
                q_id = question['id']
                if q_id in session['answers']:
                    answer = str(session['answers'][q_id]['answer'])
                    if len(answer.split()) < question.get('min_words', 20):
                        short_answer_count += 1
        
        if short_answer_count > 2:
            weaknesses.append("Brief responses (needs more detail)")
        
        # Check cheating flags
        if len(session['cheating_flags']) > 0:
            weaknesses.append(f"Integrity concerns ({len(session['cheating_flags'])} flags)")
        
        return weaknesses if weaknesses else ["None identified"]
    
    def get_session_status(self, session_id: str) -> Dict[str, Any]:
        """Get the current status of a test session."""
        if session_id not in self.test_sessions:
            return {"error": "Session not found"}
        
        session = self.test_sessions[session_id]
        return {
            "session_id": session_id,
            "status": session['status'],
            "start_time": session['start_time'],
            "questions_answered": len(session['answers']),
            "total_questions": len(session['soft_skill_questions']) + len(session['technical_questions']),
            "cheating_flags": len(session['cheating_flags'])
        }


# Create a global instance
test_system = CandidateTestSystem()
