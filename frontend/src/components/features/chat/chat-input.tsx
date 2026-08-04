"use client";

import { useState, useRef, useCallback } from "react";
import { Send, Loader2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { QuickActions } from "./quick-actions";
import { cn } from "@/lib/utils";

interface ChatInputProps {
  onSend: (message: string) => void;
  isSending: boolean;
  disabled?: boolean;
  placeholder?: string;
  maxLength?: number;
}

export function ChatInput({
  onSend,
  isSending,
  disabled,
  placeholder = "Ask anything about your recovery...",
  maxLength = 2000,
}: ChatInputProps) {
  const [input, setInput] = useState("");
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const [showQuickActions, setShowQuickActions] = useState(true);

  const handleSend = useCallback(() => {
    const trimmed = input.trim();
    if (!trimmed || isSending) return;
    onSend(trimmed);
    setInput("");
    setShowQuickActions(false);
    if (textareaRef.current) {
      textareaRef.current.style.height = "auto";
    }
  }, [input, isSending, onSend]);

  const handleKeyDown = useCallback(
    (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
      if (e.key === "Enter" && !e.shiftKey) {
        e.preventDefault();
        handleSend();
      }
    },
    [handleSend]
  );

  const handleInput = useCallback(() => {
    const el = textareaRef.current;
    if (el) {
      el.style.height = "auto";
      el.style.height = `${Math.min(el.scrollHeight, 160)}px`;
    }
  }, []);

  const handleQuickAction = useCallback(
    (prompt: string) => {
      onSend(prompt);
      setShowQuickActions(false);
    },
    [onSend]
  );

  const hasInput = input.trim().length > 0;

  return (
    <div
      className={cn(
        "border-t bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60",
        "sticky bottom-0 z-10"
      )}
    >
      {showQuickActions && !hasInput && !isSending && (
        <div className="px-4 py-3 border-b" data-testid="quick-actions">
          <QuickActions onActionClick={handleQuickAction} disabled={isSending || disabled} />
        </div>
      )}

      <div className="flex items-end gap-2 p-3">
        <div className="flex-1 relative">
          <Textarea
            ref={textareaRef}
            value={input}
            onChange={(e) => {
              setInput(e.target.value);
              handleInput();
            }}
            onKeyDown={handleKeyDown}
            placeholder={placeholder}
            className={cn(
              "min-h-[44px] max-h-[160px] resize-none pr-12 text-sm",
              "bg-transparent border border-input rounded-xl",
              "placeholder:text-muted-foreground/60",
              "focus:ring-2 focus:ring-ring focus:ring-offset-2 focus:ring-offset-background",
              "disabled:opacity-50 disabled:cursor-not-allowed",
              isSending && "opacity-50"
            )}
            rows={1}
            disabled={isSending || disabled}
            maxLength={maxLength}
            aria-label="Message input"
            autoFocus
          />
          {hasInput && (
            <span
              className={cn(
                "absolute bottom-2 right-10 text-xs text-muted-foreground/60",
                input.length > maxLength * 0.8 && "text-orange-500"
              )}
              aria-live="polite"
            >
              {input.length}/{maxLength}
            </span>
          )}
        </div>

        <Button
          size="icon"
          onClick={handleSend}
          disabled={!hasInput || isSending || disabled}
          className={cn(
            "shrink-0 rounded-xl transition-all",
            "hover:bg-primary/90",
            "disabled:opacity-50 disabled:cursor-not-allowed"
          )}
          aria-label={isSending ? "Sending..." : "Send message"}
        >
          {isSending ? (
            <Loader2 className="size-5 animate-spin" />
          ) : (
            <Send className="size-5" />
          )}
        </Button>
      </div>
    </div>
  );
}