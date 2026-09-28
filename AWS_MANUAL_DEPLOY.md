# Stage 1 AWS 수동 배포

Stage 1에서는 Streamlit과 3,000명 축소 MySQL을 같은 EC2의 Docker Compose로 실행합니다. RDS는 아직 사용하지 않습니다.

1. 강사 PC에서 `python tools/prepare_course_db.py`로 `10_fintech_realistic_class.sql.gz` 생성
2. Amazon Linux 2023 EC2 생성
3. Docker/Git 설치 및 Docker 서비스 시작
4. 저장소 clone
5. Git에서 제외한 `10_fintech_realistic_class.sql.gz`를 EC2의 `stage01_streamlit_mydata/db/init/`로 별도 전송
6. `stage01_streamlit_mydata/.env.example`을 `.env`로 복사
7. `docker compose up -d --build`
8. `docker compose ps`로 `db`가 healthy, `app`이 running인지 확인
9. 브라우저에서 EC2의 8501 포트 접속

MySQL 데이터는 Docker named volume `mysql_data_3000`에 보존됩니다. 앱 컨테이너를 다시 빌드해도 DB 데이터는 삭제되지 않습니다.

DB dump를 바꿔 처음부터 다시 복원할 때만 다음을 실행합니다.

```bash
docker compose down -v
docker compose up -d --build
```
