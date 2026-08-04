"use client";

import { Bot, User, Copy, Check } from "lucide-react";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { useState, useCallback } from "react";

interface ChatMessageProps {
  role: "user" | "assistant";
  content: string;
  id: string;
}

export function ChatMessage({ role, content, id: _id }: ChatMessageProps) {
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