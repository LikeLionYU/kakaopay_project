import os
import requests
from django.shortcuts import get_object_or_404, render, redirect
from conf.settings import secrets
from .models import Shopping
from .forms import ShoppingForm

for secret, key in secrets.items():
    if secret == 'DJANGO_APP_KAKAOPAY_API_ADMIN_KEY':
        DJANGO_APP_KAKAOPAY_API_ADMIN_KEY = key

def home(request):
    if request.method == 'POST':
        first_form = ShoppingForm(request.POST)
        if first_form.is_valid():
            # 결제 단계 넘어가면 일단, Shopping Table에 데이터 추가(대신, 구매 확정은 False)
            form = first_form.save(commit=False)
            form.total_amount = int(form.quantity)*int(form.item_price)
            form.save()

            URL = 'https://kapi.kakao.com/v1/payment/ready'
            headers = {
                "Authorization": "KakaoAK " + DJANGO_APP_KAKAOPAY_API_ADMIN_KEY,
                "Content-type": "application/x-www-form-urlencoded;charset=utf-8",
            }
            params = {
                "cid": "TC0ONETIME",    # 테스트용 제휴코드
                "partner_order_id": form.id,     # 주문번호
                "partner_user_id": form.customer_name,    # 유저 아이디
                "item_name": form.item_name,        # 구매 물품 이름
                "quantity": form.quantity,                # 구매 물품 수량
                "total_amount": form.total_amount,        # 구매 물품 가격
                "tax_free_amount": form.tax_free_amount,         # 구매 물품 비과세
                "approval_url": "http://127.0.0.1:8000/approval",
                "cancel_url": "http://127.0.0.1:8000/",
                "fail_url": "http://127.0.0.1:8000/",
            }
            response = requests.post(URL, headers=headers, params=params)

            request.session['tid'] = response.json()['tid']      # 결제 승인시 사용할 tid를 세션에 저장
            request.session['order_id'] = form.id      # 결제 승인시 사용할 order_id를 세션에 저장
            request.session['customer_name'] = form.customer_name      # 결제 승인시 사용할 customer_name을 세션에 저장
            next_url = response.json()['next_redirect_pc_url']   # 결제 페이지로 넘어갈 url을 저장
            return redirect(next_url)

    if request.method == "GET":
        form = ShoppingForm()
        context = {'form':form}
        return render(request, 'home.html', context)


def approval(request):
    if request.method == 'GET':
        # 결제 승인단계에서 해당 쇼핑을 구매 확정 처리
        order_id = request.session['order_id']
        shopped_history = get_object_or_404(Shopping, pk=order_id)
        shopped_history.is_complete = True
        shopped_history.save()

        URL = 'https://kapi.kakao.com/v1/payment/approve'
        headers = {
                "Authorization": "KakaoAK " + DJANGO_APP_KAKAOPAY_API_ADMIN_KEY,
                "Content-type": "application/x-www-form-urlencoded;charset=utf-8",
            }
        params = {
            "cid": "TC0ONETIME",    # 테스트용 코드
            "tid": request.session['tid'],  # 결제 요청시 세션에 저장한 tid
            "partner_order_id": order_id,     # 주문번호
            "partner_user_id": request.session['customer_name'],    # 유저 아이디
            "pg_token": request.GET.get("pg_token"),     # 쿼리 스트링으로 받은 pg토큰
        }
        response = requests.post(URL, headers=headers, params=params)
        amount = response.json()['amount']['total']
        context = {
            'response': response.json(),
            'amount': amount,
        }
        return render(request, 'approval.html', context)

def history(request):
    histories = Shopping.objects.filter(is_complete=True).order_by("-shopped_date")
    context = {'histories':histories}
    return render(request, 'history.html', context)