# AssistAI
# 🤖 AI Personal Assistant

An AI-powered personal assistant built using **LangChain, OpenAI, and Google APIs**.

This assistant can read emails, schedule calendar events, and generate to-do lists — all through a conversational interface.

---

## 🚀 Features

- 💬 Chat-based assistant interface  
- 📧 Fetch and read recent Gmail emails  
- 📅 Schedule real events in Google Calendar  
- ✅ Generate structured to-do lists with priorities  
- 🧠 Tool-using AI agent (function calling)  
- ⚡ Real-time interaction using Streamlit  

---

## 🛠️ Tech Stack

- Frontend: Streamlit  
- LLM: OpenAI (`gpt-4o-mini`)  
- Framework: LangChain Agents  
- APIs: Gmail API, Google Calendar API  
- Auth: OAuth 2.0  

---

## 📁 Project Structure

    .
    ├── app.py              # Main application
    ├── credentials.json    # Google OAuth credentials (DO NOT COMMIT)
    ├── token.json          # Generated after login (DO NOT COMMIT)
    ├── .env                # OpenAI API key (DO NOT COMMIT)
    ├── requirements.txt
    └── README.md

---

## ⚙️ Installation

### 1. Clone the repository

    git clone https://github.com/your-username/ai-personal-assistant.git
    cd ai-personal-assistant

### 2. Create virtual environment

    python -m venv venv
    venv\Scripts\activate   # Windows
    # or
    source venv/bin/activate  # Mac/Linux

### 3. Install dependencies

    pip install -r requirements.txt

---

## 🔑 Setup

### OpenAI API Key

Create a `.env` file:

    OPENAI_API_KEY=your_api_key_here

---

### Google API Setup

1. Go to Google Cloud Console  
2. Enable:
   - Gmail API  
   - Google Calendar API  
3. Create OAuth credentials  
4. Download `credentials.json`  
5. Place it in the project root  

---

## ▶️ Run the App

    streamlit run app.py

---

## 🧠 How It Works

1. User enters a request  
2. LangChain agent selects the appropriate tool:
   - Emails → read_emails  
   - Tasks → generate_todo  
   - Scheduling → schedule_event  
3. Tool executes real action via APIs  
4. Assistant returns the result  

---

## 🔧 Tools

- read_emails → Fetch Gmail messages  
- generate_todo → Create prioritized task list  
- schedule_event → Create Google Calendar events  

---

## 🧪 Example Prompts

- "Show my latest emails"  
- "Create a to-do list for my day"  
- "Schedule a meeting tomorrow at 5 PM"  

---

## ⚠️ Security Notes

- Never commit:
  - credentials.json  
  - token.json  
  - .env  

Add them to `.gitignore`:

    credentials.json
    token.json
    .env

---

## ⚠️ Limitations

- Requires Google OAuth setup  
- No persistent database  
- Basic UI  

---

## 🔮 Future Improvements

- Email summarization  
- Notifications and reminders  
- Multi-user support  
- Voice assistant  

---

## 🤝 Contributing

Feel free to fork and submit improvements 🚀

---

## 📜 License

MIT License

---

## 💡 Author

Built with ❤️ using LangChain, OpenAI, and Google APIs
