import "./globals.css";
import { PostHogProvider } from "../lib/analytics";

export const metadata = {
  title: "Create Next App",
  generator: "Next.js",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>
        <PostHogProvider>{children}</PostHogProvider>
      </body>
    </html>
  );
}
