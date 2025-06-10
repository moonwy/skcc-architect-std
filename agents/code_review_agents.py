from typing import Dict, List, Any, Optional
from langchain.schema import BaseMessage, HumanMessage, SystemMessage
from langchain.tools import Tool
from langchain.agents import AgentExecutor, create_react_agent
from langchain.prompts import PromptTemplate
from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages
from typing_extensions import TypedDict
import json
import logging

from utils.llm_manager import LLMManager
from utils.code_analyzer import CodeAnalyzer
from utils.rag_system import RAGSystem

logger = logging.getLogger(__name__)

class CodeReviewState(TypedDict):
    """코드 리뷰 상태 정의"""
    code: str
    filename: str
    language: str
    analysis_result: Dict
    issues: List[Dict]
    recommendations: List[Dict]
    optimized_code: str
    messages: List[BaseMessage]
    current_step: str

class CodeReviewAgents:
    """Multi-Agent 코드 리뷰 시스템"""
    
    def __init__(self, llm_manager: LLMManager, rag_system: RAGSystem):
        self.llm_manager = llm_manager
        self.rag_system = rag_system
        self.code_analyzer = CodeAnalyzer()
        self.workflow = self._create_workflow()
    
    def _create_workflow(self) -> StateGraph:
        """코드 리뷰 워크플로우 생성"""
        workflow = StateGraph(CodeReviewState)
        
        # 노드 추가
        workflow.add_node("analyzer", self._analyzer_agent)
        workflow.add_node("quality_checker", self._quality_checker_agent)
        workflow.add_node("security_reviewer", self._security_reviewer_agent)
        workflow.add_node("performance_optimizer", self._performance_optimizer_agent)
        workflow.add_node("documentation_generator", self._documentation_generator_agent)
        workflow.add_node("final_reviewer", self._final_reviewer_agent)
        
        # 엣지 추가
        workflow.set_entry_point("analyzer")
        workflow.add_edge("analyzer", "quality_checker")
        workflow.add_edge("quality_checker", "security_reviewer")
        workflow.add_edge("security_reviewer", "performance_optimizer")
        workflow.add_edge("performance_optimizer", "documentation_generator")
        workflow.add_edge("documentation_generator", "final_reviewer")
        workflow.add_edge("final_reviewer", END)
        
        return workflow.compile()
    
    def _analyzer_agent(self, state: CodeReviewState) -> CodeReviewState:
        """코드 분석 에이전트"""
        logger.info("코드 분석 시작...")
        
        code = state["code"]
        filename = state.get("filename", "")
        
        # 언어 감지
        language = self.code_analyzer.detect_language(code, filename)
        
        # 코드 구조 분석
        analysis_result = self.code_analyzer.analyze_code_structure(code, language)
        
        # 기본 이슈 체크
        issues = self.code_analyzer.check_code_quality_issues(code, language)
        
        state.update({
            "language": language,
            "analysis_result": analysis_result,
            "issues": issues,
            "current_step": "analysis_complete"
        })
        
        return state
    
    def _quality_checker_agent(self, state: CodeReviewState) -> CodeReviewState:
        """코드 품질 검사 에이전트"""
        logger.info("코드 품질 검사 시작...")
        
        code = state["code"]
        language = state["language"]
        analysis = state["analysis_result"]
        
        # 품질 검사 프롬프트
        quality_prompt = f"""
        당신은 코드 품질 전문가입니다. 다음 {language} 코드를 분석하고 품질 이슈를 찾아주세요.

        코드:
        ```{language}
        {code}
        ```

        분석 결과:
        - 함수 수: {len(analysis.get('functions', []))}
        - 클래스 수: {len(analysis.get('classes', []))}
        - 복잡도 점수: {analysis.get('complexity_score', 0)}
        - 코드 라인 수: {analysis.get('lines_of_code', 0)}

        다음 관점에서 분석해주세요:
        1. 코드 가독성
        2. 함수/클래스 설계
        3. 네이밍 컨벤션
        4. 코드 중복
        5. 복잡도

        JSON 형식으로 응답해주세요:
        {{
            "quality_score": 점수(1-10),
            "issues": [
                {{
                    "type": "Code Quality",
                    "severity": "Warning|Info|Critical",
                    "line": 라인번호,
                    "message": "이슈 설명",
                    "suggestion": "개선 제안"
                }}
            ]
        }}
        """
        
        try:
            response = self.llm_manager.generate_response("", quality_prompt)
            quality_result = json.loads(response)
            
            # 기존 이슈에 품질 이슈 추가
            current_issues = state.get("issues", [])
            current_issues.extend(quality_result.get("issues", []))
            
            state.update({
                "issues": current_issues,
                "current_step": "quality_check_complete"
            })
            
        except Exception as e:
            logger.error(f"품질 검사 실패: {e}")
        
        return state
    
    def _security_reviewer_agent(self, state: CodeReviewState) -> CodeReviewState:
        """보안 검토 에이전트"""
        logger.info("보안 검토 시작...")
        
        code = state["code"]
        language = state["language"]
        
        # 보안 관련 베스트 프랙티스 검색
        security_docs = self.rag_system.search_knowledge(f"security {language}", k=3)
        security_context = "\n".join([doc.page_content for doc in security_docs])
        
        security_prompt = f"""
        당신은 보안 전문가입니다. 다음 {language} 코드에서 보안 취약점을 찾아주세요.

        코드:
        ```{language}
        {code}
        ```

        보안 가이드라인:
        {security_context}

        다음 보안 이슈를 확인해주세요:
        1. SQL 인젝션 가능성
        2. XSS 취약점
        3. 하드코딩된 비밀번호/API 키
        4. 입력 검증 부족
        5. 권한 검사 누락

        JSON 형식으로 응답해주세요:
        {{
            "security_score": 점수(1-10),
            "vulnerabilities": [
                {{
                    "type": "Security",
                    "severity": "Critical|Warning|Info",
                    "line": 라인번호,
                    "message": "취약점 설명",
                    "suggestion": "보안 개선 제안"
                }}
            ]
        }}
        """
        
        try:
            response = self.llm_manager.generate_response("", security_prompt)
            security_result = json.loads(response)
            
            # 기존 이슈에 보안 이슈 추가
            current_issues = state.get("issues", [])
            current_issues.extend(security_result.get("vulnerabilities", []))
            
            state.update({
                "issues": current_issues,
                "current_step": "security_review_complete"
            })
            
        except Exception as e:
            logger.error(f"보안 검토 실패: {e}")
        
        return state
    
    def _performance_optimizer_agent(self, state: CodeReviewState) -> CodeReviewState:
        """성능 최적화 에이전트"""
        logger.info("성능 최적화 분석 시작...")
        
        code = state["code"]
        language = state["language"]
        analysis = state["analysis_result"]
        
        # 성능 관련 베스트 프랙티스 검색
        performance_docs = self.rag_system.search_knowledge(f"performance optimization {language}", k=3)
        performance_context = "\n".join([doc.page_content for doc in performance_docs])
        
        performance_prompt = f"""
        당신은 성능 최적화 전문가입니다. 다음 {language} 코드의 성능을 분석하고 최적화 방안을 제시해주세요.

        코드:
        ```{language}
        {code}
        ```

        현재 분석 결과:
        - 복잡도 점수: {analysis.get('complexity_score', 0)}
        - 함수 수: {len(analysis.get('functions', []))}

        성능 가이드라인:
        {performance_context}

        다음 관점에서 분석해주세요:
        1. 알고리즘 복잡도
        2. 메모리 사용량
        3. 반복문 최적화
        4. 데이터 구조 선택
        5. 캐싱 기회

        JSON 형식으로 응답해주세요:
        {{
            "performance_score": 점수(1-10),
            "optimizations": [
                {{
                    "type": "Performance",
                    "severity": "Info|Warning",
                    "line": 라인번호,
                    "message": "성능 이슈 설명",
                    "suggestion": "최적화 제안",
                    "impact": "예상 성능 개선 효과"
                }}
            ],
            "optimized_code": "최적화된 코드 (선택사항)"
        }}
        """
        
        try:
            response = self.llm_manager.generate_response("", performance_prompt)
            performance_result = json.loads(response)
            
            # 기존 이슈에 성능 이슈 추가
            current_issues = state.get("issues", [])
            current_issues.extend(performance_result.get("optimizations", []))
            
            # 최적화된 코드가 있으면 저장
            optimized_code = performance_result.get("optimized_code", "")
            
            state.update({
                "issues": current_issues,
                "optimized_code": optimized_code,
                "current_step": "performance_optimization_complete"
            })
            
        except Exception as e:
            logger.error(f"성능 최적화 분석 실패: {e}")
        
        return state
    
    def _documentation_generator_agent(self, state: CodeReviewState) -> CodeReviewState:
        """문서화 생성 에이전트"""
        logger.info("문서화 분석 시작...")
        
        code = state["code"]
        language = state["language"]
        analysis = state["analysis_result"]
        
        doc_prompt = f"""
        당신은 코드 문서화 전문가입니다. 다음 {language} 코드의 문서화 상태를 분석하고 개선 제안을 해주세요.

        코드:
        ```{language}
        {code}
        ```

        분석 결과:
        - 함수 목록: {[f['name'] for f in analysis.get('functions', [])]}
        - 클래스 목록: {[c['name'] for c in analysis.get('classes', [])]}

        다음을 확인해주세요:
        1. 함수/클래스 docstring 존재 여부
        2. 주석의 적절성
        3. README 필요성
        4. 타입 힌트 (Python/TypeScript)
        5. API 문서화 필요성

        JSON 형식으로 응답해주세요:
        {{
            "documentation_score": 점수(1-10),
            "suggestions": [
                {{
                    "type": "Documentation",
                    "severity": "Info",
                    "line": 라인번호,
                    "message": "문서화 개선 제안",
                    "suggestion": "구체적인 개선 방법"
                }}
            ]
        }}
        """
        
        try:
            response = self.llm_manager.generate_response("", doc_prompt)
            doc_result = json.loads(response)
            
            # 기존 이슈에 문서화 제안 추가
            current_issues = state.get("issues", [])
            current_issues.extend(doc_result.get("suggestions", []))
            
            state.update({
                "issues": current_issues,
                "current_step": "documentation_complete"
            })
            
        except Exception as e:
            logger.error(f"문서화 분석 실패: {e}")
        
        return state
    
    def _final_reviewer_agent(self, state: CodeReviewState) -> CodeReviewState:
        """최종 검토 에이전트"""
        logger.info("최종 검토 시작...")
        
        code = state["code"]
        language = state["language"]
        issues = state.get("issues", [])
        
        # 이슈에 관련된 베스트 프랙티스 검색
        relevant_practices = self.rag_system.get_relevant_practices(issues, language)
        
        # 최종 추천사항 생성
        recommendations = []
        for practice in relevant_practices:
            recommendations.append({
                "category": practice.metadata.get("category", "General"),
                "title": practice.metadata.get("title", "Best Practice"),
                "content": practice.page_content,
                "language": practice.metadata.get("language", "general")
            })
        
        # 이슈 우선순위 정렬
        priority_order = {"Critical": 0, "Warning": 1, "Info": 2}
        sorted_issues = sorted(issues, key=lambda x: priority_order.get(x.get("severity", "Info"), 2))
        
        state.update({
            "issues": sorted_issues,
            "recommendations": recommendations,
            "current_step": "review_complete"
        })
        
        return state
    
    def review_code(self, code: str, filename: str = "") -> Dict:
        """코드 리뷰 실행"""
        try:
            initial_state = CodeReviewState(
                code=code,
                filename=filename,
                language="",
                analysis_result={},
                issues=[],
                recommendations=[],
                optimized_code="",
                messages=[],
                current_step="start"
            )
            
            # 워크플로우 실행
            result = self.workflow.invoke(initial_state)
            
            return {
                "success": True,
                "language": result["language"],
                "analysis": result["analysis_result"],
                "issues": result["issues"],
                "recommendations": result["recommendations"],
                "optimized_code": result.get("optimized_code", ""),
                "summary": self._generate_summary(result)
            }
            
        except Exception as e:
            logger.error(f"코드 리뷰 실행 실패: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _generate_summary(self, result: Dict) -> Dict:
        """리뷰 요약 생성"""
        issues = result.get("issues", [])
        
        # 심각도별 이슈 카운트
        severity_count = {"Critical": 0, "Warning": 0, "Info": 0}
        type_count = {}
        
        for issue in issues:
            severity = issue.get("severity", "Info")
            issue_type = issue.get("type", "General")
            
            severity_count[severity] += 1
            type_count[issue_type] = type_count.get(issue_type, 0) + 1
        
        # 전체 점수 계산 (10점 만점)
        total_issues = len(issues)
        critical_weight = severity_count["Critical"] * 3
        warning_weight = severity_count["Warning"] * 2
        info_weight = severity_count["Info"] * 1
        
        penalty = critical_weight + warning_weight + info_weight
        overall_score = max(1, 10 - min(penalty, 9))
        
        return {
            "overall_score": overall_score,
            "total_issues": total_issues,
            "severity_breakdown": severity_count,
            "category_breakdown": type_count,
            "recommendations_count": len(result.get("recommendations", []))
        } 
