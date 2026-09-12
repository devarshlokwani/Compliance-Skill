import OpenAI from "openai";
import { Resend } from "resend";

const openai = new OpenAI({ apiKey: process.env.OPENAI_API_KEY });
const resend = new Resend(process.env.RESEND_API_KEY);

// The whole transcript goes to a third-party model API. Nothing in the
// product tells the user that, because there is nothing to tell them in.
export async function POST(request: Request) {
  const { transcript, email } = await request.json();

  const completion = await openai.chat.completions.create({
    model: "gpt-4o-mini",
    messages: [
      { role: "system", content: "Summarise this meeting transcript into action items." },
      { role: "user", content: transcript },
    ],
  });

  const summary = completion.choices[0]?.message?.content ?? "";

  await resend.emails.send({
    from: "notes@meetingnotes.example",
    to: email,
    subject: "Your meeting summary",
    text: summary,
  });

  return Response.json({ summary });
}
