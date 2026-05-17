"use client";

import { Loader2 } from "lucide-react";
import { cn } from "@/lib/utils";

export interface ToolCallBadgeProps {
  toolName: string;
  state: "partial-call" | "call" | "result";
  args?: Record<string, unknown>;
  result?: unknown;
}

function getFilename(path: unknown): string {
  if (typeof path !== "string" || path === "") return "";
  const segments = path.split("/");
  return segments[segments.length - 1] ?? "";
}

export function getToolLabel(
  toolName: string,
  args?: Record<string, unknown>
): string {
  if (toolName === "str_replace_editor") {
    if (!args) return "Working…";
    const file = getFilename(args.path);
    switch (args.command) {
      case "view":        return file ? `Reading ${file}`         : "Reading file";
      case "create":      return file ? `Creating ${file}`        : "Creating file";
      case "str_replace": return file ? `Editing ${file}`         : "Editing file";
      case "insert":      return file ? `Editing ${file}`         : "Editing file";
      case "undo_edit":   return file ? `Undoing edit in ${file}` : "Undoing edit";
      default:            return file ? `Working on ${file}`      : "Working…";
    }
  }

  if (toolName === "file_manager") {
    if (!args) return "Working…";
    const file = getFilename(args.path);
    switch (args.command) {
      case "delete": return file ? `Deleting ${file}` : "Deleting file";
      case "rename": {
        const newFile = getFilename(args.new_path);
        if (file && newFile) return `Renaming ${file} → ${newFile}`;
        if (file) return `Renaming ${file}`;
        return "Renaming file";
      }
      default: return file ? `Working on ${file}` : "Working…";
    }
  }

  return toolName;
}

export function ToolCallBadge({ toolName, state, args, result }: ToolCallBadgeProps) {
  const label = getToolLabel(toolName, args);
  const isDone = state === "result" && Boolean(result);

  return (
    <div
      className={cn(
        "inline-flex items-center gap-2 mt-2 px-3 py-1.5",
        "bg-neutral-50 rounded-lg text-xs font-mono border border-neutral-200"
      )}
    >
      {isDone ? (
        <div className="w-2 h-2 rounded-full bg-emerald-500" />
      ) : (
        <Loader2 className="w-3 h-3 animate-spin text-blue-600" />
      )}
      <span className="text-neutral-700">{label}</span>
    </div>
  );
}
