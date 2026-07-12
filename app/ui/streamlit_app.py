import os
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[2]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

import streamlit as st

from app.graphs.workflow_graph import run_support_workflow


def main() -> None:
    st.set_page_config(page_title="ABC Support Agent", page_icon="💬")
    st.title("ABC Technologies Support Agent")

    if "conversation_id" not in st.session_state:
        st.session_state.conversation_id = None

    with st.form("chat_form"):
        customer_name = st.text_input("Your name", value="Valued Customer")
        user_query = st.text_area("How can we help you today?")
        submitted = st.form_submit_button("Send")

    if submitted and user_query.strip():
        result = run_support_workflow(
            customer_name=customer_name,
            query=user_query,
            conversation_id=st.session_state.conversation_id,
        )
        st.session_state.conversation_id = result.get("conversation_id")
        st.success(result.get("response", ""))
        st.caption(
            f"Intent: {result.get('intent', '')} | "
            f"Department: {result.get('department', '')} | "
            f"Approval: {result.get('approval_status', 'not_required')}"
        )


if __name__ == "__main__":
    main()
