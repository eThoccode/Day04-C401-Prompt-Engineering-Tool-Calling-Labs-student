from __future__ import annotations
import json
import os
import time
from datetime import datetime
from pathlib import Path
import streamlit as st

from env_loader import load_lab_env
from providers import make_provider
from providers.base import ToolCall
from tools import TOOL_FUNCTIONS, load_tool_declarations, to_openai_tools
from versioning import build_artifact_version

# Load environment
ROOT = Path(__file__).parent
ARTIFACTS_DIR = ROOT / "artifacts"
load_lab_env(ROOT)

# UI Configuration
st.set_page_config(
    page_title="Research Agent Web UI",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Premium Sleek CSS
st.markdown("""
<style>
    .main { background-color: #0f111a; color: #e2e8f0; }
    .stSidebar { background-color: #1a1d2e; border-right: 1px solid #2e344e; }
    h1, h2, h3 { color: #58c4dc !important; font-family: 'Inter', sans-serif; }
    .chat-bubble-user { background-color: #1e293b; padding: 12px 18px; border-radius: 15px 15px 0 15px; margin-bottom: 10px; color: #f8fafc; }
    .chat-bubble-agent { background-color: #1e1b4b; padding: 12px 18px; border-radius: 15px 15px 15px 0; margin-bottom: 10px; border-left: 4px solid #6366f1; color: #f8fafc; }
    .stButton>button { background-color: #6366f1 !important; color: white !important; border-radius: 8px !important; border: none !important; }
    .tool-log { background-color: #020617; border-left: 3px solid #f59e0b; padding: 8px 12px; font-family: monospace; font-size: 13px; color: #f1f5f9; border-radius: 5px; margin-top: 5px; }
</style>
""", unsafe_allow_html=True)

st.title("🤖 Advanced Research Agent Web UI")
st.subheader("Day 04 Lab - Pair Programming with Antigravity AI")

# Sidebar configs
with st.sidebar:
    st.header("⚙️ Agent & Provider Configuration")
    provider_name = st.selectbox("Model Provider", ["openrouter", "gemini", "openai", "anthropic"], index=0)
    
    # Custom model selection
    default_models = {
        "openrouter": "google/gemini-2.5-flash",
        "gemini": "gemini-3.5-flash",
        "openai": "gpt-4o-mini",
        "anthropic": "claude-3-5-sonnet-20241022"
    }
    model_name = st.text_input("Model Name (Override)", value=default_models[provider_name])
    version = st.text_input("Version Label", value="v1")
    
    st.divider()
    st.header("🛠️ Available Active Tools")
    try:
        tools_yaml = load_tool_declarations(ARTIFACTS_DIR / "tools.yaml")
        for t in tools_yaml:
            with st.expander(f"🔧 {t['name']}"):
                st.caption(t.get("description", "No description available"))
                st.code(json.dumps(t.get("parameters", {}).get("properties", {}), indent=2, ensure_ascii=False), language="json")
    except Exception as e:
        st.error(f"Error loading tools schema: {e}")

# Initialize chat session state
if "messages" not in st.session_state:
    st.session_state.messages = []
if "history" not in st.session_state:
    st.session_state.history = []
if "awaiting_clarify" not in st.session_state:
    st.session_state.awaiting_clarify = None # holds dict of clarify options if waiting

# Setup loader & prompt
try:
    system_prompt = (ARTIFACTS_DIR / "system_prompt.md").read_text(encoding="utf-8")
    tool_declarations = load_tool_declarations(ARTIFACTS_DIR / "tools.yaml")
    openai_tools = to_openai_tools(tool_declarations)
    provider = make_provider(provider_name)
    artifact_version = build_artifact_version(version, ARTIFACTS_DIR / "system_prompt.md", ARTIFACTS_DIR / "tools.yaml")
except Exception as e:
    st.error(f"Initialization Error: {e}")
    st.stop()

# Helper functions
def json_text(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, indent=2, default=str)

def execute_tool_call(call: ToolCall) -> dict[str, Any]:
    func = TOOL_FUNCTIONS.get(call.name)
    if not func:
        return {
            "tool": call.name,
            "args": call.args,
            "result": {"error": "unknown_tool", "message": f"No local implementation for {call.name}"},
        }
    try:
        result = func(**call.args)
    except Exception as exc:
        result = {"error": type(exc).__name__, "message": str(exc)}
    return {"tool": call.name, "args": call.args, "result": result}

def render_tool_event(event: dict[str, Any]):
    with st.container():
        st.markdown(f"<div class='tool-log'>🔧 Tool Executed: <b>{event['tool']}</b><br/>Args: {json.dumps(event['args'], ensure_ascii=False)}</div>", unsafe_allow_html=True)
        if "error" in event.get("result", {}):
            st.error(f"Tool Error: {event['result']['message']}")
        else:
            with st.expander("👁️ View Tool Output"):
                st.json(event["result"])

# Render Chat History
for msg in st.session_state.messages:
    if msg["role"] == "user":
        st.markdown(f"<div class='chat-bubble-user'>👤 <b>You:</b><br/>{msg['content']}</div>", unsafe_allow_html=True)
    elif msg["role"] == "assistant":
        st.markdown(f"<div class='chat-bubble-agent'>🤖 <b>Agent:</b><br/>{msg['content']}</div>", unsafe_allow_html=True)
    elif msg["role"] == "tool_log":
        render_tool_event(msg["event"])

# If waiting for clarify
if st.session_state.awaiting_clarify:
    clarify_data = st.session_state.awaiting_clarify
    st.warning(f"💬 Clarification needed: **{clarify_data['question']}**")
    
    if clarify_data["response_type"] == "yes_no":
        col1, col2 = st.columns(2)
        with col1:
            if st.button("👍 Yes / Confirm"):
                user_reply = "yes"
                st.session_state.messages.append({"role": "user", "content": user_reply})
                st.session_state.history.append({"role": "user", "content": user_reply})
                st.session_state.awaiting_clarify = None
                st.rerun()
        with col2:
            if st.button("👎 No / Cancel"):
                user_reply = "no"
                st.session_state.messages.append({"role": "user", "content": user_reply})
                st.session_state.history.append({"role": "user", "content": user_reply})
                st.session_state.awaiting_clarify = None
                st.rerun()
    else:
        with st.form("clarify_form"):
            user_reply = st.text_input("Enter your reply here:")
            submitted = st.form_submit_button("Submit Reply")
            if submitted and user_reply.strip():
                st.session_state.messages.append({"role": "user", "content": user_reply})
                st.session_state.history.append({"role": "user", "content": user_reply})
                st.session_state.awaiting_clarify = None
                st.rerun()
    st.stop()

# Input Bar
user_input = st.chat_input("Ask the Research Agent anything...")

if user_input:
    # Append user turn
    st.session_state.messages.append({"role": "user", "content": user_input})
    st.session_state.history.append({"role": "user", "content": user_input})
    st.markdown(f"<div class='chat-bubble-user'>👤 <b>You:</b><br/>{user_input}</div>", unsafe_allow_html=True)
    
    # Run loop
    working_messages = [
        {"role": "system", "content": system_prompt},
        *st.session_state.history[-10:] # Keep latest window in context
    ]
    
    max_tool_rounds = 4
    clarify_encountered = False
    assistant_final_response = ""
    
    with st.spinner("🧠 Reasoning and calling tools..."):
        for round_index in range(1, max_tool_rounds + 1):
            response = provider.complete(working_messages, openai_tools, model=model_name, temperature=0.0)
            calls = response.tool_calls
            
            if not calls:
                assistant_final_response = response.text or ""
                break
                
            # Document assistant intent
            assistant_content = response.text or "Calling tools..."
            working_messages.append({
                "role": "assistant",
                "content": f"{assistant_content}\n\nTOOL_CALLS_JSON:\n{json_text([{'name': c.name, 'args': c.args} for c in calls])}"
            })
            
            non_clarification_events = []
            
            for call in calls:
                # Execute tool
                event = execute_tool_call(call)
                st.session_state.messages.append({"role": "tool_log", "event": event})
                render_tool_event(event)
                
                # Check for clarify wait
                result = event.get("result", {})
                if isinstance(result, dict) and result.get("awaiting_user"):
                    question = result.get("question") or call.args.get("question") or "Vui lòng cung cấp thêm thông tin."
                    st.session_state.awaiting_clarify = {
                        "question": question,
                        "response_type": result.get("response_type", "text"),
                        "options": result.get("options", [])
                    }
                    clarify_encountered = True
                    assistant_final_response = question
                    break
                    
                non_clarification_events.append(event)
                
            if clarify_encountered:
                break
                
            # Append tool results for next round
            working_messages.append({
                "role": "user",
                "content": f"TOOL_RESULTS_JSON:\n{json_text(non_clarification_events)}\n\nUse these results to reply."
            })
            # Sleep slightly between rounds
            time.sleep(1.0)
            
    # Append assistant final response
    st.session_state.messages.append({"role": "assistant", "content": assistant_final_response})
    st.session_state.history.append({"role": "assistant", "content": assistant_final_response})
    
    st.rerun()
