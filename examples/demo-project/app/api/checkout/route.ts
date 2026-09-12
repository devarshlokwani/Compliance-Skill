import Stripe from "stripe";

const stripe = new Stripe(process.env.STRIPE_SECRET_KEY!);

// A recurring subscription with a trial. No terms of service exist anywhere
// in the project, and there is no cancellation route.
export async function POST(request: Request) {
  const { customerEmail, priceId } = await request.json();

  const session = await stripe.checkout.sessions.create({
    mode: "subscription",
    customer_email: customerEmail,
    line_items: [{ price: priceId, quantity: 1 }],
    subscription_data: { trial_period_days: 14 },
    success_url: "https://meetingnotes.example/welcome",
    cancel_url: "https://meetingnotes.example/pricing",
  });

  return Response.json({ url: session.url });
}
