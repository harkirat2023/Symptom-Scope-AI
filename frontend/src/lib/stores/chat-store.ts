import { create } from "zustand";
import type { ChatMessage, ChatSession } from "@/lib/api/chat";

interface ChatState {
  isOpen: boolean;
  session: ChatSession | null;
  messages: ChatMessage[];
  isLoading: boolean;
  isSending: boolean;
  predictionContext: {
    disease: string;
    confidence: number;
    severity: string;
    symptoms: string[];
    precautions: string[];
  } | null;
  error: string | null;

  setOpen: (open: boolean) => void;
  toggle: () => void;
  setSession: (session: ChatSession | null) => void;
  setMessages: (messages: ChatMessage[]) => void;
  addMessage: (message: ChatMessage) => void;
  setLoading: (loading: boolean) => void;
  setSending: (sending: boolean) => void;
  setPredictionContext: (
    context: ChatState["predictionContext"]
  ) => void;
  setError: (error: string | null) => void;
  reset: () => void;
  clearChat: () => void;
}

export const useChatStore = create<ChatState>((set) => ({
  isOpen: false,
  session: null,
  messages: [],
  isLoading: false,
  isSending: false,
  predictionContext: null,
  error: null,

  setOpen: (open) => set({ isOpen: open }),
  toggle: () => set((s) => ({ isOpen: !s.isOpen })),
  setSession: (session) => set({ session }),
  setMessages: (messages) => set({ messages }),
  addMessage: (message) =>
    set((s) => ({ messages: [...s.messages, message] })),
  setLoading: (loading) => set({ isLoading: loading }),
  setSending: (sending) => set({ isSending: sending }),
  setPredictionContext: (context) => set({ predictionContext: context }),
  setError: (error) => set({ error }),
reset: () =>
      set({
        session: null,
        messages: [],
        isLoading: false,
        isSending: false,
        error: null,
      }),
    clearChat: () =>
      set({
        session: null,
        messages: [],
        isLoading: false,
        isSending: false,
        error: null,
      }),
}));
