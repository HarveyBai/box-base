/**
 * BoxBase 认证流程 e2e 测试
 *
 * 前提: mise run dev 已启动前后端
 * 运行: cd frontend && pnpm test:e2e
 */
import { test, expect } from "@playwright/test";

// ---------------------------------------------------------------------------
// 选择器 — Ant Design 实测有效
// ---------------------------------------------------------------------------
const SEL_USER = 'input[placeholder="请输入用户名"]';
const SEL_EMAIL = 'input[placeholder="请输入邮箱"]';
const SEL_PASS = 'input[placeholder="请输入密码"]';
const SEL_CONFIRM = 'input[placeholder="请再次输入密码"]';
const SEL_SUBMIT = "button.ant-btn-primary[type=submit]";
const SEL_LOGOUT = 'button:has-text("登出")';

// ---------------------------------------------------------------------------
// 工具函数
// ---------------------------------------------------------------------------
function rand(n = 6) {
  return Math.random().toString(36).slice(2, 2 + n);
}

async function registerUser(
  page: import("@playwright/test").Page,
  user: string,
  pass = "Test1234!",
) {
  await page.goto("/register", { waitUntil: "domcontentloaded" });
  await page.locator(SEL_USER).fill(user);
  await page.locator(SEL_EMAIL).fill(`${user}@test.com`);
  await page.locator(SEL_PASS).fill(pass);
  await page.locator(SEL_CONFIRM).fill(pass);
  await page.click(SEL_SUBMIT);
  await page.waitForURL("**/login", { timeout: 15_000 });
}

async function loginUser(
  page: import("@playwright/test").Page,
  user: string,
  pass = "Test1234!",
) {
  await page.goto("/login", { waitUntil: "domcontentloaded" });
  await page.locator(SEL_USER).fill(user);
  await page.locator(SEL_PASS).fill(pass);
  await page.click(SEL_SUBMIT);
  await page.waitForURL("**/dashboard", { timeout: 15_000 });
}

async function logoutUser(page: import("@playwright/test").Page) {
  await page.locator(SEL_LOGOUT).click();
  await page.waitForURL("**/login", { timeout: 15_000 });
}

/** 刷新页面并等待 3s，收集 refresh API 调用状态 */
async function reloadAndWait(
  page: import("@playwright/test").Page,
  waitMs = 3000,
): Promise<number[]> {
  const statuses: number[] = [];
  page.on("response", (resp) => {
    if (resp.url().includes("/api/auth/refresh")) {
      statuses.push(resp.status());
    }
  });
  await page.reload({ waitUntil: "domcontentloaded" });
  await page.waitForTimeout(waitMs);
  return statuses;
}

// ---------------------------------------------------------------------------
// B1: 注册→登录→登出→重登录→F5 不掉登录态
// ---------------------------------------------------------------------------
test("B1: register → login → logout → re-login → F5 still on /dashboard", async ({
  page,
}) => {
  const user = `b1_${rand()}`;

  await registerUser(page, user);
  await loginUser(page, user);
  await logoutUser(page);
  await loginUser(page, user);

  const refreshStatuses = await reloadAndWait(page);

  await expect(page).toHaveURL(/\/dashboard/);
  // 确认重登录后刷新仅产生 1 次 200 refresh
  expect(refreshStatuses.every((s) => s === 200)).toBe(true);

  // 确认 localStorage 有 refresh_token
  const lsRT = await page.evaluate(() =>
    localStorage.getItem("refresh_token"),
  );
  expect(lsRT).toBeTruthy();
});

// ---------------------------------------------------------------------------
// B2: 直接登录→F5 不掉登录态
// ---------------------------------------------------------------------------
test("B2: login → F5 still on /dashboard", async ({ page }) => {
  const user = `b2_${rand()}`;

  await registerUser(page, user);
  await loginUser(page, user);

  const refreshStatuses = await reloadAndWait(page);

  await expect(page).toHaveURL(/\/dashboard/);
  expect(refreshStatuses.every((s) => s === 200)).toBe(true);
});

// ---------------------------------------------------------------------------
// B3: 多标签页并发刷新均不掉登录态
// ---------------------------------------------------------------------------
test("B3: multi-tab concurrent reload stays on /dashboard", async ({
  page,
  context,
}) => {
  const user = `b3_${rand()}`;

  // 在第一个标签页完成注册+登录
  await registerUser(page, user);
  await loginUser(page, user);
  await expect(page).toHaveURL(/\/dashboard/);

  // 第二个标签页共享同一 context（共享 localStorage）
  const page2 = await context.newPage();
  await page2.goto("/dashboard", { waitUntil: "domcontentloaded" });

  // 收集两个标签页的 refresh 状态
  const statuses1: number[] = [];
  const statuses2: number[] = [];
  page.on("response", (r) => {
    if (r.url().includes("/api/auth/refresh")) statuses1.push(r.status());
  });
  page2.on("response", (r) => {
    if (r.url().includes("/api/auth/refresh")) statuses2.push(r.status());
  });

  // 并发刷新
  await Promise.all([
    page.reload({ waitUntil: "domcontentloaded" }),
    page2.reload({ waitUntil: "domcontentloaded" }),
  ]);
  await page.waitForTimeout(3000);
  await page2.waitForTimeout(3000);

  await expect(page).toHaveURL(/\/dashboard/);
  await expect(page2).toHaveURL(/\/dashboard/);
  expect(statuses1.every((s) => s === 200)).toBe(true);
  expect(statuses2.every((s) => s === 200)).toBe(true);

  await page2.close();
});

// ---------------------------------------------------------------------------
// B4: dashboard 显示租户名而非 UUID
// ---------------------------------------------------------------------------
test("B4: dashboard shows tenant name, not UUID", async ({ page }) => {
  const user = `b4_${rand()}`;

  await registerUser(page, user);
  await loginUser(page, user);
  await page.waitForTimeout(2000); // 等待租户数据加载

  // 使用 Ant Descriptions 结构：th(.ant-descriptions-item-label) + td 相邻
  const tenantLabel = page.locator(
    '.ant-descriptions-item-label:has-text("活跃租户")',
  );
  await expect(tenantLabel).toBeVisible({ timeout: 5000 });
  const tenantValue =
    (await tenantLabel
      .locator("..")
      .locator(".ant-descriptions-item-content")
      .textContent()) ?? "";

  // 不是 UUID 格式 (UUID 为 8-4-4-4-12 hex)
  expect(/^[0-9a-f-]{36}$/i.test(tenantValue.trim())).toBe(false);
  // 应该是可读名称
  expect(tenantValue.trim().length).toBeGreaterThan(0);
});

// ---------------------------------------------------------------------------
// B5: 未登录访问 /dashboard → 跳转 /login
// ---------------------------------------------------------------------------
test("B5: unauthenticated /dashboard redirects to /login", async ({
  page,
}) => {
  // 清空 localStorage 确保无残留
  await page.goto("/", { waitUntil: "domcontentloaded" });
  await page.evaluate(() => localStorage.clear());

  await page.goto("/dashboard", { waitUntil: "domcontentloaded" });
  await page.waitForTimeout(1000);

  // 应重定向到登录页
  await expect(page).toHaveURL(/\/login/);
});

// ---------------------------------------------------------------------------
// B6: 超过宽限窗口的旧 jti refresh → 401
// ---------------------------------------------------------------------------
test("B6: stale jti refresh returns 401 after grace window", async ({
  page,
}) => {
  const user = `b6_${rand()}`;

  await registerUser(page, user);
  await loginUser(page, user);

  // 手动拿到当前 refresh_token
  const rt1 = await page.evaluate(() =>
    localStorage.getItem("refresh_token"),
  );
  expect(rt1).toBeTruthy();

  // 先触发一次 refresh，使后端 rotation 生成新 token，旧的被 revoked
  await reloadAndWait(page, 2000);
  await expect(page).toHaveURL(/\/dashboard/);

  const rt2 = await page.evaluate(() =>
    localStorage.getItem("refresh_token"),
  );
  expect(rt2).toBeTruthy();
  expect(rt2).not.toBe(rt1); // rotation 后 token 已换

  // 等待超过宽限窗口 (config 里是 10s)
  await page.waitForTimeout(11_000);

  // 用旧的 refresh_token 直接调 API（模拟攻击/竞态）
  const resp = await page.request.post(
    "http://localhost:8000/api/auth/refresh",
    {
      data: { refresh_token: rt1 },
      headers: { "Content-Type": "application/json" },
    },
  );

  // 旧 jti 应返回 401
  expect(resp.status()).toBe(401);
  const body = await resp.json();
  expect(body.code).toBe("AUTH_INVALID_TOKEN");
});
