import streamlit as st
import logging
import json
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from datetime import datetime
import os

# 로컬 모듈 import
from config import Config, validate_config
from utils.llm_manager import LLMManager
from utils.rag_system import RAGSystem
from agents.code_review_agents import CodeReviewAgents

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Streamlit 페이지 설정
st.set_page_config(
    page_title="AI 코드 리뷰 & 최적화 Agent",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 세션 상태 초기화
if 'review_history' not in st.session_state:
    st.session_state.review_history = []

if 'agents_initialized' not in st.session_state:
    st.session_state.agents_initialized = False

def initialize_agents():
    """AI Agent 시스템 초기화"""
    try:
        with st.spinner("AI Agent 시스템을 초기화하는 중..."):
            # 설정 검증
            validate_config()
            
            # LLM 매니저 초기화
            llm_manager = LLMManager()
            
            # RAG 시스템 초기화
            rag_system = RAGSystem(llm_manager)
            
            # 코드 리뷰 에이전트 초기화
            code_review_agents = CodeReviewAgents(llm_manager, rag_system)
            
            return llm_manager, rag_system, code_review_agents
    
    except Exception as e:
        st.error(f"시스템 초기화 실패: {str(e)}")
        st.info("환경변수를 확인해주세요. .env 파일에 다음 정보가 필요합니다:")
        st.code("""
AZURE_OPENAI_API_KEY=your_api_key
AZURE_OPENAI_ENDPOINT=your_endpoint
AZURE_OPENAI_DEPLOYMENT_NAME=your_deployment
AZURE_OPENAI_EMBEDDING_DEPLOYMENT=your_embedding_deployment
        """)
        return None, None, None

def display_code_analysis(analysis):
    """코드 분석 결과 표시"""
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("코드 라인 수", analysis.get('lines_of_code', 0))
    
    with col2:
        st.metric("함수 수", len(analysis.get('functions', [])))
    
    with col3:
        st.metric("클래스 수", len(analysis.get('classes', [])))
    
    with col4:
        st.metric("복잡도 점수", analysis.get('complexity_score', 0))
    
    # 함수 및 클래스 정보
    if analysis.get('functions'):
        st.subheader("🔧 함수 목록")
        functions_df = pd.DataFrame(analysis['functions'])
        st.dataframe(functions_df, use_container_width=True)
    
    if analysis.get('classes'):
        st.subheader("📦 클래스 목록")
        classes_df = pd.DataFrame(analysis['classes'])
        st.dataframe(classes_df, use_container_width=True)

def display_issues(issues):
    """이슈 목록 표시"""
    if not issues:
        st.success("발견된 이슈가 없습니다! 🎉")
        return
    
    # 심각도별 색상 매핑
    severity_colors = {
        "Critical": "🔴",
        "Warning": "🟡", 
        "Info": "🔵"
    }
    
    # 심각도별 그룹화
    critical_issues = [i for i in issues if i.get('severity') == 'Critical']
    warning_issues = [i for i in issues if i.get('severity') == 'Warning']
    info_issues = [i for i in issues if i.get('severity') == 'Info']
    
    # 탭으로 구분
    tab1, tab2, tab3 = st.tabs([
        f"🔴 Critical ({len(critical_issues)})",
        f"🟡 Warning ({len(warning_issues)})", 
        f"🔵 Info ({len(info_issues)})"
    ])
    
    with tab1:
        display_issue_list(critical_issues, "Critical")
    
    with tab2:
        display_issue_list(warning_issues, "Warning")
    
    with tab3:
        display_issue_list(info_issues, "Info")

def display_issue_list(issues, severity):
    """특정 심각도의 이슈 목록 표시"""
    if not issues:
        st.info(f"{severity} 레벨의 이슈가 없습니다.")
        return
    
    for i, issue in enumerate(issues):
        with st.expander(f"라인 {issue.get('line', 'N/A')}: {issue.get('message', 'No message')[:50]}..."):
            st.write(f"**타입:** {issue.get('type', 'Unknown')}")
            st.write(f"**라인:** {issue.get('line', 'N/A')}")
            st.write(f"**메시지:** {issue.get('message', 'No message')}")
            if issue.get('suggestion'):
                st.write(f"**개선 제안:** {issue.get('suggestion')}")
            if issue.get('impact'):
                st.write(f"**예상 효과:** {issue.get('impact')}")

def display_recommendations(recommendations):
    """추천사항 표시"""
    if not recommendations:
        st.info("관련 추천사항이 없습니다.")
        return
    
    st.subheader("💡 베스트 프랙티스 추천")
    
    for rec in recommendations:
        with st.expander(f"📚 {rec.get('title', 'Best Practice')} ({rec.get('category', 'General')})"):
            st.write(rec.get('content', 'No content available'))
            if rec.get('language') != 'general':
                st.caption(f"언어: {rec.get('language')}")

def display_summary_chart(summary):
    """요약 차트 표시"""
    col1, col2 = st.columns(2)
    
    with col1:
        # 심각도별 이슈 분포
        severity_data = summary.get('severity_breakdown', {})
        if any(severity_data.values()):
            fig_severity = px.pie(
                values=list(severity_data.values()),
                names=list(severity_data.keys()),
                title="심각도별 이슈 분포",
                color_discrete_map={
                    "Critical": "#ff4444",
                    "Warning": "#ffaa00", 
                    "Info": "#4444ff"
                }
            )
            st.plotly_chart(fig_severity, use_container_width=True)
    
    with col2:
        # 카테고리별 이슈 분포
        category_data = summary.get('category_breakdown', {})
        if any(category_data.values()):
            fig_category = px.bar(
                x=list(category_data.keys()),
                y=list(category_data.values()),
                title="카테고리별 이슈 분포",
                color=list(category_data.values()),
                color_continuous_scale="viridis"
            )
            fig_category.update_layout(showlegend=False)
            st.plotly_chart(fig_category, use_container_width=True)

def main():
    """메인 애플리케이션"""
    
    # 헤더
    st.title("🔍 AI 코드 리뷰 & 최적화 Agent")
    st.markdown("---")
    
    # 사이드바
    with st.sidebar:
        st.header("⚙️ 설정")
        
        # 지원 언어 표시
        st.subheader("지원 언어")
        for lang in Config.SUPPORTED_LANGUAGES:
            st.write(f"• {lang}")
        
        st.markdown("---")
        
        # 리뷰 히스토리
        st.subheader("📊 리뷰 히스토리")
        if st.session_state.review_history:
            for i, review in enumerate(st.session_state.review_history[-5:]):  # 최근 5개만 표시
                with st.expander(f"리뷰 #{len(st.session_state.review_history) - i}"):
                    st.write(f"언어: {review.get('language', 'Unknown')}")
                    st.write(f"점수: {review.get('summary', {}).get('overall_score', 0)}/10")
                    st.write(f"이슈 수: {review.get('summary', {}).get('total_issues', 0)}")
        else:
            st.info("아직 리뷰 히스토리가 없습니다.")
    
    # 메인 컨텐츠
    tab1, tab2, tab3 = st.tabs(["🔍 코드 리뷰", "📚 지식베이스", "ℹ️ 사용법"])
    
    with tab1:
        st.header("코드 리뷰")
        
        # 코드 입력
        col1, col2 = st.columns([3, 1])
        
        with col1:
            code_input = st.text_area(
                "분석할 코드를 입력하세요:",
                height=300,
                placeholder="여기에 코드를 붙여넣으세요..."
            )
        
        with col2:
            filename = st.text_input(
                "파일명 (선택사항):",
                placeholder="example.py"
            )
            
            review_button = st.button(
                "🔍 코드 리뷰 시작",
                type="primary",
                use_container_width=True
            )
        
        # 코드 리뷰 실행
        if review_button and code_input.strip():
            # Agent 초기화
            if not st.session_state.agents_initialized:
                llm_manager, rag_system, code_review_agents = initialize_agents()
                if code_review_agents is None:
                    st.stop()
                st.session_state.llm_manager = llm_manager
                st.session_state.rag_system = rag_system
                st.session_state.code_review_agents = code_review_agents
                st.session_state.agents_initialized = True
            
            # 코드 리뷰 실행
            with st.spinner("AI Agent들이 코드를 분석하고 있습니다..."):
                result = st.session_state.code_review_agents.review_code(code_input, filename)
            
            if result.get('success'):
                # 결과 저장
                result['timestamp'] = datetime.now().isoformat()
                st.session_state.review_history.append(result)
                
                # 결과 표시
                st.success("코드 리뷰가 완료되었습니다!")
                
                # 요약 정보
                summary = result.get('summary', {})
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    score = summary.get('overall_score', 0)
                    color = "green" if score >= 8 else "orange" if score >= 6 else "red"
                    st.metric("전체 점수", f"{score}/10", delta=None)
                
                with col2:
                    st.metric("총 이슈 수", summary.get('total_issues', 0))
                
                with col3:
                    st.metric("Critical 이슈", summary.get('severity_breakdown', {}).get('Critical', 0))
                
                with col4:
                    st.metric("추천사항", summary.get('recommendations_count', 0))
                
                # 차트 표시
                if summary.get('total_issues', 0) > 0:
                    display_summary_chart(summary)
                
                st.markdown("---")
                
                # 상세 결과 탭
                detail_tab1, detail_tab2, detail_tab3, detail_tab4 = st.tabs([
                    "📊 코드 분석", "⚠️ 발견된 이슈", "💡 추천사항", "⚡ 최적화된 코드"
                ])
                
                with detail_tab1:
                    display_code_analysis(result.get('analysis', {}))
                
                with detail_tab2:
                    display_issues(result.get('issues', []))
                
                with detail_tab3:
                    display_recommendations(result.get('recommendations', []))
                
                with detail_tab4:
                    optimized_code = result.get('optimized_code', '')
                    if optimized_code:
                        st.subheader("⚡ 최적화된 코드")
                        st.code(optimized_code, language=result.get('language', 'text'))
                    else:
                        st.info("최적화 제안이 없습니다.")
            
            else:
                st.error(f"코드 리뷰 실행 중 오류가 발생했습니다: {result.get('error', 'Unknown error')}")
        
        elif review_button and not code_input.strip():
            st.warning("분석할 코드를 입력해주세요.")
    
    with tab2:
        st.header("📚 지식베이스 관리")
        
        # 지식베이스 검색
        st.subheader("🔍 베스트 프랙티스 검색")
        search_query = st.text_input("검색어를 입력하세요:", placeholder="예: python security, javascript performance")
        
        if search_query and st.session_state.agents_initialized:
            with st.spinner("지식베이스를 검색하는 중..."):
                docs = st.session_state.rag_system.search_knowledge(search_query, k=5)
            
            if docs:
                st.success(f"{len(docs)}개의 관련 문서를 찾았습니다.")
                for i, doc in enumerate(docs):
                    with st.expander(f"📄 {doc.metadata.get('title', f'문서 {i+1}')}"):
                        st.write(doc.page_content)
                        st.caption(f"카테고리: {doc.metadata.get('category', 'Unknown')} | 언어: {doc.metadata.get('language', 'general')}")
            else:
                st.info("관련 문서를 찾을 수 없습니다.")
        
        st.markdown("---")
        
        # 사용자 정의 베스트 프랙티스 추가
        st.subheader("➕ 베스트 프랙티스 추가")
        
        with st.form("add_practice_form"):
            practice_title = st.text_input("제목:")
            practice_content = st.text_area("내용:", height=150)
            practice_category = st.selectbox("카테고리:", Config.REVIEW_CATEGORIES)
            practice_language = st.selectbox("언어:", ["general"] + Config.SUPPORTED_LANGUAGES)
            
            submit_button = st.form_submit_button("추가")
            
            if submit_button and practice_title and practice_content:
                if st.session_state.agents_initialized:
                    success = st.session_state.rag_system.add_custom_practice(
                        practice_title, practice_content, practice_category, practice_language
                    )
                    if success:
                        st.success("베스트 프랙티스가 추가되었습니다!")
                    else:
                        st.error("베스트 프랙티스 추가에 실패했습니다.")
                else:
                    st.warning("먼저 시스템을 초기화해주세요.")
    
    with tab3:
        st.header("ℹ️ 사용법")
        
        st.markdown("""
        ## 🎯 AI 코드 리뷰 & 최적화 Agent 사용법
        
        ### 1. 코드 리뷰 기능
        - **코드 입력**: 분석하고 싶은 코드를 텍스트 영역에 붙여넣으세요
        - **파일명 입력**: 파일명을 입력하면 더 정확한 언어 감지가 가능합니다
        - **리뷰 시작**: "코드 리뷰 시작" 버튼을 클릭하세요
        
        ### 2. Multi-Agent 분석 과정
        1. **분석 Agent**: 코드 구조 및 언어 감지
        2. **품질 검사 Agent**: 코드 품질 및 가독성 분석
        3. **보안 검토 Agent**: 보안 취약점 검사
        4. **성능 최적화 Agent**: 성능 개선 방안 제시
        5. **문서화 Agent**: 문서화 상태 분석
        6. **최종 검토 Agent**: 종합적인 리뷰 및 추천사항 제공
        
        ### 3. 지원 기능
        - **다중 언어 지원**: Python, JavaScript, TypeScript, Java 등
        - **RAG 기반 지식베이스**: 코딩 베스트 프랙티스 검색
        - **사용자 정의 규칙**: 팀별 코딩 표준 추가 가능
        - **리뷰 히스토리**: 과거 리뷰 결과 추적
        
        ### 4. 결과 해석
        - **전체 점수**: 1-10점 (높을수록 좋음)
        - **이슈 심각도**: Critical > Warning > Info
        - **추천사항**: RAG 시스템 기반 맞춤형 제안
        
        ### 5. 팁
        - 작은 함수/클래스 단위로 리뷰하면 더 정확한 결과를 얻을 수 있습니다
        - 파일명을 정확히 입력하면 언어별 특화 분석이 가능합니다
        - 정기적인 코드 리뷰로 코드 품질을 지속적으로 개선하세요
        """)

if __name__ == "__main__":
    main() 