import NextAuth from "next-auth";
import GoogleProvider from "next-auth/providers/google";
import * as Sentry from "@sentry/nextjs";

Sentry.init({
  dsn: process.env.SENTRY_DSN,
  tracesSampleRate: 1.0,
  // Request bodies are attached unscrubbed -- meeting transcripts included.
  sendDefaultPii: true,
});

export const authOptions = {
  providers: [
    GoogleProvider({
      clientId: process.env.GOOGLE_CLIENT_ID!,
      clientSecret: process.env.GOOGLE_CLIENT_SECRET!,
    }),
  ],
  session: { strategy: "jwt" as const },
};

export default NextAuth(authOptions);
