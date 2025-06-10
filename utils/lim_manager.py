from langchain_openai import AzureChatOpenAI, AzureOpenAIEmbeddings, ChatOpenAI, OpenAIEmbeddings
from langchain.schema import HumanMessage, SystemMessage
from config import Config, validate_config
import logging

logger = logging.getLogger(__name__)

class LLMManager:
    """LLM 연결 및 관리 클래스"""
    
    def __init__(self):
        validate_config()
        self.llm = self._initialize_llm()
        self.embeddings = self._initialize_embeddings()
    
    def _initialize_llm(self):
        """LLM 초기화"""
        try:
            if Config.AZURE_OPENAI_API_KEY:
                return AzureChatOpenAI(
                    azure_endpoint=Config.AZURE_OPENAI_ENDPOINT,
                    api_key=Config.AZURE_OPENAI_API_KEY,
                    api_version=Config.AZURE_OPENAI_API_VERSION,
                    deployment_name=Config.AZURE_OPENAI_DEPLOYMENT_NAME,
                    temperature=0.1,
                    max_tokens=2000
                )
            else:
                return ChatOpenAI(
                    api_key=Config.OPENAI_API_KEY,
                    model="gpt-4",
                    temperature=0.1,
                    max_tokens=2000
                )
        except Exception as e:
            logger.error(f"LLM 초기화 실패: {e}")
            raise
    
    def _initialize_embeddings(self):
        """임베딩 모델 초기화"""
        try:
            if Config.AZURE_OPENAI_API_KEY and Config.AZURE_OPENAI_EMBEDDING_DEPLOYMENT:
                return AzureOpenAIEmbeddings(
                    azure_endpoint=Config.AZURE_OPENAI_ENDPOINT,
                    api_key=Config.AZURE_OPENAI_API_KEY,
                    api_version=Config.AZURE_OPENAI_API_VERSION,
                    deployment=Config.AZURE_OPENAI_EMBEDDING_DEPLOYMENT
                )
            else:
                return OpenAIEmbeddings(
                    api_key=Config.OPENAI_API_KEY or Config.AZURE_OPENAI_API_KEY
                )
        except Exception as e:
            logger.error(f"임베딩 모델 초기화 실패: {e}")
            raise
    
    def generate_response(self, system_prompt: str, user_prompt: str) -> str:
        """LLM 응답 생성"""
        try:
            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=user_prompt)
            ]
            response = self.llm.invoke(messages)
            return response.content
        except Exception as e:
            logger.error(f"응답 생성 실패: {e}")
            return f"오류가 발생했습니다: {str(e)}"
    
    def get_embeddings(self):
        """임베딩 모델 반환"""
        return self.embeddings 
