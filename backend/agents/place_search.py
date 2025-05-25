from langgraph.prebuilt import create_react_agent
import requests
import os
from typing import Dict, List
from langchain_core.tools import tool
from dotenv import load_dotenv
from langchain_tavily import TavilySearch
from backend import store
from langchain.chat_models import init_chat_model
from backend.prompts import PLACE_SEARCH_PROMPT

load_dotenv()

# Kakao API 키워드로 장소 검색 도구
@tool
def place_detail_tool(query: str, page: int = 1, size: int = 2) -> List[Dict]:
    """
    Kakao 로컬 API를 사용하여 키워드로 장소를 검색합니다.

    Args:
        query: 검색할 장소명
        page: 결과 페이지 번호 (기본값: 1)
        size: 한 페이지에 보여질 문서의 개수 (기본값: 2)

    Returns:
        검색된 장소 목록 (이름, 주소, URL, 카테고리, 전화번호 포함)
    """
    api_key = os.getenv("KAKAO_API_KEY")
    if not api_key:
        return {"error": "KAKAO_API_KEY가 설정되지 않았습니다."}

    url = "https://dapi.kakao.com/v2/local/search/keyword.json"
    headers = {"Authorization": f"KakaoAK {api_key}"}
    params = {"query": query, "page": page, "size": size}

    response = requests.get(url, headers=headers, params=params)

    if response.status_code != 200:
        return {"error": f"API 요청 실패: {response.status_code}"}

    data = response.json()
    results = []

    for place in data.get("documents", []):
        place_dict = {
            "place_name": place.get("place_name"),
            "place_address": place.get("address_name"),
            "place_url": place.get("place_url"),
            "place_category": place.get("category_name") or "기타",
            "place_x": place.get("x"),
            "place_y": place.get("y"),
        }
        results.append(place_dict)

    return results


web_search_tool = TavilySearch(
    max_results=10,
    topic="general",
    search_depth="advanced",
)

# 장소 검색 에이전트 생성
place_search_agent = create_react_agent(
    model=init_chat_model(model=os.getenv("PLACE_SEARCH_MODEL"), temperature=0.0),
    tools=[web_search_tool, place_detail_tool, store.save_place_info],
    store=store,
    version="v2",
    prompt=PLACE_SEARCH_PROMPT,
    name="place_search_assistant",
).with_config(tags=["place_search_agent"])
