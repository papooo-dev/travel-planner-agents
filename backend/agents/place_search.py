from langgraph.prebuilt import create_react_agent
import requests
import os
from typing import Dict, List
from langchain_core.tools import tool
from dotenv import load_dotenv
from langchain_community.agent_toolkits import PlayWrightBrowserToolkit


load_dotenv()
#TODO
# 지역의 숙소/맛집/관광지/카페 중 하나 선택하지 않고 그냥 키워드를 지역+카테고리 로 임의로 만들어서 tool을 4번 호출하도록?

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
                "x": place.get("x"),
                "y": place.get("y"),
            }
        )

    return results


# 장소 검색 에이전트 생성
place_search_agent = create_react_agent(
    model="openai:gpt-4o",
    tools=[search_places_by_keyword],
    prompt="""당신은 여행지 검색을 전문으로 지원하는 에이전트입니다.  
사용자 요청은 supervisor 에이전트로부터 전달되며, 다음 지침을 따라 장소 검색을 수행하세요.

## 검색 키워드 구성 규칙
search_places_by_keyword 도구를 호출하기 위해 query 파라미터는 아래의 형식으로 구성되어야 합니다:

> **"위치명 + 카테고리"**

- **위치명**: 예) 서울, 부산, 강릉, 제주 등
- **카테고리** (택1): 관광명소 | 숙박 | 음식점 | 카페

예시:
- “부산 관광명소”
- “제주 음식점”

### 키워드 정보 부족 시 사용자에게 물어볼 질문들

아래의 조건에 따라 추가 질문을 구성하세요:

- 🔸 위치 정보가 없는 경우 →  
  “어떤 지역의 여행지를 찾고 계신가요?”

- 🔸 카테고리가 명확하지 않은 경우 →  
  “어떤 종류의 장소를 찾고 계신가요? 관광명소, 숙박, 음식점, 카페 중 하나를 선택해 주세요.”
> 카테고리는 반드시 위 네 가지 중 **하나만** 선택되어야 합니다. (중복 선택 불가)

### 도구 사용 지침

1. **search_places_by_keyword** 도구  
   - query는 반드시 `"위치명 + 카테고리"` 형식
   - 이 도구로 여행지 장소를 검색하세요.

2. **scrape_tool** 도구  
   - 각 검색 결과의 `place_url`을 사용해 장소의 **운영시간** 정보를 크롤링하세요.

### 응답 형식 예시

최종 결과는 아래 형식으로 정리하여 사용자에게 제공합니다:

- 이름: (장소 이름)
- 주소: (전체 주소)
- 카테고리: 관광명소 | 숙박 | 음식점 | 카페
- 전화번호: (가능한 경우)
- 운영시간: (scrape_tool 결과 기반)
- 상세 링크: (place_url)

---

🎯 목표는 사용자의 의도를 명확히 파악하여 적절한 장소 정보를 **정확하고 구조적으로** 제공하는 것입니다.
모호하거나 누락된 정보가 있다면 반드시 추가 질문을 통해 보완한 뒤, 검색을 진행하세요.

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