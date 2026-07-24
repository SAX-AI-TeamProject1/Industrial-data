# 2026.07.24 (한인혁)

- docu/AGENT.md 작성: 프로젝트 구조, 실행 명령, CSV 전처리 시 주의사항 정리
- .vscode/tasks.json "필요 라이브러리 설치" 태스크 크로스플랫폼 대응 (windows: python, linux/osx: python3)
- docu/AGENT.md 프로젝트 개요/아키텍처를 실제 목표(도입 전후 대응표본 t-검정)에 맞게 재작성
- asset/ CSV 11개 파일명 접두어 "1차프로젝트-데이터 - " → "기획_"로 변경, src/plane/의 두 스크립트 참조 경로 반영
- src/plane/visualize.py, visualizetwo.py가 src/plane/으로 이동하며 어긋난 asset/visualizations 상대경로(parent 깊이 부족) 수정
- 커밋(d0e2792) 후 원격 push 거부 -> fetch/merge로 팀원 커밋 3개(venv 기반 tasks.json, visualizetwo.py 폰트 수정) 병합
  - tasks.json 충돌: 팀원의 "1. 가상환경 생성" -> "2. 필요 라이브러리 설치" 2단계 방식 채택, dependsOn 라벨 불일치 버그 수정
  - 병합 커밋(4b32c49) 후 원격 push 완료
