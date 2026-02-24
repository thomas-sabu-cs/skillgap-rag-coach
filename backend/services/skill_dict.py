"""
Deterministic skill dictionary for baseline mode.
Normalized keywords and common variants for matching.
"""
from typing import FrozenSet

# Normalized skill tokens (lowercase, no punctuation) mapped to a canonical set.
# In baseline we treat each of these as a "skill" when found in text.
SKILL_KEYWORDS: FrozenSet[str] = frozenset({
    # Programming languages
    "python", "javascript", "typescript", "java", "csharp", "c#", "cpp", "c++", "go", "golang",
    "rust", "ruby", "php", "swift", "kotlin", "scala", "r", "sql", "html", "css",
    # Frameworks & libraries
    "react", "vue", "angular", "nextjs", "next.js", "node", "nodejs", "express", "django",
    "flask", "fastapi", "spring", "rails", "laravel", "dotnet", ".net", "asp.net",
    # Data & ML
    "machine learning", "ml", "deep learning", "tensorflow", "pytorch", "keras", "pandas",
    "numpy", "scikit", "scikit-learn", "data analysis", "data science", "nlp",
    "natural language processing", "computer vision", "statistics",
    # Cloud & DevOps
    "aws", "azure", "gcp", "google cloud", "docker", "kubernetes", "k8s", "ci/cd",
    "jenkins", "github actions", "terraform", "ansible", "linux", "bash", "shell",
    # Databases
    "postgresql", "postgres", "mysql", "mongodb", "redis", "elasticsearch", "sqlite",
    # Tools & practices
    "git", "rest", "api", "graphql", "microservices", "agile", "scrum", "jira",
    "testing", "unit tests", "tdd", "oop", "design patterns", "clean code",
    # Soft & domain
    "leadership", "communication", "project management", "technical writing",
    "problem solving", "collaboration", "mentoring", "cross-functional",
})

# Single-word tokens (for simple tokenization)
SKILL_WORDS: FrozenSet[str] = frozenset({
    "python", "javascript", "typescript", "java", "golang", "rust", "ruby", "php",
    "swift", "kotlin", "scala", "react", "vue", "angular", "django", "flask", "fastapi",
    "node", "express", "spring", "rails", "docker", "kubernetes", "terraform", "aws",
    "azure", "gcp", "postgresql", "mysql", "mongodb", "redis", "git", "linux", "bash",
    "tensorflow", "pytorch", "pandas", "numpy", "sql", "html", "css", "rest", "api",
    "agile", "scrum", "jira", "testing", "oop", "nlp", "ml",
})
