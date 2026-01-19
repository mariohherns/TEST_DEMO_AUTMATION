import React from "react";
import { render, screen } from "@testing-library/react";
import Home from "@/pages/index";

describe("Home page", () => {
  it("renders title and nav links", () => {
    render(<Home />);

    expect(
      screen.getByRole("heading", { name: /AI Refinery QA Lab/i })
    ).toBeInTheDocument();

    expect(screen.getByRole("link", { name: /Login/i })).toHaveAttribute(
      "href",
      "/login"
    );
    expect(screen.getByRole("link", { name: /Jobs/i })).toHaveAttribute(
      "href",
      "/jobs"
    );
    expect(screen.getByRole("link", { name: /Analytics/i })).toHaveAttribute(
      "href",
      "/analytics"
    );
  });
});