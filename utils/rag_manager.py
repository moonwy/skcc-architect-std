import os
import json
from typing import List, Dict, Optional
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import FAISS
from langchain.docstore.document import Document
from langchain.schema import BaseRetriever
from utils.llm_manager import LLMManager
from config import Config
import logging

logger = logging.getLogger(__name__)

class RAGSystem:
    """RAG 시스템 클래스"""
    
    def __init__(self, llm_manager: LLMManager):
        self.llm_manager = llm_manager
        self.embeddings = llm_manager.get_embeddings()
        self.vector_store = None
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len
        )
        self._initialize_knowledge_base()
    
    def _initialize_knowledge_base(self):
        """지식베이스 초기화"""
        try:
            # 기존 벡터 스토어 로드 시도
            if os.path.exists(Config.VECTOR_DB_PATH):
                self.vector_store = FAISS.load_local(
                    Config.VECTOR_DB_PATH, 
                    self.embeddings,
                    allow_dangerous_deserialization=True
                )
                logger.info("기존 벡터 스토어를 로드했습니다.")
            else:
                # 새로운 지식베이스 생성
                self._create_knowledge_base()
        except Exception as e:
            logger.error(f"지식베이스 초기화 실패: {e}")
            self._create_knowledge_base()
    
    def _create_knowledge_base(self):
        """코딩 베스트 프랙티스 지식베이스 생성"""
        logger.info("새로운 지식베이스를 생성합니다...")
        
        # 코딩 베스트 프랙티스 데이터
        knowledge_data = self._get_coding_best_practices()
        
        # 문서 생성
        documents = []
        for category, practices in knowledge_data.items():
            for practice in practices:
                doc = Document(
                    page_content=practice['content'],
                    metadata={
                        'category': category,
                        'title': practice['title'],
                        'language': practice.get('language', 'general'),
                        'severity': practice.get('severity', 'info')
                    }
                )
                documents.append(doc)
        
        # 텍스트 분할
        split_docs = self.text_splitter.split_documents(documents)
        
        # 벡터 스토어 생성
        if split_docs:
            self.vector_store = FAISS.from_documents(split_docs, self.embeddings)
            
            # 벡터 스토어 저장
            os.makedirs(Config.VECTOR_DB_PATH, exist_ok=True)
            self.vector_store.save_local(Config.VECTOR_DB_PATH)
            logger.info(f"지식베이스 생성 완료: {len(split_docs)}개 문서")
        else:
            logger.warning("생성할 문서가 없습니다.")
    
    def _get_coding_best_practices(self) -> Dict:
        """코딩 베스트 프랙티스 데이터 반환"""
        return {
            "code_quality": [
                {
                    "title": "함수 길이 제한",
                    "content": "함수는 한 가지 일만 해야 하며, 일반적으로 20-30줄을 넘지 않는 것이 좋습니다. 긴 함수는 여러 개의 작은 함수로 분할하세요.",
                    "language": "general",
                    "severity": "warning"
                },
                {
                    "title": "의미있는 변수명 사용",
                    "content": "변수명은 그 목적을 명확히 나타내야 합니다. 'x', 'temp', 'data'와 같은 모호한 이름 대신 'user_count', 'temperature_celsius', 'customer_data'와 같이 구체적인 이름을 사용하세요.",
                    "language": "general",
                    "severity": "info"
                },
                {
                    "title": "코드 중복 제거",
                    "content": "DRY(Don't Repeat Yourself) 원칙을 따라 중복된 코드를 함수나 클래스로 추출하세요. 코드 중복은 유지보수를 어렵게 만듭니다.",
                    "language": "general",
                    "severity": "warning"
                }
            ],
            "python_best_practices": [
                {
                    "title": "PEP 8 스타일 가이드 준수",
                    "content": "Python의 공식 스타일 가이드인 PEP 8을 따르세요. 들여쓰기는 4칸, 라인 길이는 79자 이하, 함수와 클래스 사이는 2줄 공백을 유지하세요.",
                    "language": "python",
                    "severity": "info"
                },
                {
                    "title": "리스트 컴프리헨션 활용",
                    "content": "간단한 반복문은 리스트 컴프리헨션으로 대체할 수 있습니다. [x*2 for x in range(10)]과 같이 사용하면 더 파이썬다운 코드가 됩니다.",
                    "language": "python",
                    "severity": "info"
                },
                {
                    "title": "예외 처리 구체화",
                    "content": "except: 대신 구체적인 예외 타입을 명시하세요. except ValueError: 또는 except (TypeError, ValueError):와 같이 사용하면 더 안전한 코드가 됩니다.",
                    "language": "python",
                    "severity": "warning"
                }
            ],
            "javascript_best_practices": [
                {
                    "title": "const와 let 사용",
                    "content": "var 대신 const와 let을 사용하세요. const는 재할당이 없는 변수에, let은 재할당이 필요한 변수에 사용합니다.",
                    "language": "javascript",
                    "severity": "warning"
                },
                {
                    "title": "엄격한 비교 연산자 사용",
                    "content": "== 대신 ===을 사용하세요. ===는 타입까지 비교하므로 예상치 못한 타입 변환을 방지할 수 있습니다.",
                    "language": "javascript",
                    "severity": "warning"
                },
                {
                    "title": "화살표 함수 활용",
                    "content": "간단한 함수는 화살표 함수를 사용하세요. const add = (a, b) => a + b; 와 같이 사용하면 더 간결한 코드가 됩니다.",
                    "language": "javascript",
                    "severity": "info"
                }
            ],
            "security": [
                {
                    "title": "SQL 인젝션 방지",
                    "content": "사용자 입력을 직접 SQL 쿼리에 삽입하지 마세요. 매개변수화된 쿼리나 ORM을 사용하여 SQL 인젝션 공격을 방지하세요.",
                    "language": "general",
                    "severity": "critical"
                },
                {
                    "title": "하드코딩된 비밀번호 금지",
                    "content": "API 키, 비밀번호, 토큰 등의 민감한 정보를 코드에 직접 작성하지 마세요. 환경변수나 설정 파일을 사용하세요.",
                    "language": "general",
                    "severity": "critical"
                },
                {
                    "title": "입력 검증",
                    "content": "모든 사용자 입력은 검증해야 합니다. 길이, 형식, 허용된 문자 등을 확인하여 악의적인 입력을 차단하세요.",
                    "language": "general",
                    "severity": "warning"
                }
            ],
            "performance": [
                {
                    "title": "알고리즘 복잡도 고려",
                    "content": "시간 복잡도와 공간 복잡도를 고려하여 효율적인 알고리즘을 선택하세요. O(n²) 알고리즘보다 O(n log n) 알고리즘이 대용량 데이터에서 더 효율적입니다.",
                    "language": "general",
                    "severity": "info"
                },
                {
                    "title": "데이터베이스 쿼리 최적화",
                    "content": "N+1 쿼리 문제를 피하고, 적절한 인덱스를 사용하며, 필요한 컬럼만 선택하여 데이터베이스 성능을 최적화하세요.",
                    "language": "general",
                    "severity": "warning"
                },
                {
                    "title": "메모리 누수 방지",
                    "content": "사용하지 않는 객체에 대한 참조를 제거하고, 이벤트 리스너를 적절히 해제하여 메모리 누수를 방지하세요.",
                    "language": "general",
                    "severity": "warning"
                }
            ]
        }
    
    def search_knowledge(self, query: str, k: int = 5) -> List[Document]:
        """지식베이스에서 관련 문서 검색"""
        if not self.vector_store:
            logger.warning("벡터 스토어가 초기화되지 않았습니다.")
            return []
        
        try:
            docs = self.vector_store.similarity_search(query, k=k)
            return docs
        except Exception as e:
            logger.error(f"지식베이스 검색 실패: {e}")
            return []
    
    def get_relevant_practices(self, code_issues: List[Dict], language: str) -> List[Document]:
        """코드 이슈에 관련된 베스트 프랙티스 검색"""
        relevant_docs = []
        
        for issue in code_issues:
            # 이슈 타입과 메시지를 기반으로 검색
            query = f"{issue['type']} {issue['message']} {language}"
            docs = self.search_knowledge(query, k=2)
            relevant_docs.extend(docs)
        
        # 중복 제거
        unique_docs = []
        seen_content = set()
        for doc in relevant_docs:
            if doc.page_content not in seen_content:
                unique_docs.append(doc)
                seen_content.add(doc.page_content)
        
        return unique_docs[:5]  # 최대 5개만 반환
    
    def add_custom_practice(self, title: str, content: str, category: str, language: str = "general"):
        """사용자 정의 베스트 프랙티스 추가"""
        try:
            doc = Document(
                page_content=content,
                metadata={
                    'category': category,
                    'title': title,
                    'language': language,
                    'custom': True
                }
            )
            
            split_docs = self.text_splitter.split_documents([doc])
            
            if self.vector_store and split_docs:
                self.vector_store.add_documents(split_docs)
                self.vector_store.save_local(Config.VECTOR_DB_PATH)
                logger.info(f"사용자 정의 베스트 프랙티스 추가: {title}")
                return True
            
        except Exception as e:
            logger.error(f"베스트 프랙티스 추가 실패: {e}")
        
        return False 
