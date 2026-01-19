import React from "react";
import { act } from "react";
import { render, screen, fireEvent, waitFor, within } from "@testing-library/react";
import "@testing-library/jest-dom";

import Jobs from "@/pages/jobs";
import { createJob, listJobs, getResult, getJob } from "@/lib/api";
import { goTo } from "@/lib/nav";

jest.mock("@/lib/api", () => ({
    createJob: jest.fn(),
    listJobs: jest.fn(),
    getResult: jest.fn(),
    getJob: jest.fn(),
}));

jest.mock("@/lib/nav", () => ({
    goTo: jest.fn(),
}));

function mockToken(tokenValue) {
    jest.spyOn(Storage.prototype, "getItem").mockImplementation((k) => {
        if (k === "token") return tokenValue;
        return null;
    });
}

describe("Jobs page", () => {
    beforeEach(() => {
        jest.clearAllMocks();
        jest.useFakeTimers();
    });

    afterEach(() => {
        jest.useRealTimers();
        if (Storage.prototype.getItem?.mockRestore) {
            Storage.prototype.getItem.mockRestore();
        }
    });

    test("redirects to /login when token is missing (no API calls)", () => {
        mockToken(null);

        render(<Jobs />);

        expect(goTo).toHaveBeenCalledWith("/login");
        expect(listJobs).not.toHaveBeenCalled();
    });

    test("calls listJobs on mount and renders returned rows", async () => {
        mockToken("tkn");
        listJobs.mockResolvedValueOnce([
            { id: 1, status: "NEW", submitted_by: "viewer", created_at: "2026-01-18" },
            { id: 2, status: "DONE", submitted_by: "admin", created_at: "2026-01-18" },
        ]);

        render(<Jobs />);

        await waitFor(() => expect(listJobs).toHaveBeenCalledWith("tkn"));

        // Wait for DOM re-render with rows
        expect(await screen.findByText("NEW")).toBeInTheDocument();
        expect(await screen.findByText("DONE")).toBeInTheDocument();
        expect(screen.getByText("viewer")).toBeInTheDocument();
        expect(screen.getByText("admin")).toBeInTheDocument();

        const table = screen.getByTestId("jobs-table");
        const rows = within(table).getAllByRole("row");
        expect(rows).toHaveLength(3); // header + 2 rows
    });

    test("polls refresh every 2 seconds and stops on unmount", async () => {
        mockToken("tkn");
        listJobs.mockResolvedValue([]); // stable response

        const { unmount } = render(<Jobs />);

        // initial refresh on mount
        await waitFor(() => expect(listJobs).toHaveBeenCalledTimes(1));

        // +2s => refresh again (wrap timer tick in act)
        await act(async () => {
            await jest.advanceTimersByTimeAsync(2000);
        });
        await waitFor(() => expect(listJobs).toHaveBeenCalledTimes(2));

        // +2s => refresh again
        await act(async () => {
            await jest.advanceTimersByTimeAsync(2000);
        });
        await waitFor(() => expect(listJobs).toHaveBeenCalledTimes(3));

        // unmount also can trigger cleanup updates, so wrap it too
        await act(async () => {
            unmount();
        });

        // no more calls after unmount even if time passes
        await act(async () => {
            await jest.advanceTimersByTimeAsync(4000);
        });

        expect(listJobs).toHaveBeenCalledTimes(3);
    });

    test("submit success: calls createJob, clears input, and refreshes jobs", async () => {
        mockToken("tkn");

        // mount refresh
        listJobs.mockResolvedValueOnce([]);

        // submit succeeds
        createJob.mockResolvedValueOnce({});

        // refresh after submit returns 1 row
        listJobs.mockResolvedValueOnce([
            { id: 10, status: "NEW", submitted_by: "viewer", created_at: "now" },
        ]);

        render(<Jobs />);

        await waitFor(() => expect(listJobs).toHaveBeenCalledTimes(1));

        fireEvent.change(screen.getByTestId("job-input"), {
            target: { value: "run pipeline" },
        });

        fireEvent.click(screen.getByTestId("submit-job"));

        await waitFor(() => expect(createJob).toHaveBeenCalledWith("tkn", "run pipeline"));

        // wait until input clears
        await waitFor(() => {
            expect(screen.getByTestId("job-input")).toHaveValue("");
        });

        // refresh called again
        await waitFor(() => expect(listJobs).toHaveBeenCalledTimes(2));

        // row rendered
        expect(await screen.findByText("10")).toBeInTheDocument();
    });

    test("submit failure: shows error message and does not clear input", async () => {
        mockToken("tkn");
        listJobs.mockResolvedValueOnce([]); // mount refresh
        createJob.mockRejectedValueOnce(new Error("boom"));

        render(<Jobs />);

        await waitFor(() => expect(listJobs).toHaveBeenCalledTimes(1));

        fireEvent.change(screen.getByTestId("job-input"), {
            target: { value: "bad job" },
        });

        fireEvent.click(screen.getByTestId("submit-job"));

        expect(await screen.findByText("Failed to submit job")).toBeInTheDocument();

        // input should remain
        expect(screen.getByTestId("job-input")).toHaveValue("bad job");
    });

    test("inspect success: loads job detail + result and displays JSON", async () => {
        mockToken("tkn");
        listJobs.mockResolvedValueOnce([
            { id: 7, status: "DONE", submitted_by: "viewer", created_at: "today" },
        ]);

        getJob.mockResolvedValueOnce({ id: 7, status: "DONE", foo: "bar" });
        getResult.mockResolvedValueOnce({ job_id: 7, output: "ok" });

        render(<Jobs />);

        // ensure the row exists before clicking Inspect
        expect(await screen.findByText("7")).toBeInTheDocument();

        fireEvent.click(screen.getByRole("button", { name: "Inspect" }));

        await waitFor(() => expect(getJob).toHaveBeenCalledWith("tkn", 7));
        await waitFor(() => expect(getResult).toHaveBeenCalledWith("tkn", 7));

        expect(screen.getByText("Job #7")).toBeInTheDocument();

        // the two PRE blocks render JSON.stringify(detail) and JSON.stringify(result)
        const pres = screen.getAllByText((_, node) => node?.tagName === "PRE");

        await waitFor(() => {
            expect(pres[0].textContent).toContain('"foo": "bar"');
            expect(pres[1].textContent).toContain('"output": "ok"');
        });
    });

    test("inspect when result not ready: shows fallback message", async () => {
        mockToken("tkn");
        listJobs.mockResolvedValueOnce([
            { id: 8, status: "RUNNING", submitted_by: "viewer", created_at: "today" },
        ]);

        getJob.mockResolvedValueOnce({ id: 8, status: "RUNNING" });
        getResult.mockRejectedValueOnce(new Error("not ready"));

        render(<Jobs />);

        // ensure the row exists before clicking Inspect
        expect(await screen.findByText("8")).toBeInTheDocument();

        fireEvent.click(screen.getByRole("button", { name: "Inspect" }));

        await waitFor(() => expect(getJob).toHaveBeenCalledWith("tkn", 8));
        await waitFor(() => expect(getResult).toHaveBeenCalledWith("tkn", 8));

        expect(screen.getByText("Job #8")).toBeInTheDocument();

        const pres = screen.getAllByText((_, node) => node?.tagName === "PRE");

        await waitFor(() => {
            expect(pres[1].textContent).toMatch(/Result not ready/i);
        });
    });
});

