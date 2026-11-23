from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

# 현재 로그인된 사용자 상태 (발표자료 39, 44p)
CURRENT_USER = {
    "is_logged_in": True,
    "name": "서태민",
    "univ": "한국대학교",
    "student_id": "2025******",
    "verified": True,
    "manner_score": 4.5,
    "lend_count": 12,
    "borrow_count": 5,
    "account": "신한 110-***-******"
}

# 1. 공급자가 등록한 물품 데이터
SUPPLY_ITEMS = [
    {"id": 1, "owner": "서태민", "name": "캐논 DSLR 카메라", "price": 10000, "place": "공대 본관 1층", "desc": "배터리 2개 포함, 상태 최상입니다.", "status": "대여가능"},
    {"id": 2, "owner": "이채원", "name": "전공 서적 (경영학원론)", "price": 2000, "place": "중앙도서관 로비", "desc": "필기 거의 없는 깨끗한 책입니다.", "status": "대여가능"},
    {"id": 3, "owner": "박선우", "name": "캠핑용 돗자리 & 테이블", "price": 5000, "place": "학생회관 앞", "desc": "축제 기간 잔디밭에서 쓰기 좋습니다.", "status": "예약중"},
]

# 2. 수요자가 올린 요청 글 데이터
REQUEST_POSTS = [
    {"id": 1, "writer": "서태민", "title": "내일 발표용 맥북 충전기 빌려주세요", "content": "C타입 65W 이상 급하게 구합니다. 정문 직거래 희망", "status": "모집중"},
    {"id": 2, "writer": "최학생", "title": "이번 주말 MT용 블루투스 스피커 구해요", "content": "1박 2일 대여 원합니다. 일당 5천원 생각중입니다.", "status": "모집중"},
]

# 3. 거래 요청 및 진행 데이터
TRADE_REQUESTS = [
    {
        "id": 1,
        "type": "빌려주세요 요청",
        "partner": "김대학 (학교 인증 완료)",
        "item_name": "캐논 DSLR 카메라",
        "days": 2,
        "place": "공대 본관 1층",
        "rental_fee": 20000,
        "deposit": 10000,
        "status": "요청됨"
    }
]

# 4. 1:1 채팅 더미 데이터
CHAT_MESSAGES = [
    {"sender": "김대학", "text": "안녕하세요! 카메라 대여 1일당 만 원이던데, 2일 빌리면 혹시 조금 조정 가능할까요?"},
    {"sender": "서태민", "text": "네, 공대 본관 1층에서 직거래하시면 시간 맞춰드릴게요!"},
]

# 5. 관심(찜) 물품 ID 목록 (발표자료 42p)
WISHLIST_IDS = [1, 2]

# 6. 받은 거래 후기 목록 (발표자료 41, 43p)
RECEIVED_REVIEWS = [
    {"writer": "이채원 (한국대학교 인증)", "date": "2026.11.10", "item": "캐논 DSLR 카메라", "rating": 5, "comment": "약속 시간도 정확히 지켜주시고 카메라 관리 상태도 너무 좋았습니다!"},
    {"writer": "박선우 (한국대학교 인증)", "date": "2026.11.03", "item": "전공 서적 (경영학원론)", "rating": 5, "comment": "필기 흔적 없이 깨끗해서 시험 기간 동안 정말 유용하게 잘 빌려 썼어요."},
]

# 모든 템플릿에서 current_user를 바로 쓸 수 있게 주입
@app.context_processor
def inject_user():
    return dict(current_user=CURRENT_USER)

@app.route("/")
def index():
    return render_template("index.html", items=SUPPLY_ITEMS[:3])

@app.route("/items")
def items_list():
    return render_template("items.html", items=SUPPLY_ITEMS)

@app.route("/items/<int:item_id>", methods=["GET", "POST"])
def item_detail(item_id):
    item = next((i for i in SUPPLY_ITEMS if i["id"] == item_id), None)
    if not item:
        return "물품을 찾을 수 없습니다.", 404

    if request.method == "POST":
        days = int(request.form.get("days", 1))
        place = request.form.get("place")
        rental_fee = item["price"] * days
        TRADE_REQUESTS.append({
            "id": len(TRADE_REQUESTS) + 1,
            "type": "빌려주세요 요청",
            "partner": item["owner"] + " (학교 인증 완료)",
            "item_name": item["name"],
            "days": days,
            "place": place,
            "rental_fee": rental_fee,
            "deposit": int(rental_fee * 0.5),
            "status": "요청됨"
        })
        return redirect(url_for("manage"))

    related_items = [i for i in SUPPLY_ITEMS if i["id"] != item_id]
    is_wished = item_id in WISHLIST_IDS
    return render_template("item_detail.html", item=item, related_items=related_items, is_wished=is_wished)

# 찜하기 토글 (발표자료 42p)
@app.route("/wishlist/<int:item_id>", methods=["POST"])
def toggle_wishlist(item_id):
    if item_id in WISHLIST_IDS:
        WISHLIST_IDS.remove(item_id)
    else:
        WISHLIST_IDS.append(item_id)
    return redirect(request.referrer or url_for("mypage"))

@app.route("/lend")
def lend_list():
    return render_template("lend.html", requests=REQUEST_POSTS)

@app.route("/items/new", methods=["GET", "POST"])
def item_new():
    if request.method == "POST":
        SUPPLY_ITEMS.append({
            "id": len(SUPPLY_ITEMS) + 1,
            "owner": CURRENT_USER["name"],
            "name": request.form.get("title"),
            "price": int(request.form.get("price", 0)),
            "place": "캠퍼스 내 협의",
            "desc": request.form.get("content"),
            "status": "대여가능"
        })
        return redirect(url_for("items_list"))
    return render_template("item_new.html")

@app.route("/requests/new", methods=["GET", "POST"])
def request_new():
    if request.method == "POST":
        REQUEST_POSTS.append({
            "id": len(REQUEST_POSTS) + 1,
            "writer": CURRENT_USER["name"],
            "title": request.form.get("title"),
            "content": request.form.get("content"),
            "status": "모집중"
        })
        return redirect(url_for("lend_list"))
    return render_template("request_new.html")

@app.route("/requests/<int:req_id>", methods=["GET", "POST"])
def request_detail(req_id):
    req = next((r for r in REQUEST_POSTS if r["id"] == req_id), None)
    if not req:
        return "요청 글을 찾을 수 없습니다.", 404

    if request.method == "POST":
        TRADE_REQUESTS.append({
            "id": len(TRADE_REQUESTS) + 1,
            "type": "빌려드릴게요 요청",
            "partner": req["writer"] + " (학교 인증 완료)",
            "item_name": req["title"],
            "days": 1,
            "place": "캠퍼스 정문",
            "rental_fee": 5000,
            "deposit": 3000,
            "status": "요청됨"
        })
        return redirect(url_for("manage"))

    return render_template("request_detail.html", req=req)

@app.route("/manage", methods=["GET", "POST"])
def manage():
    if request.method == "POST":
        msg = request.form.get("message")
        if msg:
            CHAT_MESSAGES.append({"sender": CURRENT_USER["name"], "text": msg})
        return redirect(url_for("manage"))

    return render_template("manage.html", trades=TRADE_REQUESTS, chats=CHAT_MESSAGES)

@app.route("/trade/<int:trade_id>/<action>", methods=["POST"])
def trade_action(trade_id, action):
    trade = next((t for t in TRADE_REQUESTS if t["id"] == trade_id), None)
    if trade:
        if action == "accept":
            trade["status"] = "결제대기"
        elif action == "cancel":
            trade["status"] = "취소됨"
        elif action == "receive":
            trade["status"] = "대여중 (수령완료)"
        elif action == "return":
            trade["status"] = "반납완료"
    return redirect(url_for("manage"))

@app.route("/payment/<int:trade_id>", methods=["GET", "POST"])
def payment(trade_id):
    trade = next((t for t in TRADE_REQUESTS if t["id"] == trade_id), None)
    if not trade:
        return "거래 정보를 찾을 수 없습니다.", 404

    if request.method == "POST":
        trade["status"] = "결제완료"
        return redirect(url_for("manage"))

    return render_template("payment.html", trade=trade)

@app.route("/review/<int:trade_id>", methods=["GET", "POST"])
def review(trade_id):
    trade = next((t for t in TRADE_REQUESTS if t["id"] == trade_id), None)
    if not trade:
        return "거래 정보를 찾을 수 없습니다.", 404

    if request.method == "POST":
        trade["status"] = "후기완료"
        RECEIVED_REVIEWS.insert(0, {
            "writer": f"{CURRENT_USER['name']} ({CURRENT_USER['univ']} 인증)",
            "date": "2026.11.23",
            "item": trade["item_name"],
            "rating": int(request.form.get("rating", 5)),
            "comment": request.form.get("comment")
        })
        return redirect(url_for("mypage"))

    return render_template("review.html", trade=trade)

# ---------------------------------------------------------
# [신규] 로그인 / 회원가입 (학교·학번 인증 팝업 포함)
# ---------------------------------------------------------
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        CURRENT_USER["is_logged_in"] = True
        return redirect(url_for("index"))
    return render_template("login.html")

@app.route("/logout")
def logout():
    CURRENT_USER["is_logged_in"] = False
    return redirect(url_for("login"))

@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        CURRENT_USER["is_logged_in"] = True
        CURRENT_USER["name"] = request.form.get("user_id") or "신규학생"
        CURRENT_USER["univ"] = request.form.get("univ_name") or "한국대학교"
        CURRENT_USER["student_id"] = (request.form.get("student_id") or "2026")[:4] + "******"
        CURRENT_USER["verified"] = True
        return redirect(url_for("index"))
    return render_template("signup.html")

# ---------------------------------------------------------
# [신규] 마이페이지 (발표자료 39~44p)
# ---------------------------------------------------------
@app.route("/mypage")
def mypage():
    my_supply = [i for i in SUPPLY_ITEMS if i["owner"] == CURRENT_USER["name"]]
    my_requests = [r for r in REQUEST_POSTS if r["writer"] == CURRENT_USER["name"]]
    wished_items = [i for i in SUPPLY_ITEMS if i["id"] in WISHLIST_IDS]
    return render_template(
        "mypage.html",
        trades=TRADE_REQUESTS,
        my_supply=my_supply,
        my_requests=my_requests,
        wished_items=wished_items,
        reviews=RECEIVED_REVIEWS
    )

if __name__ == "__main__":
    app.run(debug=True)