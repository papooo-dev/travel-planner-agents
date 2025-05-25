from langgraph.prebuilt import create_react_agent
import requests
import os
from typing import Dict, List
from langchain_core.tools import tool
from dotenv import load_dotenv
from langchain_tavily import TavilySearch
from backend import store
from langchain.chat_models import init_chat_model


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
            "place_phone": place.get("phone"),
            "place_x": place.get("x"),
            "place_y": place.get("y"),
        }
        results.append(place_dict)

    return results


web_search_tool = TavilySearch(
    max_results=10,
    topic="general",
    # include_answer=False,
    # include_raw_content=False,
    # include_images=False,
    # include_image_descriptions=False,
    search_depth="advanced",
    # time_range="day",
    # include_domains=None,
    # exclude_domains=None
)

# 장소 검색 에이전트 생성
place_search_agent = create_react_agent(
    model=init_chat_model(model=os.getenv("PLACE_SEARCH_MODEL"), temperature=0.0),
    tools=[web_search_tool, place_detail_tool, store.save_place_info],
    store=store,
    version="v2",
    prompt="""당신은 여행 관련 장소를 검색하는 전문 에이전트입니다.  
사용자로부터 Supervisor Agent를 통해 전달받은 **지역**과 **키워드**를 기반으로,  
아래 두 가지 툴을 사용해 여행 장소 정보를 수집하고 가공합니다.

---

## 당신이 사용할 수 있는 툴:

### `WebSearchTool`
- 목적: 입력받은 지역과 키워드를 조합하여 관련된 여행지, 맛집, 관광명소, 카페 등을 웹에서 검색합니다.
- 출력 예: 장소 이름, 대략적인 설명

### `PlaceDetailTool`
- 목적: Tool1을 통해 얻은 장소 이름을 기반으로, 해당 장소의 상세 정보(주소, 전화번호, 운영시간 등)를 조회합니다.

### `save_place_info`
- 목적: 검색된 장소 정보를 저장합니다.

---

## 작동 흐름:

1. Supervisor Agent가 제공한 지역과 키워드를 조합하여 **`WebSearchTool`**을 사용해 웹에서 장소를 검색합니다.
2. 결과에서 관련성이 높고 다양한 장소를 3~7개 선택합니다.
3. 각 장소에 대해 **`PlaceDetailTool`**를 호출하여 상세 정보를 조회합니다.
4. 조회 결과를 **`save_place_info`**를 통해 저장합니다.

---

## 최종 출력 포맷:

```json
[
    {
        "place_name": "장소명",
        "place_description": "장소 설명",
        "address_name": "주소",
        "place_url": "상세링크",
        "category_name": "카테고리",
        "phone": "전화번호",
        "x": "x좌표",
        "y": "y좌표",
    },
    ...
]

""",
    name="place_search_assistant",
).with_config(tags=["place_search_agent"])

if __name__ == "__main__":
    user_input = "부산 가족 여행"
    # result = search_places_by_keyword.invoke(user_input)
    # for place in result:
    #     print(len(result))
    #     print(place)
    # # print(search_places_by_keyword.invoke(user_input))
    for token, metadata in place_search_agent.stream(
        {"messages": [{"role": "user", "content": user_input}]}, stream_mode="messages"
    ):
        print("Token", token)
        print("Metadata", metadata)
        print("\n")
