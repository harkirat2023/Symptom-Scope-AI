"use client";

import { useEffect, useRef } from "react";
import { useAuth } from "@clerk/nextjs";
import { MessageCircle, X, AlertTriangle, Loader2 } from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";
import { Button } from "@/components/ui/button";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Alert, AlertTitle, AlertDescription } from "@/components/ui/alert";
import { useChatStore } from "@/lib/stores/chat-store";
import {
  createChatSession,
  sendChatMessage,
} from "@/lib/api/chat";
import { ChatMessage } from "./chat-message";
import { ChatInput } from "./chat-input";

export function ChatWidget() {
  const { getToken } = useAuth();
  const {
    isOpen,
    session,
    messages,
    isLoading,
    isSending,
    predictionContext,
    error,
    setOpen,
    setSession,
    addMessage,
    setLoading,
    setSending,
    setError,
  } = useChatStore();

  const messagesEndRef = useRef<HTMLDivElement>(null);
  const initializedRef = useRef(false);

  useEffect(() => {
    if (messagesEndRef.current) {
      messagesEndRef.current.scrollIntoView({ behavior: "smooth" });
    }
  }, [messages]);

  useEffect(() => {
    if (!isOpen || initializedRef.current) return;
    initializedRef.current = true;

    const initSession = async () => {
      setLoading(true);
      setError(null);
      try {
        const token = await getToken();
        const s = await createChatSession(
          undefined,
          token ?? undefined
        );
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
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [isOpen]);

  const handleSend = async (content: string) => {
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
  };

  const handleClose = () => {
    setOpen(false);
  };

  const handleOpen = () => {
    setOpen(true);
    initializedRef.current = false;
  };

  return (
    <>
      {!isOpen && (
        <Button
          onClick={handleOpen}
          className="fixed bottom-6 right-6 z-50 size-14 rounded-full shadow-lg"
          size="icon"
          aria-label="Open health chat assistant"
        >
          <MessageCircle className="size-6" />
        </Button>
      )}

      <AnimatePresence>
        {isOpen && (
          <motion.div
            initial={{ opacity: 0, y: 20, scale: 0.95 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: 20, scale: 0.95 }}
            transition={{ duration: 0.2 }}
            className="fixed bottom-6 right-6 z-50 flex w-[380px] max-w-[calc(100vw-2rem)] flex-col rounded-xl border bg-background shadow-2xl"
            style={{ height: "min(600px, 80vh)" }}
          >
            <div className="flex items-center justify-between border-b px-4 py-3">
              <div className="flex items-center gap-2">
                <MessageCircle className="size-5 text-primary" />
                <span className="font-semibold text-sm">Health Assistant</span>
              </div>
              <Button
                variant="ghost"
                size="icon"
                className="size-7"
                onClick={handleClose}
                aria-label="Close chat"
              >
                <X className="size-4" />
              </Button>
            </div>

            {predictionContext && (
              <div className="border-b bg-primary/5 px-4 py-2">
                <p className="text-xs text-muted-foreground">
                  Discussing: <strong>{predictionContext.disease}</strong>
                  {" | "}Confidence: {predictionContext.confidence}%
                  {" | "}Severity: {predictionContext.severity}
                </p>
              </div>
            )}

            <ScrollArea className="flex-1 px-4 py-3">
              {isLoading && (
                <div className="flex items-center justify-center py-12">
                  <Loader2 className="size-6 animate-spin text-muted-foreground" />
                </div>
              )}

              {!isLoading && messages.length === 0 && (
                <div className="flex flex-col items-center justify-center py-12 text-center">
                  <MessageCircle className="size-10 text-muted-foreground/40 mb-3" />
                  <p className="text-sm text-muted-foreground">
                    Ask me anything about your health symptoms, predictions,
                    or general wellness information.
                  </p>
                </div>
              )}

              <div className="space-y-4">
                {messages.map((msg) => (
                  <ChatMessage
                    key={msg.id}
                    role={msg.role}
                    content={msg.content}
                  />
                ))}
              </div>

              {isSending && (
                <div className="flex items-center gap-2 text-xs text-muted-foreground mt-2">
                  <Loader2 className="size-3 animate-spin" />
                  Assistant is typing...
                </div>
              )}

              <div ref={messagesEndRef} />
            </ScrollArea>

            {error && (
              <div className="px-3 pb-1">
                <Alert variant="destructive" className="py-2">
                  <AlertTriangle className="size-3" />
                  <AlertTitle className="text-xs">Error</AlertTitle>
                  <AlertDescription className="text-xs">
                    {error}
                  </AlertDescription>
                </Alert>
              </div>
            )}

            <ChatInput onSend={handleSend} isSending={isSending} />

            <div className="border-t px-4 py-1.5">
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
