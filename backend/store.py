from langgraph.store.memory import InMemoryStore
from typing_extensions import TypedDict
from langchain_core.runnables import RunnableConfig
from langgraph.config import get_store
from langchain_core.tools import tool

store = InMemoryStore()


class Place(TypedDict):
    place_name: str
    place_description: str
    place_address: str
    place_url: str
    place_category: str
    place_phone: str
    place_x: float
    place_y: float


class TravelSchedule(TypedDict):
    travel_schedule: str


class TravelInfo(TypedDict):
    location: str  # 여행 지역 이름 (예: "부산", "제주도")
    start_date: str # 여행 시작 날짜 (YYYY-MM-DD 형식)
    end_date: str # 여행 종료 날짜 (YYYY-MM-DD 형식)


@tool
def save_travel_info(config: RunnableConfig, travel_info: TravelInfo):
    """여행 정보를 저장하는 도구입니다.

    사용자가 입력한 여행 지역과 키워드를 저장합니다.

    Args:
        config: 실행 설정 정보
        travel_info: 여행 지역(location)과 여행일정(start_date, end_date) 정보를 포함하는 객체
    """
    memory_store = get_store()
    thread_id = config.get("configurable", {}).get("thread_id")
    memory_store.put(
        (thread_id, "travel_info"),
        thread_id,
        travel_info,
    )


@tool
def get_travel_info(config: RunnableConfig) -> TravelInfo | None:
    """저장된 여행 정보를 조회하는 도구입니다.

    이전에 저장된 여행 지역과 키워드 정보를 가져옵니다.

    Args:
        config: 실행 설정 정보

    Returns:
        TravelInfo: 저장된 여행 지역과 여행 일정 정보
    """
    memory_store = get_store()
    thread_id = config.get("configurable", {}).get("thread_id")
    return memory_store.get(
        (thread_id, "travel_info"),
        thread_id,
    )


@tool
def save_place_info(config: RunnableConfig, place_name: str, place_dict: Place):
    """장소 정보를 저장하는 도구입니다.

    검색한 여행 장소의 상세 정보를 저장합니다.

    Args:
        config: 실행 설정 정보
        place_name: 장소 이름
        place_dict: 장소의 상세 정보를 포함하는 Place 객체
    """
    memory_store = get_store()
    memory_store.put(
        (config.get("configurable", {}).get("thread_id"), "places"),
        place_name,
        place_dict,
    )


@tool
def get_place_info(config: RunnableConfig) -> Place | None:
    """저장된 장소 정보를 조회하는 도구입니다.

    이전에 저장된 여행 장소의 상세 정보를 가져옵니다.

    Args:
        config: 실행 설정 정보

    Returns:
        Place: 저장된 장소 정보
    """
    memory_store = get_store()
    return memory_store.search(
        (config.get("configurable", {}).get("thread_id"), "places")
    )


@tool
def save_travel_schedule(config: RunnableConfig, travel_schedule: TravelSchedule):
    """여행 일정표(계획서)을 저장하는 도구입니다.

    생성된 여행 일정표(계획서)을 저장합니다.

    Args:
        config: 실행 설정 정보
        travel_schedule: 여행 일정 정보를 포함하는 객체
    """
    memory_store = get_store()
    thread_id = config.get("configurable", {}).get("thread_id")
    memory_store.put(
        (thread_id, "travel_schedule"),
        thread_id,
        travel_schedule,
    )


@tool
def get_travel_schedule(config: RunnableConfig) -> TravelSchedule | None:
    """저장된 여행 일정표(계획)을 조회하는 도구입니다.

    이전에 저장된 여행 일정표 정보를 가져옵니다.

    Args:
        config: 실행 설정 정보

    Returns:
        TravelSchedule: 저장된 여행 일정표 정보
    """
    memory_store = get_store()
    thread_id = config.get("configurable", {}).get("thread_id")
    return memory_store.get(
        (thread_id, "travel_schedule"),
        thread_id,
    )

