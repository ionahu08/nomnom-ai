import { test, expect, afterEach } from "vitest";
import { render, screen, cleanup } from "@testing-library/react";
import { getToolLabel, ToolCallBadge } from "../ToolCallBadge";

afterEach(() => {
  cleanup();
});

// ── getToolLabel pure function ─────────────────────────────────────────────

test("getToolLabel returns raw toolName for unknown tools", () => {
  expect(getToolLabel("my_custom_tool")).toBe("my_custom_tool");
});

test("getToolLabel returns 'Working…' for str_replace_editor with no args", () => {
  expect(getToolLabel("str_replace_editor")).toBe("Working…");
});

test("getToolLabel str_replace_editor view command", () => {
  expect(
    getToolLabel("str_replace_editor", { command: "view", path: "src/components/Card.tsx" })
  ).toBe("Reading Card.tsx");
});

test("getToolLabel str_replace_editor create command", () => {
  expect(
    getToolLabel("str_replace_editor", { command: "create", path: "src/components/Card.tsx" })
  ).toBe("Creating Card.tsx");
});

test("getToolLabel str_replace_editor str_replace command", () => {
  expect(
    getToolLabel("str_replace_editor", { command: "str_replace", path: "src/lib/utils.ts" })
  ).toBe("Editing utils.ts");
});

test("getToolLabel str_replace_editor insert command", () => {
  expect(
    getToolLabel("str_replace_editor", { command: "insert", path: "src/lib/config.ts" })
  ).toBe("Editing config.ts");
});

test("getToolLabel str_replace_editor undo_edit command", () => {
  expect(
    getToolLabel("str_replace_editor", { command: "undo_edit", path: "src/components/Button.tsx" })
  ).toBe("Undoing edit in Button.tsx");
});

test("getToolLabel str_replace_editor unknown command falls back with filename", () => {
  expect(
    getToolLabel("str_replace_editor", { command: "unknown_cmd", path: "src/foo.ts" })
  ).toBe("Working on foo.ts");
});

test("getToolLabel extracts only the last path segment", () => {
  expect(
    getToolLabel("str_replace_editor", { command: "view", path: "a/b/c/deep/File.tsx" })
  ).toBe("Reading File.tsx");
});

test("getToolLabel returns 'Working…' for file_manager with no args", () => {
  expect(getToolLabel("file_manager")).toBe("Working…");
});

test("getToolLabel file_manager delete command", () => {
  expect(
    getToolLabel("file_manager", { command: "delete", path: "src/components/Button.tsx" })
  ).toBe("Deleting Button.tsx");
});

test("getToolLabel file_manager rename command with both paths", () => {
  expect(
    getToolLabel("file_manager", {
      command: "rename",
      path: "src/components/Card.tsx",
      new_path: "src/components/NewCard.tsx",
    })
  ).toBe("Renaming Card.tsx → NewCard.tsx");
});

test("getToolLabel file_manager rename command with only path", () => {
  expect(getToolLabel("file_manager", { command: "rename", path: "src/components/Card.tsx" })).toBe(
    "Renaming Card.tsx"
  );
});

// ── ToolCallBadge component rendering ─────────────────────────────────────

test("ToolCallBadge renders label for str_replace_editor create", () => {
  render(
    <ToolCallBadge
      toolName="str_replace_editor"
      state="call"
      args={{ command: "create", path: "src/components/Button.tsx" }}
    />
  );
  expect(screen.getByText("Creating Button.tsx")).toBeDefined();
});

test("ToolCallBadge shows spinner when state is 'call'", () => {
  const { container } = render(
    <ToolCallBadge
      toolName="str_replace_editor"
      state="call"
      args={{ command: "view", path: "src/App.tsx" }}
    />
  );
  expect(container.querySelector(".animate-spin")).toBeDefined();
  expect(container.querySelector(".bg-emerald-500")).toBeNull();
});

test("ToolCallBadge shows spinner when state is 'partial-call'", () => {
  const { container } = render(
    <ToolCallBadge toolName="str_replace_editor" state="partial-call" />
  );
  expect(container.querySelector(".animate-spin")).toBeDefined();
  expect(container.querySelector(".bg-emerald-500")).toBeNull();
});

test("ToolCallBadge shows green dot when state is 'result' with truthy result", () => {
  const { container } = render(
    <ToolCallBadge
      toolName="str_replace_editor"
      state="result"
      args={{ command: "create", path: "src/components/Card.tsx" }}
      result="Success"
    />
  );
  expect(container.querySelector(".bg-emerald-500")).toBeDefined();
  expect(container.querySelector(".animate-spin")).toBeNull();
});

test("ToolCallBadge shows spinner when state is 'result' but result is falsy", () => {
  const { container } = render(
    <ToolCallBadge
      toolName="str_replace_editor"
      state="result"
      args={{ command: "view", path: "src/App.tsx" }}
      result={undefined}
    />
  );
  expect(container.querySelector(".animate-spin")).toBeDefined();
  expect(container.querySelector(".bg-emerald-500")).toBeNull();
});

test("ToolCallBadge renders raw toolName for unknown tool", () => {
  render(<ToolCallBadge toolName="my_tool" state="call" />);
  expect(screen.getByText("my_tool")).toBeDefined();
});

test("ToolCallBadge wrapper has pill styling class", () => {
  const { container } = render(
    <ToolCallBadge toolName="str_replace_editor" state="call" />
  );
  const pill = container.firstChild as HTMLElement;
  expect(pill.className).toContain("bg-neutral-50");
  expect(pill.className).toContain("rounded-lg");
});
