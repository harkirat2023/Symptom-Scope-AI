"use client";

import { Bot, User, Copy, Check, ShieldAlert, Loader2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { useState, useCallback } from "react";
import type { PendingAction } from "@/lib/api/chat";

interface ChatMessageProps {
  role: "user" | "assistant";
  content: string;
  id?: string;
  pendingAction?: PendingAction | null;
  pendingStatus?: "pending" | "processing" | "resolved";
  onResolve?: (id: string, decision: "approve" | "decline") => void;
}

export function ChatMessage({
  role,
  content,
  pendingAction,
  pendingStatus = "pending",
  onResolve,
}: ChatMessageProps) {
  const isUser = role === "user";
  const [copied, setCopied] = useState(false);

  const handleCopy = useCallback(async () => {
    await navigator.clipboard.writeText(content);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  }, [content]);

  return (
    <div
      className={cn(
        "flex gap-3 w-full",
        isUser ? "justify-end" : "justify-start"
      )}
    >
      {!isUser && (
        <div className="flex size-8 shrink-0 items-center justify-center rounded-full bg-primary/10 self-start mt-1">
          <Bot className="size-4 text-primary" />
        </div>
      )}

      <div
        className={cn(
          "relative max-w-[85%] rounded-2xl px-4 py-2.5 text-sm leading-relaxed group",
          isUser
            ? "bg-primary text-primary-foreground rounded-br-sm"
            : "bg-muted text-foreground rounded-bl-sm"
        )}
      >
        <div className="prose prose-sm dark:prose-invert max-w-none">
          {isUser ? (
            <p className="whitespace-pre-wrap break-words m-0">{content}</p>
          ) : (
            <ReactMarkdown remarkPlugins={[remarkGfm]}>
              {content}
            </ReactMarkdown>
          )}
        </div>

        {pendingAction && (
          <div className="mt-3 rounded-xl border bg-background p-3">
            <div className="flex items-start gap-2">
              <ShieldAlert className="size-4 shrink-0 text-amber-500 mt-0.5" />
              <div className="min-w-0">
                <p className="text-xs font-semibold text-foreground">
                  Pending action
                </p>
                <p className="text-xs text-muted-foreground mt-0.5">
                  {pendingAction.summary}
                </p>
              </div>
            </div>
            {pendingStatus === "processing" ? (
              <div className="mt-3 flex items-center gap-2 text-xs text-muted-foreground">
                <Loader2 className="size-3.5 animate-spin" />
                Processing...
              </div>
            ) : pendingStatus === "resolved" ? (
              <p className="mt-3 text-xs text-muted-foreground">Handled ✓</p>
            ) : (
              <div className="mt-3 flex gap-2">
                <Button
                  type="button"
                  size="sm"
                  className="flex-1"
                  onClick={() => onResolve?.(pendingAction.id, "approve")}
                >
                  Approve
                </Button>
                <Button
                  type="button"
                  size="sm"
                  variant="outline"
                  className="flex-1"
                  onClick={() => onResolve?.(pendingAction.id, "decline")}
                >
                  Decline
                </Button>
              </div>
            )}
          </div>
        )}

        <div
          className="absolute -right-8 top-1/2 -translate-y-1/2 flex gap-1 opacity-0 transition-opacity group-hover:opacity-100"
          role="group"
          aria-label="Message actions"
        >
          <Button
            variant="ghost"
            size="icon"
            className="size-7 rounded-lg hover:bg-accent"
            onClick={handleCopy}
            aria-label={copied ? "Copied!" : "Copy message"}
          >
            {copied ? (
              <Check className="size-3.5 text-green-500" />
            ) : (
              <Copy className="size-3.5" />
            )}
          </Button>
        </div>
      </div>

      {isUser && (
        <div className="flex size-8 shrink-0 items-center justify-center rounded-full bg-primary self-start mt-1">
          <User className="size-4 text-primary-foreground" />
        </div>
      )}
    </div>
  );
}