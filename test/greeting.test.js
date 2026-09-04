import test from "node:test";
import assert from "node:assert/strict";
import { greeting } from "../src/greeting.js";

test("greets the supplied name", () => {
  assert.equal(greeting("Codex"), "Hello, Codex!");
});
