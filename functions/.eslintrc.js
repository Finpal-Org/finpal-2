module.exports = {
  root: true,
  env: {
    es6: true,
    node: true,
  },
  extends: [
    "eslint:recommended",
    "plugin:@typescript-eslint/recommended"
  ],
  parser: "@typescript-eslint/parser",
  parserOptions: {
    sourceType: "module",
  },
  rules: {
    "no-debugger": "warn",  // Change from error to warning
    "@typescript-eslint/no-explicit-any": "warn", // Allow 'any' with warning
    "@typescript-eslint/no-var-requires": "off"  // Shut up about CommonJS requires
  }
};
