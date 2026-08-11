"use client";

import { useEffect, useRef, useCallback } from "react";
import { useAuth } from "@clerk/nextjs";
import {
  Bot,
  X,
  Trash2,
  MessageCircle,
  Loader2,
  Sparkles,
} from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";
import { Button } from "@/components/ui/button";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Badge } from "@/components/ui/badge";
import { Separator } from "@/components/ui/separator";
import { cn } from "@/lib/utils";
import { useChatStore } from "@/lib/stores/chat-store";
import {
  createChatSession,
  sendChatMessage,
} from "@/lib/api/chat";
import { ChatMessage } from "./chat-message";
import { ChatInput } from "./chat-input";
import { TypingIndicator } from "./typing-indicator";
import { EmptyState } from "./empty-state";
import { ErrorCard } from "./error-card";

export function ChatPanel() {
  const { getToken } = useAuth();
  const {
    isOpen,
    setOpen,
    session,
    messages,
    isLoading,
    isSending,
    predictionContext,
    error,
    setSession,
    addMessage,
    setLoading,
    setSending,
    setError,
    clearChat,
  } = useChatStore();

  const messagesEndRef = useRef<HTMLDivElement>(null);
  const initializedRef = useRef(false);
  const scrollAreaRef = useRef<HTMLDivElement>(null);
  const hasUserScrolledRef = useRef(false);

  const scrollToBottom = useCallback((smooth = true) => {
    if (messagesEndRef.current) {
      messagesEndRef.current.scrollIntoView({ behavior: smooth ? "smooth" : "auto" });
    }
  }, []);

  const handleScroll = useCallback(() => {
    const scrollArea = scrollAreaRef.current;
    if (!scrollArea) return;

    const { scrollTop, scrollHeight, clientHeight } = scrollArea;
    const isAtBottom = scrollHeight - scrollTop - clientHeight < 50;
    hasUserScrolledRef.current = !isAtBottom;
  }, []);

  useEffect(() => {
    if (!hasUserScrolledRef.current) {
      scrollToBottom();
    }
  }, [messages, isSending, scrollToBottom]);

  useEffect(() => {
    if (!isOpen || initializedRef.current) return;
    initializedRef.current = true;

    const initSession = async () => {
      setLoading(true);
      setError(null);
      try {
        const token = await getToken();
        const s = await createChatSession(undefined, token ?? undefined);
        setSession(s);
      } catch {
        setError("Could not start chat. Please try again.");
      } finally {
        setLoading(false);
      }
    };

    if (!session) {
      initSession();
    }
  }, [isOpen, getToken, session, setLoading, setError, setSession]);

  const handleSend = useCallback(
    async (content: string) => {
      if (!session) return;
      setSending(true);
      setError(null);

      const tempId = `temp-${Date.now()}`;
      addMessage({
        id: tempId,
        session_id: session.id,
        role: "user",
        content,
        created_at: new Date().toISOString(),
      });

      try {
        const token = await getToken();
        const response = await sendChatMessage(
          session.id,
          content,
          token ?? undefined
        );
        addMessage(response);
      } catch (err) {
        setError(
          err instanceof Error ? err.message : "Failed to send message"
        );
      } finally {
        setSending(false);
      }
    },
    [session, getToken, addMessage, setSending, setError]
  );

  const handleClearChat = useCallback(async () => {
    clearChat();
    initializedRef.current = false;
    if (isOpen) {
      try {
        setLoading(true);
        const token = await getToken();
        const s = await createChatSession(undefined, token ?? undefined);
        setSession(s);
      } catch {
        setError("Could not start new chat. Please try again.");
      } finally {
        setLoading(false);
      }
    }
  }, [clearChat, isOpen, getToken, setLoading, setError, setSession]);

  const isOnline = !isLoading && !isSending && !error;

  return (
    <>
      {/* Floating action button (bottom-right) */}
      <motion.button
        initial={{ opacity: 0, scale: 0.8, y: 20 }}
        animate={{ opacity: 1, scale: 1, y: 0 }}
        transition={{ duration: 0.2 }}
        onClick={() => setOpen(!isOpen)}
        className={cn(
          "fixed bottom-6 right-6 z-50 size-14 rounded-full shadow-lg",
          "bg-primary text-primary-foreground",
          "hover:bg-primary/90 transition-all"
        )}
        aria-label={isOpen ? "Close health chat assistant" : "Open health chat assistant"}
        type="button"
      >
        {isOpen ? <X className="size-6" /> : <MessageCircle className="size-6" />}
        <span className="sr-only">Health Assistant</span>
      </motion.button>

      {/* Floating chat widget */}
      <AnimatePresence>
        {isOpen && (
          <motion.div
            initial={{ opacity: 0, y: 20, scale: 0.95 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: 20, scale: 0.95 }}
            transition={{ duration: 0.2, ease: [0.25, 0.1, 0.25, 1] }}
            className="fixed bottom-24 right-6 z-50 flex h-[75vh] w-[380px] max-w-[calc(100vw-3rem)] flex-col overflow-hidden rounded-xl border bg-background shadow-2xl"
            role="dialog"
            aria-label="Health Assistant"
          >
            {/* Header */}
            <div className="flex items-center justify-between border-b px-4 py-3 bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60 sticky top-0 z-10">
              <div className="flex items-center gap-3 min-w-0 flex-1">
                <div className="flex size-10 shrink-0 items-center justify-center rounded-xl bg-primary/10">
                  <Sparkles className="size-5 text-primary" />
                </div>
                <div className="min-w-0">
                  <h2 className="truncate font-semibold text-sm text-foreground">
                    Health Assistant
                  </h2>
                  <p className="truncate text-xs text-muted-foreground">
                    Personalized Recovery Assistant
                  </p>
                </div>
              </div>

              <div className="flex items-center gap-1.5">
                {/* Status Badge */}
                <Badge
                  variant={isOnline ? "default" : "secondary"}
                  className={cn(
                    "gap-1.5 text-xs px-2 py-0.5",
                    "hidden sm:inline-flex"
                  )}
                >
                  <span
                    className={cn(
                      "size-1.5 rounded-full",
                      isOnline ? "bg-green-500" : "bg-yellow-500 animate-pulse"
                    )}
                  />
                  {isOnline ? "Online" : isSending ? "Thinking..." : "Connecting..."}
                </Badge>

                {/* Action Buttons */}
                <Button
                  variant="ghost"
                  size="icon"
                  className="size-8 rounded-lg hover:bg-accent"
                  onClick={handleClearChat}
                  aria-label="Clear chat history"
                  disabled={messages.length === 0 && !isLoading}
                >
                  <Trash2 className="size-4" />
                </Button>
                <Button
                  variant="ghost"
                  size="icon"
                  className="size-8 rounded-lg hover:bg-accent hover:text-destructive"
                  onClick={() => setOpen(false)}
                  aria-label="Close chat"
                >
                  <X className="size-4" />
                </Button>
              </div>
            </div>

            {/* Prediction Context Bar */}
            {predictionContext && (
              <div className="border-b bg-primary/5 px-4 py-2.5">
                <div className="flex items-center gap-2 text-xs text-muted-foreground">
                  <Bot className="size-3.5 text-primary" />
                  <span className="font-medium text-foreground">
                    Discussing: <strong>{predictionContext.disease}</strong>
                  </span>
                  <Separator className="h-3 w-px bg-border" />
                  <span>Confidence: {predictionContext.confidence}%</span>
                  <Separator className="h-3 w-px bg-border" />
                  <span>Severity: {predictionContext.severity}</span>
                </div>
              </div>
            )}

            {/* Messages Area */}
            <ScrollArea
              ref={scrollAreaRef}
              onScroll={handleScroll}
              className="flex-1 overflow-hidden"
            >
              <div className="flex flex-col gap-4 px-4 py-4">
                {isLoading && (
                  <div className="flex items-center justify-center py-8">
                    <Loader2 className="size-8 animate-spin text-muted-foreground" />
                  </div>
                )}

                {!isLoading && messages.length === 0 && (
                  <EmptyState onPromptClick={handleSend} className="flex-1" />
                )}

                {messages.map((msg) => (
                  <ChatMessage
                    key={msg.id}
                    role={msg.role}
                    content={msg.content}
                    id={msg.id}
                  />
                ))}

                {isSending && <TypingIndicator />}

                <div ref={messagesEndRef} />
              </div>
            </ScrollArea>

            {/* Error Display */}
            {error && (
              <ErrorCard
                message={error}
                onRetry={() => {}}
                onDismiss={() => setError(null)}
                className="px-4 pb-2"
              />
            )}

            {/* Input Area */}
            <ChatInput
              onSend={handleSend}
              isSending={isSending}
              disabled={isLoading}
              placeholder="Ask anything about your recovery..."
            />

            {/* Disclaimer */}
            <div className="border-t px-4 py-2 bg-background/50">
              <p className="text-[10px] text-muted-foreground text-center">
                Educational purposes only. Not a substitute for professional
                medical advice.
              </p>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </>
  );
}
