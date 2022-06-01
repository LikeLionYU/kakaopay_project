from django.shortcuts import render, redirect
import requests

def home(request):
    if request.method == 'POST':
        URL = 'https://kapi.kakao.com/v1/payment/ready'
        headers = {
            "Authorization": "KakaoAK " + "88ca1875a9b3176b59b0098a0345ed1e",
            "Content-type": "application/x-www-form-urlencoded;charset=utf-8",
        }

        params = {
            "cid": "TC0ONETIME",    # 테스트용 제휴코드
            "partner_order_id": "1001",     # 주문번호
            "partner_user_id": "german",    # 유저 아이디
            "item_name": "연어초밥",        # 구매 물품 이름
            "quantity": "1",                # 구매 물품 수량
            "total_amount": "12000",        # 구매 물품 가격
            "tax_free_amount": "0",         # 구매 물품 비과세
            "approval_url": "http://127.0.0.1:8000/admin",
            "cancel_url": "http://127.0.0.1:8000/",
            "fail_url": "http://127.0.0.1:8000/",
        }

        response = requests.post(URL, headers=headers, params=params)
        request.session['tid'] = response.json()['tid']      # 결제 승인시 사용할 tid를 세션에 저장
        next_url = response.json()['next_redirect_pc_url']   # 결제 페이지로 넘어갈 url을 저장
        return redirect(next_url)

    return render(request, 'home.html')