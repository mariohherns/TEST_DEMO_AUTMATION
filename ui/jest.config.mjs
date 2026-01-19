import nextJest from "next/jest.js";

const createJestConfig = nextJest({
  dir: "./",
});

const customJestConfig = {
  testEnvironment: "jsdom",

  // Centralized tests folder
  testMatch: ["<rootDir>/tests/**/*.test.(js|jsx|ts|tsx)"],

  setupFilesAfterEnv: ["<rootDir>/tests/setup/setupTests.js"],

  // Optional alias (so we can import like "@/pages/index")
  moduleNameMapper: {
    "^@/(.*)$": "<rootDir>/$1",
    "\\.(css|less|scss|sass)$": "identity-obj-proxy",
  },

  clearMocks: true,
  restoreMocks: true,
};

export default createJestConfig(customJestConfig);