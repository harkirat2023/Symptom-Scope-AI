"use client";

import { useState } from "react";
import { AnimatePresence, motion } from "framer-motion";
import { DashboardHeader } from "@/components/layouts/dashboard-header";
import { DashboardSidebar } from "@/components/layouts/dashboard-sidebar";
import { ChatPanel } from "@/components/features/chat/chat-panel";
import { useChatStore } from "@/lib/stores/chat-store";

export default function DashboardLayoutClient({
  children,
}: {
  children: React.ReactNode;
}) {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [chatOpen, setChatOpen] = useState(false);
  const setChatOpenStore = useChatStore((s) => s.setOpen);

  const handleChatToggle = (open: boolean) => {
    setChatOpen(open);
    setChatOpenStore(open);
  };

  return (
    <div className="min-h-screen bg-background">
      <DashboardHeader
        onMenuClick={() => setSidebarOpen(true)}
        onChatClick={() => handleChatToggle(true)}
      />

      <div className="flex">
        <AnimatePresence>
          {sidebarOpen && (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="fixed inset-0 z-40 bg-black/50 lg:hidden"
              onClick={() => setSidebarOpen(false)}
              aria-hidden="true"
            />
          )}
        </AnimatePresence>

        <DashboardSidebar open={sidebarOpen} onClose={() => setSidebarOpen(false)} />

        <div className="flex-1 flex flex-col min-w-0 lg:flex-row">
          <main
            id="main-content"
            className="flex-1 flex flex-col p-4 lg:p-6 min-w-0"
            tabIndex={-1}
          >
            {children}
            <footer className="mt-8 border-t border-border pt-4 text-center text-xs text-muted-foreground">
              Not a medical device. Always consult a qualified healthcare provider for medical advice.
            </footer>
          </main>

          <aside className="hidden lg:flex lg:flex-1 lg:max-w-[420px] lg:min-w-[380px]">
            <ChatPanel isOpen={chatOpen} onClose={() => handleChatToggle(false)} />
          </aside>
        </div>
      </div>

      <AnimatePresence>
        {chatOpen && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 z-50 lg:hidden"
            onClick={() => handleChatToggle(false)}
            aria-hidden="true"
          />
        )}
      </AnimatePresence>

      <AnimatePresence>
        {chatOpen && (
          <motion.div
            initial={{ opacity: 0, x: "100%" }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: "100%" }}
            transition={{ duration: 0.3, ease: [0.4, 0, 0.2, 1] }}
            className="fixed inset-0 z-50 lg:hidden flex justify-end"
            onClick={(e) => e.stopPropagation()}
          >
            <ChatPanel isOpen={chatOpen} onClose={() => handleChatToggle(false)} />
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}