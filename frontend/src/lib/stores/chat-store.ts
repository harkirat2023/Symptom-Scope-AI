import { create } from "zustand";
import type { ChatMessage, ChatSession } from "@/lib/api/chat";

interface ChatState {
  isOpen: boolean;
  session: ChatSession | null;
  messages: ChatMessage[];
  isLoading: boolean;
  isSending: boolean;
  pendingActions: Record<string, "pending" | "processing" | "resolved">;
  predictionContext: {
    disease: string;
    confidence: number;
    severity: string;
    symptoms: string[];
    precautions: string[];
  } | null;
  error: string | null;

  setOpen: (open: boolean) => void;
  setSession: (session: ChatSession | null) => void;
  addMessage: (message: ChatMessage) => void;
  setLoading: (loading: boolean) => void;
  setSending: (sending: boolean) => void;
  setPendingAction: (id: string, status: "pending" | "processing" | "resolved") => void;
  setError: (error: string | null) => void;
  clearChat: () => void;
}

export const useChatStore = create<ChatState>((set) => ({
  isOpen: false,
  session: null,
  messages: [],
  isLoading: false,
  isSending: false,
  pendingActions: {},
  predictionContext: null,
  error: null,

  setOpen: (open) => set({ isOpen: open }),
  setSession: (session) => set({ session }),
  addMessage: (message) =>
    set((s) => ({ messages: [...s.messages, message] })),
  setLoading: (loading) => set({ isLoading: loading }),
  setSending: (sending) => set({ isSending: sending }),
  setPendingAction: (id, status) =>
    set((s) => ({ pendingActions: { ...s.pendingActions, [id]: status } })),
  setError: (error) => set({ error }),
  clearChat: () =>
    set({
      session: null,
      messages: [],
      isLoading: false,
      isSending: false,
      pendingActions: {},
      error: null,
    }),
}));
