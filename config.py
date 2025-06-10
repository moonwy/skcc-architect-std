import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    """Configuration class for the AI Code Review Agent"""
    
    # Demo mode flag
    DEMO_MODE = os.getenv("DEMO_MODE", "false").lower() == "true"
    
    # Azure OpenAI Configuration (updated to match user's env vars)
    AZURE_OPENAI_API_KEY = os.getenv("AOAI_API_KEY")
    AZURE_OPENAI_ENDPOINT = os.getenv("AOAI_ENDPOINT")
    AZURE_OPENAI_API_VERSION = os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-15-preview")
    AZURE_OPENAI_DEPLOYMENT_NAME = os.getenv("AOAI_DEPLOY_GPT4O_MINI", "gpt-4o-mini")
    AZURE_OPENAI_EMBEDDING_DEPLOYMENT = os.getenv("AOAI_DEPLOY_EMBED_3_LARGE", "text-embedding-3-large")
    
    # OpenAI Configuration (fallback)
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    
    # Vector Database Configuration
    VECTOR_DB_PATH = "data/vector_db"
    KNOWLEDGE_BASE_PATH = "data/knowledge_base.json"
    
    # Supported Programming Languages
    SUPPORTED_LANGUAGES = [
        "Python",
        "JavaScript", 
        "TypeScript",
        "Java",
        "C++",
        "C#",
        "Go",
        "Rust",
        "PHP",
        "Ruby",
        "Swift",
        "Kotlin",
        "Scala",
        "R",
        "SQL",
        "HTML",
        "CSS",
        "Shell",
        "PowerShell",
        "Dockerfile",
        "YAML",
        "JSON",
        "XML",
        "Markdown",
        "Testing"
    ]
    
    # Code Quality Thresholds
    MAX_LINE_LENGTH = 120
    MAX_FUNCTION_LENGTH = 50
    MAX_CLASS_LENGTH = 500
    MAX_COMPLEXITY = 10
    
    # Review Categories
    REVIEW_CATEGORIES = {
        "quality": "코드 품질",
        "security": "보안",
        "performance": "성능",
        "maintainability": "유지보수성",
        "documentation": "문서화",
        "best_practices": "베스트 프랙티스"
    }
    
    # Severity Levels
    SEVERITY_LEVELS = {
        "critical": "심각",
        "warning": "경고", 
        "info": "정보"
    }
    
    @classmethod
    def validate_config(cls):
        """Validate configuration settings"""
        errors = []
        
        if not cls.DEMO_MODE:
            if not cls.AZURE_OPENAI_API_KEY and not cls.OPENAI_API_KEY:
                errors.append("API 키가 설정되지 않았습니다. AOAI_API_KEY 또는 OPENAI_API_KEY를 설정해주세요.")
            
            if cls.AZURE_OPENAI_API_KEY and not cls.AZURE_OPENAI_ENDPOINT:
                errors.append("Azure OpenAI 엔드포인트가 설정되지 않았습니다. AOAI_ENDPOINT를 설정해주세요.")
        
        return errors 