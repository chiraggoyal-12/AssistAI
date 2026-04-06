import base64
import json
import os
import re
from datetime import datetime, timedelta

import httpx
import streamlit as st
from dotenv import load_dotenv
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from langchain.agents import AgentExecutor, create_openai_functions_agent
from langchain.prompts import MessagesPlaceholder
from langchain.tools import tool
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from proto import Message

# ================== ENV ==================
load_dotenv()

# ================== LLM ==================
def get_llm():
  api_key = os.getenv("OPENAI_API_KEY")

  if not api_key:
    raise ValueError("❌ OPENAI_API_KEY not found.")

  client = httpx.Client(trust_env=False)

  return ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0,
    http_client=client
  )

# ================== GOOGLE AUTH ==================
SCOPES = [
  "https://www.googleapis.com/auth/gmail.readonly",
  "https://www.googleapis.com/auth/calendar"
]

def get_gmail_service():
  creds = None

  if os.path.exists("token.json"):
    creds = Credentials.from_authorized_user_file("token.json", SCOPES)

  if not creds or not creds.valid:
    if creds and creds.expired and creds.refresh_token:
      creds.refresh(Request())
    else:
      flow = InstalledAppFlow.from_client_secrets_file(
          "credentials.json", SCOPES
      )
      creds = flow.run_local_server(port=0)

    with open("token.json", "w") as token:
      token.write(creds.to_json())

  return build("gmail", "v1", credentials=creds)

def get_calendar_service():
    creds = get_gmail_service()._http.credentials
    return build("calendar", "v3", credentials=creds)

# ================== TOOLS ==================

@tool
def read_emails(input_text: str = "latest emails") -> str:
    """Fetch latest emails from Gmail."""
    service = get_gmail_service()

    results = service.users().messages().list(
        userId="me",
        maxResults=5
    ).execute()

    messages = results.get("messages", [])
    email_texts = []

    for msg in messages:
        msg_data = service.users().messages().get(
            userId="me",
            id=msg["id"],
            format="full"
        ).execute()

        parts = msg_data.get("payload", {}).get("parts", [])

        for part in parts:
            if part["mimeType"] == "text/plain":
                data = part["body"]["data"]
                text = base64.urlsafe_b64decode(data).decode("utf-8")
                email_texts.append(text)

    return "\n\n".join(email_texts[:3]) if email_texts else "No emails found."


@tool
def generate_todo(text: str) -> str:
    """Generate structured to-do list with priorities."""
    llm = get_llm()

    prompt = f"""
    Convert into actionable tasks:

    {text}

    Format:
    - Task (Priority: High/Medium/Low)
    """

    return llm.invoke(prompt).content


@tool
def schedule_event(details: str) -> str:
    """Schedule an event in Google Calendar.
      Use this tool whenever the user wants to:
    - schedule a meeting
    - book an appointment
    - create a calendar event

    Input should be natural language describing the event.
    """
    llm = get_llm()

    # ⚠️ FIXED: variable name bug (text → details)
    prompt = f"""
    Extract event details from this text:

    "{details}"
    Rules:
    - Convert relative dates like "tomorrow" into exact date (YYYY-MM-DD)
    - Use 24-hour format for time
    - Return ONLY JSON (no text)

    Return JSON:
    {{
      "title": "Event Title",
      "date": "YYYY-MM-DD",
      "time": "HH:MM",
      "duration_minutes": 60
    }}
    """

    response = llm.invoke(prompt).content


    # ✅ Extract JSON safely
    match = re.search(r"\{.*\}", response, re.DOTALL)

    if not match:
      return f"❌ Could not extract JSON.\nLLM output:\n{response}"

    try:
        event_data = json.loads(match.group())
    except:
        return f"❌ Failed to parse event.\nLLM output:\n{response}"
    
    
    # ⚠️ FIXED: "data" → "date"
    start_time = datetime.strptime(
        event_data["date"] + " " + event_data["time"],
        "%Y-%m-%d %H:%M"
    )

    end_time = start_time + timedelta(
        minutes=event_data["duration_minutes"]
    )

    service = get_calendar_service()

    event = {
      "summary": event_data["title"],
      "start": {
        "dateTime": start_time.isoformat(),
        "timeZone": "Asia/Kolkata"
      },
      "end": {
        "dateTime": end_time.isoformat(),
        "timeZone": "Asia/Kolkata"
      },
    }

    print("📅 Creating event:", event)

    try:
      created_event = service.events().insert(
        calendarId="primary",
        body=event
      ).execute()

      print("✅ Event created:", created_event.get("htmlLink"))

      return f"✅ Event scheduled: {event_data['title']} on {event_data['date']}"
    
    except Exception as e:
        return f"❌ Failed to create event: {str(e)}"

# ================== AGENT ==================

def get_agent_executor():
    llm = get_llm()

    tools = [
        read_emails,
        generate_todo,
        schedule_event
    ]

    prompt = ChatPromptTemplate.from_messages([
        ("system", """You are an AI personal assistant.

        CRITICAL RULES:

        1. If the user asks to schedule, book, or create an event:
          → You MUST call the `schedule_event` tool.
          → DO NOT respond directly.
          → DO NOT say "scheduled" unless the tool has executed.

        2. The `schedule_event` tool creates real events in Google Calendar.

        3. Never fake actions. Only confirm after tool execution.
         
        Use tools when needed:
        - Emails → read_emails
        - Tasks → generate_todo
        - Scheduling → schedule_event

        Always choose the best tool.
        """),
        ("human", "{input}"),

        MessagesPlaceholder(variable_name="agent_scratchpad")
    ])

    agent = create_openai_functions_agent(llm, tools, prompt)

    return AgentExecutor(
        agent=agent,
        tools=tools,
        verbose=True
    )

def run_agent(user_input):
    agent_executor = get_agent_executor()
    return agent_executor.invoke({"input": user_input})["output"]

# ================== STREAMLIT UI ==================

st.set_page_config(page_title="AI Assistant")
st.title("🤖 AI Personal Assistant")

if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

user_input = st.chat_input("What can I help you with?")

if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})

    with st.chat_message("user"):
        st.write(user_input)

    with st.spinner("Thinking..."):
        response = run_agent(user_input)

    with st.chat_message("assistant"):
        st.write(response)

    st.session_state.messages.append(
        {"role": "assistant", "content": response}
    )