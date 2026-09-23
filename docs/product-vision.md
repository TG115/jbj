# JBJ 제품 비전

> 목적: JBJ가 **무엇을 위한 서비스인지**를 짧게 고정한다.  
> 구현 세부·스키마·API·KOSIS 해석은 각각 `README.md`, `docs/development-setup.md`, `docs/kosis-labor-demand.md`를 본다.

---

## 핵심 질문

**「나는 뭐하고 살지?」**

JBJ(Job by Job / 직바직)는 이 질문에 답하기 위해 공식 직업·노동시장 데이터를 연결한다.

---

## 제품이 아닌 것

JBJ는 **채용 공고 게시판(job board)이 아니다.**

공고를 모아 지원하게 하는 서비스가 아니라, **직업 선택·전환을 데이터로 판단**하게 돕는 커리어 데이터 서비스다.

---

## 의도된 흐름

```text
시장 탐색
  → Job DNA (직업의 특성·수요·구조 이해)
  → Prep (준비·학습·자격)
  → Career mobility (이동·전환)
```

현재 저장소 구현 초점은 **직업분류 + KOSIS 노동수요 파이프라인 + Laravel labor-demand API**다.  
위 흐름의 UI/도메인 모듈이 모두 구현된 상태는 아니다.

---

## 데이터로 다루는 문제

- 서로 다른 공식 직업분류(KSCO, KECO 등)를 같은 기준으로 탐색·비교할 수 있게 한다.
- 노동수요 등 공식 통계의 **원천 grain과 부재**를 왜곡하지 않고 전달한다.
- 공식 지표와 JBJ 파생 지표를 구분한다.

---

## 관련 문서

- [README](../README.md) — 현재 구현 요약
- [KOSIS Labor Demand](kosis-labor-demand.md) — 수집 범위·grain·missing≠0
- [Development Setup](development-setup.md) — 재현 가이드
- [AGENTS.md](../AGENTS.md) — 엔지니어링 불변 조건
