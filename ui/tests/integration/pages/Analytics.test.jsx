import React from "react";
import { render, screen, waitFor } from "@testing-library/react";
import "@testing-library/jest-dom";

import Analytics from "@/pages/analytics";
import { getAnalytics } from "@/lib/api";
import { goTo } from "@/lib/nav";

jest.mock("@/lib/api", () => ({
    getAnalytics: jest.fn(),
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

describe("Analytics page", () => {
    beforeEach(() => {
        jest.clearAllMocks();
    });

    afterEach(() => {
        if (Storage.prototype.getItem?.mockRestore) {
            Storage.prototype.getItem.mockRestore();
        }
    });

    test("redirects to /login when token is missing and does not call API", () => {
        mockToken(null);

        render(<Analytics />);

        expect(goTo).toHaveBeenCalledWith("/login");
        expect(getAnalytics).not.toHaveBeenCalled();
    });

    test("calls getAnalytics with token on mount and renders JSON", async () => {
        mockToken("tkn");
        getAnalytics.mockResolvedValueOnce({
            totals: { jobs: 12, done: 9 },
            byUser: [{ user: "viewer", count: 7 }],
        });

        render(<Analytics />);

        await waitFor(() => {
            expect(getAnalytics).toHaveBeenCalledWith("tkn");
        });

        // ✅ wait for <pre> to update from null -> JSON
        const pre = screen.getByText((_, node) => node?.tagName === "PRE");
        await waitFor(() => {
            expect(pre.textContent).toContain('"jobs": 12');
            expect(pre.textContent).toContain('"done": 9');
            expect(pre.textContent).toContain('"viewer"');
        });

        expect(screen.getByRole("link", { name: /Back to Jobs/i })).toHaveAttribute("href", "/jobs");
    });

    test("renders null JSON initially (before API resolves)", () => {
        mockToken("tkn");
        getAnalytics.mockImplementationOnce(
            () => new Promise(() => { }) // never resolves
        );

        render(<Analytics />);

        // Should show null while waiting
        expect(screen.getByText((_, node) => node?.tagName === "PRE")).toHaveTextContent("null");
    });
});
