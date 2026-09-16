"""방명록(Guestboard) 웹 애플리케이션

모든 글은 guestboard.json 파일에 저장된다.
작성자의 IP는 함께 기록하되, 화면에는 절대 노출하지 않는다.
"""

import json
import os
import uuid
from datetime import datetime

from flask import Flask, jsonify, render_template, request
from werkzeug.security import check_password_hash, generate_password_hash

app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(BASE_DIR, "guestboard.json")

MAX_NAME_LENGTH = 20
MAX_MESSAGE_LENGTH = 300


def load_entries():
    if not os.path.exists(DATA_FILE):
        return []
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return []


def save_entries(entries):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(entries, f, ensure_ascii=False, indent=2)


def get_client_ip():
    forwarded = request.headers.get("X-Forwarded-For", "")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.remote_addr or "unknown"


def public_entry(entry):
    """비밀번호 해시와 IP를 제거한, 클라이언트에 노출 가능한 형태."""
    return {
        "id": entry["id"],
        "name": entry["name"],
        "message": entry["message"],
        "mood": entry.get("mood", "😊"),
        "created_at": entry["created_at"],
    }


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/entries", methods=["GET"])
def get_entries():
    entries = load_entries()
    entries_sorted = sorted(entries, key=lambda e: e["created_at"], reverse=True)
    return jsonify({
        "count": len(entries_sorted),
        "entries": [public_entry(e) for e in entries_sorted],
    })


@app.route("/api/entries", methods=["POST"])
def add_entry():
    data = request.get_json(silent=True) or {}
    name = str(data.get("name", "")).strip()
    message = str(data.get("message", "")).strip()
    password = str(data.get("password", ""))
    mood = str(data.get("mood", "😊")).strip() or "😊"

    if not name or not message or not password:
        return jsonify({"error": "이름, 내용, 비밀번호를 모두 입력해주세요."}), 400
    if len(name) > MAX_NAME_LENGTH:
        return jsonify({"error": f"이름은 {MAX_NAME_LENGTH}자 이내로 입력해주세요."}), 400
    if len(message) > MAX_MESSAGE_LENGTH:
        return jsonify({"error": f"내용은 {MAX_MESSAGE_LENGTH}자 이내로 입력해주세요."}), 400
    if len(password) < 4:
        return jsonify({"error": "비밀번호는 4자 이상으로 입력해주세요."}), 400

    entry = {
        "id": uuid.uuid4().hex,
        "name": name,
        "message": message,
        "mood": mood,
        "password_hash": generate_password_hash(password),
        "ip": get_client_ip(),
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }

    entries = load_entries()
    entries.append(entry)
    save_entries(entries)

    return jsonify({"entry": public_entry(entry)}), 201


@app.route("/api/entries/<entry_id>", methods=["DELETE"])
def delete_entry(entry_id):
    data = request.get_json(silent=True) or {}
    password = str(data.get("password", ""))

    entries = load_entries()
    target = next((e for e in entries if e["id"] == entry_id), None)

    if target is None:
        return jsonify({"error": "글을 찾을 수 없습니다."}), 404
    if not check_password_hash(target["password_hash"], password):
        return jsonify({"error": "비밀번호가 일치하지 않습니다."}), 403

    entries = [e for e in entries if e["id"] != entry_id]
    save_entries(entries)
    return jsonify({"success": True})


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
