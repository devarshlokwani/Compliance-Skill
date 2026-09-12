"use client";

import { useState } from "react";
import SignupForm from "../components/SignupForm";

export default function Home() {
  const [open, setOpen] = useState(false);

  return (
    <main className="card">
      {/* No alt text: a screen reader announces "hero-dashboard.png". */}
      <img src="/hero-dashboard.png" width={880} height={420} />

      <h1>MeetingNotes</h1>
      <p>Record a meeting, get the summary in your inbox before you leave the room.</p>

      {/* Loaded over plain http from a third-party host. */}
      <img src="http://cdn.partner-widgets.example.net/badge.png" width={120} height={40} alt="Featured" />

      {/* A div doing a button's job: no keyboard access, no announced role. */}
      <div onClick={() => setOpen(!open)} className="cta">
        See how it works
      </div>

      {open && (
        <section>
          <h2>Start free</h2>
          <SignupForm />
        </section>
      )}
    </main>
  );
}
