# 방명록 (Guestboard)

Flask 기반 방명록 게시판.

## 실행 방법

```bash
pip install -r requirements.txt
python app.py
```

브라우저에서 http://localhost:5000 접속.

## 특징

- 이름 / 기분 이모지 / 내용 / 비밀번호(삭제용)를 남길 수 있는 방명록
- 모든 글은 `guestboard.json`에 저장됨
- 작성자의 IP는 함께 기록되지만, 화면이나 API 응답에는 노출되지 않음 (`guestboard.json` 원본 파일에만 존재)
- 삭제 시 작성한 비밀번호 확인 필요 (해시로 저장)
- 메인 컬러: 녹색 테마
