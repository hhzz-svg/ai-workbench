# Cloudflare domain setup

`aihzcc.top` is the canonical custom domain for the AI Workbench landing page. The site is deployed by Cloudflare Pages from this repository.

## Current routing

- `aihzcc.top` -> Cloudflare Pages project `ai-workbench` (`ai-workbench-cvs.pages.dev`)
- `www.aihzcc.top` -> 301 redirect to `https://aihzcc.top/` through `landing-page/_redirects`
- Email Routing remains enabled through Cloudflare MX, SPF, DKIM, and DMARC records.

## Pages files

- `landing-page/index.html`: personal homepage and project hub.
- `landing-page/_redirects`: canonical redirect from `www` to apex.
- `landing-page/_headers`: static security headers for the landing page.

## Rollback

Revert the commit that changed the files above, then remove the custom domains or point the DNS CNAME records away from `ai-workbench-cvs.pages.dev` in Cloudflare if the domain should no longer serve this Pages project.
