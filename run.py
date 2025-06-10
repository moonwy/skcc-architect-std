#!/usr/bin/env python3
"""
AI 코드 리뷰 & 최적화 Agent 실행 스크립트
"""

import os
import sys
import subprocess
import logging

def check_requirements():
    """필수 패키지 설치 확인"""
    try:
        import streamlit
        import langchain
        import langgraph
        import faiss
        import openai
        print("✅ 모든 필수 패키지가 설치되어 있습니다.")
        return True
    except ImportError as e:
        print(f"❌ 필수 패키지가 누락되었습니다: {e}")
        print("다음 명령어로 패키지를 설치하세요:")
        print("pip install -r requirements.txt")
        return False

def check_env_variables():
    """환경변수 확인"""
    required_vars = [
        "AZURE_OPENAI_API_KEY",
        "AZURE_OPENAI_ENDPOINT", 
        "AZURE_OPENAI_DEPLOYMENT_NAME"
    ]
    
    missing_vars = []
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print("❌ 다음 환경변수가 설정되지 않았습니다:")
        for var in missing_vars:
            print(f"  - {var}")
        print("\n.env 파일을 생성하고 필요한 환경변수를 설정하세요.")
        return False
    
    print("✅ 환경변수가 올바르게 설정되어 있습니다.")
    return True

def create_directories():
    """필요한 디렉토리 생성"""
    directories = [
        "data",
        "data/vector_db",
        "data/knowledge_base"
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
    
    print("✅ 필요한 디렉토리가 생성되었습니다.")

def run_streamlit():
    """Streamlit 애플리케이션 실행"""
    try:
        print("🚀 AI 코드 리뷰 Agent를 시작합니다...")
        print("브라우저에서 http://localhost:8501 로 접속하세요.")
        print("종료하려면 Ctrl+C를 누르세요.")
        
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", "app.py",
            "--server.port", "8501",
            "--server.address", "localhost"
        ])
    except KeyboardInterrupt:
        print("\n👋 애플리케이션이 종료되었습니다.")
    except Exception as e:
        print(f"❌ 애플리케이션 실행 중 오류가 발생했습니다: {e}")

def main():
    """메인 실행 함수"""
    print("=" * 50)
    print("🔍 AI 코드 리뷰 & 최적화 Agent")
    print("=" * 50)
    
    # 1. 패키지 확인
    if not check_requirements():
        sys.exit(1)
    
    # 2. 환경변수 확인
    if not check_env_variables():
        sys.exit(1)
    
    # 3. 디렉토리 생성
    create_directories()
    
    # 4. Streamlit 실행
    run_streamlit()

if __name__ == "__main__":
    main() 