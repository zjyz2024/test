import os
import random
import time
from playwright.sync_api import sync_playwright

EMAIL = os.getenv("EMAIL")
PASSWORD = os.getenv("PASSWORD")
TWOFA = os.getenv("TWOFA", "")

URL = os.getenv("URL")

PROXY = None  # 可设置为 "socks5://127.0.0.1:1080" 或 None

def run():
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True, # True=无窗口 False=有窗口 
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

        # 判断是否需要取消账户保护
        email_input = page.query_selector('input.form-control.maxwidth-auth#email')
        if email_input:
            print("检测到账户保护，正在尝试取消...")
            email_input.fill(EMAIL)
            page.click('button#reactive')
            page.wait_for_load_state("networkidle")
            print("✅ 已取消账户保护。")
            page.click("a:has-text('用户面板')")

        # 自动签到
        el = page.query_selector('#checkin')
        if el:
            el.click()

        # 点击“套餐购买”链接
        page.click("a:has-text('套餐购买')")

        # 等待跳转完成
        page.wait_for_load_state("networkidle")

        # 点击购买按钮
        # 3 days ID=8
        # 1 days ID=9
        page.wait_for_selector('a[onclick="buy(\'8\',0)"]', timeout=5000)
        page.click('a[onclick="buy(\'8\',0)"]')

        # 等待弹出确认按钮加载并点击“确定”
        page.wait_for_selector('#coupon_input', timeout=5000)
        page.click('#coupon_input')

        # 点击再次确定按钮
        page.wait_for_selector('#order_input', timeout=5000)
        page.click('#order_input')

        # 等待购买完成
        page.wait_for_timeout(10000)

        print("✅ 任务完成！")

        browser.close()

def random_delay():
    random_seconds = random.randint(0, 30)
    time.sleep(random_seconds)
    print("✅ 已随机休眠{}秒！".format(random_seconds))

random_delay()
run()
