# Cloudflare Pages domain setup

This repository owns the AI Workbench project showcase page, not the personal portfolio homepage. The public showcase is deployed by Cloudflare Pages from `landing-page/`.

## Current routing

- Project showcase URL: `https://ai-workbench-cvs.pages.dev/`
- The Cloudflare Pages project name is `ai-workbench`.
- `aihzcc.top` and `www.aihzcc.top` may still be attached as Cloudflare custom domains at the account level, but the content served by this repository should remain the AI Workbench showcase unless a separate personal-homepage project is created.
- `www.aihzcc.top` currently has a Worker route `www.aihzcc.top/*` using Worker `aihzcc-www-redirect`, which returns a 301 redirect to `https://aihzcc.top/`.
- Email Routing remains enabled through Cloudflare MX, SPF, DKIM, and DMARC records.

## Pages files

- `landing-page/index.html`: AI Workbench project showcase page.
- `landing-page/_redirects`: backup canonical redirect rule for Pages-level routing.
- `landing-page/_headers`: static security headers for the landing page.

## Protection currently used

- Cloudflare Pages HTTPS certificate validation for attached hostnames.
- Cloudflare managed Free WAF and L7 DDoS managed rulesets visible on the zone.
- Static security headers through Pages `_headers`.
- Email Routing authentication records: MX, SPF, DKIM, and DMARC.

## Rollback

Revert the commit that changed the files above. If a separate personal homepage is needed later, create a new Pages project or Worker and bind `aihzcc.top` to that project instead of changing this repository's AI Workbench showcase page.
