import random
import uuid

import uvicorn
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, RedirectResponse

app = FastAPI()

# session_id -> {"answer": int, "tries": int, "history": list[str]}
games: dict[str, dict] = {}


def new_game() -> dict:
    return {"answer": random.randint(1, 100), "tries": 0, "history": []}


def render_page(game: dict, won: bool = False) -> str:
    history_html = "".join(f"<li>{line}</li>" for line in game["history"])

    if won:
        body = f"""
        <p class="result win">🎉 정답입니다! {game['tries']}번 만에 맞추셨습니다. 축하합니다! 🎉</p>
        <a class="button" href="/reset">다시 하기</a>
        """
    else:
        body = f"""
        <form action="/guess" method="get">
            <input type="number" name="value" min="1" max="100" placeholder="1~100" autofocus required>
            <button type="submit">확인</button>
        </form>
        <p>시도 횟수: {game['tries']}</p>
        """

    return f"""
    <!DOCTYPE html>
    <html lang="ko">
    <head>
        <meta charset="UTF-8">
        <title>숫자 맞추기 게임</title>
        <style>
            body {{ font-family: sans-serif; max-width: 480px; margin: 60px auto; text-align: center; }}
            input {{ font-size: 1.2rem; padding: 8px; width: 100px; text-align: center; }}
            button, .button {{ font-size: 1.2rem; padding: 8px 16px; margin-left: 8px; cursor: pointer; text-decoration: none; }}
            .result {{ font-size: 1.2rem; }}
            .win {{ color: #2a7d2a; }}
            ul {{ list-style: none; padding: 0; color: #555; }}
        </style>
    </head>
    <body>
        <h1>1부터 100 사이의 숫자를 맞춰보세요!</h1>
        {body}
        <ul>{history_html}</ul>
    </body>
    </html>
    """


def get_or_create_session(request: Request) -> tuple[str, dict, bool]:
    session_id = request.cookies.get("session_id")
    is_new_cookie = False

    if session_id is None or session_id not in games:
        session_id = uuid.uuid4().hex
        games[session_id] = new_game()
        is_new_cookie = True

    return session_id, games[session_id], is_new_cookie


@app.get("/", response_class=HTMLResponse)
def index(request: Request):
    session_id, game, is_new_cookie = get_or_create_session(request)
    response = HTMLResponse(render_page(game))

    if is_new_cookie:
        response.set_cookie("session_id", session_id, httponly=True)

    return response


@app.get("/guess", response_class=HTMLResponse)
def guess(request: Request, value: int):
    session_id, game, is_new_cookie = get_or_create_session(request)

    if not 1 <= value <= 100:
        game["history"].insert(0, f"{value}: 1~100 사이의 숫자만 입력해주세요.")
    else:
        game["tries"] += 1

        if value < game["answer"]:
            game["history"].insert(0, f"{value}: 더 높은 숫자입니다.")
        elif value > game["answer"]:
            game["history"].insert(0, f"{value}: 더 낮은 숫자입니다.")
        else:
            game["history"].insert(0, f"{value}: 정답!")
            response = HTMLResponse(render_page(game, won=True))
            if is_new_cookie:
                response.set_cookie("session_id", session_id, httponly=True)
            return response

    response = HTMLResponse(render_page(game))
    if is_new_cookie:
        response.set_cookie("session_id", session_id, httponly=True)

    return response


@app.get("/reset")
def reset(request: Request):
    session_id = request.cookies.get("session_id") or uuid.uuid4().hex
    games[session_id] = new_game()

    response = RedirectResponse(url="/")
    response.set_cookie("session_id", session_id, httponly=True)

    return response


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
