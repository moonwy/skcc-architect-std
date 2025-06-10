import re
import ast
import tokenize
from io import StringIO
from typing import Dict, List, Tuple, Optional
from config import Config

class CodeAnalyzer:
    """코드 분석 유틸리티 클래스"""
    
    def __init__(self):
        self.language_patterns = {
            'python': {
                'extension': ['.py'],
                'comment': ['#', '"""', "'''"],
                'keywords': ['def', 'class', 'import', 'from', 'if', 'for', 'while', 'try', 'except']
            },
            'javascript': {
                'extension': ['.js', '.jsx'],
                'comment': ['//', '/*', '*/'],
                'keywords': ['function', 'var', 'let', 'const', 'if', 'for', 'while', 'try', 'catch']
            },
            'typescript': {
                'extension': ['.ts', '.tsx'],
                'comment': ['//', '/*', '*/'],
                'keywords': ['function', 'var', 'let', 'const', 'interface', 'type', 'class']
            },
            'java': {
                'extension': ['.java'],
                'comment': ['//', '/*', '*/'],
                'keywords': ['public', 'private', 'class', 'interface', 'if', 'for', 'while', 'try', 'catch']
            }
        }
    
    def detect_language(self, code: str, filename: str = "") -> str:
        """코드 언어 감지"""
        # 파일 확장자로 먼저 판단
        if filename:
            for lang, info in self.language_patterns.items():
                for ext in info['extension']:
                    if filename.endswith(ext):
                        return lang
        
        # 코드 패턴으로 판단
        scores = {}
        for lang, info in self.language_patterns.items():
            score = 0
            for keyword in info['keywords']:
                score += len(re.findall(r'\b' + keyword + r'\b', code))
            scores[lang] = score
        
        return max(scores, key=scores.get) if scores else 'unknown'
    
    def analyze_code_structure(self, code: str, language: str) -> Dict:
        """코드 구조 분석"""
        analysis = {
            'lines_of_code': len(code.split('\n')),
            'functions': [],
            'classes': [],
            'imports': [],
            'complexity_score': 0,
            'issues': []
        }
        
        if language == 'python':
            analysis.update(self._analyze_python_code(code))
        else:
            analysis.update(self._analyze_generic_code(code, language))
        
        return analysis
    
    def _analyze_python_code(self, code: str) -> Dict:
        """Python 코드 상세 분석"""
        analysis = {
            'functions': [],
            'classes': [],
            'imports': [],
            'complexity_score': 0,
            'issues': []
        }
        
        try:
            tree = ast.parse(code)
            
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    analysis['functions'].append({
                        'name': node.name,
                        'line': node.lineno,
                        'args': len(node.args.args),
                        'docstring': ast.get_docstring(node)
                    })
                
                elif isinstance(node, ast.ClassDef):
                    analysis['classes'].append({
                        'name': node.name,
                        'line': node.lineno,
                        'methods': len([n for n in node.body if isinstance(n, ast.FunctionDef)]),
                        'docstring': ast.get_docstring(node)
                    })
                
                elif isinstance(node, (ast.Import, ast.ImportFrom)):
                    if isinstance(node, ast.Import):
                        for alias in node.names:
                            analysis['imports'].append(alias.name)
                    else:
                        analysis['imports'].append(node.module)
                
                # 복잡도 계산 (if, for, while, try 등)
                elif isinstance(node, (ast.If, ast.For, ast.While, ast.Try)):
                    analysis['complexity_score'] += 1
        
        except SyntaxError as e:
            analysis['issues'].append(f"구문 오류: {str(e)}")
        
        return analysis
    
    def _analyze_generic_code(self, code: str, language: str) -> Dict:
        """일반적인 코드 분석"""
        analysis = {
            'functions': [],
            'classes': [],
            'imports': [],
            'complexity_score': 0,
            'issues': []
        }
        
        lines = code.split('\n')
        
        # 함수 패턴 찾기
        function_patterns = {
            'javascript': r'function\s+(\w+)',
            'typescript': r'function\s+(\w+)',
            'java': r'(public|private|protected)?\s*(static)?\s*\w+\s+(\w+)\s*\('
        }
        
        if language in function_patterns:
            pattern = function_patterns[language]
            for i, line in enumerate(lines):
                matches = re.findall(pattern, line)
                if matches:
                    analysis['functions'].append({
                        'name': matches[0] if isinstance(matches[0], str) else matches[0][-1],
                        'line': i + 1
                    })
        
        # 복잡도 계산
        complexity_keywords = ['if', 'for', 'while', 'switch', 'case', 'try', 'catch']
        for line in lines:
            for keyword in complexity_keywords:
                analysis['complexity_score'] += len(re.findall(r'\b' + keyword + r'\b', line))
        
        return analysis
    
    def check_code_quality_issues(self, code: str, language: str) -> List[Dict]:
        """코드 품질 이슈 체크"""
        issues = []
        lines = code.split('\n')
        
        # 공통 이슈 체크
        for i, line in enumerate(lines):
            line_num = i + 1
            
            # 긴 라인 체크
            if len(line) > 120:
                issues.append({
                    'type': 'Code Quality',
                    'severity': 'Warning',
                    'line': line_num,
                    'message': f'라인이 너무 깁니다 ({len(line)} 문자). 120자 이하로 줄이는 것을 권장합니다.'
                })
            
            # 하드코딩된 값 체크
            if re.search(r'["\'][^"\']*[0-9]{2,}[^"\']*["\']', line):
                issues.append({
                    'type': 'Best Practices',
                    'severity': 'Info',
                    'line': line_num,
                    'message': '하드코딩된 값이 발견되었습니다. 상수로 정의하는 것을 고려해보세요.'
                })
        
        # 언어별 특정 이슈 체크
        if language == 'python':
            issues.extend(self._check_python_issues(code, lines))
        elif language in ['javascript', 'typescript']:
            issues.extend(self._check_js_issues(code, lines))
        
        return issues
    
    def _check_python_issues(self, code: str, lines: List[str]) -> List[Dict]:
        """Python 특정 이슈 체크"""
        issues = []
        
        for i, line in enumerate(lines):
            line_num = i + 1
            stripped = line.strip()
            
            # import 순서 체크
            if stripped.startswith('from ') and i > 0:
                prev_line = lines[i-1].strip()
                if prev_line.startswith('import ') and not prev_line.startswith('from '):
                    issues.append({
                        'type': 'Best Practices',
                        'severity': 'Info',
                        'line': line_num,
                        'message': 'from import는 일반 import 앞에 위치하는 것이 좋습니다.'
                    })
            
            # 예외 처리 체크
            if 'except:' in stripped:
                issues.append({
                    'type': 'Best Practices',
                    'severity': 'Warning',
                    'line': line_num,
                    'message': '구체적인 예외 타입을 명시하는 것이 좋습니다.'
                })
        
        return issues
    
    def _check_js_issues(self, code: str, lines: List[str]) -> List[Dict]:
        """JavaScript/TypeScript 특정 이슈 체크"""
        issues = []
        
        for i, line in enumerate(lines):
            line_num = i + 1
            stripped = line.strip()
            
            # var 사용 체크
            if re.search(r'\bvar\b', stripped):
                issues.append({
                    'type': 'Best Practices',
                    'severity': 'Warning',
                    'line': line_num,
                    'message': 'var 대신 let 또는 const 사용을 권장합니다.'
                })
            
            # == 사용 체크
            if '==' in stripped and '===' not in stripped:
                issues.append({
                    'type': 'Best Practices',
                    'severity': 'Warning',
                    'line': line_num,
                    'message': '== 대신 === 사용을 권장합니다.'
                })
        
        return issues 
