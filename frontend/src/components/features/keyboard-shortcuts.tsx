"use client";

import { useEffect, useState, useCallback } from "react";
import { Button } from "@/components/ui/button";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription } from "@/components/ui/dialog";
import { Keyboard } from "lucide-react";

interface Shortcut {
  key: string;
  description: string;
  category: string;
}

const SHORTCUTS: Shortcut[] = [
  { key: "?", description: "Show keyboard shortcuts", category: "General" },
  { key: "g then d", description: "Go to Dashboard", category: "Navigation" },
  { key: "g then s", description: "Go to Symptom Checker", category: "Navigation" },
  { key: "g then h", description: "Go to History", category: "Navigation" },
  { key: "g then r", description: "Go to Reports", category: "Navigation" },
  { key: "g then t", description: "Go to Settings", category: "Navigation" },
  { key: "n", description: "Start new symptom check", category: "Actions" },
  { key: "Escape", description: "Close sidebar or dialog", category: "General" },
  { key: "Tab", description: "Navigate through interactive elements", category: "General" },
  { key: "Shift + Tab", description: "Navigate backwards", category: "General" },
  { key: "Enter", description: "Activate button or link", category: "General" },
];

export function KeyboardShortcutsHelp() {
  const [open, setOpen] = useState(false);

  const handleKeyDown = useCallback(
    (event: KeyboardEvent) => {
      if (
        event.key === "?" &&
        !event.ctrlKey &&
        !event.metaKey &&
        !event.altKey
      ) {
        const target = event.target as HTMLElement;
        if (target.tagName === "INPUT" || target.tagName === "TEXTAREA" || target.isContentEditable) {
          return;
        }
        event.preventDefault();
        setOpen((prev) => !prev);
      }

      if (event.key === "Escape" && open) {
        setOpen(false);
      }
    },
    [open]
  );

  useEffect(() => {
    document.addEventListener("keydown", handleKeyDown);
    return () => document.removeEventListener("keydown", handleKeyDown);
  }, [handleKeyDown]);

  const categories = [...new Set(SHORTCUTS.map((s) => s.category))];

  return (
    <>
      <Button
        variant="ghost"
        size="icon"
        className="fixed bottom-4 right-4 z-50 size-10 rounded-full shadow-lg"
        onClick={() => setOpen(true)}
        aria-label="Keyboard shortcuts"
      >
        <Keyboard className="size-5" />
      </Button>

      <Dialog open={open} onOpenChange={setOpen}>
        <DialogContent className="sm:max-w-md">
          <DialogHeader>
            <DialogTitle className="flex items-center gap-2">
              <Keyboard className="size-5" />
              Keyboard Shortcuts
            </DialogTitle>
            <DialogDescription>
              Use these keyboard shortcuts to navigate SymptomScope AI more efficiently.
              Press <kbd className="rounded border bg-muted px-1.5 py-0.5 text-xs font-mono">?</kbd> at any time to toggle this dialog.
            </DialogDescription>
          </DialogHeader>

          <div className="max-h-80 overflow-y-auto space-y-4">
            {categories.map((category) => (
              <div key={category}>
                <h4 className="text-sm font-semibold text-muted-foreground mb-2">
                  {category}
                </h4>
                <div className="space-y-1">
                  {SHORTCUTS.filter((s) => s.category === category).map((shortcut) => (
                    <div
                      key={shortcut.key}
                      className="flex items-center justify-between py-1"
                    >
                      <span className="text-sm">{shortcut.description}</span>
                      <kbd className="rounded border bg-muted px-2 py-0.5 text-xs font-mono whitespace-nowrap">
                        {shortcut.key}
                      </kbd>
                    </div>
                  ))}
                </div>
              </div>
            ))}
          </div>

          <p className="text-xs text-muted-foreground mt-2">
            Note: Navigation shortcuts (g then d, g then s, etc.) allow you to press g followed by
            another key within the same page to navigate.
          </p>
        </DialogContent>
      </Dialog>
    </>
  );
}
