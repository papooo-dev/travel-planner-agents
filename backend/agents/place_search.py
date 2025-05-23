from langgraph.prebuilt import create_react_agent
import requests
import os
import dotenv
from typing import Dict, List, Optional
from langchain_core.tools import tool

dotenv.load_dotenv()


# Kakao API 키워드로 장소 검색 도구
@tool
def search_places_by_keyword(query: str, page: int = 1, size: int = 15) -> List[Dict]:
    """
    Kakao 로컬 API를 사용하여 키워드로 장소를 검색합니다.

    Args:
        query: 검색할 키워드
        page: 결과 페이지 번호 (기본값: 1)
        size: 한 페이지에 보여질 문서의 개수 (기본값: 5)

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
        results.append(
            {
                "이름": place.get("place_name"),
                "주소": place.get("address_name"),
                "place_url": place.get("place_url"),
                "카테고리": place.get("category_name"),
                "전화번호": place.get("phone"),
            }
        )

    return results


# 장소 검색 에이전트 생성
place_search_agent = create_react_agent(
    model="openai:gpt-4o",
    tools=[search_places_by_keyword],
    prompt="""당신은 여행지 검색을 도와주는 전문 에이전트입니다.
사용자가 여행지 검색을 요청하면, 이를 바탕으로 적절한 키워드를 만들어 여행 장소를 검색하세요.
검색 결과는 이름, 주소, place_url, 카테고리명, 전화번호 형식으로 정리하여 제공하세요.

이 과정에서 search_places_by_keyword 도구를 사용하여 장소를 검색할 수 있습니다.
""",
    name="place_search_assistant",
)

if __name__ == "__main__":
    user_input = "부산 가족 여행"
    # result = search_places_by_keyword.invoke(user_input)
    # for place in result:
    #     print(len(result))
    #     print(place)
    # # print(search_places_by_keyword.invoke(user_input))
    for token, metadata in place_search_agent.stream(
        {"messages": [{"role": "user", "content": user_input}]},
        stream_mode="messages"
    ):
        print("Token", token)
        print("Metadata", metadata)
        print("\n")