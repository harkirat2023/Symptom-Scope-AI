import { create } from "zustand";
import type {
  RiskScoreResponse,
  RiskScoreHistoryResponse,
  UserHealthProfile,
  UserHealthProfileResponse,
} from "@/lib/api/risk-score";

interface RiskScoreState {
  score: RiskScoreResponse | null;
  history: RiskScoreHistoryResponse["history"];
  tips: string[];
  profile: UserHealthProfileResponse | null;
  loading: boolean;
  error: string | null;
  getToken: (() => Promise<string | null>) | null;

  setGetToken: (fn: () => Promise<string | null>) => void;
  setScore: (score: RiskScoreResponse) => void;
  setHistory: (history: RiskScoreHistoryResponse["history"]) => void;
  setTips: (tips: string[]) => void;
  setProfile: (profile: UserHealthProfileResponse | null) => void;
  setLoading: (loading: boolean) => void;
  setError: (error: string | null) => void;

  fetchScore: () => Promise<void>;
  fetchHistory: (range?: string) => Promise<void>;
  fetchTips: () => Promise<void>;
  fetchProfile: () => Promise<void>;
  updateProfile: (data: UserHealthProfile) => Promise<void>;
}

export const useRiskScoreStore = create<RiskScoreState>((set, get) => ({
  score: null,
  history: [],
  tips: [],
  profile: null,
  loading: false,
  error: null,
  getToken: null,

  setGetToken: (fn) => set({ getToken: fn }),

  setScore: (score) => set({ score }),
  setHistory: (history) => set({ history }),
  setTips: (tips) => set({ tips }),
  setProfile: (profile) => set({ profile }),
  setLoading: (loading) => set({ loading }),
  setError: (error) => set({ error }),

  fetchScore: async () => {
    set({ loading: true, error: null });
    try {
      const { getRiskScore } = await import("@/lib/api/risk-score");
      const token = await get().getToken?.();
      const data = await getRiskScore(token ?? undefined);
      set({ score: data, loading: false });
    } catch (err) {
      set({
        error: err instanceof Error ? err.message : "Failed to fetch score",
        loading: false,
      });
    }
  },

  fetchHistory: async (range = "6m") => {
    try {
      const { getRiskScoreHistory } = await import("@/lib/api/risk-score");
      const token = await get().getToken?.();
      const data = await getRiskScoreHistory(range, token ?? undefined);
      set({ history: data.history });
    } catch {
      // silently fail for history
    }
  },

  fetchTips: async () => {
    try {
      const { getRiskTips } = await import("@/lib/api/risk-score");
      const token = await get().getToken?.();
      const data = await getRiskTips(token ?? undefined);
      set({ tips: data.tips });
    } catch {
      // silently fail
    }
  },

  fetchProfile: async () => {
    try {
      const { getHealthProfile } = await import("@/lib/api/risk-score");
      const token = await get().getToken?.();
      const data = await getHealthProfile(token ?? undefined);
      set({ profile: data });
    } catch {
      // silently fail
    }
  },

  updateProfile: async (data) => {
    set({ loading: true, error: null });
    try {
      const { updateHealthProfile } = await import("@/lib/api/risk-score");
      const token = await get().getToken?.();
      const profile = await updateHealthProfile(data, token ?? undefined);
      set({ profile, loading: false });
    } catch (err) {
      set({
        error: err instanceof Error ? err.message : "Failed to update profile",
        loading: false,
      });
    }
  },
}));
