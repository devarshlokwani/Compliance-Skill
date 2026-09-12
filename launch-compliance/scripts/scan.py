#!/usr/bin/env python3
"""
launch-compliance scanner.

Walks a project and reports the compliance, privacy, security and
launch-readiness signals that are visible in the source itself:
third-party services that have become subprocessors, personal-data fields,
auth/payment/AI integrations, cookie and storage use, exposed secrets,
missing governance documents, launch-readiness gaps and common
accessibility defects.

Design rules -- do not break these:

  * Standard library only. No dependencies, ever. This runs as a CI gate
    and in environments with no install step.

  * Absence is reliable; presence is not. The scanner can prove a privacy
    policy is missing. It cannot prove an existing one is accurate. Report
    wording must never imply otherwise.

  * Exit code is non-zero only for an exposed secret (see --fail-on).
    The shipped CI workflow depends on that.

  * Findings are signals, not verdicts. Severity is assigned honestly:
    inflating everything to blocking gets the whole list ignored.

Usage:
    python3 scan.py PATH [--out scan.json] [--report scan.md] [--quiet]
"""

from __future__ import annotations

import argparse
import json
import math
import os
import re
import subprocess
import sys
from collections import Counter
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable, Iterator, Sequence

SCANNER_VERSION = "1.0.0"

# --------------------------------------------------------------------------
# Severity
# --------------------------------------------------------------------------

# Four buckets, in the order they are reported. The definitions are the
# contract; see SKILL.md Phase 2.
SEVERITIES = ("blocking", "month", "know", "polish")

SEVERITY_LABEL = {
    "blocking": "Blocking",
    "month": "Fix this month",
    "know": "Know about it",
    "polish": "Polish",
}

SEVERITY_BLURB = {
    "blocking": "Do not open signups until this is fixed.",
    "month": "A real obligation with real penalties, but not on fire.",
    "know": "Not triggered yet, or lower probability -- but know the trigger.",
    "polish": "Won't get you sued. Will make the launch look unfinished.",
}

# --------------------------------------------------------------------------
# Walking
# --------------------------------------------------------------------------

SKIP_DIRS = {
    ".git", ".hg", ".svn", "node_modules", "bower_components", "vendor",
    "__pycache__", ".mypy_cache", ".pytest_cache", ".ruff_cache",
    "venv", ".venv", "env", "virtualenv",
    "dist", "build", "out", ".next", ".nuxt", ".svelte-kit", ".astro",
    ".output", ".vercel", ".netlify", ".turbo", ".parcel-cache", ".cache",
    "coverage", ".nyc_output", "target", "Pods",
    ".terraform", ".gradle", ".idea", ".vscode",
}

# Extensions we will open and read as text.
TEXT_EXTS = {
    ".ts", ".tsx", ".js", ".jsx", ".mjs", ".cjs", ".mts", ".cts",
    ".py", ".rb", ".go", ".rs", ".java", ".kt", ".kts", ".swift", ".m",
    ".php", ".cs", ".scala", ".ex", ".exs", ".dart", ".c", ".cc", ".cpp", ".h",
    ".html", ".htm", ".vue", ".svelte", ".astro", ".hbs", ".ejs", ".erb", ".liquid",
    ".css", ".scss", ".sass", ".less", ".styl",
    ".json", ".jsonc", ".yaml", ".yml", ".toml", ".ini", ".cfg", ".conf",
    ".md", ".mdx", ".txt", ".xml", ".graphql", ".gql", ".prisma", ".sql",
    ".sh", ".bash", ".zsh", ".ps1", ".dockerfile", ".tf", ".tfvars",
    ".env", ".example", ".sample", ".template", ".webmanifest",
}

# Filenames without a useful extension that we still want to read.
TEXT_NAMES = {
    "dockerfile", "makefile", "procfile", "gemfile", "rakefile",
    "license", "licence", "notice", "readme", "changelog", "security",
    "robots.txt", ".gitignore", ".dockerignore", ".npmrc", ".nvmrc",
    ".launch-compliance-ignore",
}

CODE_EXTS = {
    ".ts", ".tsx", ".js", ".jsx", ".mjs", ".cjs", ".mts", ".cts",
    ".py", ".rb", ".go", ".rs", ".java", ".kt", ".swift", ".php", ".cs",
    ".vue", ".svelte", ".astro", ".html", ".htm", ".erb", ".ejs", ".hbs",
    ".prisma", ".sql", ".graphql", ".gql",
}

MARKUP_EXTS = {".html", ".htm", ".tsx", ".jsx", ".vue", ".svelte", ".astro",
               ".ejs", ".erb", ".hbs", ".liquid", ".php", ".md", ".mdx"}

# Stylesheets, plus anything that can carry an inline <style> block. Server-
# rendered templates keep their CSS in the document more often than SPAs do.
STYLE_EXTS = {".css", ".scss", ".sass", ".less", ".styl", ".tsx", ".jsx",
              ".ts", ".js", ".vue", ".svelte", ".astro",
              ".html", ".htm", ".erb", ".ejs", ".hbs", ".liquid", ".php"}

MAX_FILE_BYTES = 1_500_000
MAX_FILES = 20_000
MAX_EVIDENCE = 6


@dataclass
class SourceFile:
    path: str          # project-relative, posix separators
    ext: str
    name: str          # lowercase basename
    text: str
    size: int


def line_of(text: str, index: int) -> int:
    """1-based line number of a character offset."""
    return text.count("\n", 0, index) + 1


def snippet(line: str, limit: int = 150) -> str:
    line = " ".join(line.split())
    if len(line) > limit:
        line = line[: limit - 1].rstrip() + "…"
    return line


def collect_files(root: Path) -> list[SourceFile]:
    files: list[SourceFile] = []
    root = root.resolve()
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = sorted(d for d in dirnames if d not in SKIP_DIRS)
        for fname in sorted(filenames):
            if len(files) >= MAX_FILES:
                return files
            abs_path = Path(dirpath) / fname
            try:
                rel = abs_path.relative_to(root).as_posix()
            except ValueError:
                continue
            ext = abs_path.suffix.lower()
            low = fname.lower()
            readable = (
                ext in TEXT_EXTS
                or low in TEXT_NAMES
                or low.startswith(".env")
                or low.split(".")[0] in TEXT_NAMES
            )
            try:
                size = abs_path.stat().st_size
            except OSError:
                continue
            if not readable or size > MAX_FILE_BYTES:
                # Still record the path so presence checks (favicon, sitemap,
                # images) work for binary files too.
                files.append(SourceFile(path=rel, ext=ext, name=low, text="", size=size))
                continue
            try:
                text = abs_path.read_text(encoding="utf-8", errors="replace")
            except OSError:
                text = ""
            files.append(SourceFile(path=rel, ext=ext, name=low, text=text, size=size))
    return files


# --------------------------------------------------------------------------
# Model
# --------------------------------------------------------------------------


@dataclass
class Evidence:
    file: str
    line: int
    snippet: str

    def as_dict(self) -> dict:
        return {"file": self.file, "line": self.line, "snippet": self.snippet}


@dataclass
class Signal:
    """A fact about the codebase. Not necessarily a problem."""
    kind: str            # service | personal_data | auth | payment | ai | cookie
    name: str
    detail: str = ""
    category: str = ""
    evidence: list[Evidence] = field(default_factory=list)

    def as_dict(self) -> dict:
        return {
            "kind": self.kind,
            "name": self.name,
            "detail": self.detail,
            "category": self.category,
            "evidence": [e.as_dict() for e in self.evidence[:MAX_EVIDENCE]],
            "evidence_count": len(self.evidence),
        }


@dataclass
class Finding:
    id: str
    title: str
    severity: str
    detail: str
    fix: str
    reference: str = ""
    evidence: list[Evidence] = field(default_factory=list)
    basis: str = "absence"
    fix_snippet: str = ""

    def extra_evidence(self) -> int:
        return max(0, len(self.evidence) - MAX_EVIDENCE)

    def as_dict(self) -> dict:
        return {
            "id": self.id,
            "title": self.title,
            "severity": self.severity,
            "basis": self.basis,
            "detail": self.detail,
            "fix": self.fix,
            "fix_snippet": self.fix_snippet,
            "reference": self.reference,
            "evidence": [e.as_dict() for e in self.evidence[:MAX_EVIDENCE]],
            "evidence_count": len(self.evidence),
        }


# How each finding was arrived at. This is the design principle "absence is
# reliable; presence is not", made machine-readable:
#
#   absence    -- we looked for a file or a route and it is not there. The
#                 claim that it is missing is reliable.
#   pattern    -- a specific pattern matched in source. Usually right; read the
#                 evidence lines before acting.
#   inference  -- we inferred meaning from names, imports or dependencies.
#                 Confirm with a human before it reaches a published document.
#
# Anything not listed here defaults to "absence".
FINDING_BASIS: dict[str, str] = {
    "secret.exposed": "pattern",
    "launch.robots-blocks-all": "pattern",
    "launch.framework-title": "pattern",
    "launch.insecure-assets": "pattern",
    "launch.pre-ticked-consent": "pattern",
    "a11y.img-missing-alt": "pattern",
    "a11y.focus-removed": "pattern",
    "a11y.div-as-button": "pattern",
    "a11y.placeholder-as-label": "pattern",
    "ai.provider-disclosure": "inference",
    "risk.special-category": "inference",
    "content.user-uploads": "inference",
    "mechanism.deletion-missing": "inference",
    "mechanism.export-missing": "inference",
    "docs.subprocessors-missing": "inference",
    "docs.cookie-policy-missing": "inference",
    # Absence *inside* a document that exists is as reliable as absence of the
    # file itself -- the name is either in the text or it is not.
    "docs.policy-omits-service": "absence",
    "docs.policy-undated": "absence",
    "docs.placeholder-published": "pattern",
    "docs.policy-stale": "pattern",
    "secret.in-history": "pattern",
}

BASIS_NOTE = {
    "absence": "we looked and it is not there",
    "pattern": "a pattern matched in your source -- read the evidence",
    "inference": "inferred from names and imports -- confirm before publishing",
}

# Copy-pasteable fixes for the mechanical findings. Only for things where a
# snippet is genuinely the whole answer -- never for anything needing a
# judgement call, where a snippet would imply the judgement has been made.
FIX_SNIPPETS: dict[str, str] = {
    "launch.og-tags-missing": """\
// Next.js app/layout.tsx
export const metadata = {
  metadataBase: new URL('https://example.com'),   // makes relative image paths absolute
  openGraph: {
    title: 'Product name',
    description: 'One sentence someone would repeat to a colleague.',
    url: 'https://example.com',
    siteName: 'Product name',
    images: [{ url: '/og.png', width: 1200, height: 630 }],
    type: 'website',
  },
}

<!-- plain HTML equivalent; og:image MUST be an absolute URL -->
<meta property="og:title"       content="Product name" />
<meta property="og:description" content="One sentence." />
<meta property="og:image"       content="https://example.com/og.png" />
<meta property="og:url"         content="https://example.com" />
<meta property="og:type"        content="website" />""",

    "launch.twitter-tags-missing": """\
// Next.js metadata
twitter: {
  card: 'summary_large_image',
  title: 'Product name',
  description: 'One sentence.',
  images: ['/og.png'],
}

<!-- plain HTML -->
<meta name="twitter:card" content="summary_large_image" />""",

    "launch.robots-missing": """\
# public/robots.txt
User-agent: *
Allow: /
Disallow: /api/
Disallow: /admin/

Sitemap: https://example.com/sitemap.xml""",

    "launch.sitemap-missing": """\
// Next.js app/sitemap.ts
import type { MetadataRoute } from 'next'

export default function sitemap(): MetadataRoute.Sitemap {
  return [
    { url: 'https://example.com',          lastModified: new Date(), priority: 1 },
    { url: 'https://example.com/pricing',  lastModified: new Date() },
  ]
}""",

    "launch.canonical-missing": """\
// Next.js metadata
metadataBase: new URL('https://example.com'),
alternates: { canonical: '/' },

<!-- plain HTML -->
<link rel="canonical" href="https://example.com/" />""",

    "launch.meta-description-missing": """\
// Next.js metadata -- 140-160 characters
description: 'What it does and who it is for, in one sentence someone would repeat.',

<!-- plain HTML -->
<meta name="description" content="..." />""",

    "launch.manifest-missing": """\
// Next.js app/manifest.ts
import type { MetadataRoute } from 'next'

export default function manifest(): MetadataRoute.Manifest {
  return {
    name: 'Product name',
    short_name: 'Product',
    start_url: '/',
    display: 'standalone',
    background_color: '#ffffff',
    theme_color: '#000000',
    icons: [{ src: '/icon-512.png', sizes: '512x512', type: 'image/png' }],
  }
}""",

    "launch.favicon-missing": """\
# Next.js App Router picks these up by filename -- no markup needed:
app/icon.png              # 512x512 works everywhere
app/apple-icon.png        # 180x180, for iOS home screens

<!-- anything else -->
<link rel="icon" href="/favicon.ico" sizes="any" />
<link rel="apple-touch-icon" href="/apple-touch-icon.png" />""",

    "a11y.focus-removed": """\
/* Replace the ring instead of deleting it. :focus-visible only shows it for
   keyboard users, which is the reason people reach for `outline: none`. */
button:focus-visible,
a:focus-visible,
input:focus-visible {
  outline: 2px solid currentColor;
  outline-offset: 2px;
}""",

    "a11y.div-as-button": """\
// Before
<div onClick={handleClick}>See how it works</div>

// After -- keyboard accessible and announced correctly, for free
<button type="button" onClick={handleClick}>See how it works</button>

// If the markup genuinely cannot change:
<div
  role="button"
  tabIndex={0}
  onClick={handleClick}
  onKeyDown={(e) => { if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); handleClick(); } }}
>""",

    "a11y.placeholder-as-label": """\
// Before -- the label vanishes as soon as they type
<input type="email" placeholder="Work email" />

// After
<label htmlFor="email">Work email</label>
<input id="email" type="email" placeholder="you@company.com" />

/* If the design has no room for a visible label, hide it from sight only --
   never use display:none, which hides it from screen readers too. */
.sr-only {
  position: absolute; width: 1px; height: 1px;
  padding: 0; margin: -1px; overflow: hidden;
  clip: rect(0 0 0 0); white-space: nowrap; border: 0;
}""",

    "a11y.img-missing-alt": """\
<img src="/hero.png" alt="The dashboard, showing this week's meeting summaries" />

<!-- Decorative only? An empty alt is a decision; a missing one is an omission. -->
<img src="/divider.svg" alt="" />""",

    "launch.pre-ticked-consent": """\
// Before -- not valid consent under GDPR, and it bundles two separate things
<input type="checkbox" name="marketingOptIn" defaultChecked />
Send me product updates, and I accept the terms

// After -- unticked, and the two are separated
<input type="checkbox" name="marketingOptIn" />
Send me occasional product updates (optional)

<input type="checkbox" name="acceptedTerms" required />
I accept the <a href="/terms">terms</a> and <a href="/privacy">privacy policy</a>

// Record what they consented to, when, and to which version of the text.""",

    "docs.security-missing": """\
# SECURITY.md at the repository root

## Reporting a vulnerability
Email security@example.com. You'll get an acknowledgement within 2 business
days and an assessment within 7.

We won't pursue legal action against good-faith research under this policy.
Please don't access data that isn't yours, and give us time to fix it before
disclosing publicly.""",
}


# --------------------------------------------------------------------------
# Project shape
# --------------------------------------------------------------------------
#
# Launch-readiness findings are only meaningful for something with a web
# surface. Telling a Python library it has no Open Graph tags is exactly the
# noise that gets a scanner switched off, so those checks are gated on this.

# (name, surface, path fragments, package names)
FRAMEWORK_SIGNS: list[tuple[str, str, tuple[str, ...], tuple[str, ...]]] = [
    ("Next.js", "web", ("next.config.",), ("next",)),
    ("Nuxt", "web", ("nuxt.config.",), ("nuxt",)),
    ("Astro", "web", ("astro.config.",), ("astro",)),
    ("SvelteKit", "web", ("svelte.config.",), ("@sveltejs/kit",)),
    ("Remix", "web", ("remix.config.",), ("@remix-run/react",)),
    ("Gatsby", "web", ("gatsby-config.",), ("gatsby",)),
    ("Angular", "web", ("angular.json",), ("@angular/core",)),
    ("Create React App", "web", (), ("react-scripts",)),
    ("Vite", "web", ("vite.config.",), ("vite",)),
    ("Django", "web", ("manage.py", "wsgi.py", "asgi.py"), ("django",)),
    ("Rails", "web", ("config.ru", "config/routes.rb"), ()),
    ("Laravel", "web", ("artisan",), ()),
    ("Phoenix", "web", ("mix.exs",), ()),
    ("Hugo / Jekyll", "web", ("_config.yml", "hugo.toml", "config.toml"), ()),
    ("Express", "api", (), ("express",)),
    ("Fastify", "api", (), ("fastify",)),
    ("NestJS", "api", (), ("@nestjs/core",)),
    ("Hono", "api", (), ("hono",)),
    ("Flask", "api", (), ("flask",)),
    ("FastAPI", "api", (), ("fastapi",)),
    ("React Native / Expo", "mobile", (), ("react-native", "expo")),
    ("Flutter", "mobile", ("pubspec.yaml",), ()),
]

MANIFEST_NAMES = {"package.json", "requirements.txt", "pyproject.toml", "go.mod",
                  "gemfile", "composer.json", "cargo.toml", "pubspec.yaml", "setup.py"}

# Where an environment variable is genuinely read or set, across the runtimes
# and config formats a small project actually uses. `{env}` is the escaped
# variable-name prefix.
ENV_USE_TEMPLATE = (
    r"(?:"
    r"process\.env\.{env}"                       # node
    r"|process\.env\[[\"']{env}"                 # node, bracket form
    r"|import\.meta\.env\.{env}"                 # vite
    r"|os\.environ(?:\.get)?[\[(][\"']{env}"     # python
    r"|os\.getenv\([\"']{env}"                   # python
    r"|getenv\([\"']{env}"                       # php, c
    r"|ENV\[[\"']{env}"                          # ruby
    r"|System\.getenv\([\"']{env}"               # java
    r"|env\([\"']{env}"                          # prisma, laravel, elixir
    r"|\$\{{?{env}"                              # shell, docker-compose
    r"|secrets\.{env}"                           # github actions
    r"|^\s*(?:export\s+)?{env}[A-Z0-9_]*\s*[=:]" # .env files, yaml, compose
    r")[A-Z0-9_]*"
)


@dataclass
class ProjectShape:
    frameworks: list[str] = field(default_factory=list)
    web: bool = False
    api: bool = False
    mobile: bool = False
    library: bool = False
    reason: str = ""

    def label(self) -> str:
        parts = []
        if self.frameworks:
            parts.append(", ".join(self.frameworks))
        kinds = [k for k, on in (("web", self.web), ("API", self.api),
                                 ("mobile", self.mobile), ("library", self.library)) if on]
        if kinds:
            parts.append("/".join(kinds))
        # ASCII only: this goes to stdout, and Windows consoles are not
        # reliably UTF-8.
        return " - ".join(parts) if parts else "unrecognised"

    def as_dict(self) -> dict:
        return {"frameworks": self.frameworks, "web": self.web, "api": self.api,
                "mobile": self.mobile, "library": self.library, "reason": self.reason}


# --------------------------------------------------------------------------
# Service registry -- these become the subprocessor list
# --------------------------------------------------------------------------
#
# Each entry: packages (dependency names / prefixes), modules (import
# specifiers), envs (env-var prefixes), hosts (API hostnames in source).
# `data` describes what typically flows to them -- confirm before publishing.

SERVICES: list[dict] = [
    # -- payments ---------------------------------------------------------
    {"name": "Stripe", "category": "payments", "purpose": "Payments and subscription billing",
     "data": "Name, email, billing address, card token, purchase history",
     "packages": ["stripe", "@stripe/"], "modules": ["stripe"], "envs": ["STRIPE_"],
     "hosts": ["api.stripe.com", "js.stripe.com", "checkout.stripe.com"]},
    {"name": "Paddle", "category": "payments", "purpose": "Merchant of record, billing and sales tax",
     "data": "Name, email, billing country, purchase history",
     "packages": ["@paddle/"], "modules": ["@paddle"], "envs": ["PADDLE_"], "hosts": ["api.paddle.com"]},
    {"name": "Lemon Squeezy", "category": "payments", "purpose": "Merchant of record and billing",
     "data": "Name, email, billing country, purchase history",
     "packages": ["@lemonsqueezy/"], "modules": ["lemonsqueezy"], "envs": ["LEMON"],
     "hosts": ["api.lemonsqueezy.com"]},
    {"name": "PayPal", "category": "payments", "purpose": "Payments",
     "data": "Name, email, transaction data",
     "packages": ["@paypal/"], "modules": ["paypal"], "envs": ["PAYPAL_"], "hosts": ["api-m.paypal.com"]},
    {"name": "Polar", "category": "payments", "purpose": "Merchant of record and billing",
     "data": "Name, email, purchase history",
     "packages": ["@polar-sh/"], "modules": ["polar"], "envs": ["POLAR_"], "hosts": ["api.polar.sh"]},
    {"name": "RevenueCat", "category": "payments", "purpose": "Mobile subscription management",
     "data": "Device/app user ID, purchase history",
     "packages": ["react-native-purchases", "@revenuecat/"], "modules": ["purchases"],
     "envs": ["REVENUECAT"], "hosts": ["api.revenuecat.com"]},

    # -- auth -------------------------------------------------------------
    {"name": "NextAuth / Auth.js", "category": "auth", "purpose": "Authentication and session management",
     "data": "Email, name, avatar, provider account ID",
     "packages": ["next-auth", "@auth/"], "modules": ["next-auth", "@auth/core"],
     "envs": ["NEXTAUTH_", "AUTH_"], "hosts": []},
    {"name": "Clerk", "category": "auth", "purpose": "Hosted authentication and user management",
     "data": "Email, phone, name, avatar, session and device metadata",
     "packages": ["@clerk/"], "modules": ["@clerk"], "envs": ["CLERK_"],
     "hosts": ["api.clerk.com", "clerk.accounts.dev"]},
    {"name": "Auth0", "category": "auth", "purpose": "Hosted authentication",
     "data": "Email, name, avatar, login metadata, IP address",
     "packages": ["auth0", "@auth0/"], "modules": ["auth0"], "envs": ["AUTH0_"], "hosts": ["auth0.com"]},
    {"name": "Supabase", "category": "backend", "purpose": "Hosted Postgres, auth and file storage",
     "data": "Everything stored in the database; auth identifiers; uploaded files",
     "packages": ["@supabase/"], "modules": ["@supabase"], "envs": ["SUPABASE_"],
     "hosts": ["supabase.co", "supabase.in"]},
    {"name": "Firebase", "category": "backend", "purpose": "Hosted database, auth and storage",
     "data": "Everything stored; auth identifiers; device and install IDs",
     "packages": ["firebase", "firebase-admin", "@firebase/"], "modules": ["firebase"],
     "envs": ["FIREBASE_"], "hosts": ["firebaseio.com"]},
    {"name": "WorkOS", "category": "auth", "purpose": "Enterprise SSO and directory sync",
     "data": "Email, name, directory attributes",
     "packages": ["@workos-inc/"], "modules": ["@workos"], "envs": ["WORKOS_"], "hosts": ["api.workos.com"]},
    {"name": "Kinde", "category": "auth", "purpose": "Hosted authentication",
     "data": "Email, name, session metadata",
     "packages": ["@kinde-oss/"], "modules": ["@kinde"], "envs": ["KINDE_"], "hosts": ["kinde.com"]},
    {"name": "Better Auth", "category": "auth", "purpose": "Self-hosted authentication library",
     "data": "Email, session identifiers (stored in your own database)",
     "packages": ["better-auth"], "modules": ["better-auth"], "envs": ["BETTER_AUTH"], "hosts": []},
    {"name": "Lucia", "category": "auth", "purpose": "Self-hosted session management",
     "data": "Session identifiers (stored in your own database)",
     "packages": ["lucia"], "modules": ["lucia"], "envs": [], "hosts": []},
    {"name": "Passport", "category": "auth", "purpose": "Self-hosted authentication middleware",
     "data": "Provider profile data (email, name, avatar)",
     "packages": ["passport"], "modules": ["passport"], "envs": [], "hosts": []},
    {"name": "Google OAuth", "category": "auth", "purpose": "Sign in with Google",
     "data": "Email, name, avatar, Google account ID",
     "packages": ["google-auth-library"], "modules": ["google-auth"], "envs": ["GOOGLE_CLIENT_"],
     "hosts": ["accounts.google.com"]},

    # -- analytics --------------------------------------------------------
    {"name": "Google Analytics", "category": "analytics", "purpose": "Product and marketing analytics",
     "data": "IP address, device and browser data, pages viewed, advertising identifiers",
     "packages": ["react-ga", "react-ga4", "@next/third-parties"], "modules": ["react-ga"],
     "envs": ["GA_", "GOOGLE_ANALYTICS"], "hosts": ["googletagmanager.com", "google-analytics.com"]},
    {"name": "PostHog", "category": "analytics", "purpose": "Product analytics, session replay, feature flags",
     "data": "IP address, device data, events, and anything captured in session replay",
     "packages": ["posthog-js", "posthog-node"], "modules": ["posthog"], "envs": ["POSTHOG_"],
     "hosts": ["posthog.com", "i.posthog.com"]},
    {"name": "Mixpanel", "category": "analytics", "purpose": "Product analytics",
     "data": "IP address, device data, user ID, events",
     "packages": ["mixpanel", "mixpanel-browser"], "modules": ["mixpanel"], "envs": ["MIXPANEL_"],
     "hosts": ["api.mixpanel.com"]},
    {"name": "Amplitude", "category": "analytics", "purpose": "Product analytics",
     "data": "IP address, device data, user ID, events",
     "packages": ["@amplitude/"], "modules": ["@amplitude"], "envs": ["AMPLITUDE_"], "hosts": ["amplitude.com"]},
    {"name": "Segment", "category": "analytics", "purpose": "Event routing to other analytics tools",
     "data": "Everything you send it, forwarded to each connected destination",
     "packages": ["@segment/", "analytics-node"], "modules": ["@segment"], "envs": ["SEGMENT_"],
     "hosts": ["segment.io", "segment.com"]},
    {"name": "Plausible", "category": "analytics", "purpose": "Cookieless web analytics",
     "data": "Page views, referrer, coarse device data (no cookies by default)",
     "packages": ["next-plausible", "plausible-tracker"], "modules": ["plausible"], "envs": ["PLAUSIBLE_"],
     "hosts": ["plausible.io"]},
    {"name": "Fathom", "category": "analytics", "purpose": "Cookieless web analytics",
     "data": "Page views, referrer, coarse device data",
     "packages": ["fathom-client"], "modules": ["fathom"], "envs": ["FATHOM_"], "hosts": ["usefathom.com"]},
    {"name": "Vercel Analytics", "category": "analytics", "purpose": "Web and speed analytics",
     "data": "Page views, route, coarse device data",
     "packages": ["@vercel/analytics", "@vercel/speed-insights"], "modules": ["@vercel/analytics"],
     "envs": [], "hosts": ["vitals.vercel-insights.com"]},
    {"name": "Hotjar", "category": "analytics", "purpose": "Heatmaps and session recording",
     "data": "Session recordings -- can capture form input unless masked",
     "packages": ["@hotjar/"], "modules": ["hotjar"], "envs": ["HOTJAR_"], "hosts": ["hotjar.com"]},
    {"name": "FullStory", "category": "analytics", "purpose": "Session recording",
     "data": "Session recordings -- can capture form input unless masked",
     "packages": ["@fullstory/"], "modules": ["fullstory"], "envs": ["FULLSTORY_"], "hosts": ["fullstory.com"]},
    {"name": "LogRocket", "category": "analytics", "purpose": "Session recording and error replay",
     "data": "Session recordings, network payloads -- can capture personal data unless masked",
     "packages": ["logrocket"], "modules": ["logrocket"], "envs": ["LOGROCKET_"], "hosts": ["logrocket.com"]},
    {"name": "Meta Pixel", "category": "advertising", "purpose": "Conversion tracking for paid ads",
     "data": "IP address, browser data, page and event data, hashed email if configured",
     "packages": ["react-facebook-pixel"], "modules": ["facebook-pixel"], "envs": ["FB_PIXEL", "META_PIXEL"],
     "hosts": ["connect.facebook.net"]},

    # -- error tracking / monitoring --------------------------------------
    {"name": "Sentry", "category": "error-tracking", "purpose": "Error and performance monitoring",
     "data": "Stack traces, request URLs, and request bodies/headers if not scrubbed; user ID if set",
     "packages": ["@sentry/"], "modules": ["@sentry"], "envs": ["SENTRY_"], "hosts": ["sentry.io"]},
    {"name": "Bugsnag", "category": "error-tracking", "purpose": "Error monitoring",
     "data": "Stack traces, request metadata, user ID if set",
     "packages": ["@bugsnag/"], "modules": ["@bugsnag"], "envs": ["BUGSNAG_"], "hosts": ["bugsnag.com"]},
    {"name": "Datadog", "category": "monitoring", "purpose": "Logs, metrics and APM",
     "data": "Logs and traces, including anything logged from request handlers",
     "packages": ["dd-trace", "@datadog/"], "modules": ["dd-trace", "@datadog"], "envs": ["DD_", "DATADOG_"],
     "hosts": ["datadoghq.com"]},
    {"name": "Axiom", "category": "monitoring", "purpose": "Log storage and querying",
     "data": "Application logs",
     "packages": ["@axiomhq/"], "modules": ["@axiomhq"], "envs": ["AXIOM_"], "hosts": ["api.axiom.co"]},
    {"name": "New Relic", "category": "monitoring", "purpose": "APM and logs",
     "data": "Traces, logs, request metadata",
     "packages": ["newrelic"], "modules": ["newrelic"], "envs": ["NEW_RELIC_"], "hosts": ["newrelic.com"]},

    # -- email / messaging ------------------------------------------------
    {"name": "Resend", "category": "email", "purpose": "Transactional email delivery",
     "data": "Recipient email address, email content",
     "packages": ["resend", "@react-email/"], "modules": ["resend"], "envs": ["RESEND_"],
     "hosts": ["api.resend.com"]},
    {"name": "SendGrid", "category": "email", "purpose": "Transactional and marketing email",
     "data": "Recipient email address, email content, open/click events",
     "packages": ["@sendgrid/"], "modules": ["@sendgrid"], "envs": ["SENDGRID_"], "hosts": ["api.sendgrid.com"]},
    {"name": "Postmark", "category": "email", "purpose": "Transactional email delivery",
     "data": "Recipient email address, email content",
     "packages": ["postmark"], "modules": ["postmark"], "envs": ["POSTMARK_"], "hosts": ["api.postmarkapp.com"]},
    {"name": "Mailgun", "category": "email", "purpose": "Transactional email delivery",
     "data": "Recipient email address, email content",
     "packages": ["mailgun.js"], "modules": ["mailgun"], "envs": ["MAILGUN_"], "hosts": ["api.mailgun.net"]},
    {"name": "Loops", "category": "email", "purpose": "Marketing and lifecycle email",
     "data": "Email address, name, behavioural attributes",
     "packages": ["loops"], "modules": ["loops"], "envs": ["LOOPS_"], "hosts": ["app.loops.so"]},
    {"name": "Mailchimp", "category": "email", "purpose": "Marketing email and audience management",
     "data": "Email address, name, engagement history, IP address",
     "packages": ["@mailchimp/"], "modules": ["mailchimp"], "envs": ["MAILCHIMP_"], "hosts": ["api.mailchimp.com"]},
    {"name": "Twilio", "category": "messaging", "purpose": "SMS and voice",
     "data": "Phone number, message content",
     "packages": ["twilio"], "modules": ["twilio"], "envs": ["TWILIO_"], "hosts": ["api.twilio.com"]},
    {"name": "Slack", "category": "messaging", "purpose": "Internal notifications",
     "data": "Whatever the notification payload contains -- often user email or content",
     "packages": ["@slack/"], "modules": ["@slack"], "envs": ["SLACK_"], "hosts": ["hooks.slack.com"]},
    {"name": "Discord", "category": "messaging", "purpose": "Community or notification integration",
     "data": "Whatever the webhook payload contains",
     "packages": ["discord.js"], "modules": ["discord"], "envs": ["DISCORD_"], "hosts": ["discord.com/api"]},

    # -- AI / LLM ---------------------------------------------------------
    {"name": "OpenAI", "category": "ai", "purpose": "LLM inference",
     "data": "Prompt content -- including any user text, files or context you pass",
     "packages": ["openai", "@ai-sdk/openai"], "modules": ["openai", "@ai-sdk/openai"], "envs": ["OPENAI_"],
     "hosts": ["api.openai.com"]},
    {"name": "Anthropic", "category": "ai", "purpose": "LLM inference",
     "data": "Prompt content -- including any user text, files or context you pass",
     "packages": ["@anthropic-ai/", "@ai-sdk/anthropic"], "modules": ["@anthropic-ai", "@ai-sdk/anthropic"],
     "envs": ["ANTHROPIC_"], "hosts": ["api.anthropic.com"]},
    {"name": "Google Gemini", "category": "ai", "purpose": "LLM inference",
     "data": "Prompt content",
     "packages": ["@google/generative-ai", "@google/genai", "@ai-sdk/google"],
     "modules": ["@google/generative-ai", "@google/genai"],
     "envs": ["GEMINI_", "GOOGLE_GENERATIVE"], "hosts": ["generativelanguage.googleapis.com"]},
    {"name": "Mistral", "category": "ai", "purpose": "LLM inference",
     "data": "Prompt content",
     "packages": ["@mistralai/", "@ai-sdk/mistral"], "modules": ["@mistralai"], "envs": ["MISTRAL_"],
     "hosts": ["api.mistral.ai"]},
    {"name": "Cohere", "category": "ai", "purpose": "LLM inference and embeddings",
     "data": "Prompt and document content",
     "packages": ["cohere-ai"], "modules": ["cohere"], "envs": ["COHERE_"], "hosts": ["api.cohere.ai"]},
    {"name": "Groq", "category": "ai", "purpose": "LLM inference",
     "data": "Prompt content",
     "packages": ["groq-sdk", "@ai-sdk/groq"], "modules": ["groq"], "envs": ["GROQ_"], "hosts": ["api.groq.com"]},
    {"name": "OpenRouter", "category": "ai", "purpose": "LLM routing across multiple providers",
     "data": "Prompt content, forwarded to whichever upstream model is selected",
     "packages": ["@openrouter/"], "modules": ["openrouter"], "envs": ["OPENROUTER_"], "hosts": ["openrouter.ai"]},
    {"name": "Replicate", "category": "ai", "purpose": "Hosted model inference",
     "data": "Prompt content, uploaded images or audio",
     "packages": ["replicate"], "modules": ["replicate"], "envs": ["REPLICATE_"], "hosts": ["api.replicate.com"]},
    {"name": "Hugging Face", "category": "ai", "purpose": "Hosted model inference",
     "data": "Prompt content, uploaded files",
     "packages": ["@huggingface/"], "modules": ["@huggingface"], "envs": ["HUGGINGFACE_", "HF_TOKEN"],
     "hosts": ["huggingface.co"]},
    {"name": "ElevenLabs", "category": "ai", "purpose": "Speech synthesis",
     "data": "Text to be spoken; voice samples if cloning",
     "packages": ["elevenlabs", "@elevenlabs/"], "modules": ["elevenlabs"], "envs": ["ELEVENLABS_", "ELEVEN_"],
     "hosts": ["api.elevenlabs.io"]},
    {"name": "Deepgram", "category": "ai", "purpose": "Speech-to-text",
     "data": "Audio recordings -- voice is a biometric identifier in some jurisdictions",
     "packages": ["@deepgram/"], "modules": ["@deepgram"], "envs": ["DEEPGRAM_"], "hosts": ["api.deepgram.com"]},
    {"name": "AssemblyAI", "category": "ai", "purpose": "Speech-to-text",
     "data": "Audio recordings",
     "packages": ["assemblyai"], "modules": ["assemblyai"], "envs": ["ASSEMBLYAI_"], "hosts": ["api.assemblyai.com"]},
    {"name": "Pinecone", "category": "ai", "purpose": "Vector database for retrieval",
     "data": "Embedded document content and metadata",
     "packages": ["@pinecone-database/"], "modules": ["@pinecone-database"], "envs": ["PINECONE_"],
     "hosts": ["pinecone.io"]},
    {"name": "LangChain", "category": "ai", "purpose": "LLM orchestration framework",
     "data": "Whatever the chain sends to its configured providers",
     "packages": ["langchain", "@langchain/"], "modules": ["langchain"], "envs": ["LANGCHAIN_"], "hosts": []},

    # -- storage / media --------------------------------------------------
    {"name": "AWS S3", "category": "storage", "purpose": "Object storage",
     "data": "Uploaded files and their metadata",
     "packages": ["@aws-sdk/client-s3", "aws-sdk"], "modules": ["@aws-sdk/client-s3"], "envs": ["AWS_"],
     "hosts": ["amazonaws.com"]},
    {"name": "Cloudflare R2", "category": "storage", "purpose": "Object storage",
     "data": "Uploaded files and their metadata",
     "packages": ["@cloudflare/"], "modules": ["@cloudflare"], "envs": ["R2_", "CLOUDFLARE_"],
     "hosts": ["r2.cloudflarestorage.com"]},
    {"name": "UploadThing", "category": "storage", "purpose": "File upload handling and hosting",
     "data": "Uploaded files, uploader identifier",
     "packages": ["uploadthing", "@uploadthing/"], "modules": ["uploadthing"], "envs": ["UPLOADTHING_"],
     "hosts": ["uploadthing.com"]},
    {"name": "Cloudinary", "category": "storage", "purpose": "Image and video hosting and transformation",
     "data": "Uploaded media; image content may include faces or location EXIF",
     "packages": ["cloudinary", "next-cloudinary"], "modules": ["cloudinary"], "envs": ["CLOUDINARY_"],
     "hosts": ["cloudinary.com"]},
    {"name": "Mux", "category": "storage", "purpose": "Video hosting and streaming",
     "data": "Uploaded video, viewer playback analytics",
     "packages": ["@mux/"], "modules": ["@mux"], "envs": ["MUX_"], "hosts": ["api.mux.com"]},
    {"name": "Vercel Blob", "category": "storage", "purpose": "Object storage",
     "data": "Uploaded files",
     "packages": ["@vercel/blob"], "modules": ["@vercel/blob"], "envs": ["BLOB_READ_WRITE"], "hosts": []},

    # -- data / infra -----------------------------------------------------
    {"name": "Neon", "category": "database", "purpose": "Hosted Postgres",
     "data": "Everything stored in the database",
     "packages": ["@neondatabase/"], "modules": ["@neondatabase"], "envs": ["NEON_"], "hosts": ["neon.tech"]},
    {"name": "PlanetScale", "category": "database", "purpose": "Hosted MySQL",
     "data": "Everything stored in the database",
     "packages": ["@planetscale/"], "modules": ["@planetscale"], "envs": ["PLANETSCALE_"],
     "hosts": ["planetscale.com"]},
    {"name": "MongoDB Atlas", "category": "database", "purpose": "Hosted document database",
     "data": "Everything stored in the database",
     "packages": ["mongodb", "mongoose"], "modules": ["mongodb", "mongoose"], "envs": ["MONGODB_", "MONGO_"],
     "hosts": ["mongodb.net"]},
    {"name": "Upstash", "category": "database", "purpose": "Hosted Redis, queues and rate limiting",
     "data": "Cached values and rate-limit keys (often IP addresses or user IDs)",
     "packages": ["@upstash/"], "modules": ["@upstash"], "envs": ["UPSTASH_"], "hosts": ["upstash.io"]},
    {"name": "Turso", "category": "database", "purpose": "Hosted SQLite",
     "data": "Everything stored in the database",
     "packages": ["@libsql/"], "modules": ["@libsql"], "envs": ["TURSO_"], "hosts": ["turso.io"]},
    {"name": "Prisma", "category": "database", "purpose": "ORM -- its schema is the best source for your data inventory",
     "data": "Local library; no data leaves your infrastructure",
     "packages": ["prisma", "@prisma/"], "modules": ["@prisma/client"], "envs": [], "hosts": []},
    {"name": "Drizzle", "category": "database", "purpose": "ORM -- its schema is the best source for your data inventory",
     "data": "Local library; no data leaves your infrastructure",
     "packages": ["drizzle-orm"], "modules": ["drizzle-orm"], "envs": [], "hosts": []},

    # -- support / product ------------------------------------------------
    {"name": "Intercom", "category": "support", "purpose": "Customer messaging and support",
     "data": "Email, name, conversation content, browsing metadata",
     "packages": ["@intercom/"], "modules": ["intercom"], "envs": ["INTERCOM_"], "hosts": ["intercom.io"]},
    {"name": "Crisp", "category": "support", "purpose": "Live chat support",
     "data": "Email, name, conversation content",
     "packages": ["crisp-sdk-web"], "modules": ["crisp"], "envs": ["CRISP_"], "hosts": ["crisp.chat"]},
    {"name": "Zendesk", "category": "support", "purpose": "Support ticketing",
     "data": "Email, name, ticket content",
     "packages": ["@zendesk/"], "modules": ["zendesk"], "envs": ["ZENDESK_"], "hosts": ["zendesk.com"]},
    {"name": "Algolia", "category": "search", "purpose": "Hosted search",
     "data": "Indexed records and search queries",
     "packages": ["algoliasearch", "react-instantsearch"], "modules": ["algoliasearch"], "envs": ["ALGOLIA_"],
     "hosts": ["algolia.net"]},
    {"name": "Mapbox", "category": "maps", "purpose": "Maps and geocoding",
     "data": "Coordinates and search queries -- location is sensitive in several regimes",
     "packages": ["mapbox-gl", "@mapbox/"], "modules": ["mapbox"], "envs": ["MAPBOX_"], "hosts": ["api.mapbox.com"]},
    {"name": "Google Maps", "category": "maps", "purpose": "Maps, places and geocoding",
     "data": "Coordinates and search queries",
     "packages": ["@googlemaps/", "@react-google-maps/"], "modules": ["@googlemaps"], "envs": ["GOOGLE_MAPS"],
     "hosts": ["maps.googleapis.com"]},
    {"name": "Google Fonts", "category": "cdn", "purpose": "Web fonts served from Google",
     "data": "Visitor IP address at font-fetch time -- self-host to avoid the transfer entirely",
     "packages": [], "modules": [], "envs": [], "hosts": ["fonts.googleapis.com", "fonts.gstatic.com"]},
]


# --------------------------------------------------------------------------
# Compiled service matchers
# --------------------------------------------------------------------------
#
# Everything here is built once. The naive version -- constructing a pattern
# string per service per line -- costs tens of millions of re.escape calls on
# a real codebase, which is slow enough to make people delete the CI step.


@dataclass
class ServiceMatcher:
    name: str
    package_rx: re.Pattern | None
    module_rx: re.Pattern | None
    env_rx: re.Pattern | None
    host_rx: re.Pattern | None


def _alt(parts: Sequence[str]) -> re.Pattern | None:
    return re.compile("|".join(parts)) if parts else None


_SERVICE_MATCHERS: list[ServiceMatcher] | None = None


def build_service_matchers() -> list[ServiceMatcher]:
    global _SERVICE_MATCHERS
    if _SERVICE_MATCHERS is not None:
        return _SERVICE_MATCHERS
    built: list[ServiceMatcher] = []
    for svc in SERVICES:
        built.append(ServiceMatcher(
            name=svc["name"],
            package_rx=_alt([r"""["']""" + re.escape(p) + r"""[^"']*["']\s*:""" for p in svc["packages"]]
                            + [r"^\s*" + re.escape(p) + r"[\s=><~^!\[]" for p in svc["packages"]]),
            module_rx=_alt([r"""(?:from|import|require\()\s*["']""" + re.escape(m)
                            for m in svc["modules"]]),
            env_rx=_alt([ENV_USE_TEMPLATE.format(env=re.escape(e)) for e in svc["envs"]]),
            host_rx=_alt([r"(?://|@|\bhttps?:)[^\s\"'`]*" + re.escape(h) for h in svc["hosts"]]),
        ))
    _SERVICE_MATCHERS = built
    return built


def _service_needles() -> list[str]:
    """Literal fragments that must appear before a line is worth examining."""
    needles: set[str] = set()
    for svc in SERVICES:
        for group in ("packages", "modules", "envs", "hosts"):
            for value in svc[group]:
                # The shortest distinctive piece: hostnames reduce to their
                # registrable part, scoped packages to the scope.
                token = value.strip("@/_-")
                if not token:
                    continue
                needles.add(token.split("/")[0].split(".")[0])
    return sorted(n for n in needles if len(n) >= 2)


# A single cheap pass that rejects lines mentioning nothing service-shaped.
SERVICE_PRESCREEN = re.compile(
    "|".join(re.escape(n) for n in _service_needles()), re.I)


# --------------------------------------------------------------------------
# Personal-data field vocabulary
# --------------------------------------------------------------------------
#
# (token regex, human label, category, high_risk, template subset)
#   category: identity | contact | credential | financial | location |
#             device | behavioural | special
#   template subset: None for all of PII_CONTEXT_TEMPLATES, or the indices to
#     use. Tokens that are ordinary English words ("name", "age") need the
#     narrow declaration contexts only, or they match every object literal in
#     the codebase.

PII_TOKENS: list[tuple[str, str, str, bool, tuple[int, ...] | None]] = [
    (r"e?mail(?:_?address)?", "Email address", "contact", False, None),
    (r"(?:phone|mobile|telephone)(?:_?number)?", "Phone number", "contact", False, None),
    (r"(?:full|first|last|given|family|display)_?name", "Name", "identity", False, None),
    (r"name", "Name", "identity", False, (1, 2, 3, 4, 5)),
    (r"username", "Username", "identity", False, None),
    (r"(?:street|postal|mailing|billing|shipping)_?address", "Postal address", "contact", False, None),
    (r"(?:post|zip)_?code", "Postcode", "contact", False, None),
    (r"(?:date_?of_?birth|dob|birth_?date|birthday)", "Date of birth", "identity", True, None),
    (r"age", "Age", "identity", True, (1, 2, 3, 4, 5)),
    (r"gender", "Gender", "identity", False, None),
    (r"(?:ssn|social_?security)", "Social Security number", "special", True, None),
    (r"(?:national_?id|passport_?number|drivers?_?licen[cs]e|tax_?id|aadhaar)",
     "Government identifier", "special", True, None),
    (r"(?:password|passwd|password_?hash)", "Password / credential", "credential", False, None),
    (r"(?:credit_?card|card_?number|cc_?num|cvv|cvc)", "Card data", "financial", True, None),
    (r"(?:bank_?account|iban|routing_?number|sort_?code)", "Bank details", "financial", True, None),
    (r"(?:salary|income|net_?worth|credit_?score)", "Financial status", "financial", True, None),
    (r"(?:ip_?address|remote_?addr|client_?ip)", "IP address", "device", False, None),
    (r"user_?agent", "User agent", "device", False, None),
    (r"(?:device_?id|fingerprint|advertising_?id|idfa)", "Device identifier", "device", False, None),
    (r"(?:latitude|longitude|geo_?location|coordinates)", "Location", "location", True, None),
    (r"(?:avatar\w*|profile_?(?:image|photo|picture)|photo_?url)", "Profile image", "identity", False, None),
    (r"(?:health|medical|diagnosis|prescription|symptom|patient)", "Health data", "special", True, None),
    (r"(?:biometric|face_?(?:id|print|embedding)|voice_?print|iris_?scan)",
     "Biometric data", "special", True, None),
    (r"(?:ethnicity|religion|political_?view|sexual_?orientation|union_?member)",
     "Special-category attribute", "special", True, None),
    (r"(?:utm_?source|utm_?campaign|referrer)", "Marketing attribution", "behavioural", False, None),
    (r"(?:last_?login|login_?count|last_?seen|session_?count)", "Usage metadata", "behavioural", False, None),
]

PII_CONTEXT_TEMPLATES = [
    r"^\s*[\"']?{tok}[\"']?\s*[:?]\s*\S",                                  # ts / json / graphql / prisma
    r"^\s*{tok}\s+(?:String|Int|Float|Boolean|DateTime|Json|Bytes|Decimal|BigInt)\b",
    r"^\s*[\"'`]?{tok}[\"'`]?\s+(?:VARCHAR|TEXT|CHAR|INT|INTEGER|BIGINT|DATE|TIMESTAMP|BOOLEAN|NUMERIC|SERIAL)",
    r"\b{tok}\s*=\s*(?:models\.|db\.|Column|Field|sa\.|text\(|varchar\()",  # django / sqlalchemy / drizzle
    r"(?:name|id)\s*=\s*[\"']{tok}[\"']",                                  # form inputs
    r"\b{tok}\s*:\s*z\.",                                                  # zod schemas
]

PII_FILE_EXTS = {".prisma", ".sql", ".ts", ".tsx", ".js", ".jsx", ".py", ".rb",
                 ".go", ".java", ".kt", ".swift", ".php", ".cs", ".graphql",
                 ".gql", ".vue", ".svelte", ".astro", ".html"}

# One cheap pass to reject lines containing no personal-data vocabulary at all,
# before any of the per-token context patterns run.
PII_PRESCREEN = re.compile("|".join(tok for tok, *_ in PII_TOKENS), re.I)

_PII_MATCHERS: list[tuple[str, str, bool, list[re.Pattern]]] | None = None


def build_pii_matchers() -> list[tuple[str, str, bool, list[re.Pattern]]]:
    global _PII_MATCHERS
    if _PII_MATCHERS is not None:
        return _PII_MATCHERS
    built = []
    for token_rx, label, category, high_risk, subset in PII_TOKENS:
        templates = (PII_CONTEXT_TEMPLATES if subset is None
                     else [PII_CONTEXT_TEMPLATES[i] for i in subset])
        built.append((label, category, high_risk,
                      [re.compile(t.format(tok=token_rx), re.I) for t in templates]))
    _PII_MATCHERS = built
    return built


# --------------------------------------------------------------------------
# Secret detection
# --------------------------------------------------------------------------
#
# Provider prefixes are assembled from fragments so that this file does not
# match itself when the scanner is pointed at its own repository.

_SK = "s" + "k"
_AKIA = "AK" + "IA"
_AIZA = "AI" + "za"

SECRET_PATTERNS: list[tuple[str, re.Pattern]] = [
    ("AWS access key ID", re.compile(_AKIA + r"[0-9A-Z]{16}")),
    ("Stripe live secret key", re.compile(r"\b(?:" + _SK + r"|rk)_live_[0-9A-Za-z]{20,}")),
    ("Anthropic API key", re.compile(_SK + r"-ant-(?:api|admin)[0-9]{2}-[A-Za-z0-9_\-]{24,}")),
    ("OpenAI API key", re.compile(_SK + r"-(?:proj-)?[A-Za-z0-9]{32,}")),
    ("GitHub token", re.compile(r"\b(?:ghp|gho|ghs|ghu|ghr)_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{30,}")),
    ("Google API key", re.compile(r"\b" + _AIZA + r"[0-9A-Za-z_\-]{33}")),
    ("Slack token", re.compile(r"\bxox[baprs]-[0-9A-Za-z\-]{12,}")),
    ("SendGrid API key", re.compile(r"\bSG\.[A-Za-z0-9_\-]{20,}\.[A-Za-z0-9_\-]{20,}")),
    ("Twilio account SID", re.compile(r"\bAC[0-9a-f]{32}\b")),
    ("Private key block", re.compile(r"-----BEGIN (?:RSA |EC |DSA |OPENSSH |PGP )?PRIVATE KEY-----")),
    ("Signed JWT", re.compile(r"\beyJ[A-Za-z0-9_\-]{10,}\.eyJ[A-Za-z0-9_\-]{10,}\.[A-Za-z0-9_\-]{10,}")),
]

GENERIC_SECRET_RE = re.compile(
    r"""(?ix)
    \b(
        api[_-]?key | secret(?:[_-]?key)? | client[_-]?secret | access[_-]?key |
        auth[_-]?token | private[_-]?key | password | passwd | service[_-]?role[_-]?key |
        webhook[_-]?secret | encryption[_-]?key | session[_-]?secret
    )
    \s* [:=] \s*
    ["']([^"'\s]{16,})["']
    """
)

PLACEHOLDER_HINTS = (
    "your", "example", "sample", "placeholder", "changeme", "change-me",
    "dummy", "fake", "todo", "xxxx", "test", "redacted", "insert", "replace",
    "abc123", "123456", "secret_here", "key_here", "goes_here", "<", ">",
    "{{", "${", "process.env", "os.environ", "getenv", "...", "****", "null",
    "none", "undefined", "lorem",
)

# Files whose values are expected to be placeholders.
PLACEHOLDER_FILE_RE = re.compile(
    r"(?i)(?:^|/)(?:\.env\.(?:example|sample|template|defaults)|env\.example|"
    r"[^/]*\.example(?:\.[a-z]+)?|[^/]*\.sample(?:\.[a-z]+)?|[^/]*\.template)$"
)

# Directories where a literal-looking value is usually a fixture.
FIXTURE_PATH_RE = re.compile(r"(?i)(?:^|/)(?:tests?|__tests__|__mocks__|fixtures?|spec|mocks?)(?:/|$)")

LOCKFILE_RE = re.compile(r"(?i)(?:^|/)(?:package-lock\.json|pnpm-lock\.yaml|yarn\.lock|poetry\.lock|"
                         r"cargo\.lock|composer\.lock|gemfile\.lock)$")


def shannon_entropy(value: str) -> float:
    if not value:
        return 0.0
    counts = Counter(value)
    n = len(value)
    return -sum((c / n) * math.log2(c / n) for c in counts.values())


def looks_like_placeholder(value: str) -> bool:
    low = value.lower()
    if any(hint in low for hint in PLACEHOLDER_HINTS):
        return True
    if len(set(value)) <= 4:
        return True
    return False


# --------------------------------------------------------------------------
# Launch-readiness and accessibility patterns
# --------------------------------------------------------------------------

FRAMEWORK_TITLES = {
    "create next app", "next.js app", "welcome to next.js", "next app",
    "vite + react", "vite + react + ts", "vite app", "react app", "create react app",
    "nuxt app", "vue app", "svelte app", "sveltekit app",
    "astro basics", "astro app", "my app", "untitled", "document",
    "laravel", "django site", "example domain", "hello world", "home",
}

IMG_TAG_RE = re.compile(r"<(?:img|Image)\b[^>]*/?>", re.I | re.S)
DIV_CLICK_RE = re.compile(r"<(?:div|span)\b[^>]*\bon[cC]lick\b[^>]*>", re.S)
INPUT_TAG_RE = re.compile(r"<input\b[^>]*/?>", re.I | re.S)
OUTLINE_NONE_RE = re.compile(r"outline\s*:\s*(?:none|0)\b", re.I)
INSECURE_ASSET_RE = re.compile(r"""(?:src|href|content)\s*=\s*["']http://([^"'/\s]+)""", re.I)
TITLE_RE = re.compile(r"""<title[^>]*>([^<]{1,120})</title>|(?:^|[\s{,])title\s*:\s*["']([^"']{1,120})["']""",
                      re.I | re.M)

LOCAL_HOSTS = ("localhost", "127.0.0.1", "0.0.0.0", "[::1]", "host.docker.internal")
SCHEMA_HOSTS = ("www.w3.org", "w3.org", "schema.org", "purl.org", "ns.adobe.com",
                "sodipodi.sourceforge.net", "inkscape.org", "example.com", "example.org",
                "creativecommons.org", "www.inkscape.org")

CONSENT_WORDS = ("consent", "marketing", "newsletter", "subscribe", "terms",
                 "agree", "privacy", "opt-in", "optin", "updates", "emails",
                 "offers", "accept")


# --------------------------------------------------------------------------
# Document accuracy -- reading the documents that DO exist
# --------------------------------------------------------------------------
#
# "Absence is reliable; presence is not" normally means saying nothing about a
# document that exists, because we cannot prove it is accurate.
#
# But absence *inside* a present document is exactly as reliable as absence of
# the file. If a privacy policy never contains the string "OpenAI" and the code
# calls OpenAI, that is a fact. And it is the case this skill treats as the
# worst one: a policy that is published and wrong is a written misstatement of
# your practices, where no policy at all is merely a gap.

# Where a service's name in prose differs from its name in the registry.
# Default search term is the registry name, lowercased.
SERVICE_ALIASES: dict[str, list[str]] = {
    "NextAuth / Auth.js": ["nextauth", "auth.js", "authjs"],
    "Google OAuth": ["google"],
    "Google Analytics": ["google analytics", "google"],
    "Google Gemini": ["gemini", "google"],
    "Google Maps": ["google maps", "google"],
    "Google Fonts": ["google fonts", "google"],
    "Meta Pixel": ["meta", "facebook"],
    "AWS S3": ["aws", "amazon", "s3"],
    "Cloudflare R2": ["cloudflare", "r2"],
    "MongoDB Atlas": ["mongodb", "mongo"],
    "Vercel Analytics": ["vercel"],
    "Vercel Blob": ["vercel"],
    "React Native / Expo": ["expo", "react native"],
    "Hugging Face": ["hugging face", "huggingface"],
    "Vercel AI SDK": ["vercel"],
    "Better Auth": ["better auth", "better-auth"],
    "Lemon Squeezy": ["lemon squeezy", "lemonsqueezy"],
}

# Libraries that run inside your own process. They show up in the service
# table for context, but no data leaves your infrastructure because of them,
# so a policy that does not name them is not wrong -- and demanding that it
# does would train people to ignore this check.
NOT_A_RECIPIENT = {
    "Prisma", "Drizzle", "Lucia", "Passport", "Better Auth",
    "NextAuth / Auth.js", "LangChain", "Vercel AI SDK",
}

# An unfilled template bracket: [COMPANY NAME], [DATE], [PRIVACY EMAIL].
# The lookahead keeps markdown links such as [LICENSE](LICENSE) out of it.
PLACEHOLDER_IN_DOC_RE = re.compile(r"\[([A-Z][A-Z0-9 _/&.'-]{2,60})\](?!\()")

DATE_MARKER_RE = re.compile(
    r"(?:last\s+updated|last\s+revised|last\s+modified|effective(?:\s+date)?|updated)"
    r"\s*[:\-—]?\s*\*{0,2}\s*([A-Za-z0-9][A-Za-z0-9 ,/.-]{5,30})",
    re.I,
)

DATE_FORMATS = ("%Y-%m-%d", "%d %B %Y", "%d %b %Y", "%B %d, %Y", "%b %d, %Y",
                "%d/%m/%Y", "%m/%d/%Y", "%Y/%m/%d", "%B %Y", "%d.%m.%Y")

# How old a published policy has to be before it is worth mentioning. Long
# enough that a stable product is not nagged, short enough to catch the policy
# generated once and never revisited.
STALE_AFTER_DAYS = 550


def parse_doc_date(raw: str) -> datetime | None:
    candidate = raw.strip().strip("*_.,;").strip()
    for cut in range(len(candidate), 5, -1):
        chunk = candidate[:cut].strip().rstrip(",.")
        for fmt in DATE_FORMATS:
            try:
                return datetime.strptime(chunk, fmt).replace(tzinfo=timezone.utc)
            except ValueError:
                continue
    return None


def robots_blocks_everything(text: str) -> bool:
    """True if robots.txt disallows everything for all user agents."""
    agent: str | None = None
    blocked = False
    for raw in text.splitlines():
        line = raw.split("#", 1)[0].strip()
        if not line or ":" not in line:
            continue
        key, _, value = line.partition(":")
        key = key.strip().lower()
        value = value.strip()
        if key == "user-agent":
            agent = value
        elif agent in ("*", None):
            if key == "disallow" and value == "/":
                blocked = True
            elif key == "allow" and value == "/":
                blocked = False
    return blocked


# --------------------------------------------------------------------------
# The scan
# --------------------------------------------------------------------------


class Scan:
    def __init__(self, root: Path, display_path: str):
        self.root = root
        self.display_path = display_path
        self.files = collect_files(root)
        self.paths = {f.path for f in self.files}
        self.lower_paths = {f.path.lower() for f in self.files}
        self.text_files = [f for f in self.files if f.text]
        self.signals: list[Signal] = []
        self.findings: list[Finding] = []
        self.suppressed: list[str] = []
        self.shape = ProjectShape()
        self._mechanisms: dict[str, list[Evidence]] | None = None

    # -- helpers ---------------------------------------------------------

    def by_ext(self, exts: Iterable[str]) -> list[SourceFile]:
        wanted = set(exts)
        return [f for f in self.text_files if f.ext in wanted]

    def find_path(self, *fragments: str) -> list[str]:
        return [p for p in sorted(self.lower_paths) if any(frag in p for frag in fragments)]

    def grep(self, pattern: str | re.Pattern,
             files: Sequence[SourceFile] | None = None) -> Iterator[tuple[SourceFile, int, str]]:
        rx = re.compile(pattern) if isinstance(pattern, str) else pattern
        for f in (self.text_files if files is None else files):
            lines = f.text.splitlines()
            for m in rx.finditer(f.text):
                ln = line_of(f.text, m.start())
                raw = lines[ln - 1] if ln - 1 < len(lines) else m.group(0)
                yield f, ln, raw

    def add_signal(self, kind: str, name: str, detail: str = "", category: str = "",
                   evidence: Sequence[Evidence] = ()) -> None:
        for s in self.signals:
            if s.kind == kind and s.name == name:
                s.evidence.extend(evidence)
                return
        self.signals.append(Signal(kind=kind, name=name, detail=detail,
                                   category=category, evidence=list(evidence)))

    def add_finding(self, id: str, title: str, severity: str, detail: str, fix: str,
                    reference: str = "", evidence: Sequence[Evidence] = ()) -> None:
        self.findings.append(Finding(
            id=id, title=title, severity=severity, detail=detail, fix=fix,
            reference=reference, evidence=list(evidence),
            basis=FINDING_BASIS.get(id, "absence"),
            fix_snippet=FIX_SNIPPETS.get(id, ""),
        ))

    def web_gap(self, *args, **kwargs) -> None:
        """A 'this is missing' launch finding, recorded only for web surfaces.

        Absence of a favicon means nothing in a CLI tool or a library. Firing
        these everywhere is how a scanner trains people to ignore it.
        """
        if self.shape.web:
            self.add_finding(*args, **kwargs)

    def signals_of(self, kind: str) -> list[Signal]:
        return [s for s in self.signals if s.kind == kind]

    def services_in(self, *categories: str) -> list[Signal]:
        wanted = set(categories)
        return [s for s in self.signals if s.kind == "service" and s.category in wanted]

    # -- phase 0: what kind of project is this -----------------------------

    def detect_project_shape(self) -> ProjectShape:
        """Work out whether this thing has a web surface at all.

        Launch-readiness checks are gated on the answer. A scanner that tells a
        CLI tool it needs Open Graph tags is a scanner people switch off.
        """
        shape = ProjectShape()
        manifest_text = "\n".join(f.text for f in self.text_files if f.name in MANIFEST_NAMES)
        reasons: list[str] = []

        for name, surface, fragments, packages in FRAMEWORK_SIGNS:
            hit = ""
            for frag in fragments:
                if self.find_path(frag):
                    hit = frag
                    break
            if not hit:
                for pkg in packages:
                    if re.search(r"""["']""" + re.escape(pkg) + r"""["']\s*:""", manifest_text) or \
                       re.search(r"(?im)^\s*" + re.escape(pkg) + r"[\s=><~^\[]", manifest_text):
                        hit = pkg
                        break
            if not hit:
                continue
            shape.frameworks.append(name)
            reasons.append(f"{name} ({hit})")
            setattr(shape, surface, True)

        if not shape.web:
            html = [f.path for f in self.files if f.ext in {".html", ".htm"}]
            templates = [f.path for f in self.files
                         if re.search(r"(?:^|/)(?:templates|views)/", f.path)
                         and f.ext in {".html", ".htm", ".erb", ".ejs", ".hbs", ".liquid", ".jinja", ".j2"}]
            if html:
                shape.web = True
                reasons.append(f"HTML files present ({html[0]})")
            elif templates:
                shape.web = True
                reasons.append(f"server-rendered templates ({templates[0]})")

        has_manifest = any(f.name in MANIFEST_NAMES for f in self.files)
        shape.library = has_manifest and not (shape.web or shape.api or shape.mobile)
        if shape.library:
            reasons.append("a package manifest with no web, API or mobile entry point")

        shape.reason = "; ".join(reasons)
        self.shape = shape
        return shape

    # -- suppression -------------------------------------------------------

    IGNORE_FILENAME = ".launch-compliance-ignore"

    def load_ignores(self, extra: Sequence[str] = ()) -> list[tuple[str, str]]:
        """Parse `.launch-compliance-ignore` plus any --ignore flags.

        One rule per line: a finding id, optionally scoped to a path prefix
        with `id:path/prefix`. Blank lines and `#` comments are skipped.
        """
        rules: list[tuple[str, str]] = []
        for raw in extra:
            fid, _, scope = raw.partition(":")
            rules.append((fid.strip(), scope.strip()))
        for f in self.text_files:
            if f.path != self.IGNORE_FILENAME:
                continue
            for line in f.text.splitlines():
                line = line.split("#", 1)[0].strip()
                if not line:
                    continue
                fid, _, scope = line.partition(":")
                rules.append((fid.strip(), scope.strip()))
        return rules

    def apply_ignores(self, rules: Sequence[tuple[str, str]]) -> None:
        if not rules:
            return
        kept: list[Finding] = []
        for finding in self.findings:
            scopes = [scope for fid, scope in rules if fid == finding.id]
            if not scopes:
                kept.append(finding)
                continue
            if any(scope == "" for scope in scopes):
                self.suppressed.append(finding.id)
                continue
            # Scoped rule: drop matching evidence, and the finding with it if
            # nothing is left to point at.
            before = len(finding.evidence)
            finding.evidence = [e for e in finding.evidence
                                if not any(e.file.startswith(s) for s in scopes)]
            if before and not finding.evidence:
                self.suppressed.append(finding.id)
                continue
            kept.append(finding)
        self.findings = kept

    # -- phase 1: third-party services ------------------------------------

    def detect_services(self) -> None:
        manifests = [f for f in self.text_files if f.name in {
            "package.json", "requirements.txt", "pyproject.toml", "go.mod",
            "gemfile", "composer.json", "cargo.toml", "pubspec.yaml"}]
        code = [f for f in self.text_files
                if f.ext in CODE_EXTS or f.name.startswith(".env")
                or f.ext in {".yml", ".yaml", ".toml", ".json"}]

        # Patterns are compiled once, and the files are walked once. Doing
        # either per-service turns a 100k-line project into a minute of regex
        # -- which is the same thing as a broken CI gate.
        matchers = build_service_matchers()
        hits_by_name: dict[str, list[Evidence]] = {}

        for f in manifests:
            for i, line in enumerate(f.text.splitlines(), 1):
                if not SERVICE_PRESCREEN.search(line):
                    continue
                for m in matchers:
                    if m.package_rx is not None and m.package_rx.search(line):
                        hits_by_name.setdefault(m.name, []).append(
                            Evidence(f.path, i, snippet(line)))

        for f in code:
            for i, line in enumerate(f.text.splitlines(), 1):
                if len(line) > 500:
                    continue
                # One cheap pass rejects the ~99% of lines that mention nothing
                # service-shaped, before any per-service work happens.
                if not SERVICE_PRESCREEN.search(line):
                    continue
                for m in matchers:
                    # An env var counts only where it is actually read or
                    # assigned, and a hostname only inside a URL -- not where
                    # the name merely appears in a string. Otherwise any file
                    # that documents service names (a registry, a README table,
                    # this scanner) reads as a dependency on all of them.
                    if ((m.module_rx is not None and m.module_rx.search(line))
                            or (m.env_rx is not None and m.env_rx.search(line))
                            or (m.host_rx is not None and m.host_rx.search(line))):
                        hits_by_name.setdefault(m.name, []).append(
                            Evidence(f.path, i, snippet(line)))

        for svc in SERVICES:
            hits = hits_by_name.get(svc["name"])
            if not hits:
                continue

            self.add_signal("service", svc["name"], detail=svc["purpose"],
                            category=svc["category"], evidence=hits[: MAX_EVIDENCE * 2])
            if svc["category"] == "ai":
                self.add_signal("ai", svc["name"], detail=svc["data"], category="ai",
                                evidence=hits[:MAX_EVIDENCE])
            elif svc["category"] == "payments":
                self.add_signal("payment", svc["name"], detail=svc["purpose"], category="payments",
                                evidence=hits[:MAX_EVIDENCE])
            elif svc["category"] in {"auth", "backend"}:
                self.add_signal("auth", svc["name"], detail=svc["purpose"], category=svc["category"],
                                evidence=hits[:MAX_EVIDENCE])

    # -- phase 1: personal data -------------------------------------------

    def detect_personal_data(self) -> None:
        files = [f for f in self.text_files if f.ext in PII_FILE_EXTS]

        # Compiled once, and the files walked once -- see detect_services for
        # why that matters.
        token_matchers = build_pii_matchers()
        hits_by_label: dict[str, list[Evidence]] = {}
        meta: dict[str, tuple[str, bool]] = {}

        for f in files:
            for i, line in enumerate(f.text.splitlines(), 1):
                if len(line) > 400:
                    continue
                if not PII_PRESCREEN.search(line):
                    continue
                for label, category, high_risk, patterns in token_matchers:
                    bucket = hits_by_label.setdefault(label, [])
                    if len(bucket) >= 40:
                        continue
                    for rx in patterns:
                        if rx.search(line):
                            bucket.append(Evidence(f.path, i, snippet(line)))
                            meta.setdefault(label, (category, high_risk))
                            break

        for label, hits in hits_by_label.items():
            if not hits:
                continue
            category, high_risk = meta[label]
            self.add_signal("personal_data", label,
                            detail="high risk" if high_risk else "",
                            category=category, evidence=hits)

        # typed inputs in markup
        for f in self.by_ext(MARKUP_EXTS):
            for m in INPUT_TAG_RE.finditer(f.text):
                tag = m.group(0)
                tm = re.search(r"""type\s*=\s*["'](email|tel|password)["']""", tag, re.I)
                if not tm:
                    continue
                label = {"email": "Email address", "tel": "Phone number",
                         "password": "Password / credential"}[tm.group(1).lower()]
                category = "credential" if tm.group(1).lower() == "password" else "contact"
                self.add_signal("personal_data", label, category=category,
                                evidence=[Evidence(f.path, line_of(f.text, m.start()), snippet(tag))])

    # -- phase 1: cookies and client storage ------------------------------

    def detect_storage(self) -> None:
        checks = [
            (r"document\.cookie", "document.cookie", "First-party cookie written in client code"),
            (r"cookies\(\)\s*\.\s*set\b|\bres\.cookie\(|\bsetCookie\(|['\"]Set-Cookie['\"]",
             "Server-set cookie", "Cookie set from the server"),
            (r"\blocalStorage\.", "localStorage", "Persistent client-side storage"),
            (r"\bsessionStorage\.", "sessionStorage", "Session-scoped client-side storage"),
            (r"\bindexedDB\b", "IndexedDB", "Persistent client-side storage"),
            (r"\bgtag\(|googletagmanager", "Google tag", "Advertising and analytics tag"),
            (r"\bfbq\(", "Meta Pixel", "Advertising tag"),
        ]
        code = [f for f in self.text_files if f.ext in CODE_EXTS]
        for pattern, name, detail in checks:
            hits = [Evidence(f.path, ln, snippet(raw)) for f, ln, raw in self.grep(pattern, code)]
            if hits:
                self.add_signal("cookie", name, detail=detail, evidence=hits)

    # -- phase 1: secrets --------------------------------------------------

    def detect_secrets(self) -> list[Evidence]:
        exposed: list[Evidence] = []

        for f in self.text_files:
            if PLACEHOLDER_FILE_RE.search(f.path) or LOCKFILE_RE.search(f.path):
                continue
            lines = f.text.splitlines()

            for label, rx in SECRET_PATTERNS:
                for m in rx.finditer(f.text):
                    token = m.group(0)
                    ln = line_of(f.text, m.start())
                    raw = lines[ln - 1] if ln - 1 < len(lines) else token
                    if label != "Private key block" and looks_like_placeholder(token):
                        continue
                    if re.search(r"(?i)(example|placeholder|redacted|sample|fake|dummy)", raw):
                        continue
                    masked = token[:6] + "…" + token[-2:] if len(token) > 14 else token[:4] + "…"
                    exposed.append(Evidence(f.path, ln, f"{label}: {masked}"))

            if FIXTURE_PATH_RE.search(f.path):
                continue
            for m in GENERIC_SECRET_RE.finditer(f.text):
                value = m.group(2)
                if looks_like_placeholder(value) or shannon_entropy(value) < 3.2:
                    continue
                ln = line_of(f.text, m.start())
                exposed.append(Evidence(f.path, ln, f"{m.group(1)} assigned a literal value"))

        # a real .env in the working tree
        env_present = [p for p in sorted(self.paths)
                       if Path(p).name == ".env" or Path(p).name.startswith((".env.local", ".env.production"))]
        if env_present:
            ignored = self.env_is_gitignored()
            for p in env_present:
                note = ".env file present in the working tree"
                if not ignored:
                    note += " and NOT matched by .gitignore"
                    exposed.append(Evidence(p, 1, note))

        return exposed

    def env_is_gitignored(self) -> bool:
        for f in self.text_files:
            if f.name == ".gitignore":
                for line in f.text.splitlines():
                    if line.strip() in {".env", ".env*", "*.env", ".env.*", "**/.env", ".env.local"}:
                        return True
        return False

    # -- phase 2: governance documents -------------------------------------

    DOC_CHECKS = (
        ("privacy", ("privacy",)),
        ("terms", ("terms", "tos.md", "tos.html", "conditions")),
        ("cookies", ("cookie-policy", "cookies.md", "cookies.html", "cookie-notice")),
        ("subprocessors", ("subprocessor", "sub-processor")),
        ("security", ("security.md", "security.txt")),
        ("license", ("license", "licence", "copying")),
        ("compliance", ("compliance.md",)),
    )

    DOC_EXTS = (".md", ".mdx", ".html", ".htm", ".txt", ".tsx", ".jsx",
                ".ts", ".js", ".vue", ".svelte", ".astro", ".pdf")

    def document_presence(self) -> dict[str, list[str]]:
        found: dict[str, list[str]] = {}
        for key, fragments in self.DOC_CHECKS:
            hits = []
            for p in sorted(self.lower_paths):
                if "launch-compliance/" in p:      # our own templates are not the project's documents
                    continue
                base = p.rsplit("/", 1)[-1]
                # LICENSE, NOTICE and COPYING are conventionally extensionless,
                # so an extension is sufficient but not necessary.
                if any(frag in p for frag in fragments) and (
                        base.endswith(self.DOC_EXTS) or "." not in base):
                    hits.append(p)
            if hits:
                found[key] = hits
        return found

    def mechanisms(self) -> dict[str, list[Evidence]]:
        if self._mechanisms is not None:
            return self._mechanisms
        mech: dict[str, list[Evidence]] = {}
        patterns = {
            "deletion": r"(?i)(delete[_-]?account|account[_-]?deletion|deleteUser|removeAccount|erase[_-]?data)",
            "export": r"(?i)(export[_-]?(?:data|account)|data[_-]?export|downloadMyData)",
            "consent": r"(?i)(cookie[_-]?consent|consent[_-]?banner|CookieBanner|consentMode|hasConsent)",
            "retention": r"(?i)(retention|purge[_-]?old|cleanup[_-]?job|deleteOlderThan)",
        }
        code = [f for f in self.text_files
                if f.ext in CODE_EXTS and "launch-compliance/" not in f.path]
        for key, pat in patterns.items():
            hits = [Evidence(f.path, ln, snippet(raw)) for f, ln, raw in self.grep(pat, code)]
            if hits:
                mech[key] = hits[:MAX_EVIDENCE]
        for key, frags in (("deletion", ("delete-account", "account/delete")),
                           ("export", ("export-data", "account/export"))):
            for p in self.find_path(*frags):
                mech.setdefault(key, []).append(Evidence(p, 1, "route present"))
        self._mechanisms = mech
        return mech

    # -- phase 3: launch readiness -----------------------------------------

    def detect_launch_readiness(self) -> None:
        # Markdown is excluded: documentation that *shows* an og:title tag is
        # not a page that *has* one, and counting it hides the real finding.
        markup = self.by_ext((MARKUP_EXTS - {".md", ".mdx"}) | {".ts", ".js", ".json"})
        blob = "\n".join(f.text for f in markup)

        def present(*patterns: str) -> bool:
            return any(re.search(p, blob, re.I | re.M) for p in patterns)

        if not (self.find_path("sitemap.xml", "sitemap.ts", "sitemap.js", "sitemap.tsx")
                or present(r"next-sitemap", r"generateSitemaps")):
            self.web_gap(
                "launch.sitemap-missing", "No sitemap", "polish",
                "Nothing in the project generates a sitemap. Crawlers will still find linked pages, but "
                "discovery of new ones is slower and you lose the coverage reporting in Search Console "
                "that makes indexing problems visible in the first place.",
                "Add `app/sitemap.ts` (Next.js), a static `public/sitemap.xml`, or your framework's "
                "equivalent, and point robots.txt at it.",
                "launch-readiness.md")

        robots_files = [f for f in self.text_files if f.name.startswith("robots.")]
        if not robots_files:
            self.web_gap(
                "launch.robots-missing", "No robots.txt", "polish",
                "There is no robots.txt. Crawlers will index anything they can reach, including staging "
                "routes, admin pages and any API endpoint that happens to return HTML.",
                "Add `public/robots.txt` (or `app/robots.ts`): allow your public pages, disallow `/api/`, "
                "`/admin/` and preview routes, and reference the sitemap.",
                "launch-readiness.md")
        else:
            for f in robots_files:
                if f.text and robots_blocks_everything(f.text):
                    self.add_finding(
                        "launch.robots-blocks-all", "robots.txt blocks every crawler", "know",
                        "robots.txt has a blanket `Disallow: /` for all user agents. That is correct for a "
                        "staging site and a silent disaster for a launched one: the site will not be "
                        "indexed at all, and nothing anywhere raises an error to tell you.",
                        "If this is production, drop the blanket rule and disallow only the paths you "
                        "actually want hidden. If the file was copied from staging, check what else came "
                        "with it.",
                        "launch-readiness.md",
                        [Evidence(f.path, 1, "User-agent: * / Disallow: /")])

        if not present(r"og:title", r"openGraph", r"property=[\"']og:"):
            self.web_gap(
                "launch.og-tags-missing", "No Open Graph tags", "polish",
                "No Open Graph metadata. Every link shared to Slack, iMessage, LinkedIn, Discord or X "
                "renders as a bare grey box with a URL under it. This is the most visible launch-day "
                "defect there is and it takes about ten minutes to fix.",
                "Set `openGraph: { title, description, url, images: [...] }` in your root metadata, or add "
                "`og:title`, `og:description`, `og:image` and `og:url` meta tags. Use a 1200x630 image and "
                "check it with a preview debugger before you post anywhere.",
                "launch-readiness.md")

        if not present(r"twitter:card", r"twitter:\s*\{", r"name=[\"']twitter:"):
            self.web_gap(
                "launch.twitter-tags-missing", "No Twitter/X card tags", "polish",
                "No `twitter:card` metadata. X and several other clients fall back to Open Graph, but "
                "without `summary_large_image` you get the small thumbnail card instead of the large one.",
                "Add `twitter: { card: 'summary_large_image', title, description, images }` to your "
                "metadata, or the equivalent meta tags.",
                "launch-readiness.md")

        if not present(r"rel=[\"']canonical[\"']", r"canonical\s*:", r"alternates\s*:"):
            self.web_gap(
                "launch.canonical-missing", "No canonical URLs", "polish",
                "No canonical URL is declared. If the site answers on more than one hostname -- apex and "
                "www, a preview deployment domain, http and https -- search engines treat each as a "
                "separate site and split ranking signals between them.",
                "Set `metadataBase` plus `alternates: { canonical: '/' }` in Next.js metadata, or add "
                "`<link rel=\"canonical\">` to the document head.",
                "launch-readiness.md")

        if not present(r"name=[\"']description[\"']", r"^\s*description\s*:\s*[\"']", r"\bdescription:\s*[\"']"):
            self.web_gap(
                "launch.meta-description-missing", "No meta description", "polish",
                "No meta description. Search engines will synthesise one from page text, usually badly, "
                "and you lose control of the single line most people read before deciding whether to click.",
                "Add a 140-160 character description to the root metadata and override it per page where "
                "it matters.",
                "launch-readiness.md")

        if not (self.find_path("favicon.ico", "favicon.png", "apple-icon", "apple-touch-icon",
                               "app/icon.", "src/app/icon.")
                or any(re.search(r"""rel=["'](?:shortcut )?icon["']""", f.text, re.I) for f in markup)):
            self.web_gap(
                "launch.favicon-missing", "No favicon", "polish",
                "No favicon or app icon. Browsers fall back to a blank document icon in tabs, bookmarks "
                "and history -- the site looks broken next to every other open tab.",
                "Add `app/icon.png` (Next.js) or `public/favicon.ico`, plus a 180x180 "
                "`apple-touch-icon.png` for iOS home screens.",
                "launch-readiness.md")

        if not (self.find_path("manifest.json", "site.webmanifest", "manifest.ts", "manifest.webmanifest")
                or present(r"rel=[\"']manifest[\"']")):
            self.web_gap(
                "launch.manifest-missing", "No web app manifest", "polish",
                "No web app manifest. The site cannot be installed to a home screen, and Android share "
                "targets and splash screens fall back to the bare URL.",
                "Add `app/manifest.ts` or `public/site.webmanifest` with name, short_name, icons, "
                "theme_color and display.",
                "launch-readiness.md")

        title_hits: list[Evidence] = []
        for f in markup:
            for m in TITLE_RE.finditer(f.text):
                value = (m.group(1) or m.group(2) or "").strip().lower()
                if value in FRAMEWORK_TITLES:
                    title_hits.append(Evidence(f.path, line_of(f.text, m.start()), snippet(m.group(0))))
        if title_hits:
            self.web_gap(
                "launch.framework-title", "Default framework title still in place", "polish",
                "The page title is still the scaffold default. It shows in browser tabs, bookmarks, search "
                "results and every link preview -- it is the first thing that says nobody finished this.",
                "Set a real `title`, and a `title.template` so child pages inherit a consistent suffix.",
                "launch-readiness.md", title_hits)

        insecure: list[Evidence] = []
        for f in markup + self.by_ext({".css", ".scss", ".sass", ".less"}):
            for m in INSECURE_ASSET_RE.finditer(f.text):
                host = m.group(1).lower()
                if host.startswith(LOCAL_HOSTS) or host in SCHEMA_HOSTS or host.endswith(".local"):
                    continue
                insecure.append(Evidence(f.path, line_of(f.text, m.start()), snippet(m.group(0))))
        if insecure:
            self.add_finding(
                "launch.insecure-assets", "Assets referenced over http://", "month",
                "One or more assets load over plain http. Browsers block mixed active content outright and "
                "downgrade or warn on passive content, so on launch day these either fail silently or put "
                "a security warning in front of your users.",
                "Switch every reference to https, or self-host the asset.",
                "launch-readiness.md", insecure)

        preticked: list[Evidence] = []
        for f in self.by_ext(MARKUP_EXTS):
            for m in INPUT_TAG_RE.finditer(f.text):
                tag = m.group(0)
                if not re.search(r"""type\s*=\s*["']checkbox["']""", tag, re.I):
                    continue
                if not re.search(r"\b(?:defaultChecked|checked)\b(?!\s*=\s*\{?\s*false)", tag):
                    continue
                context = f.text[max(0, m.start() - 300): m.end() + 300].lower()
                if not any(word in context for word in CONSENT_WORDS):
                    continue
                preticked.append(Evidence(f.path, line_of(f.text, m.start()), snippet(tag)))
        if preticked:
            self.add_finding(
                "launch.pre-ticked-consent", "Consent checkbox is pre-ticked", "month",
                "A consent or marketing checkbox is checked by default. Under GDPR consent has to be a "
                "freely given, specific, informed and unambiguous affirmative action -- a pre-ticked box is "
                "named in the recitals as exactly what does not qualify. It is also one of the most "
                "commonly enforced points precisely because it is visible from outside the product.",
                "Default the box to unchecked, keep marketing consent separate from accepting the terms, "
                "and record when and how each user consented.",
                "privacy-law.md", preticked)

    # -- phase 3: accessibility --------------------------------------------

    def detect_accessibility(self) -> None:
        markup = self.by_ext(MARKUP_EXTS - {".md", ".mdx"})

        missing_alt: list[Evidence] = []
        for f in markup:
            for m in IMG_TAG_RE.finditer(f.text):
                tag = m.group(0)
                if "{..." in tag or re.search(r"\balt\s*=", tag):
                    continue
                missing_alt.append(Evidence(f.path, line_of(f.text, m.start()), snippet(tag)))
        if missing_alt:
            self.add_finding(
                "a11y.img-missing-alt", "Images without alt text", "know",
                "One or more image elements have no `alt` attribute, so screen readers announce the file "
                "name instead. This is WCAG 1.1.1 Level A -- the single most frequently cited failure in "
                "US ADA web accessibility complaints, and in scope for the European Accessibility Act for "
                "consumer-facing services.",
                "Add `alt` text describing the image's purpose, or `alt=\"\"` if it is purely decorative so "
                "assistive technology skips it.",
                "launch-readiness.md", missing_alt)

        focus_killed: list[Evidence] = []
        for f in self.by_ext(STYLE_EXTS):
            if ":focus-visible" in f.text:
                continue
            for m in OUTLINE_NONE_RE.finditer(f.text):
                focus_killed.append(Evidence(f.path, line_of(f.text, m.start()), snippet(m.group(0))))
        if focus_killed:
            self.add_finding(
                "a11y.focus-removed", "Focus indicator removed with no replacement", "know",
                "`outline: none` appears in a stylesheet that never defines a `:focus-visible` style. "
                "Keyboard users then have no way to see where they are, which makes forms and navigation "
                "effectively unusable without a mouse. WCAG 2.4.7.",
                "Replace the default ring rather than deleting it: pair `outline: none` with a "
                "`:focus-visible` rule that draws something clearly visible against your background.",
                "launch-readiness.md", focus_killed)

        div_buttons: list[Evidence] = []
        for f in markup:
            for m in DIV_CLICK_RE.finditer(f.text):
                tag = m.group(0)
                if re.search(r"\brole\s*=", tag) and re.search(r"\btab[iI]ndex\s*=", tag):
                    continue
                div_buttons.append(Evidence(f.path, line_of(f.text, m.start()), snippet(tag)))
        if div_buttons:
            self.add_finding(
                "a11y.div-as-button", "Clickable div or span used instead of a button", "know",
                "An element with an `onClick` handler is neither a button nor a link and carries no role or "
                "tab index. It cannot be reached by keyboard, is not announced as interactive, and does not "
                "respond to Enter or Space. WCAG 2.1.1 and 4.1.2.",
                "Use a real `<button type=\"button\">`. If the markup genuinely cannot change, add "
                "`role=\"button\"`, `tabIndex={0}` and a key handler for Enter and Space.",
                "launch-readiness.md", div_buttons)

        placeholder_only: list[Evidence] = []
        for f in markup:
            label_ids = set(re.findall(r"""(?:htmlFor|for)\s*=\s*["']([^"']+)["']""", f.text))
            for m in INPUT_TAG_RE.finditer(f.text):
                tag = m.group(0)
                if re.search(r"""type\s*=\s*["'](?:hidden|submit|button|checkbox|radio)["']""", tag, re.I):
                    continue
                if not re.search(r"\bplaceholder\s*=", tag):
                    continue
                if re.search(r"\baria-label(?:ledby)?\s*=", tag):
                    continue
                idm = re.search(r"""\bid\s*=\s*["']([^"']+)["']""", tag)
                if idm and idm.group(1) in label_ids:
                    continue
                placeholder_only.append(Evidence(f.path, line_of(f.text, m.start()), snippet(tag)))
        if placeholder_only:
            self.add_finding(
                "a11y.placeholder-as-label", "Input labelled only by its placeholder", "polish",
                "An input has a placeholder but no associated label or aria-label. The placeholder "
                "disappears the moment someone types, so anyone interrupted mid-form loses the only "
                "indication of what the field was for, and screen readers may not announce it at all. "
                "WCAG 3.3.2.",
                "Add a `<label htmlFor=...>` -- visually hidden if the design needs it -- or an "
                "`aria-label`. Keep the placeholder for an example value, not for the field name.",
                "launch-readiness.md", placeholder_only)

    # -- phase 3b: the documents that already exist -------------------------

    LEGAL_DOC_KEYS = ("privacy", "terms", "cookies", "subprocessors")

    def detect_document_accuracy(self) -> None:
        """Check published legal documents against what the code does.

        Only makes claims that absence supports: a name that is not in the
        text, a bracket that was never filled, a date that is not there. It
        never asserts that a document IS accurate -- that needs a human.
        """
        docs = self.document_presence()
        by_path = {f.path.lower(): f for f in self.files}

        paths: list[str] = []
        for key in self.LEGAL_DOC_KEYS:
            paths.extend(docs.get(key, []))
        legal = [by_path[p] for p in dict.fromkeys(paths)
                 if p in by_path and by_path[p].text]
        if not legal:
            return

        combined = "\n".join(f.text for f in legal).lower()
        doc_list = ", ".join(f"`{f.path}`" for f in legal[:4])

        # (a) Services the code uses that the documents never name.
        if "privacy" in docs:
            unnamed = []
            for signal in self.signals_of("service"):
                if signal.name in NOT_A_RECIPIENT:
                    continue
                terms = SERVICE_ALIASES.get(signal.name, [signal.name.lower()])
                if not any(term in combined for term in terms):
                    unnamed.append(signal)
            if unnamed:
                names = ", ".join(s.name for s in unnamed)
                self.add_finding(
                    "docs.policy-omits-service",
                    f"Published policy never mentions {len(unnamed)} service(s) in use",
                    "month",
                    f"A privacy policy is published, and the text of {doc_list} does not contain "
                    f"the name of: **{names}**. Each of these appears in the code and receives "
                    "data. Transparency rules require disclosing the recipients of personal "
                    "data, and naming them is the accepted way to do it -- but the more "
                    "immediate problem is that a published policy which omits a recipient is a "
                    "statement of your practices that is incomplete in a checkable way. This is "
                    "the failure mode that is worse than having no policy at all: a missing "
                    "policy is a gap, an inaccurate one is a written misstatement.\n\n"
                    "The scanner can only tell you a name is absent from the text. It cannot "
                    "tell you the rest of the document is right -- read it.",
                    "Add each service to the privacy policy or the subprocessor list, saying "
                    "what it receives and why. If one of these is no longer in use, remove the "
                    "dependency rather than leaving it in the code.",
                    "writing-policies.md",
                    [e for s in unnamed for e in s.evidence[:1]][:MAX_EVIDENCE])

        # (b) Template brackets that were never filled in.
        placeholders: list[Evidence] = []
        for f in legal:
            seen: set[str] = set()
            for m in PLACEHOLDER_IN_DOC_RE.finditer(f.text):
                token = m.group(0)
                if token in seen:
                    continue
                seen.add(token)
                placeholders.append(Evidence(f.path, line_of(f.text, m.start()), snippet(token)))
        if placeholders:
            self.add_finding(
                "docs.placeholder-published", "Unfilled template brackets in a published document",
                "month",
                "A published legal document still contains template placeholders. Beyond looking "
                "unconsidered, it undermines the document's whole purpose: a policy that clearly "
                "nobody read is poor evidence that you understood and adopted the practices it "
                "describes, and it is the first thing an opposing party quotes.",
                "Fill every bracket, or delete the section it belongs to. A clause about something "
                "you do not do is a misrepresentation -- deleting it is the right answer more "
                "often than filling it.",
                "writing-policies.md", placeholders)

        # (c) A policy with no date, or one that has not been touched in a
        #     long time while the code kept moving.
        undated = [f for f in legal if not DATE_MARKER_RE.search(f.text[:2000])]
        if undated:
            self.add_finding(
                "docs.policy-undated", "Published document has no last-updated date", "know",
                "No 'last updated' or 'effective date' line was found near the top of "
                f"{', '.join('`' + f.path + '`' for f in undated[:4])}. Users and regulators both "
                "use that date to know which version of your practices they are reading, and "
                "you need it to show a material change was communicated before it took effect.",
                "Add a dated line near the top, and change it whenever the document changes.",
                "writing-policies.md",
                [Evidence(f.path, 1, "no last-updated line in the opening section") for f in undated])

        now = datetime.now(timezone.utc)
        for f in legal:
            marker = DATE_MARKER_RE.search(f.text[:2000])
            if not marker:
                continue
            when = parse_doc_date(marker.group(1))
            if not when:
                continue
            age = (now - when).days
            if age < STALE_AFTER_DAYS:
                continue
            self.add_finding(
                "docs.policy-stale", "Published document has not been updated in a long time",
                "know",
                f"`{f.path}` says it was last updated {when.date().isoformat()}, about "
                f"{age // 30} months ago. Documents do not go stale on a timer, but products "
                "change: a new analytics tool, a new AI feature, a new provider, a new country. "
                "Any of those makes the published text wrong without anyone editing it.",
                "Re-read it against the current data inventory. If it is still accurate, say so "
                "by bumping the date. If it is not, fix it and tell users about material changes.",
                "writing-policies.md",
                [Evidence(f.path, line_of(f.text, marker.start()), snippet(marker.group(0)))])

    # -- phase 4: synthesise document and mechanism findings ----------------

    def synthesise(self, secrets: list[Evidence]) -> None:
        docs = self.document_presence()
        mech = self.mechanisms()
        pii = self.signals_of("personal_data")
        services = self.signals_of("service")
        ai = self.signals_of("ai")
        payments = self.signals_of("payment")
        cookies = self.signals_of("cookie")
        third_party = [s for s in services if s.category not in {"database"}]
        high_risk = [s for s in pii if s.category == "special" or s.detail == "high risk"]

        if secrets:
            self.add_finding(
                "secret.exposed", "Credential material in the working tree", "blocking",
                "A value matching a credential format is sitting in the source. Treat it as compromised: "
                "anything that has been committed stays in the reflog and in every clone, and "
                "secret-scanning bots find keys in public repositories within minutes of a push.",
                "Rotate the key at the provider first -- deleting the line does not invalidate it. Then "
                "move it to an environment variable, confirm `.env` is gitignored, and purge the history "
                "if the repository is or will be public.",
                "security-baseline.md", secrets)

        if pii and "privacy" not in docs:
            self.add_finding(
                "docs.privacy-policy-missing", "Personal data is collected with no privacy policy", "blocking",
                f"The project handles {len(pii)} categor{'y' if len(pii) == 1 else 'ies'} of personal data "
                "and no privacy policy was found. A privacy notice is a precondition for lawful processing "
                "under GDPR Art. 13-14, required by every US state comprehensive privacy law, required "
                "under the Australian Privacy Act's APP 1, and required by both mobile app stores before a "
                "listing goes live. It is also the first document any integration partner or business "
                "customer asks for.",
                "Draft it from the data inventory rather than from a template's guesses: the actual "
                "categories, the actual purposes, the actual retention periods, the actual recipients.",
                "privacy-law.md",
                [e for s in pii[:4] for e in s.evidence[:1]])

        if payments and "terms" not in docs:
            self.add_finding(
                "docs.terms-missing-with-payments", "Taking money with no terms of service", "blocking",
                "A payment integration is present and no terms of service were found. Without terms there "
                "is no agreed refund policy, no limitation of liability, no chosen governing law and no "
                "stated right to suspend an abusive account. If billing recurs, several jurisdictions "
                "additionally require specific pre-purchase disclosure and a cancellation path at least as "
                "easy as the signup path.",
                "Write terms covering subscription mechanics, renewal and cancellation, refunds, acceptable "
                "use, suspension, liability and governing law -- then make the cancellation flow match what "
                "they promise.",
                "payments-and-billing.md",
                [e for s in payments[:3] for e in s.evidence[:1]])
        elif "terms" not in docs and (self.shape.web or self.shape.api or self.shape.mobile):
            self.add_finding(
                "docs.terms-missing", "No terms of service", "month",
                "No terms of service were found. Terms are what let you set acceptable use, disclaim "
                "warranties, cap liability, choose a governing law and terminate accounts that abuse the "
                "service. Without them, each of those is decided by whatever default the user's "
                "jurisdiction supplies.",
                "Draft terms proportionate to the product: a free read-only tool needs a page, anything "
                "with accounts, payments or user content needs more.",
                "user-content.md")

        if third_party and "subprocessors" not in docs:
            self.add_finding(
                "docs.subprocessors-missing", "No subprocessor list", "month",
                f"{len(third_party)} third-party services were detected in the code. Each one that receives "
                "personal data is a processor acting on your behalf, and transparency rules require you to "
                "disclose the categories of recipients -- naming them is the accepted way to do that. You "
                "will also need this list the first time a business customer sends you a DPA to sign.",
                "Publish `legal/subprocessors.md` naming each provider, what it is used for, what data it "
                "receives and where it processes. Keep it as a page you update, link it from the privacy "
                "policy, and offer notice before you add a new one.",
                "privacy-law.md",
                [Evidence(s.evidence[0].file, s.evidence[0].line, f"{s.name} -- {s.detail}")
                 for s in third_party[:MAX_EVIDENCE] if s.evidence])

        tracking = bool(self.services_in("analytics", "advertising")) or any(
            s.name in {"Google tag", "Meta Pixel", "document.cookie", "localStorage"} for s in cookies)
        if tracking and "cookies" not in docs:
            self.add_finding(
                "docs.cookie-policy-missing", "Trackers in use with no cookie policy or consent gate", "month",
                "Cookies, client-side storage or analytics tags are in use and no cookie policy was found. "
                "In the EU and UK, anything beyond strictly necessary storage needs informed consent "
                "*before* it is set: the ePrivacy rule bites on the act of storing or reading, whether or "
                "not the data is personal. A banner that fires the tag and then asks is the specific "
                "pattern regulators keep fining.",
                "List every cookie and storage key with its purpose and lifetime. If you serve the EU or "
                "UK, gate non-essential tags behind consent and make refusing exactly as easy as accepting.",
                "privacy-law.md",
                [s.evidence[0] for s in cookies[:MAX_EVIDENCE] if s.evidence])

        if ai:
            names = ", ".join(s.name for s in ai)
            self.add_finding(
                "ai.provider-disclosure", f"User data is sent to an AI provider ({names})", "month",
                "Calls to a hosted model API were found. Whatever context you pass -- user messages, "
                "uploaded documents, rows from your database -- leaves your infrastructure and becomes a "
                "cross-border transfer to a subprocessor most users have no idea is involved. 'We use AI' "
                "is not a disclosure.",
                "Name the provider in the privacy policy and the subprocessor list, say what is sent and "
                "why, check in the provider's own settings whether your data trains their models (the "
                "default differs between consumer and API tiers), and compare their retention window "
                "against what your policy promises.",
                "ai-features.md",
                [e for s in ai for e in s.evidence[:1]][:MAX_EVIDENCE])

        if pii and "deletion" not in mech:
            self.add_finding(
                "mechanism.deletion-missing", "No account or data deletion path", "month",
                "Personal data is stored and nothing in the code looks like a deletion route. Deletion on "
                "request is a right under GDPR Art. 17, under every US state comprehensive privacy law, and "
                "under APP 11.2 in Australia -- and both mobile app stores now require an in-app account "
                "deletion path for any app that lets people create an account. A policy that promises "
                "deletion with no mechanism behind it is the worst of both worlds: the obligation without "
                "the ability to meet it.",
                "Build a deletion endpoint that covers the primary database, uploaded files, backups, logs, "
                "caches and third-party copies (analytics, email, support tooling). Decide up front what "
                "you must keep for legal reasons, and say exactly that in the policy.",
                "privacy-law.md")

        if pii and "export" not in mech:
            self.add_finding(
                "mechanism.export-missing", "No data export path", "know",
                "No data export route was found. Portability is a right under GDPR Art. 20 and most US "
                "state laws, but the practical trigger is usually a support email rather than a regulator "
                "-- and hand-writing a database query every time does not scale past the first few.",
                "Add an export route returning the user's records in a structured, machine-readable format "
                "such as JSON or CSV.",
                "privacy-law.md")

        if "security" not in docs:
            self.add_finding(
                "docs.security-missing", "No vulnerability disclosure contact", "know",
                "There is no SECURITY.md or security.txt. When a researcher finds something, the absence of "
                "a named contact is what turns a quiet report into a public disclosure, or into an email to "
                "a support address that nobody reads for three weeks.",
                "Add `SECURITY.md` with a contact address, what is in scope, the response time you commit "
                "to, and whether you permit good-faith testing.",
                "security-baseline.md")

        if "license" not in docs:
            self.add_finding(
                "repo.license-missing", "No licence file", "know",
                "The repository has no licence. Under default copyright that means nobody may copy, modify "
                "or distribute the code -- including the contributor who wanted to send you a fix.",
                "Add a LICENSE file. MIT for maximum permissiveness, Apache-2.0 if you also want an express "
                "patent grant. If the code is deliberately not open, say so explicitly instead of leaving "
                "it ambiguous.",
                "security-baseline.md")

        if high_risk:
            names = ", ".join(sorted({s.name for s in high_risk}))
            self.add_finding(
                "risk.special-category", f"Possible high-risk data categories: {names}", "know",
                "Field names suggest data that carries obligations beyond the general privacy regime: "
                "special-category data under GDPR Art. 9, sector rules such as HIPAA or GLBA, biometric "
                "statutes such as Illinois BIPA (which carries a private right of action and per-scan "
                "damages), or children's data under COPPA and the age-appropriate design codes. These are "
                "the categories where a generated policy is not adequate.",
                "First confirm you actually hold this data -- field names lie in both directions. If you do, "
                "this is the part to take to a lawyer; the exposure is wildly out of proportion to the cost "
                "of one conversation.",
                "high-risk-categories.md",
                [e for s in high_risk for e in s.evidence[:1]][:MAX_EVIDENCE])

        uploads = self.services_in("storage")
        if uploads:
            self.add_finding(
                "content.user-uploads", "User file uploads are handled", "know",
                "File upload handling was detected. Accepting user content brings its own set of "
                "obligations: a notice-and-takedown path (and, in the US, a registered DMCA agent if you "
                "want to keep safe-harbour protection), a moderation policy, and metadata hygiene -- photos "
                "carry GPS coordinates and device identifiers in EXIF unless you strip them.",
                "Add takedown and acceptable-use terms, strip EXIF on upload, validate content types "
                "server-side rather than trusting the extension, and serve user files from a separate "
                "origin so a malicious upload cannot execute as your site.",
                "user-content.md",
                [s.evidence[0] for s in uploads[:3] if s.evidence])

        # Only worth tracking if there is something to track.
        if "compliance" not in docs and (pii or payments or self.shape.web):
            self.add_finding(
                "docs.compliance-missing", "No compliance checklist in the repo", "polish",
                "Nothing records what was decided, who owns it, or what should trigger another look. The "
                "obligations change when the product changes, and the change that matters is usually small "
                "enough that nobody thinks to revisit anything.",
                "Write `COMPLIANCE.md` with the open items, owners, dates and review triggers: a new "
                "third-party service, a new country, a paid tier, file uploads, an AI feature, a first "
                "enterprise customer.",
                "")


# --------------------------------------------------------------------------
# Reporting
# --------------------------------------------------------------------------

PREAMBLE = """\
> **What this scan is.** A pass over the source for signals that carry legal,
> privacy, security or launch obligations. It reports what the code shows.
>
> **What it is not.** Legal advice, and not an audit. It can tell you a document
> is *missing* -- that part is reliable. It cannot tell you that an existing
> document is *accurate*, that a consent banner actually blocks the tag it sits
> in front of, or that a deletion endpoint deletes everything it should.
> Anything reported as present still needs a human to read it.
"""


def scan_git_history(root: Path, limit: int) -> tuple[list[Evidence], str]:
    """Look for credential formats in added lines across recent history.

    Removing a key from the working tree does not remove it from the repo.
    It stays in the reflog and in every clone, which is exactly what the
    working-tree finding tells people -- so it is worth actually checking.

    Returns (evidence, note). The note explains any reason the scan could not
    run, so a missing git is reported rather than silently passing.
    """
    try:
        proc = subprocess.run(
            ["git", "-C", str(root), "log", f"-{limit}", "-p", "--no-color",
             "--no-merges", "--diff-filter=AM", "--unified=0"],
            capture_output=True, text=True, errors="replace", timeout=180,
        )
    except FileNotFoundError:
        return [], "git is not installed, so history was not scanned"
    except subprocess.TimeoutExpired:
        return [], "git log timed out, so history was not fully scanned"
    except OSError as exc:
        return [], f"git could not be run ({exc}), so history was not scanned"

    if proc.returncode != 0:
        detail = (proc.stderr or "").strip().splitlines()
        reason = detail[0] if detail else f"exit {proc.returncode}"
        return [], f"git log failed ({reason}), so history was not scanned"

    found: list[Evidence] = []
    seen: set[tuple[str, str]] = set()
    commit = ""
    path = ""
    for line in proc.stdout.splitlines():
        if line.startswith("commit "):
            commit = line[7:14]
            continue
        if line.startswith("+++ b/"):
            path = line[6:]
            continue
        if not line.startswith("+") or line.startswith("+++"):
            continue
        if PLACEHOLDER_FILE_RE.search(path) or LOCKFILE_RE.search(path):
            continue
        added = line[1:]
        if re.search(r"(?i)(example|placeholder|redacted|sample|fake|dummy)", added):
            continue
        for label, rx in SECRET_PATTERNS:
            m = rx.search(added)
            if not m:
                continue
            token = m.group(0)
            if label != "Private key block" and looks_like_placeholder(token):
                continue
            key = (label, token)
            if key in seen:
                continue
            seen.add(key)
            masked = token[:6] + "…" + token[-2:] if len(token) > 14 else token[:4] + "…"
            found.append(Evidence(path or "(unknown file)", 0,
                                  f"{label}: {masked} — added in commit {commit}"))
    return found, ""


@dataclass
class Diff:
    """What changed since a previous scan.

    The review triggers in COMPLIANCE.md are all of the form "re-run this when
    X changes". This is what makes that answerable: a new subprocessor since
    March is exactly the thing nobody notices.
    """
    baseline_date: str = ""
    baseline_project: str = ""
    new_findings: list[str] = field(default_factory=list)
    resolved_findings: list[str] = field(default_factory=list)
    new_services: list[str] = field(default_factory=list)
    removed_services: list[str] = field(default_factory=list)
    new_data: list[str] = field(default_factory=list)

    def any_change(self) -> bool:
        return bool(self.new_findings or self.resolved_findings or self.new_services
                    or self.removed_services or self.new_data)

    def as_dict(self) -> dict:
        return {
            "baseline_date": self.baseline_date,
            "baseline_project": self.baseline_project,
            "new_findings": self.new_findings,
            "resolved_findings": self.resolved_findings,
            "new_services": self.new_services,
            "removed_services": self.removed_services,
            "new_data": self.new_data,
        }


def compare_to_baseline(scan: Scan, path: Path) -> Diff | None:
    try:
        previous = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(f"scan.py: could not read baseline {path}: {exc}", file=sys.stderr)
        return None

    def names(payload: dict, kind: str) -> set[str]:
        return {s["name"] for s in payload.get("signals", []) if s.get("kind") == kind}

    old_findings = {f["id"] for f in previous.get("findings", [])}
    now_findings = {f.id for f in scan.findings}
    old_services = names(previous, "service")
    now_services = {s.name for s in scan.signals_of("service")}
    old_data = names(previous, "personal_data")
    now_data = {s.name for s in scan.signals_of("personal_data")}

    return Diff(
        baseline_date=previous.get("generated", "an earlier scan"),
        baseline_project=previous.get("project", ""),
        new_findings=sorted(now_findings - old_findings),
        resolved_findings=sorted(old_findings - now_findings),
        new_services=sorted(now_services - old_services),
        removed_services=sorted(old_services - now_services),
        new_data=sorted(now_data - old_data),
    )


def render_diff(diff: Diff) -> list[str]:
    out = [f"\n## Changes since {diff.baseline_date}\n"]
    if not diff.any_change():
        out.append("Nothing changed: same findings, same services, same data categories.\n")
        return out

    if diff.new_services:
        out.append(f"**{len(diff.new_services)} new third-party service(s):** "
                   + ", ".join(f"**{n}**" for n in diff.new_services) + "\n")
        out.append("Adding a service is a review trigger in its own right. Each one needs to "
                   "reach the subprocessor list and the privacy policy, and needs its data "
                   "processing agreement on file.\n")
    if diff.removed_services:
        out.append(f"**No longer detected:** {', '.join(diff.removed_services)}. If these are "
                   "genuinely gone, remove them from the published subprocessor list too -- "
                   "naming a recipient you no longer use is its own inaccuracy.\n")
    if diff.new_data:
        out.append(f"**New personal-data categories:** {', '.join(diff.new_data)}. Each needs a "
                   "purpose, a lawful basis and a retention period.\n")
    if diff.new_findings:
        out.append(f"**{len(diff.new_findings)} new finding(s):**\n")
        for fid in diff.new_findings:
            out.append(f"- `{fid}`")
        out.append("")
    if diff.resolved_findings:
        out.append(f"**{len(diff.resolved_findings)} finding(s) no longer reported:**\n")
        for fid in diff.resolved_findings:
            out.append(f"- `{fid}`")
        out.append("")
        out.append("_No longer reported is not the same as fixed -- a finding also disappears if "
                   "the code it pointed at was deleted, or if an ignore rule was added._\n")
    return out


def render_markdown(scan: Scan, generated: str, diff: Diff | None = None) -> str:
    counts = Counter(f.severity for f in scan.findings)
    out: list[str] = []
    a = out.append

    a(f"# Launch compliance scan: `{scan.display_path}`\n")
    a(f"_Generated {generated} by launch-compliance scan.py v{SCANNER_VERSION}. "
      f"{len(scan.files)} files scanned. Detected: {scan.shape.label()}._\n")
    a(PREAMBLE)

    if not scan.shape.web:
        a("\n> **No web surface detected**, so launch-readiness checks (social preview\n"
          "> tags, favicon, sitemap, canonical URLs) were skipped — they would be noise\n"
          "> for a library, CLI or API. If this project does serve pages and they were\n"
          "> skipped wrongly, that is a bug worth reporting.\n")

    a("\n## Summary\n")
    a("| Severity | What it means | Count |")
    a("| --- | --- | --- |")
    for sev in SEVERITIES:
        a(f"| **{SEVERITY_LABEL[sev]}** | {SEVERITY_BLURB[sev]} | {counts.get(sev, 0)} |")
    a("")
    if scan.suppressed:
        a(f"_{len(set(scan.suppressed))} finding type(s) suppressed by ignore rules: "
          f"{', '.join('`' + i + '`' for i in sorted(set(scan.suppressed)))}._\n")
    if diff is not None:
        out.extend(render_diff(diff))

    a("Each finding is tagged with how it was arrived at:\n")
    a("| Tag | Meaning |")
    a("| --- | --- |")
    for key in ("absence", "pattern", "inference"):
        a(f"| `{key}` | {BASIS_NOTE[key]} |")
    a("")

    if not scan.findings:
        a("Nothing matched the checks in this scanner. That is not the same as compliant -- "
          "it means none of the specific signals it looks for were present.\n")

    for sev in SEVERITIES:
        group = [f for f in scan.findings if f.severity == sev]
        if not group:
            continue
        a(f"\n## {SEVERITY_LABEL[sev]}\n")
        a(f"_{SEVERITY_BLURB[sev]}_\n")
        for f in group:
            a(f"### {f.title}\n")
            a(f"{f.detail}\n")
            a(f"**Fix.** {f.fix}\n")
            if f.fix_snippet:
                a("```")
                a(f.fix_snippet)
                a("```\n")
            if f.evidence:
                a("<details><summary>Where this showed up</summary>\n")
                a("```")
                for e in f.evidence[:MAX_EVIDENCE]:
                    a(f"{e.file}:{e.line}  {e.snippet}")
                if f.extra_evidence():
                    a(f"... and {f.extra_evidence()} more")
                a("```")
                a("</details>\n")
            meta = [f"`{f.id}`", f"basis: `{f.basis}`"]
            if f.reference:
                meta.append(f"reference: `references/{f.reference}`")
            a(f"<sub>{' &middot; '.join(meta)}</sub>\n")

    a("\n## What the code shows\n")
    a("Confirm every row below with whoever built the feature before it goes into a published "
      "document. The scanner sees imports and field names; it cannot see intent, and it cannot see "
      "anything configured in a dashboard rather than in the repository.\n")

    services = scan.signals_of("service")
    if services:
        a("\n### Third-party services (candidate subprocessors)\n")
        a("| Service | Category | Used for | Typically receives |")
        a("| --- | --- | --- | --- |")
        detected = {s.name for s in services}
        for svc in SERVICES:
            if svc["name"] in detected:
                a(f"| {svc['name']} | {svc['category']} | {svc['purpose']} | {svc['data']} |")
        a("")

    pii = scan.signals_of("personal_data")
    if pii:
        a("\n### Personal data found in schemas, forms and types\n")
        a("| Data | Category | First seen |")
        a("| --- | --- | --- |")
        for s in sorted(pii, key=lambda s: (s.category, s.name)):
            where = f"`{s.evidence[0].file}:{s.evidence[0].line}`" if s.evidence else "-"
            flag = " **(high-risk)**" if s.category == "special" or s.detail == "high risk" else ""
            a(f"| {s.name}{flag} | {s.category} | {where} |")
        a("")
        a("This is the raw material for a data inventory, not the inventory itself. For each row you "
          "still need: why it is collected, the lawful basis, where it is stored, how long it is kept, "
          "and who else can see it.\n")

    cookies = scan.signals_of("cookie")
    if cookies:
        a("\n### Cookies and client-side storage\n")
        for s in cookies:
            where = f"`{s.evidence[0].file}:{s.evidence[0].line}`" if s.evidence else ""
            a(f"- **{s.name}** -- {s.detail} {where}")
        a("")

    mech = scan.mechanisms()
    a("\n### Mechanisms the documents will have to promise\n")
    a("| Mechanism | Signal in the code |")
    a("| --- | --- |")
    for key, label in (("deletion", "Account / data deletion"),
                       ("export", "Data export"),
                       ("consent", "Consent gate"),
                       ("retention", "Retention / cleanup job")):
        hits = mech.get(key)
        if hits:
            a(f"| {label} | something matching at `{hits[0].file}:{hits[0].line}` -- read it, a "
              f"promising function name is not proof it is complete |")
        else:
            a(f"| {label} | nothing found |")
    a("")

    a("\n## Next\n")
    a("1. Confirm the inventory above with whoever built each feature. Scanners miss anything "
      "configured in a dashboard rather than in code.\n"
      "2. Work the blocking list first, then the monthly one. Resist the urge to start with the "
      "polish items because they are easy.\n"
      "3. Verify any threshold, deadline or fee before relying on it -- privacy law moves faster than "
      "any static reference, this one included.\n"
      "4. Re-run this when you add a third-party service, open to a new country, add a paid tier, add "
      "file uploads, add an AI feature, or sign a first enterprise customer.\n")
    return "\n".join(out) + "\n"


def render_stdout(scan: Scan, diff: Diff | None = None) -> str:
    counts = Counter(f.severity for f in scan.findings)
    lines = [f"launch-compliance scan of {scan.display_path} ({len(scan.files)} files)"]
    lines.append(f"  {scan.shape.label()}")
    lines.append("  " + ", ".join(f"{counts.get(s, 0)} {SEVERITY_LABEL[s].lower()}" for s in SEVERITIES))
    lines.append(f"  {len(scan.signals_of('service'))} third-party services, "
                 f"{len(scan.signals_of('personal_data'))} personal-data categories detected")
    if scan.suppressed:
        lines.append(f"  {len(set(scan.suppressed))} finding type(s) suppressed by ignore rules")
    blocking = [f for f in scan.findings if f.severity == "blocking"]
    if blocking:
        lines.append("")
        for f in blocking:
            lines.append(f"  BLOCKING  {f.title}")
    if diff is not None and diff.any_change():
        lines.append("")
        lines.append(f"  since {diff.baseline_date}:")
        if diff.new_services:
            lines.append(f"    + services: {', '.join(diff.new_services)}")
        if diff.removed_services:
            lines.append(f"    - services: {', '.join(diff.removed_services)}")
        if diff.new_data:
            lines.append(f"    + data: {', '.join(diff.new_data)}")
        if diff.new_findings:
            lines.append(f"    + {len(diff.new_findings)} new finding(s)")
        if diff.resolved_findings:
            lines.append(f"    - {len(diff.resolved_findings)} no longer reported")
    lines.append("")
    lines.append("  Absence is reliable; presence is not -- a document that exists may still be wrong.")
    return "\n".join(lines)


# --------------------------------------------------------------------------
# CLI
# --------------------------------------------------------------------------


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="scan.py",
        description="Scan a project for compliance, privacy, security and launch-readiness signals.",
        epilog="Exit codes: 0 clean, 2 triggered by --fail-on, 1 usage error. "
               "Not legal advice.",
    )
    parser.add_argument("path", help="project directory to scan")
    parser.add_argument("--out", metavar="FILE", help="write structured findings as JSON")
    parser.add_argument("--report", metavar="FILE", help="write a Markdown report")
    parser.add_argument("--quiet", action="store_true", help="suppress the stdout summary")
    parser.add_argument("--fail-on", choices=["secret", "blocking", "never"], default="secret",
                        help="what makes the exit code non-zero (default: secret)")
    parser.add_argument("--git-history", nargs="?", type=int, const=500, metavar="N",
                        help="also scan the last N commits (default 500) for credentials "
                             "that were committed and later removed. Requires git.")
    parser.add_argument("--baseline", metavar="FILE",
                        help="a previous --out JSON file; report what changed since it")
    parser.add_argument("--ignore", metavar="ID[:PATH]", action="append",
                        help="suppress a finding id, optionally only under a path prefix. "
                             "Repeatable. A .launch-compliance-ignore file in the scanned "
                             "project does the same thing, one rule per line.")
    parser.add_argument("--version", action="version", version=f"scan.py {SCANNER_VERSION}")
    args = parser.parse_args(argv)

    root = Path(args.path)
    if not root.is_dir():
        parser.error(f"not a directory: {args.path}")

    # The path is echoed exactly as typed so that committed sample output stays
    # machine-independent.
    display = args.path.replace("\\", "/").rstrip("/") or "."

    scan = Scan(root, display)
    scan.detect_project_shape()
    scan.detect_services()
    scan.detect_personal_data()
    scan.detect_storage()
    secrets = scan.detect_secrets()
    scan.detect_launch_readiness()
    scan.detect_accessibility()
    scan.detect_document_accuracy()

    if args.git_history:
        history, note = scan_git_history(root, args.git_history)
        if note:
            print(f"scan.py: {note}", file=sys.stderr)
        if history:
            scan.add_finding(
                "secret.in-history", "Credential material in git history", "blocking",
                f"Credential formats were found in added lines across the last "
                f"{args.git_history} commits. Removing a key from the working tree does not "
                "invalidate it: it stays in the reflog, in every clone, and in every fork, "
                "and on a public repository scanning bots find it within minutes of the push "
                "that introduced it. Treat every key below as compromised, including ones "
                "that look long gone.",
                "Rotate each key at the provider -- that is the step that actually fixes it. "
                "Rewriting history is optional and does not help on its own, because forks "
                "and cached views keep the old objects.",
                "security-baseline.md", history)
            secrets = secrets + history

    scan.synthesise(secrets)
    scan.apply_ignores(scan.load_ignores(args.ignore or ()))

    order = {sev: i for i, sev in enumerate(SEVERITIES)}
    scan.findings.sort(key=lambda f: (order[f.severity], f.id))

    generated = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    diff = compare_to_baseline(scan, Path(args.baseline)) if args.baseline else None

    if args.report:
        path = Path(args.report)
        if path.parent != Path(""):
            path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(render_markdown(scan, generated, diff), encoding="utf-8")

    if args.out:
        path = Path(args.out)
        if path.parent != Path(""):
            path.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "scanner_version": SCANNER_VERSION,
            "generated": generated,
            "project": display,
            "project_shape": scan.shape.as_dict(),
            "files_scanned": len(scan.files),
            "counts": {sev: sum(1 for f in scan.findings if f.severity == sev) for sev in SEVERITIES},
            "suppressed": sorted(set(scan.suppressed)),
            "diff": diff.as_dict() if diff else None,
            "findings": [f.as_dict() for f in scan.findings],
            "signals": [s.as_dict() for s in scan.signals],
            "caveat": ("Absence is reliable; presence is not. This tool reports signals found in "
                       "source code. It is not legal advice and it is not an audit."),
        }
        path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")

    if not args.quiet:
        print(render_stdout(scan, diff))

    if args.fail_on == "never":
        return 0
    if args.fail_on == "secret":
        return 2 if secrets else 0
    return 2 if any(f.severity == "blocking" for f in scan.findings) else 0


if __name__ == "__main__":
    sys.exit(main())
