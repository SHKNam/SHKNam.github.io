#!/usr/bin/env python3
"""포트폴리오 플로우 다이어그램 SVG 생성기.

노드/엣지 스펙(dict)을 받아 사이트 색 톤과 일치하는 SVG를
assets/diagrams/ 에 일괄 생성한다.  수정 후 재실행하면 전부 갱신됨.
    python3 tools/generate_diagrams.py
"""
import html, os, math

OUT = os.path.join(os.path.dirname(__file__), "..", "assets", "diagrams")

# ── 팔레트 (css/style.css 와 동일 톤) ─────────────────────────
BG        = "none"        # 투명 배경 (카드 위에 얹힘)
NODE_FILL = "#151D2E"
NODE_STR  = "#2C3A55"
TEXT      = "#E8EDF6"
MUTED     = "#8B99B3"
ACCENT    = "#7C9CF5"     # 인디고 — 핵심/결과 노드
AMBER     = "#F0B35C"     # 앰버 — 경고/저장소/하이라이트
EDGE      = "#46557A"

NW, NH   = 172, 58        # 노드 크기
GX, GY   = 64, 34         # 간격
MARGIN   = 26
FONT     = "'Pretendard','Apple SD Gothic Neo','Malgun Gothic',sans-serif"
MONO     = "'JetBrains Mono','SF Mono',monospace"


def esc(s): return html.escape(s, quote=True)


def node_xy(col, row):
    x = MARGIN + col * (NW + GX)
    y = MARGIN + 34 + row * (NH + GY)
    return x, y


def render(spec, fname):
    nodes = {n["id"]: n for n in spec["nodes"]}
    ncols = max(n["col"] for n in spec["nodes"]) + 1
    nrows = max(n["row"] for n in spec["nodes"]) + 1
    W = MARGIN * 2 + ncols * NW + (ncols - 1) * GX
    H = MARGIN * 2 + 34 + nrows * NH + (nrows - 1) * GY

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" '
        f'font-family="{FONT}" role="img" aria-label="{esc(spec["title"])}">',
        '<defs><marker id="ah" viewBox="0 0 10 10" refX="9" refY="5" '
        'markerWidth="7" markerHeight="7" orient="auto-start-reverse">'
        f'<path d="M0,0 L10,5 L0,10 z" fill="{EDGE}"/></marker></defs>',
        f'<text x="{MARGIN}" y="{MARGIN - 4}" font-family="{MONO}" '
        f'font-size="12" letter-spacing="2" fill="{MUTED}">'
        f'{esc(spec["title"].upper())}</text>',
    ]

    # 엣지 먼저 (노드 아래 깔리게)
    for e in spec.get("edges", []):
        a, b = nodes[e[0]], nodes[e[1]]
        label = e[2] if len(e) > 2 else None
        ax, ay = node_xy(a["col"], a["row"])
        bx, by = node_xy(b["col"], b["row"])
        if a["col"] < b["col"]:                    # 좌→우
            x1, y1 = ax + NW, ay + NH / 2
            x2, y2 = bx, by + NH / 2
        elif a["col"] > b["col"]:                  # 우→좌 (피드백)
            x1, y1 = ax, ay + NH / 2
            x2, y2 = bx + NW, by + NH / 2
        else:                                      # 상→하 / 하→상
            if a["row"] < b["row"]:
                x1, y1 = ax + NW / 2, ay + NH
                x2, y2 = bx + NW / 2, by
            else:
                x1, y1 = ax + NW / 2, ay
                x2, y2 = bx + NW / 2, by + NH
        if y1 == y2 or x1 == x2:
            d = f"M{x1},{y1} L{x2},{y2}"
        else:  # 베지어
            mx = (x1 + x2) / 2
            d = f"M{x1},{y1} C{mx},{y1} {mx},{y2} {x2},{y2}"
        dash = ' stroke-dasharray="5 4"' if len(e) > 3 and e[3] == "dash" else ""
        parts.append(f'<path d="{d}" fill="none" stroke="{EDGE}" '
                     f'stroke-width="1.6" marker-end="url(#ah)"{dash}/>')
        if label:
            lx, ly = (x1 + x2) / 2, (y1 + y2) / 2 - 7
            parts.append(f'<text x="{lx}" y="{ly}" text-anchor="middle" '
                         f'font-size="11" fill="{MUTED}">{esc(label)}</text>')

    # 노드
    for n in spec["nodes"]:
        x, y = node_xy(n["col"], n["row"])
        t = n.get("type", "normal")
        stroke, sw, fill = NODE_STR, 1.4, NODE_FILL
        if t == "accent":  stroke, sw = ACCENT, 1.8
        if t == "warn":    stroke, sw = AMBER, 1.8
        if t == "store":   stroke = AMBER
        rx = 12 if t != "store" else 6
        parts.append(f'<rect x="{x}" y="{y}" width="{NW}" height="{NH}" '
                     f'rx="{rx}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>')
        if t == "store":   # 저장소 상단 라인
            parts.append(f'<line x1="{x}" y1="{y+10}" x2="{x+NW}" y2="{y+10}" '
                         f'stroke="{stroke}" stroke-width="1" opacity="0.55"/>')
        lines = n["label"].split("\n")
        sub = n.get("sub")
        total = len(lines) + (1 if sub else 0)
        fs = 13 if max(len(l) for l in lines) <= 14 else 12
        y0 = y + NH / 2 - (total - 1) * 8
        color = TEXT
        if t == "accent": color = "#C3D2FF"
        if t == "warn":   color = "#FFD9A0"
        for i, ln in enumerate(lines):
            parts.append(f'<text x="{x + NW/2}" y="{y0 + i*16 + 4}" '
                         f'text-anchor="middle" font-size="{fs}" '
                         f'font-weight="600" fill="{color}">{esc(ln)}</text>')
        if sub:
            parts.append(f'<text x="{x + NW/2}" y="{y0 + len(lines)*16 + 4}" '
                         f'text-anchor="middle" font-size="10.5" '
                         f'fill="{MUTED}">{esc(sub)}</text>')

    parts.append("</svg>")
    path = os.path.join(OUT, fname)
    with open(path, "w") as f:
        f.write("\n".join(parts))
    print("wrote", fname, f"({W}x{H})")


# ══════════════════════ 다이어그램 스펙 ══════════════════════
S = []

# ── 카드 1 · DUOGREEN RPA ──
S.append(("c01-supply-chain.svg", {
 "title": "Supply Chain 자동화",
 "nodes": [
  {"id":"a","col":0,"row":0,"label":"메일 주문 확인","sub":"수신 트리거"},
  {"id":"b","col":1,"row":0,"label":"B2B / B2C\n분기"},
  {"id":"c","col":2,"row":0,"label":"B2B","sub":"Shopify·Amazon SKU·수량"},
  {"id":"d","col":2,"row":1,"label":"B2C","sub":"FedEx 고객정보"},
  {"id":"e","col":3,"row":0,"label":"플랫폼\n클릭·입력"},
  {"id":"f","col":4,"row":0,"label":"사내 ERP\n조회·입력"},
  {"id":"g","col":5,"row":0,"label":"엑셀 정리·분석","type":"store"},
  {"id":"h","col":6,"row":0,"label":"결과 리포트\n이메일 발송","type":"accent"},
 ],
 "edges":[("a","b"),("b","c"),("b","d"),("c","e"),("d","e"),
          ("e","f"),("f","g"),("g","h")]}))

S.append(("c01-market-research.svg", {
 "title": "Market Research 자동화",
 "nodes": [
  {"id":"a","col":0,"row":0,"label":"제품명 입력"},
  {"id":"b","col":1,"row":0,"label":"검색 소스 분기"},
  {"id":"c","col":2,"row":0,"label":"제조사 사이트"},
  {"id":"d","col":2,"row":1,"label":"검색엔진"},
  {"id":"e","col":3,"row":0,"label":"웹 크롤링\n+ OCR 추출"},
  {"id":"f","col":4,"row":0,"label":"엑셀 정리·분석","type":"store"},
  {"id":"g","col":5,"row":0,"label":"보고서 발송","type":"accent"},
 ],
 "edges":[("a","b"),("b","c"),("b","d"),("c","e"),("d","e"),("e","f"),("f","g")]}))

S.append(("c01-finance.svg", {
 "title": "Finance 자동화",
 "nodes": [
  {"id":"a","col":0,"row":0,"label":"ERP 데이터 추출"},
  {"id":"b","col":1,"row":0,"label":"재무 사이트 입력"},
  {"id":"c","col":2,"row":0,"label":"금액 대사\n(용도별 매칭)"},
  {"id":"d","col":3,"row":0,"label":"검증 완료","type":"accent"},
 ],
 "edges":[("a","b"),("b","c"),("c","d")]}))

S.append(("c01-marketing.svg", {
 "title": "Marketing 자동화",
 "nodes": [
  {"id":"a","col":0,"row":0,"label":"웹사이트\n고객정보 추출"},
  {"id":"b","col":1,"row":0,"label":"고객 특성 분류"},
  {"id":"c","col":2,"row":0,"label":"맞춤 광고 메일\n자동 발송","type":"accent"},
 ],
 "edges":[("a","b"),("b","c")]}))

# ── 카드 2 · GraphRAG 해커톤 ──
S.append(("c02-graphrag-arch.svg", {
 "title": "Graph RAG × 멀티 에이전트 아키텍처",
 "nodes": [
  {"id":"a","col":0,"row":0,"label":"운영 데이터","sub":"프로젝트·인력·고객·재무"},
  {"id":"b","col":1,"row":0,"label":"Neo4j\nKnowledge Graph","type":"store"},
  {"id":"c","col":2,"row":0,"label":"Graph RAG 챗봇","sub":"자연어→그래프 조회→GPT"},
  {"id":"d","col":2,"row":1,"label":"멀티 에이전트\n페르소나 토론","sub":"해결책·보고서 생성"},
  {"id":"e","col":3,"row":0,"label":"Flask REST API","sub":"6종 엔드포인트"},
  {"id":"f","col":4,"row":0,"label":"Vue 3 + D3.js\n대시보드","type":"accent"},
  {"id":"g","col":4,"row":1,"label":"Power Automate","sub":"Teams·메일 자동 발송","type":"accent"},
 ],
 "edges":[("a","b"),("b","c"),("b","d"),("c","e"),("d","e"),("e","f"),
          ("c","g","",""),("d","g")]}))

# ── 카드 3 · EST-MoE ──
S.append(("c03-estmoe-arch.svg", {
 "title": "EST-MoE 제안 아키텍처",
 "nodes": [
  {"id":"a","col":0,"row":0,"label":"시계열 입력"},
  {"id":"b","col":0,"row":1,"label":"외부 이벤트\n컨텍스트","sub":"경제 충격·재난 등"},
  {"id":"c","col":1,"row":0,"label":"Contextual\nEncoding"},
  {"id":"d","col":2,"row":0,"label":"Contextual\nGating"},
  {"id":"e","col":3,"row":0,"label":"Dynamic Routing","sub":"MoE Experts"},
  {"id":"f","col":4,"row":0,"label":"Multi-Resolution\nForecasting","type":"accent"},
  {"id":"g","col":2,"row":1,"label":"Contextual\nSensitivity Loss","type":"warn"},
 ],
 "edges":[("a","c"),("b","c"),("c","d"),("d","e"),("e","f"),
          ("g","d","학습 신호","dash"),("g","f","","dash")]}))

# ── 카드 5 · Gender Gap 파이프라인 ──
S.append(("c05-gendergap-pipeline.svg", {
 "title": "GGI·아동노동 예측 파이프라인",
 "nodes": [
  {"id":"a","col":0,"row":0,"label":"데이터 수집","sub":"WB·ILO·UNICEF·FB API","type":"store"},
  {"id":"b","col":1,"row":0,"label":"표준화·결측 보정","sub":"KNN·Yeo-Johnson"},
  {"id":"c","col":2,"row":0,"label":"피처 선택","sub":"상관 기반 39 features"},
  {"id":"d","col":3,"row":0,"label":"모델 비교·튜닝","sub":"Elastic Net · LOOCV"},
  {"id":"e","col":4,"row":0,"label":"예측·해석","sub":"R² 59.18% (190개국)"},
  {"id":"f","col":5,"row":0,"label":"Streamlit\n정책 대시보드","type":"accent"},
 ],
 "edges":[("a","b"),("b","c"),("c","d"),("d","e"),("e","f")]}))

# ── 카드 7 · MyMedGlobal 3종 ──
S.append(("c07-fake-review.svg", {
 "title": "가짜 리뷰 탐지 — 3중 규칙",
 "nodes": [
  {"id":"a","col":0,"row":1,"label":"리뷰 데이터"},
  {"id":"b","col":1,"row":0,"label":"단시간\n대량 작성"},
  {"id":"c","col":1,"row":1,"label":"동일 IP 지역"},
  {"id":"d","col":1,"row":2,"label":"TF-IDF 유사도","sub":"중복·상투 문구"},
  {"id":"e","col":2,"row":1,"label":"규칙 스코어 결합"},
  {"id":"f","col":3,"row":1,"label":"의심 리뷰 플래깅","type":"accent"},
 ],
 "edges":[("a","b"),("a","c"),("a","d"),("b","e"),("c","e"),("d","e"),("e","f")]}))

S.append(("c07-patients-like-you.svg", {
 "title": "Patients Like You 추천 흐름",
 "nodes": [
  {"id":"a","col":0,"row":1,"label":"환자 프로필"},
  {"id":"b","col":1,"row":0,"label":"geopy 측지 거리"},
  {"id":"c","col":1,"row":1,"label":"연령 유사도"},
  {"id":"d","col":1,"row":2,"label":"조건·관심사\n텍스트 유사도"},
  {"id":"e","col":2,"row":1,"label":"유사 환자 매칭"},
  {"id":"f","col":3,"row":1,"label":"조회 이력 기반\n클리닉 추천","type":"accent"},
 ],
 "edges":[("a","b"),("a","c"),("a","d"),("b","e"),("c","e"),("d","e"),("e","f")]}))

S.append(("c07-completeness-score.svg", {
 "title": "클리닉 완성도 스코어",
 "nodes": [
  {"id":"a","col":0,"row":0,"label":"클리닉 프로필"},
  {"id":"b","col":1,"row":0,"label":"11개 지표\n가중 스코어링","sub":"인증·응답률·리뷰 등"},
  {"id":"c","col":2,"row":0,"label":"100점 만점\n품질 스코어","type":"store"},
  {"id":"d","col":3,"row":0,"label":"미완성·비활성\n자동 플래깅","type":"accent"},
 ],
 "edges":[("a","b"),("b","c"),("c","d")]}))

# ── 카드 8 · CookLens ──
S.append(("c08-cooklens-pipeline.svg", {
 "title": "CookLens 하이브리드 파이프라인",
 "nodes": [
  {"id":"a","col":0,"row":0,"label":"재료 사진 업로드"},
  {"id":"b","col":1,"row":0,"label":"Gemma Vision\n재료 인식","sub":"YOLO에서 전환"},
  {"id":"c","col":2,"row":0,"label":"사용자 보정","sub":"Human-in-the-loop"},
  {"id":"d","col":3,"row":0,"label":"레시피 DB 검색","type":"store"},
  {"id":"e","col":4,"row":0,"label":"레시피 추천","type":"accent"},
  {"id":"f","col":4,"row":1,"label":"GPT 레시피 생성"},
  {"id":"g","col":3,"row":1,"label":"저장 시 DB 축적","sub":"self-expanding","type":"store"},
 ],
 "edges":[("a","b"),("b","c"),("c","d"),("d","e","발견"),
          ("d","f","미발견"),("f","g"),("g","d","","dash")]}))

# ── 카드 9 · ChiEAC 2종 ──
S.append(("c09-two-stage-model.svg", {
 "title": "학업 이탈 위험 — 2단 모델",
 "nodes": [
  {"id":"a","col":0,"row":0,"label":"인종별 CDR\n25년치","sub":"1999–2024 코호트","type":"store"},
  {"id":"b","col":0,"row":1,"label":"텍스트 데이터","sub":"정규화·감성 분석"},
  {"id":"c","col":1,"row":0,"label":"표준화·전처리","sub":"4년/5년 코호트 구조"},
  {"id":"d","col":2,"row":0,"label":"① 분류 모델","sub":"위험 학생 식별 · CV 검증"},
  {"id":"e","col":3,"row":0,"label":"② 추세 모델","sub":"향후 위험 예측"},
  {"id":"f","col":4,"row":0,"label":"Secure 대시보드","sub":"Streamlit·Tableau","type":"accent"},
 ],
 "edges":[("a","c"),("b","c"),("c","d"),("d","e"),("e","f")]}))

S.append(("c09-chatbot-safety.svg", {
 "title": "RAG 챗봇 안전장치 흐름",
 "nodes": [
  {"id":"a","col":0,"row":0,"label":"학생 질문","sub":"Telegram"},
  {"id":"b","col":1,"row":0,"label":"1차 입력 필터"},
  {"id":"c","col":2,"row":0,"label":"RAG 지식베이스\n조회"},
  {"id":"d","col":3,"row":0,"label":"근거 기반 답변","sub":"grounded-only","type":"accent"},
  {"id":"e","col":3,"row":1,"label":"답변 회피","sub":"지식베이스 밖 질문","type":"warn"},
  {"id":"f","col":1,"row":1,"label":"유해 입력 차단","type":"warn"},
 ],
 "edges":[("a","b"),("b","c","통과"),("b","f","차단"),
          ("c","d","근거 있음"),("c","e","근거 없음")]}))

# ── 카드 10 · Spark 메달리온 ──
S.append(("c10-medallion.svg", {
 "title": "메달리온 스트리밍 파이프라인",
 "nodes": [
  {"id":"a","col":0,"row":0,"label":"트윗 JSON 스트림","sub":"Autoloader (cloudFiles)"},
  {"id":"b","col":1,"row":0,"label":"Bronze","sub":"원본 적재","type":"store"},
  {"id":"c","col":2,"row":0,"label":"Silver","sub":"타임스탬프·멘션 정제","type":"store"},
  {"id":"d","col":3,"row":0,"label":"Gold","sub":"감성 추론 결과","type":"store"},
  {"id":"e","col":4,"row":0,"label":"멘션별 집계","sub":"Top 20 pos/neg","type":"accent"},
  {"id":"f","col":2,"row":1,"label":"HF Transformer","sub":"spark_udf 분산 추론"},
  {"id":"g","col":3,"row":1,"label":"MLflow 추적","sub":"지표·버전 자동 기록"},
 ],
 "edges":[("a","b"),("b","c"),("c","d"),("d","e"),
          ("f","d"),("d","g","","dash")]}))

# ── 카드 11 · 2-Method 비교 ──
S.append(("c11-two-method.svg", {
 "title": "직접 분류 vs FP-Growth 증강",
 "nodes": [
  {"id":"a","col":0,"row":0,"label":"SAMHSA MHCLD","sub":"650만 건 · 13개 플래그","type":"store"},
  {"id":"b","col":1,"row":0,"label":"Method 1\n직접 분류","sub":"5개 분류기 · k-fold CV"},
  {"id":"c","col":2,"row":0,"label":"정확도 함정","sub":"98% 정확도 · F1 0.02","type":"warn"},
  {"id":"d","col":1,"row":1,"label":"Method 2\nFP-Growth 마이닝","sub":"lift>1 규칙 프루닝"},
  {"id":"e","col":2,"row":1,"label":"피처 재정의\n+ 언더샘플링"},
  {"id":"f","col":3,"row":1,"label":"F1 0.69–0.87","sub":"13개 플래그 전반","type":"accent"},
 ],
 "edges":[("a","b"),("a","d"),("b","c"),("d","e"),("e","f")]}))

# ── 카드 12 · COVID-19 Ohio ──
S.append(("c12-model-comparison.svg", {
 "title": "역전 분할에서의 일반화 비교",
 "nodes": [
  {"id":"a","col":0,"row":0,"label":"awareness 피처","sub":"4,600만 트윗 파생"},
  {"id":"b","col":0,"row":1,"label":"카운티 인구통계"},
  {"id":"c","col":1,"row":0,"label":"전처리·피처 실험","sub":"채택/폐기 기록"},
  {"id":"d","col":2,"row":0,"label":"RF (학습 1위)","sub":"학습 R² 0.950"},
  {"id":"e","col":2,"row":1,"label":"XGBoost 정규화"},
  {"id":"f","col":3,"row":0,"label":"테스트 과적합 역전","type":"warn"},
  {"id":"g","col":3,"row":1,"label":"테스트 R² 0.835","sub":"40팀 중 Top 10","type":"accent"},
 ],
 "edges":[("a","c"),("b","c"),("c","d"),("c","e"),("d","f"),("e","g")]}))

# ── 카드 13 · GitHub 네트워크 3단계 ──
S.append(("c13-three-stage.svg", {
 "title": "3단계 방법론 비교",
 "nodes": [
  {"id":"a","col":0,"row":1,"label":"GitHub 네트워크","sub":"37.7K 노드 · 289K 엣지","type":"store"},
  {"id":"b","col":1,"row":0,"label":"① 베이스라인","sub":"RF · 로지스틱"},
  {"id":"c","col":1,"row":1,"label":"② Node2Vec\n임베딩 증강"},
  {"id":"d","col":1,"row":2,"label":"③ 3-layer GCN","sub":"dropout·neg sampling"},
  {"id":"e","col":2,"row":1,"label":"Node2Vec + RF\nF1 0.9341","sub":"최고 성능","type":"accent"},
  {"id":"f","col":2,"row":2,"label":"GCN 열세","sub":"실패 원인 분석·문서화","type":"warn"},
 ],
 "edges":[("a","b"),("a","c"),("a","d"),("c","e"),("d","f")]}))

# ── 카드 14 · 지정학 4단 파이프라인 ──
S.append(("c14-four-stage.svg", {
 "title": "4단 이벤트 기반 인텔리전스 파이프라인",
 "nodes": [
  {"id":"a","col":0,"row":0,"label":"리포트 이메일","sub":"24시간 불규칙 수신"},
  {"id":"b","col":1,"row":0,"label":"① 수집 (RPA)","sub":"15단계 라우팅 · 폴백 다운로드"},
  {"id":"c","col":2,"row":0,"label":"② 요약·적재","sub":"OCR → GPT → Excel 8섹션"},
  {"id":"d","col":3,"row":0,"label":"③ 주간 웹앱","sub":"6모델 병렬 + LLM Judge"},
  {"id":"e","col":4,"row":0,"label":"④ 배포·보관","sub":"뉴스레터 · PDF 아카이빙"},
  {"id":"f","col":5,"row":0,"label":"C-Level 구독","sub":"주간 브리핑 운영 중","type":"accent"},
  {"id":"g","col":2,"row":1,"label":"이중 예외 알림","sub":"AI 거부 · 시스템 오류","type":"warn"},
  {"id":"h","col":3,"row":1,"label":"블라인드 평가","sub":"A~F 라벨 · Judge 폴백"},
 ],
 "edges":[("a","b"),("b","c"),("c","d"),("d","e"),("e","f"),
          ("c","g","","dash"),("h","d","","dash")]}))

# ── 카드 15 · memo-ai ──
S.append(("c15-memoai-arch.svg", {
 "title": "Outbox 동기화 + 하이브리드 변환",
 "nodes": [
  {"id":"a","col":0,"row":0,"label":"문서 업로드","sub":"PDF · Office · 이미지"},
  {"id":"b","col":1,"row":0,"label":"Docling 1차 변환","sub":"TableFormer + EasyOCR"},
  {"id":"c","col":1,"row":1,"label":"GPT-4o Vision 2차","sub":"누락 청크만 · hard cap"},
  {"id":"d","col":2,"row":0,"label":"Markdown 노트","sub":"BlockNote 에디터"},
  {"id":"e","col":3,"row":0,"label":"MSSQL (본문)","type":"store"},
  {"id":"f","col":4,"row":0,"label":"Outbox 패턴","sub":"비동기 동기화 + 대사"},
  {"id":"g","col":5,"row":0,"label":"FalkorDB (그래프)","type":"store"},
  {"id":"h","col":5,"row":1,"label":"3D 지식 그래프","sub":"3-Shell 동심구 레이아웃","type":"accent"},
 ],
 "edges":[("a","b"),("b","c","누락 시","dash"),("c","d"),("b","d"),
          ("d","e"),("e","f"),("f","g"),("g","h")]}))

if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    for fname, spec in S:
        render(spec, fname)
    print(f"\n총 {len(S)}개 다이어그램 생성 완료 → assets/diagrams/")
