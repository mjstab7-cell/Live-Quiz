from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit

app = Flask(__name__)
app.config["SECRET_KEY"] = "change-this-secret-key"
socketio = SocketIO(app, cors_allowed_origins="*")

# ------------------------------------------------------------------
# QUIZ QUESTIONS — edit this list to add your own questions.
# media_type can be None, "image", or "video".
# For "image": media_url = "/static/yourimage.jpg" (put file in static/)
# For "video": media_url = a YouTube/Vimeo embed link
# ------------------------------------------------------------------
QUESTIONS = [
    {
        "text": "What is the capital of France?",
        "options": ["Paris", "London", "Berlin", "Madrid"],
        "correct": 0,
        "media_type": None,
        "media_url": None,
    },
    {
        "text": "Which planet is known as the Red Planet?",
        "options": ["Earth", "Mars", "Jupiter", "Venus"],
        "correct": 1,
        "media_type": None,
        "media_url": None,
    },
    {
        "text": "2 + 2 x 2 = ?",
        "options": ["8", "6", "4", "2"],
        "correct": 1,
        "media_type": None,
        "media_url": None,
    },
]

# In-memory state (resets whenever the server restarts / redeploys)
state = {
    "current_question": -1,          # -1 = waiting screen before quiz starts
    "answers": {},                   # {question_index: {choice_index: count}}
    "participants": {},              # {socket_id: name}
    "answered_this_round": set(),    # socket ids who already answered current q
}


def reset_answers_for(qi):
    state["answers"][qi] = {i: 0 for i in range(len(QUESTIONS[qi]["options"]))}


def public_state():
    qi = state["current_question"]
    payload = {
        "current_question": qi,
        "total_questions": len(QUESTIONS),
        "num_participants": len(state["participants"]),
    }
    if qi >= 0:
        q = QUESTIONS[qi]
        payload["question"] = {
            "text": q["text"],
            "options": q["options"],
            "media_type": q["media_type"],
            "media_url": q["media_url"],
        }
        payload["tally"] = state["answers"].get(qi, {})
        payload["correct"] = q["correct"]
    return payload


@app.route("/")
def index():
    return render_template("present.html")


@app.route("/present")
def present():
    return render_template("present.html")


@app.route("/join")
def join():
    return render_template("join.html")


@socketio.on("connect")
def on_connect():
    emit("state_update", public_state())


@socketio.on("register_participant")
def on_register(data):
    name = (data.get("name") or "Anonymous").strip()[:30] or "Anonymous"
    state["participants"][request.sid] = name
    emit("state_update", public_state(), broadcast=True)


@socketio.on("submit_answer")
def on_submit_answer(data):
    qi = state["current_question"]
    if qi < 0:
        return
    sid = request.sid
    if sid in state["answered_this_round"]:
        return
    choice = data.get("choice")
    if choice is None or not (0 <= choice < len(QUESTIONS[qi]["options"])):
        return
    state["answers"].setdefault(qi, {i: 0 for i in range(len(QUESTIONS[qi]["options"]))})
    state["answers"][qi][choice] += 1
    state["answered_this_round"].add(sid)
    emit("state_update", public_state(), broadcast=True)
    emit("answer_received", {"choice": choice}, room=sid)


@socketio.on("next_question")
def on_next():
    state["current_question"] = min(state["current_question"] + 1, len(QUESTIONS) - 1)
    reset_answers_for(state["current_question"])
    state["answered_this_round"] = set()
    emit("state_update", public_state(), broadcast=True)


@socketio.on("prev_question")
def on_prev():
    state["current_question"] = max(0, state["current_question"] - 1)
    state["answered_this_round"] = set()
    emit("state_update", public_state(), broadcast=True)


@socketio.on("disconnect")
def on_disconnect():
    state["participants"].pop(request.sid, None)
    emit("state_update", public_state(), broadcast=True)


if __name__ == "__main__":
    socketio.run(app, debug=True)
