import { jest } from "@jest/globals";

describe("lib/api", () => {
  beforeEach(() => {
    jest.resetModules();
    global.fetch = jest.fn();
  });

  afterEach(() => {
    jest.clearAllMocks();
  });

  async function loadApiWithBase(base) {
    // Must set env BEFORE importing the module because API_BASE is read at module load
    process.env.NEXT_PUBLIC_API_BASE = base;
    const mod = await import("../../lib/api.js");
    return mod;
  }

  function mockFetchOk(jsonData) {
    fetch.mockResolvedValueOnce({
      ok: true,
      json: async () => jsonData,
    });
  }

  function mockFetchFail(status = 500) {
    fetch.mockResolvedValueOnce({
      ok: false,
      status,
      json: async () => ({ detail: "error" }),
    });
  }

  test("login(): posts form-urlencoded to /auth/login and returns json", async () => {
    const { login } = await loadApiWithBase("http://example.com");
    mockFetchOk({ access_token: "t", token_type: "bearer" });

    const data = await login("viewer", "viewer123");

    expect(fetch).toHaveBeenCalledTimes(1);

    const [url, opts] = fetch.mock.calls[0];
    expect(url).toBe("http://example.com/auth/login");
    expect(opts.method).toBe("POST");
    expect(opts.headers).toEqual({
      "Content-Type": "application/x-www-form-urlencoded",
    });

    // Body should be URLSearchParams
    expect(opts.body).toBeInstanceOf(URLSearchParams);
    expect(opts.body.get("username")).toBe("viewer");
    expect(opts.body.get("password")).toBe("viewer123");

    expect(data).toEqual({ access_token: "t", token_type: "bearer" });
  });

  test("login(): throws on non-ok response", async () => {
    const { login } = await loadApiWithBase("http://example.com");
    mockFetchFail(401);

    await expect(login("viewer", "bad")).rejects.toThrow("Login failed");
  });

  test("createJob(): posts json with Bearer token", async () => {
    const { createJob } = await loadApiWithBase("http://example.com");
    mockFetchOk({ id: 123 });

    const data = await createJob("abc", "hello");

    const [url, opts] = fetch.mock.calls[0];
    expect(url).toBe("http://example.com/jobs");
    expect(opts.method).toBe("POST");
    expect(opts.headers).toEqual({
      "Content-Type": "application/json",
      Authorization: "Bearer abc",
    });
    expect(opts.body).toBe(JSON.stringify({ input_text: "hello" }));
    expect(data).toEqual({ id: 123 });
  });

  test("createJob(): throws on non-ok response", async () => {
    const { createJob } = await loadApiWithBase("http://example.com");
    mockFetchFail(400);

    await expect(createJob("abc", "x")).rejects.toThrow("Create job failed");
  });

  test("listJobs(): sends Authorization header and returns json", async () => {
    const { listJobs } = await loadApiWithBase("http://example.com");
    mockFetchOk([{ id: 1 }]);

    const data = await listJobs("tok");

    const [url, opts] = fetch.mock.calls[0];
    expect(url).toBe("http://example.com/jobs");
    expect(opts.headers).toEqual({ Authorization: "Bearer tok" });
    expect(data).toEqual([{ id: 1 }]);
  });

  test("listJobs(): throws on non-ok response", async () => {
    const { listJobs } = await loadApiWithBase("http://example.com");
    mockFetchFail(500);

    await expect(listJobs("tok")).rejects.toThrow("List jobs failed");
  });

  test("getJob(): fetches /jobs/:id and returns json", async () => {
    const { getJob } = await loadApiWithBase("http://example.com");
    mockFetchOk({ id: 7 });

    const data = await getJob("tok", 7);

    const [url, opts] = fetch.mock.calls[0];
    expect(url).toBe("http://example.com/jobs/7");
    expect(opts.headers).toEqual({ Authorization: "Bearer tok" });
    expect(data).toEqual({ id: 7 });
  });

  test("getJob(): throws on non-ok response", async () => {
    const { getJob } = await loadApiWithBase("http://example.com");
    mockFetchFail(404);

    await expect(getJob("tok", 999)).rejects.toThrow("Get job failed");
  });

  test("getResult(): fetches /jobs/:id/result and returns json", async () => {
    const { getResult } = await loadApiWithBase("http://example.com");
    mockFetchOk({ output: "ok" });

    const data = await getResult("tok", 7);

    const [url, opts] = fetch.mock.calls[0];
    expect(url).toBe("http://example.com/jobs/7/result");
    expect(opts.headers).toEqual({ Authorization: "Bearer tok" });
    expect(data).toEqual({ output: "ok" });
  });

  test("getResult(): throws 'Result not ready' on non-ok response", async () => {
    const { getResult } = await loadApiWithBase("http://example.com");
    mockFetchFail(404);

    await expect(getResult("tok", 7)).rejects.toThrow("Result not ready");
  });

  test("getAnalytics(): fetches /analytics/summary and returns json", async () => {
    const { getAnalytics } = await loadApiWithBase("http://example.com");
    mockFetchOk({ totals: { jobs: 1 } });

    const data = await getAnalytics("tok");

    const [url, opts] = fetch.mock.calls[0];
    expect(url).toBe("http://example.com/analytics/summary");
    expect(opts.headers).toEqual({ Authorization: "Bearer tok" });
    expect(data).toEqual({ totals: { jobs: 1 } });
  });

  test("getAnalytics(): throws on non-ok response", async () => {
    const { getAnalytics } = await loadApiWithBase("http://example.com");
    mockFetchFail(500);

    await expect(getAnalytics("tok")).rejects.toThrow("Analytics failed");
  });
});
