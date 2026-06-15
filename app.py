from flask import Flask, request, jsonify, render_template_string
import re

app = Flask(__name__)

# ─────────────────────────────────────────────
#  RULE-BASED KNOWLEDGE BASE
# ─────────────────────────────────────────────
RULES = [
    # Greetings
    {
        "patterns": [r"\b(hi|hello|hey|howdy|greetings|good morning|good afternoon|good evening)\b"],
        "response": "👋 Hello! Welcome to **CampusBot** — your 24/7 campus assistant!\n\nI can help you with:\n• 📅 Exam schedules & timetables\n• 📚 Library & study resources\n• 🏫 Admission & registration\n• 🍽️ Canteen & hostel info\n• 🏥 Health & counselling services\n• 📞 Contact details\n\nWhat would you like to know?"
    },
    # Farewell
    {
        "patterns": [r"\b(bye|goodbye|see you|take care|later|exit|quit)\b"],
        "response": "👋 Goodbye! Have a great day. Feel free to come back anytime — CampusBot is always here for you! 😊"
    },
    # Thanks
    {
        "patterns": [r"\b(thanks|thank you|thank u|thx|cheers)\b"],
        "response": "You're welcome! 😊 Is there anything else I can help you with?"
    },
    # Exam schedule
    {
        "patterns": [r"\b(exam|exams|examination|test|mid.?term|end.?term|semester exam)\b"],
        "response": "📅 **Exam Schedule Information**\n\n• **Mid-Term Exams:** Week 8 of each semester\n• **End-Term Exams:** Week 16–17 of each semester\n• **Practical Exams:** As announced by respective departments\n\n📌 Check the official exam schedule on the **Student Portal → Academics → Exam Schedule**\n\n⚠️ Admit cards are available 5 days before exams. Any more questions about exams?"
    },
    # Timetable
    {
        "patterns": [r"\b(timetable|time table|class schedule|lecture schedule|schedule)\b"],
        "response": "🗓️ **Class Timetable**\n\n• Timetables are posted on the **Student Portal** at the start of each semester.\n• You can also check the **Notice Board** outside your department office.\n• Classes run **Monday–Friday, 9:00 AM – 5:00 PM**\n• Saturday: Special/extra classes only (as announced)\n\nNeed help navigating the student portal?"
    },
    # Library
    {
        "patterns": [r"\b(library|books|borrow|return book|reading room|e-library|digital library)\b"],
        "response": "📚 **Library Services**\n\n• **Location:** Block C, Ground Floor\n• **Hours:** Mon–Fri: 8:00 AM – 8:00 PM | Sat: 9:00 AM – 5:00 PM\n• **Book Borrowing:** Up to 3 books for 14 days\n• **E-Library:** Access via Student Portal → Library → E-Resources\n• **Late Fine:** ₹2 per day per book\n\n📞 Library Desk: ext. 204\n\nAnything else about the library?"
    },
    # Admission
    {
        "patterns": [r"\b(admission|admissions|apply|application|enrollment|enroll|joining)\b"],
        "response": "🏫 **Admission Information**\n\n• **Undergraduate:** Applications open in April–May\n• **Postgraduate:** Applications open in June–July\n• **Documents Required:** 10th & 12th marksheets, ID proof, passport photos, transfer certificate\n• **Admission Office:** Block A, Room 101\n• **Hours:** Mon–Fri, 10:00 AM – 4:00 PM\n\n📧 admissions@campus.edu\n📞 +91-98765-43210\n\nDo you need info about a specific programme?"
    },
    # Fees
    {
        "patterns": [r"\b(fee|fees|tuition|payment|pay|scholarship|finance)\b"],
        "response": "💳 **Fee & Payment Information**\n\n• **Fee Payment Portal:** Student Portal → Finance → Pay Fees\n• **Payment Modes:** Online (UPI, Net Banking, Card) or Demand Draft\n• **Due Date:** 30th of the first month of each semester\n• **Late Fee:** ₹500 after due date\n\n🎓 **Scholarships:** Visit Block A, Room 105 or email scholarships@campus.edu\n\n📞 Finance Office: ext. 210\n\nNeed help with anything else?"
    },
    # Hostel
    {
        "patterns": [r"\b(hostel|dorm|dormitory|accommodation|pg|paying guest|room|stay)\b"],
        "response": "🏠 **Hostel & Accommodation**\n\n• **Boys Hostel:** Block H1 & H2 (capacity: 500 students)\n• **Girls Hostel:** Block H3 (capacity: 300 students)\n• **Facilities:** Wi-Fi, laundry, 24/7 security, common room, indoor games\n• **Mess Timings:** Breakfast 7–9 AM | Lunch 12–2 PM | Dinner 7–9 PM\n• **Hostel Fee:** Included in annual fees (optional)\n\n📞 Hostel Warden: ext. 220\n📧 hostel@campus.edu\n\nAny other questions?"
    },
    # Canteen / Food
    {
        "patterns": [r"\b(canteen|food|cafeteria|eat|lunch|breakfast|dinner|cafe|restaurant)\b"],
        "response": "🍽️ **Canteen & Food Services**\n\n• **Main Canteen:** Near Block B, open 7:30 AM – 7:30 PM\n• **Mini Cafe:** Library Block, open 9 AM – 5 PM\n• **Menu:** Veg & Non-Veg options, South Indian, North Indian, snacks, beverages\n• **Meal Cards:** Available at the canteen counter (reloadable)\n\n🌿 Special dietary needs? Contact the canteen manager at ext. 215.\n\nAnything else I can help with?"
    },
    # Health / Medical
    {
        "patterns": [r"\b(health|medical|doctor|clinic|sick|hospital|nurse|medicine|first aid|injury)\b"],
        "response": "🏥 **Health & Medical Services**\n\n• **Campus Clinic:** Block D, Ground Floor\n• **Hours:** Mon–Sat, 9:00 AM – 5:00 PM\n• **Emergency:** 24/7 first aid available at Security Office (Gate 1)\n• **Doctor Visits:** Tue & Thu, 11 AM – 1 PM\n\n🚨 **Emergency Contact:** ext. 100 (Campus Security)\n🏥 **Nearest Hospital:** City General Hospital (~2 km)\n\nStay healthy! Anything else?"
    },
    # Counselling
    {
        "patterns": [r"\b(counsell?ing|counsellor|mental health|stress|anxiety|depression|support|therapy)\b"],
        "response": "💙 **Student Counselling Services**\n\nYour well-being matters to us!\n\n• **Counsellor:** Ms. Priya Sharma (Block A, Room 108)\n• **Hours:** Mon–Fri, 10 AM – 4 PM\n• **Appointment:** Call ext. 206 or email counselling@campus.edu\n• **All sessions are completely confidential**\n\n🤝 You're not alone. Don't hesitate to reach out anytime.\n\nIs there anything else you'd like help with?"
    },
    # Wi-Fi / Internet
    {
        "patterns": [r"\b(wi.?fi|internet|network|password|connect|broadband|login)\b"],
        "response": "📶 **Campus Wi-Fi**\n\n• **Network Name:** CampusNet_Student\n• **Password:** Issued with your student ID card\n• **Coverage:** All academic blocks, library, hostel, and canteen\n• **Speed:** 100 Mbps shared\n\n🔧 **Wi-Fi Issues?** Contact IT Help Desk:\n• Location: Block B, Room 005\n• Email: itsupport@campus.edu\n• Hours: Mon–Fri, 9 AM – 6 PM\n\nAnything else?"
    },
    # Contact / Phone
    {
        "patterns": [r"\b(contact|phone|number|email|address|reach|helpdesk|help desk)\b"],
        "response": "📞 **Campus Contact Directory**\n\n| Department | Extension | Email |\n|---|---|---|\n| Reception | 100 | info@campus.edu |\n| Admissions | 101 | admissions@campus.edu |\n| Exam Cell | 102 | exams@campus.edu |\n| Library | 204 | library@campus.edu |\n| Finance | 210 | finance@campus.edu |\n| IT Support | 205 | itsupport@campus.edu |\n| Hostel | 220 | hostel@campus.edu |\n\n🌐 Website: www.campus.edu\n📍 Address: 123 University Road, City – 400001\n\nNeed anything else?"
    },
    # Result / Marks
    {
        "patterns": [r"\b(result|results|marks|grade|grades|gpa|cgpa|scorecard|marksheet)\b"],
        "response": "📊 **Results & Grades**\n\n• Results are published on the **Student Portal** within 4 weeks of exams.\n• **Login:** studentportal.campus.edu → Academics → Results\n• **Grade Scale:** O (Outstanding) → A+ → A → B+ → B → C → F\n• **Revaluation:** Apply within 10 days of result via portal (fee: ₹200/subject)\n\n📄 Official marksheets are available from the Exam Cell after 2 weeks.\n\nAny other questions?"
    },
    # Holidays
    {
        "patterns": [r"\b(holiday|holidays|vacation|break|leave|off day|closed)\b"],
        "response": "🎉 **Holiday & Leave Schedule**\n\n• **Summer Break:** May 15 – June 15\n• **Winter Break:** Dec 24 – Jan 2\n• **Diwali Break:** As per academic calendar\n• **Public Holidays:** All national holidays are observed\n\n📅 Full academic calendar is available on the **Student Portal → Academics → Calendar**\n\nAnything else you'd like to know?"
    },
    # Who are you / About bot
    {
        "patterns": [r"\b(who are you|what are you|your name|about you|what can you do|help me)\b"],
        "response": "🤖 **I'm CampusBot!**\n\nYour 24/7 virtual campus assistant. I'm here to help students with:\n\n• 📅 Exam & timetable queries\n• 📚 Library information\n• 🏫 Admissions & registration\n• 💳 Fees & scholarships\n• 🏠 Hostel & accommodation\n• 🍽️ Canteen services\n• 🏥 Health & counselling\n• 📶 Wi-Fi & IT support\n• 📞 Contact information\n\nJust type your question and I'll do my best to help! 😊"
    },
]

# ─────────────────────────────────────────────
#  MATCHING ENGINE
# ─────────────────────────────────────────────
def get_response(user_input: str) -> str:
    text = user_input.lower().strip()
    if not text:
        return "Please type a message so I can help you! 😊"

    for rule in RULES:
        for pattern in rule["patterns"]:
            if re.search(pattern, text, re.IGNORECASE):
                return rule["response"]

    # Fallback
    return (
        "🤔 I'm sorry, I didn't quite understand that.\n\n"
        "Here are some things I can help you with:\n"
        "• **Exams** – schedules, results, revaluation\n"
        "• **Library** – books, hours, e-resources\n"
        "• **Admissions** – process, documents, fees\n"
        "• **Hostel** – accommodation, facilities\n"
        "• **Health** – clinic, counselling services\n"
        "• **Contact** – department phone numbers\n\n"
        "Try rephrasing your question, or type **'help'** to see all topics!"
    )


# ─────────────────────────────────────────────
#  HTML TEMPLATE
# ─────────────────────────────────────────────
HTML = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1.0"/>
<title>CampusBot – Campus Assistant</title>
<style>
  @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
  *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

  :root {
    --primary: #4F46E5;
    --primary-light: #EEF2FF;
    --accent: #06B6D4;
    --bg: #F8FAFC;
    --surface: #FFFFFF;
    --text: #1E293B;
    --muted: #64748B;
    --border: #E2E8F0;
    --bot-bg: #F1F5F9;
    --user-bg: #4F46E5;
    --shadow: 0 4px 24px rgba(79,70,229,0.10);
  }

  body {
    font-family: 'Inter', sans-serif;
    background: var(--bg);
    display: flex; align-items: center; justify-content: center;
    min-height: 100vh; padding: 16px;
    background-image: radial-gradient(circle at 20% 20%, #EEF2FF 0%, transparent 50%),
                      radial-gradient(circle at 80% 80%, #ECFEFF 0%, transparent 50%);
  }

  .chat-container {
    width: 100%; max-width: 780px;
    background: var(--surface);
    border-radius: 20px;
    box-shadow: var(--shadow), 0 1px 3px rgba(0,0,0,0.06);
    display: flex; flex-direction: column;
    height: 88vh; max-height: 780px;
    overflow: hidden; border: 1px solid var(--border);
  }

  /* Header */
  .chat-header {
    background: linear-gradient(135deg, var(--primary) 0%, #6366F1 100%);
    padding: 18px 24px;
    display: flex; align-items: center; gap: 14px;
    color: white;
  }
  .bot-avatar {
    width: 46px; height: 46px; border-radius: 14px;
    background: rgba(255,255,255,0.2);
    display: flex; align-items: center; justify-content: center;
    font-size: 22px; flex-shrink: 0;
  }
  .header-info h1 { font-size: 17px; font-weight: 700; letter-spacing: -0.3px; }
  .header-info p  { font-size: 12px; opacity: 0.8; margin-top: 2px; }
  .status-dot {
    width: 8px; height: 8px; border-radius: 50%;
    background: #4ADE80; margin-right: 6px;
    display: inline-block; animation: pulse 2s infinite;
  }
  @keyframes pulse { 0%,100%{opacity:1} 50%{opacity:0.4} }

  /* Messages */
  .chat-messages {
    flex: 1; overflow-y: auto; padding: 20px;
    display: flex; flex-direction: column; gap: 16px;
    scroll-behavior: smooth;
  }
  .chat-messages::-webkit-scrollbar { width: 4px; }
  .chat-messages::-webkit-scrollbar-track { background: transparent; }
  .chat-messages::-webkit-scrollbar-thumb { background: var(--border); border-radius: 99px; }

  .msg-row { display: flex; gap: 10px; align-items: flex-end; }
  .msg-row.user { flex-direction: row-reverse; }

  .avatar {
    width: 32px; height: 32px; border-radius: 10px;
    display: flex; align-items: center; justify-content: center;
    font-size: 15px; flex-shrink: 0;
  }
  .bot-av  { background: var(--primary-light); }
  .user-av { background: var(--user-bg); }

  .bubble {
    max-width: 72%; padding: 12px 16px;
    border-radius: 18px; line-height: 1.6;
    font-size: 14px; color: var(--text);
  }
  .bot-bubble {
    background: var(--bot-bg);
    border-bottom-left-radius: 4px;
    border: 1px solid var(--border);
  }
  .user-bubble {
    background: var(--user-bg); color: white;
    border-bottom-right-radius: 4px;
  }

  /* Markdown-like rendering */
  .bubble strong { font-weight: 600; }
  .bubble ul { padding-left: 18px; margin-top: 6px; }
  .bubble li { margin-bottom: 3px; }
  .bubble table { border-collapse: collapse; margin-top: 8px; font-size: 13px; width: 100%; }
  .bubble th, .bubble td { border: 1px solid var(--border); padding: 5px 10px; text-align: left; }
  .bubble th { background: var(--primary-light); font-weight: 600; }

  .timestamp {
    font-size: 10px; color: var(--muted); margin-top: 4px;
    text-align: right; padding: 0 4px;
  }
  .msg-row.bot-row .timestamp { text-align: left; }

  /* Quick replies */
  .quick-replies {
    display: flex; flex-wrap: wrap; gap: 8px;
    padding: 0 20px 14px;
  }
  .quick-btn {
    background: var(--primary-light); color: var(--primary);
    border: 1px solid #C7D2FE; border-radius: 20px;
    padding: 6px 14px; font-size: 12.5px; font-weight: 500;
    cursor: pointer; transition: all 0.15s;
    font-family: inherit;
  }
  .quick-btn:hover { background: var(--primary); color: white; border-color: var(--primary); }

  /* Input */
  .chat-input-area {
    padding: 14px 20px 18px;
    border-top: 1px solid var(--border);
    background: white;
  }
  .input-row {
    display: flex; gap: 10px; align-items: center;
    background: var(--bg); border: 1.5px solid var(--border);
    border-radius: 14px; padding: 8px 8px 8px 16px;
    transition: border-color 0.2s;
  }
  .input-row:focus-within { border-color: var(--primary); }
  #userInput {
    flex: 1; border: none; background: transparent;
    font-size: 14px; font-family: inherit; color: var(--text);
    outline: none; resize: none; max-height: 100px;
    line-height: 1.5;
  }
  #userInput::placeholder { color: var(--muted); }
  #sendBtn {
    width: 38px; height: 38px; border-radius: 10px;
    background: var(--primary); color: white; border: none;
    cursor: pointer; display: flex; align-items: center; justify-content: center;
    transition: background 0.15s; flex-shrink: 0;
    font-size: 16px;
  }
  #sendBtn:hover { background: #4338CA; }

  /* Typing indicator */
  .typing-indicator { display: flex; gap: 4px; padding: 12px 16px; }
  .typing-indicator span {
    width: 7px; height: 7px; border-radius: 50%; background: var(--muted);
    animation: bounce 1.2s infinite;
  }
  .typing-indicator span:nth-child(2) { animation-delay: 0.2s; }
  .typing-indicator span:nth-child(3) { animation-delay: 0.4s; }
  @keyframes bounce { 0%,80%,100%{transform:translateY(0)} 40%{transform:translateY(-6px)} }

  .hidden { display: none !important; }
</style>
</head>
<body>
<div class="chat-container">
  <!-- Header -->
  <div class="chat-header">
    <div class="bot-avatar">🎓</div>
    <div class="header-info">
      <h1>CampusBot</h1>
      <p><span class="status-dot"></span>Online · Your 24/7 Campus Assistant</p>
    </div>
  </div>

  <!-- Messages -->
  <div class="chat-messages" id="chatMessages"></div>

  <!-- Quick reply chips -->
  <div class="quick-replies" id="quickReplies">
    <button class="quick-btn" onclick="sendQuick('Exam schedule')">📅 Exam Schedule</button>
    <button class="quick-btn" onclick="sendQuick('Library hours')">📚 Library</button>
    <button class="quick-btn" onclick="sendQuick('Admission process')">🏫 Admissions</button>
    <button class="quick-btn" onclick="sendQuick('Hostel facilities')">🏠 Hostel</button>
    <button class="quick-btn" onclick="sendQuick('Contact information')">📞 Contacts</button>
    <button class="quick-btn" onclick="sendQuick('Health clinic')">🏥 Health</button>
  </div>

  <!-- Input -->
  <div class="chat-input-area">
    <div class="input-row">
      <textarea id="userInput" placeholder="Type your question here…" rows="1"></textarea>
      <button id="sendBtn" onclick="sendMessage()">➤</button>
    </div>
  </div>
</div>

<script>
  const chatMessages = document.getElementById('chatMessages');
  const userInput   = document.getElementById('userInput');

  // Auto-resize textarea
  userInput.addEventListener('input', () => {
    userInput.style.height = 'auto';
    userInput.style.height = userInput.scrollHeight + 'px';
  });

  userInput.addEventListener('keydown', e => {
    if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); sendMessage(); }
  });

  function getTime() {
    return new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  }

  function renderMarkdown(text) {
    return text
      .replace(/\\n/g, '\n')  // Handle escaped newlines
      .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
      .replace(/^• (.+)$/gm, '<li>$1</li>')
      .replace(/((?:<li>.*<\/li>\n?)+)/g, '<ul>$1</ul>')
      .replace(/\|(.+)\|/g, row => {
        const cells = row.split('|').filter(c => c.trim() !== '');
        return '<tr>' + cells.map(c => {
          const t = c.trim();
          return t === '---' ? '' : `<td>${t}</td>`;
        }).join('') + '</tr>';
      })
      .replace(/((?:<tr>.*<\/tr>\n?)+)/, t => `<table>${t}</table>`)
      .replace(/\n/g, '<br>');
  }

  function appendMessage(text, sender) {
    const isBot = sender === 'bot';
    const row = document.createElement('div');
    row.className = 'msg-row ' + (isBot ? 'bot-row' : 'user');

    const av = document.createElement('div');
    av.className = 'avatar ' + (isBot ? 'bot-av' : 'user-av');
    av.textContent = isBot ? '🎓' : '👤';

    const wrap = document.createElement('div');

    const bubble = document.createElement('div');
    bubble.className = 'bubble ' + (isBot ? 'bot-bubble' : 'user-bubble');
    bubble.innerHTML = isBot ? renderMarkdown(text) : escapeHtml(text);

    const ts = document.createElement('div');
    ts.className = 'timestamp';
    ts.textContent = getTime();

    wrap.appendChild(bubble);
    wrap.appendChild(ts);

    if (isBot) { row.appendChild(av); row.appendChild(wrap); }
    else        { row.appendChild(wrap); row.appendChild(av); }

    chatMessages.appendChild(row);
    chatMessages.scrollTop = chatMessages.scrollHeight;
  }

  function escapeHtml(t) {
    return t.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');
  }

  function showTyping() {
    const row = document.createElement('div');
    row.className = 'msg-row bot-row'; row.id = 'typingRow';
    const av = document.createElement('div');
    av.className = 'avatar bot-av'; av.textContent = '🎓';
    const ind = document.createElement('div');
    ind.className = 'typing-indicator';
    ind.innerHTML = '<span></span><span></span><span></span>';
    row.appendChild(av); row.appendChild(ind);
    chatMessages.appendChild(row);
    chatMessages.scrollTop = chatMessages.scrollHeight;
  }

  function hideTyping() {
    const el = document.getElementById('typingRow');
    if (el) el.remove();
  }

  async function sendMessage() {
    const text = userInput.value.trim();
    if (!text) return;
    userInput.value = '';
    userInput.style.height = 'auto';
    appendMessage(text, 'user');
    showTyping();

    try {
      const res = await fetch('/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: text })
      });
      
      if (!res.ok) {
        throw new Error(`Server error: ${res.status}`);
      }
      
      const data = await res.json();
      setTimeout(() => {
        hideTyping();
        appendMessage(data.response, 'bot');
      }, 700);
    } catch (error) {
      console.error('Error:', error);
      hideTyping();
      appendMessage("⚠️ Oops! Something went wrong. Please try again. Make sure the Flask server is running at http://localhost:5000", 'bot');
    }
  }

  function sendQuick(text) {
    userInput.value = text;
    sendMessage();
  }

  // Initial greeting
  window.addEventListener('load', () => {
    setTimeout(() => {
      appendMessage(
        "👋 Hello! Welcome to **CampusBot** — your 24/7 campus assistant!\n\nI can help you with:\n• 📅 Exam schedules & timetables\n• 📚 Library & study resources\n• 🏫 Admission & registration\n• 🍽️ Canteen & hostel info\n• 🏥 Health & counselling services\n• 📞 Contact details\n\nWhat would you like to know?",
        'bot'
      );
    }, 400);
  });
</script>
</body>
</html>
"""

# ─────────────────────────────────────────────
#  ROUTES
# ─────────────────────────────────────────────
@app.route("/")
def index():
    return render_template_string(HTML)

@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json(force=True)
    user_msg = data.get("message", "").strip()
    reply = get_response(user_msg)
    return jsonify({"response": reply})

if __name__ == "__main__":
    print("=" * 50)
    print("  CampusBot — Campus Assistant Chatbot")
    print("  Running at: http://localhost:5000")
    print("=" * 50)
    app.run(debug=True, port=5000)
