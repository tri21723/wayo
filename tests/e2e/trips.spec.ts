import { test, expect, type Page } from "@playwright/test";

const userId = "11111111-1111-4111-8111-111111111111";
const tripId = "22222222-2222-4222-8222-222222222222";

async function mockAuth(page: Page) {
  // These tests exercise browser state only. Backend tests independently verify real JWT signatures.
  const now = Math.floor(Date.now() / 1000);
  const payload = Buffer.from(
    JSON.stringify({
      sub: userId,
      aud: "authenticated",
      role: "authenticated",
      iat: now,
      exp: now + 3600,
    }),
  ).toString("base64url");
  const token = `eyJhbGciOiJSUzI1NiJ9.${payload}.dGVzdA`;
  await page.route("**/auth/v1/**", async (route) => {
    if (route.request().url().includes("/token")) {
      await route.fulfill({
        json: {
          access_token: token,
          token_type: "bearer",
          expires_in: 3600,
          refresh_token: "e2e-refresh",
          user: {
            id: userId,
            aud: "authenticated",
            email: "traveler@example.com",
            role: "authenticated",
            app_metadata: {},
            user_metadata: {},
            created_at: new Date().toISOString(),
          },
        },
      });
    } else await route.fulfill({ status: 200, json: {} });
  });
}

async function signIn(page: Page) {
  await page.goto("/login");
  await page.getByLabel("Email", { exact: true }).fill("traveler@example.com");
  await page.getByLabel("Mật khẩu").fill("test-password");
  await page.getByRole("button", { name: "Đăng nhập", exact: true }).click();
  await expect(page).toHaveURL(/\/trips$/);
}

test("sign in, create, reopen, edit and delete a saved draft", async ({
  page,
}) => {
  await mockAuth(page);
  let saved: Record<string, unknown> | null = null;
  await page.route("**/api/trips**", async (route) => {
    const request = route.request();
    const url = new URL(request.url());
    if (url.pathname.endsWith("/validate")) {
      const trip = request.postDataJSON();
      return route.fulfill({
        json: {
          status: "input_valid",
          trip_days: 3,
          total_budget_vnd: 8000000,
          notices: [],
          trip,
        },
      });
    }
    expect(request.headers().authorization).toContain("Bearer ");
    if (request.method() === "POST") {
      const input = request.postDataJSON();
      expect(input.request_id).toMatch(/^[a-f0-9-]{36}$/);
      saved = {
        id: tripId,
        title: input.title,
        trip: input.trip,
        revision: 1,
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
      };
      return route.fulfill({ status: 201, json: saved });
    }
    if (request.method() === "PUT") {
      const input = request.postDataJSON();
      expect(input.expected_revision).toBe(1);
      saved = { ...saved, title: input.title, trip: input.trip, revision: 2 };
      return route.fulfill({ json: saved });
    }
    if (request.method() === "DELETE") {
      expect(url.searchParams.get("expected_revision")).toBe("2");
      saved = null;
      return route.fulfill({ status: 204 });
    }
    return route.fulfill({
      json: url.pathname.endsWith(tripId)
        ? saved
        : {
            items: saved ? [saved] : [],
            total: saved ? 1 : 0,
            offset: 0,
            limit: 20,
          },
    });
  });
  await signIn(page);
  await expect(page.getByText("Chuyến đi đầu tiên đang chờ bạn")).toBeVisible();
  await page.getByRole("link", { name: "+ Tạo chuyến đi mới" }).click();
  await page.getByLabel("Tên chuyến đi").fill("Cuối tuần Đà Lạt");
  await page.getByLabel("Đến Đà Lạt lúc").fill("2026-11-06T12:00");
  await page.getByLabel("Rời Đà Lạt lúc").fill("2026-11-08T17:00");
  await page
    .getByRole("button", { name: "Kiểm tra thông tin chuyến đi" })
    .click();
  await page
    .getByRole("button", { name: "Lưu chuyến đi", exact: true })
    .click();
  await page.getByRole("link", { name: "Mở bản đã lưu →" }).click();
  await expect(page).toHaveURL(new RegExp(`/trips/${tripId}$`));
  await expect(
    page.getByRole("heading", { name: "Chỉnh sửa chuyến đi" }),
  ).toBeVisible();
  await expect(page.getByLabel("Tên chuyến đi")).toHaveValue(
    "Cuối tuần Đà Lạt",
  );
  await expect(page.getByLabel("Đến Đà Lạt lúc")).toHaveValue(
    "2026-11-06T12:00",
  );
  await page.getByLabel("Tên chuyến đi").fill("Một chuyến đi thảnh thơi");
  await page
    .getByRole("button", { name: "Kiểm tra thông tin chuyến đi" })
    .click();
  await page.getByRole("button", { name: "Lưu thay đổi" }).click();
  await expect(page.getByText("Đã lưu thay đổi chuyến đi.")).toBeVisible();
  await page.reload();
  await expect(page.getByLabel("Tên chuyến đi")).toHaveValue(
    "Một chuyến đi thảnh thơi",
  );
  await page
    .getByRole("button", { name: "Xóa chuyến đi", exact: true })
    .click();
  await page.getByRole("button", { name: "Giữ lại" }).click();
  await expect(page.getByLabel("Tên chuyến đi")).toBeVisible();
  await page
    .getByRole("button", { name: "Xóa chuyến đi", exact: true })
    .click();
  await page.getByRole("button", { name: "Xác nhận xóa" }).click();
  await expect(page).toHaveURL(/\/trips$/);
  await expect(page.getByText("Chuyến đi đầu tiên đang chờ bạn")).toBeVisible();
});

test("failed save can retry without duplicating request; logout hides private data", async ({
  page,
}) => {
  await mockAuth(page);
  const requestIds: string[] = [];
  await page.route("**/api/trips**", async (route) => {
    const request = route.request();
    if (request.url().endsWith("/validate"))
      return route.fulfill({
        json: {
          status: "input_valid",
          trip_days: 3,
          total_budget_vnd: 8000000,
          notices: [],
          trip: request.postDataJSON(),
        },
      });
    if (request.method() === "POST") {
      requestIds.push(request.postDataJSON().request_id);
      return route.fulfill({
        status: 503,
        json: { code: "API_UNAVAILABLE", message: "Thử lại sau.", details: [] },
      });
    }
    return route.fulfill({
      json: { items: [], total: 0, offset: 0, limit: 20 },
    });
  });
  await signIn(page);
  await page.goto("/");
  await page.getByLabel("Đến Đà Lạt lúc").fill("2026-11-06T12:00");
  await page.getByLabel("Rời Đà Lạt lúc").fill("2026-11-08T17:00");
  await page
    .getByRole("button", { name: "Kiểm tra thông tin chuyến đi" })
    .click();
  await page
    .getByRole("button", { name: "Lưu chuyến đi", exact: true })
    .click();
  await expect(
    page.getByRole("alert").filter({ hasText: "Thử lại sau." }),
  ).toBeVisible();
  await page
    .getByRole("button", { name: "Lưu chuyến đi", exact: true })
    .click();
  await expect(
    page.getByRole("alert").filter({ hasText: "Thử lại sau." }),
  ).toBeVisible();
  expect(requestIds).toHaveLength(2);
  expect(requestIds[0]).toBe(requestIds[1]);
  await page.getByRole("link", { name: "Chuyến đi của tôi" }).click();
  await page.getByRole("button", { name: "Đăng xuất" }).click();
  await expect(
    page.getByText("Đăng nhập để xem các chuyến đi đã lưu của bạn."),
  ).toBeVisible();
});

test("profile saves, reloads, handles stale writes and clears on sign out", async ({
  page,
}) => {
  await mockAuth(page);
  await page.route("**/api/trips?**", (route) =>
    route.fulfill({ json: { items: [], total: 0, limit: 20, offset: 0 } }),
  );
  let stored: Record<string, unknown> = {
    revision: 0,
    schema_version: 1,
    answers: null,
    vector: {},
  };
  let conflict = false;
  await page.route("**/api/profile", async (route) => {
    expect(route.request().headers().authorization).toContain("Bearer ");
    if (route.request().method() === "PUT") {
      const input = route.request().postDataJSON();
      if (conflict)
        return route.fulfill({
          status: 409,
          json: {
            code: "REVISION_CONFLICT",
            message: "Sở thích đã thay đổi. Hãy tải lại trước khi lưu.",
            details: [],
          },
        });
      expect(input.expected_revision).toBe(0);
      stored = { ...stored, revision: 1, answers: input.answers };
    }
    await route.fulfill({ json: stored });
  });
  await signIn(page);
  await page.getByRole("link", { name: "Sở thích của tôi" }).click();
  await expect(
    page.getByRole("button", { name: "Lưu sở thích" }),
  ).toBeDisabled();
  await page.getByLabel("Thiên nhiên", { exact: true }).check();
  await page.getByLabel("5. Chế độ ăn").selectOption("vegan");
  await page.getByLabel("Trekking", { exact: true }).check();
  await page.getByRole("button", { name: "Lưu sở thích" }).click();
  await expect(page.getByText("Đã lưu sở thích của bạn.")).toBeVisible();
  await page.reload();
  await expect(page.getByLabel("Thiên nhiên", { exact: true })).toBeChecked();
  await expect(page.getByLabel("5. Chế độ ăn")).toHaveValue("vegan");
  await expect(page.getByLabel("Trekking", { exact: true })).toBeChecked();
  conflict = true;
  await page.getByLabel("Cà phê", { exact: true }).check();
  await page.getByRole("button", { name: "Lưu sở thích" }).click();
  await expect(
    page.getByText("Sở thích đã thay đổi. Hãy tải lại trước khi lưu."),
  ).toBeVisible();
  await expect(page.getByLabel("Cà phê", { exact: true })).toBeChecked();
  await page.getByRole("button", { name: "Tải lại sở thích đã lưu" }).click();
  await expect(page.getByLabel("Cà phê", { exact: true })).not.toBeChecked();
  await page.getByRole("button", { name: "Đăng xuất", exact: true }).click();
  await expect(
    page.getByRole("link", { name: "Đăng nhập để lưu sở thích" }),
  ).toBeVisible();
  await expect(page.getByLabel("5. Chế độ ăn")).toHaveCount(0);
});

test("discovery handles empty catalog, errors, sources and stale trip revisions", async ({
  page,
}) => {
  await mockAuth(page);
  let mode: "empty" | "error" | "populated" | "stale" = "empty";
  const trip = {
    id: tripId,
    title: "Discovery fixture",
    revision: 1,
    created_at: "2026-10-01T00:00:00Z",
    updated_at: "2026-10-01T00:00:00Z",
    trip: {
      destination_id: "da-lat",
      origin: "TP.HCM",
      arrival_at: "2026-11-06T12:00:00+07:00",
      departure_at: "2026-11-08T17:00:00+07:00",
      people_count: 2,
      group_type: "couple",
      budget: {
        amount_vnd: 4000000,
        scope: "per_person",
        mode: "soft",
        currency: "VND",
      },
      pace: "relaxed",
      preferences: ["Cafe"],
      exclusions: ["Trekking"],
    },
  };
  await page.route("**/api/trips**", async (route) => {
    const path = new URL(route.request().url()).pathname;
    if (path.endsWith("/recommendations")) {
      expect(route.request().headers().authorization).toContain("Bearer ");
      if (mode === "error")
        return route.fulfill({
          status: 503,
          json: {
            code: "UNAVAILABLE",
            message: "Chưa tải được gợi ý thử nghiệm.",
            details: [],
          },
        });
      return route.fulfill({
        json: {
          trip_revision: mode === "stale" ? 2 : 1,
          notices: [
            {
              code: "NOTICE",
              message:
                mode === "empty"
                  ? "Chưa có địa điểm được xác minh gần đây đáp ứng bộ lọc của chuyến đi."
                  : "Chưa kiểm tra tuyến đường hoặc tổng chi phí.",
            },
          ],
          items:
            mode === "populated"
              ? [
                  {
                    place: {
                      slug: "synthetic-cafe",
                      name: "Synthetic cafe fixture",
                      address: "Test address",
                      price: null,
                      duration_minutes: 60,
                      sources: [
                        {
                          url: "https://example.org/test-fixture",
                          checked_at: "2026-10-01T00:00:00Z",
                          note: "Synthetic browser fixture only.",
                        },
                      ],
                    },
                    reasons: ["Hợp sở thích: Cà phê"],
                    warnings: ["Chưa có giờ mở cửa được xác minh."],
                  },
                ]
              : [],
        },
      });
    }
    return route.fulfill({
      json: path.endsWith(tripId)
        ? trip
        : { items: [trip], total: 1, limit: 20, offset: 0 },
    });
  });
  await signIn(page);
  await page.getByRole("link", { name: "Discovery fixture" }).click();
  const load = page.getByRole("button", { name: "Xem gợi ý địa điểm" });
  await load.click();
  await expect(
    page.getByText(
      "Chưa có địa điểm được xác minh gần đây đáp ứng bộ lọc của chuyến đi.",
    ),
  ).toBeVisible();
  mode = "error";
  await load.click();
  await expect(page.getByText("Chưa tải được gợi ý thử nghiệm.")).toBeVisible();
  mode = "populated";
  await load.click();
  await expect(
    page.getByRole("heading", { name: "Synthetic cafe fixture" }),
  ).toBeVisible();
  await expect(page.getByText("Giá: chưa xác minh")).toBeVisible();
  await page.getByText("Nguồn thông tin", { exact: true }).click();
  await expect(page.getByRole("link", { name: "Nguồn 1" })).toHaveAttribute(
    "href",
    "https://example.org/test-fixture",
  );
  mode = "stale";
  await load.click();
  await expect(
    page.getByText(
      "Chuyến đi đã thay đổi ở nơi khác. Hãy tải lại bản đã lưu trước khi xem gợi ý.",
    ),
  ).toBeVisible();
  await expect(
    page.getByRole("heading", { name: "Synthetic cafe fixture" }),
  ).toHaveCount(0);
});
