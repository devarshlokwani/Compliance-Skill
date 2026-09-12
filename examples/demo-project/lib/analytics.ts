"use client";

import posthog from "posthog-js";

// Fires on load. No consent gate anywhere in the project.
if (typeof window !== "undefined") {
  posthog.init(process.env.NEXT_PUBLIC_POSTHOG_KEY!, {
    api_host: "https://eu.i.posthog.com",
    session_recording: { maskAllInputs: false },
  });

  document.cookie = `mn_visitor=${crypto.randomUUID()}; path=/; max-age=31536000`;
  localStorage.setItem("mn_last_seen", new Date().toISOString());
}

export function PostHogProvider({ children }: { children: React.ReactNode }) {
  return children;
}

export function identify(userId: string, email: string) {
  posthog.identify(userId, { email });
}
