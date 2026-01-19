import React from "react";
import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import "@testing-library/jest-dom";

import Login from "@/pages/login";
import { login } from "@/lib/api";
import { goTo } from "@/lib/nav";

jest.mock("@/lib/api", () => ({
    login: jest.fn(),
}));

jest.mock("@/lib/nav", () => ({
    goTo: jest.fn(),
}));

describe("Login page", () => {
    beforeEach(() => {
        jest.clearAllMocks();
        jest.spyOn(Storage.prototype, "setItem").mockImplementation(() => { });
    });

    afterEach(() => {
        Storage.prototype.setItem.mockRestore();
    });

    test("renders UI and default input values", () => {
        render(<Login />);

        expect(screen.getByRole("heading", { name: /QA Lab/i })).toBeInTheDocument();
        expect(screen.getByText(/OAuth2 password flow/i)).toBeInTheDocument();
        expect(screen.getByTestId("username")).toHaveValue("viewer");
        expect(screen.getByTestId("password")).toHaveValue("viewer123");
    });

    test("updates username and password when typing", () => {
        render(<Login />);

        fireEvent.change(screen.getByTestId("username"), { target: { value: "admin" } });
        fireEvent.change(screen.getByTestId("password"), { target: { value: "admin123" } });

        expect(screen.getByTestId("username")).toHaveValue("admin");
        expect(screen.getByTestId("password")).toHaveValue("admin123");
    });

    test("successful login stores token and navigates to /jobs", async () => {
        login.mockResolvedValueOnce({ access_token: "abc123" });

        render(<Login />);

        fireEvent.change(screen.getByTestId("username"), { target: { value: "viewer" } });
        fireEvent.change(screen.getByTestId("password"), { target: { value: "viewer123" } });

        fireEvent.click(screen.getByTestId("login-btn"));

        await waitFor(() => {
            expect(login).toHaveBeenCalledWith("viewer", "viewer123");
        });

        expect(Storage.prototype.setItem).toHaveBeenCalledWith("token", "abc123");
        expect(goTo).toHaveBeenCalledWith("/jobs");
    });

    test("failed login shows error and does not navigate or store token", async () => {
        login.mockRejectedValueOnce(new Error("bad creds"));

        render(<Login />);

        fireEvent.click(screen.getByTestId("login-btn"));

        expect(await screen.findByText(/Login failed/i)).toBeInTheDocument();
        expect(Storage.prototype.setItem).not.toHaveBeenCalled();
        expect(goTo).not.toHaveBeenCalled();
    });
});





