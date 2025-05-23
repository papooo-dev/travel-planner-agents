# 환경 변수 설정 가이드

이 프로젝트를 실행하기 위해서는 다음과 같은 환경 변수가 필요합니다.

## 필요한 환경 변수

1. `KAKAO_API_KEY`: 카카오 로컬 API를 사용하기 위한 API 키
2. `OPENAI_API_KEY`: OpenAI GPT 모델을 사용하기 위한 API 키

## 환경 변수 설정 방법

### 1. `.env` 파일 생성

프로젝트 루트 디렉토리에 `.env` 파일을 생성하고 다음과 같이 환경 변수를 설정합니다:

```
# Kakao API 키 
KAKAO_API_KEY=your_kakao_api_key_here

# OpenAI API 키
OPENAI_API_KEY=your_openai_api_key_here
```

### 2. Kakao API 키 발급 방법

1. [Kakao Developers](https://developers.kakao.com/) 사이트에 로그인합니다.
2. 애플리케이션을 생성합니다.
3. 앱 설정 > 요약 정보에서 REST API 키를 확인합니다.
4. 앱 설정 > 플랫폼에서 Web 플랫폼을 등록합니다.
5. 앱 설정 > 카카오 로컬 API를 활성화합니다.

### 3. OpenAI API 키 발급 방법

1. [OpenAI API](https://platform.openai.com/) 사이트에 로그인합니다.
2. API 키를 생성합니다.

## 주의사항

- `.env` 파일은 민감한 정보를 포함하고 있으므로 버전 관리 시스템(Git)에 포함되지 않도록 주의하세요.
- 이 프로젝트에서는 `.env` 파일이 `.gitignore`에 이미 추가되어 있습니다. 