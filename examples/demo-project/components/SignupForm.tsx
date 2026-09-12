"use client";

import { useState } from "react";

export default function SignupForm() {
  const [submitting, setSubmitting] = useState(false);

  async function onSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setSubmitting(true);
    const form = new FormData(event.currentTarget);
    await fetch("/api/signup", {
      method: "POST",
      body: JSON.stringify({
        email: form.get("email"),
        password: form.get("password"),
        phoneNumber: form.get("phoneNumber"),
        marketingOptIn: form.get("marketingOptIn") === "on",
      }),
    });
    setSubmitting(false);
  }

  return (
    <form onSubmit={onSubmit}>
      {/* Placeholder doing the job of a label. */}
      <input type="email" name="email" placeholder="Work email" required />
      <input type="password" name="password" placeholder="Password" required />
      <input type="tel" name="phoneNumber" placeholder="Mobile (optional)" />

      {/* Pre-ticked marketing consent, bundled with accepting the terms. */}
      <label>
        <input type="checkbox" name="marketingOptIn" defaultChecked />
        Send me product updates and offers, and I accept the terms
      </label>

      <button type="submit" disabled={submitting}>
        {submitting ? "Creating account..." : "Create account"}
      </button>
    </form>
  );
}
