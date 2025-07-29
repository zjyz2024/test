import os
import random
import time

from playwright.sync_api import sync_playwright

EMAIL = os.getenv("EMAIL")
PASSWORD = os.getenv("PASSWORD")
TWOFA = os.getenv("TWOFA", "")

PROXY = None  # 可设置为 "socks5://127.0.0.1:1080" 或 None

URL = os.getenv("URL", "")







# # 下面执行你的自动购买逻辑
def run():
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            proxy={"server": PROXY} if PROXY else None
        )
        context = browser.new_context()
        page = context.new_page()

        # 打开登录页面
        page.goto(URL)

        # 填写邮箱和密码
        page.fill('input[name="Email"]', EMAIL)
        page.fill('input[name="Password"]', PASSWORD)

        # 如果启用了两步验证码
        if TWOFA:
            page.fill('input[name="Code"]', TWOFA)

        # 点击“确认登录”按钮
        page.click('button#login')

        # 等待登录后跳转（如 dashboard 或首页）
        page.wait_for_load_state("networkidle")

        el = page.query_selector('#checkin')
        if el:
            el.click()
        else:
            pass  # 没找到就跳过，不打印也不报错

        # 点击“套餐购买”链接
        page.click("a:has-text('套餐购买')")

        # 等待跳转完成
        page.wait_for_load_state("networkidle")

        # 点击购买按钮（套餐ID为8）
        # 3 days 80
        # 1 days 90
        page.wait_for_selector('a[onclick="buy(\'8\',0)"]', timeout=5000)
        page.click('a[onclick="buy(\'8\',0)"]')

        # ✅ 等待弹出确认按钮加载并点击“确定”
        page.wait_for_selector('#coupon_input', timeout=5000)
        page.click('#coupon_input')

        # ✅ 第二步弹窗：点击 order_input 确定按钮
        page.wait_for_selector('#order_input', timeout=5000)
        page.click('#order_input')
        print("已点击第二个确认按钮（order_input）")

        page.wait_for_timeout(10000)
        browser.close()

wait_minutes = random.randint(0, 300)
print(f"随机等待 {wait_minutes} seconds再开始执行任务")
time.sleep(wait_minutes)
run()
