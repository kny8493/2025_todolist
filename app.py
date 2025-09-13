"""
ToDoList 웹 애플리케이션
Python Streamlit을 사용한 할 일 관리 시스템

기능:
- 할 일 추가/삭제/완료/수정
- 필터링 (전체/미완료/완료)
- 통계 표시
- 세션 상태 유지
"""

import streamlit as st
from typing import List, Dict, Any
from datetime import datetime


def initialize_session_state() -> None:
    """세션 상태 초기화"""
    if 'todos' not in st.session_state:
        st.session_state.todos = []
    if 'next_id' not in st.session_state:
        st.session_state.next_id = 1


def add_todo(text: str) -> None:
    """할 일 추가"""
    if text.strip():
        todo = {
            'id': st.session_state.next_id,
            'text': text.strip(),
            'completed': False,
            'created_at': datetime.now().strftime("%Y-%m-%d %H:%M")
        }
        st.session_state.todos.append(todo)
        st.session_state.next_id += 1


def delete_todo(todo_id: int) -> None:
    """할 일 삭제"""
    st.session_state.todos = [todo for todo in st.session_state.todos if todo['id'] != todo_id]


def toggle_todo(todo_id: int) -> None:
    """할 일 완료/미완료 토글"""
    for todo in st.session_state.todos:
        if todo['id'] == todo_id:
            todo['completed'] = not todo['completed']
            break


def update_todo(todo_id: int, new_text: str) -> None:
    """할 일 텍스트 수정"""
    if new_text.strip():
        for todo in st.session_state.todos:
            if todo['id'] == todo_id:
                todo['text'] = new_text.strip()
                break


def get_filtered_todos(filter_type: str) -> List[Dict[str, Any]]:
    """필터에 따른 할 일 목록 반환"""
    if filter_type == "완료":
        return [todo for todo in st.session_state.todos if todo['completed']]
    elif filter_type == "미완료":
        return [todo for todo in st.session_state.todos if not todo['completed']]
    else:  # "전체"
        return st.session_state.todos


def get_statistics() -> Dict[str, int]:
    """통계 정보 계산"""
    total = len(st.session_state.todos)
    completed = sum(1 for todo in st.session_state.todos if todo['completed'])
    pending = total - completed
    
    return {
        'total': total,
        'completed': completed,
        'pending': pending
    }


def mark_all_completed() -> None:
    """모든 할 일 완료 처리"""
    for todo in st.session_state.todos:
        todo['completed'] = True


def delete_all_todos() -> None:
    """모든 할 일 삭제"""
    st.session_state.todos = []


def render_header() -> None:
    """헤더 및 제목 렌더링"""
    st.title("📋 ToDoList")
    st.markdown("---")


def render_statistics() -> None:
    """통계 정보 렌더링"""
    stats = get_statistics()
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("총 개수", stats['total'])
    
    with col2:
        st.metric("완료", stats['completed'])
    
    with col3:
        st.metric("진행 중", stats['pending'])
    
    st.markdown("---")


def render_input_section() -> None:
    """할 일 입력 섹션 렌더링"""
    st.subheader("➕ 새 할 일 추가")
    
    # 입력창 초기화 상태 관리
    if 'clear_input' not in st.session_state:
        st.session_state.clear_input = False
    
    col1, col2 = st.columns([4, 1])
    
    with col1:
        # 입력창 초기화가 필요한 경우 빈 값으로 설정
        input_value = "" if st.session_state.clear_input else st.session_state.get("new_todo_input", "")
        
        new_todo = st.text_input(
            "할 일을 입력하세요",
            value=input_value,
            placeholder="예: 프로젝트 계획서 작성",
            key="new_todo_input"
        )
        
        # 초기화 플래그 리셋
        if st.session_state.clear_input:
            st.session_state.clear_input = False
    
    with col2:
        if st.button("추가", type="primary", use_container_width=True):
            if new_todo.strip():  # 빈 값이 아닐 때만 추가
                add_todo(new_todo)
                # 입력창 초기화 플래그 설정
                st.session_state.clear_input = True
                st.rerun()
    
    st.markdown("---")


def render_filter_section() -> None:
    """필터 섹션 렌더링"""
    st.subheader("🔍 필터")
    
    filter_options = ["전체", "미완료", "완료"]
    selected_filter = st.selectbox(
        "상태별로 필터링",
        options=filter_options,
        key="filter_select"
    )
    
    return selected_filter


def render_todo_list(filter_type: str) -> None:
    """할 일 목록 렌더링"""
    st.subheader("📝 할 일 목록")
    
    filtered_todos = get_filtered_todos(filter_type)
    
    if not filtered_todos:
        st.info("할 일이 없습니다. 새로운 할 일을 추가해보세요!")
        return
    
    for todo in filtered_todos:
        render_todo_item(todo)


def render_todo_item(todo: Dict[str, Any]) -> None:
    """개별 할 일 항목 렌더링"""
    col1, col2, col3, col4 = st.columns([1, 6, 1, 1])
    
    with col1:
        # 완료 체크박스
        completed = st.checkbox(
            "완료",
            value=todo['completed'],
            key=f"checkbox_{todo['id']}",
            on_change=toggle_todo,
            args=(todo['id'],),
            label_visibility="collapsed"
        )
    
    with col2:
        # 할 일 텍스트 (편집 모드 처리)
        if f"edit_mode_{todo['id']}" not in st.session_state:
            st.session_state[f"edit_mode_{todo['id']}"] = False
        
        if st.session_state[f"edit_mode_{todo['id']}"]:
            # 편집 모드
            new_text = st.text_input(
                "",
                value=todo['text'],
                key=f"edit_input_{todo['id']}",
                label_visibility="collapsed"
            )
        else:
            # 표시 모드
            text_style = "text-decoration: line-through; color: #666;" if todo['completed'] else ""
            st.markdown(f'<p style="{text_style}">{todo["text"]}</p>', unsafe_allow_html=True)
    
    with col3:
        # 편집 버튼
        if st.session_state[f"edit_mode_{todo['id']}"]:
            if st.button("💾", key=f"save_{todo['id']}", help="저장"):
                new_text = st.session_state[f"edit_input_{todo['id']}"]
                update_todo(todo['id'], new_text)
                st.session_state[f"edit_mode_{todo['id']}"] = False
                st.rerun()
        else:
            if st.button("✏️", key=f"edit_{todo['id']}", help="편집"):
                st.session_state[f"edit_mode_{todo['id']}"] = True
                st.rerun()
    
    with col4:
        # 삭제 버튼
        if st.button("🗑️", key=f"delete_{todo['id']}", help="삭제"):
            delete_todo(todo['id'])
            st.rerun()
    
    # 할 일 생성 시간 표시
    st.caption(f"생성: {todo['created_at']}")
    st.markdown("---")


def render_bulk_actions() -> None:
    """일괄 작업 버튼 렌더링"""
    st.subheader("⚡ 일괄 작업")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("✅ 전체 완료", use_container_width=True, type="secondary"):
            mark_all_completed()
            st.rerun()
    
    with col2:
        if st.button("🗑️ 전체 삭제", use_container_width=True, type="secondary"):
            delete_all_todos()
            st.rerun()


def main() -> None:
    """메인 애플리케이션 함수"""
    # 페이지 설정
    st.set_page_config(
        page_title="ToDoList",
        page_icon="📋",
        layout="wide",
        initial_sidebar_state="collapsed"
    )
    
    # 세션 상태 초기화
    initialize_session_state()
    
    # UI 렌더링
    render_header()
    render_statistics()
    render_input_section()
    
    filter_type = render_filter_section()
    st.markdown("---")
    
    render_todo_list(filter_type)
    render_bulk_actions()
    
    # 푸터
    st.markdown("---")
    st.markdown(
        "<div style='text-align: center; color: #666;'>"
        "💡 <strong>팁:</strong> 체크박스를 클릭하여 완료 상태를 변경하고, "
        "편집 버튼으로 할 일을 수정할 수 있습니다."
        "</div>",
        unsafe_allow_html=True
    )


if __name__ == "__main__":
    main()
