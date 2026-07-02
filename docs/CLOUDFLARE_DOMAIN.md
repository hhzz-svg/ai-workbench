# Cloudflare domain setup

`aihzcc.top` is the canonical custom domain for the AI Workbench landing page. The site is deployed by Cloudflare Pages from this repository.

## Current routing

- `aihzcc.top` -> Cloudflare Pages project `ai-workbench` (`ai-workbench-cvs.pages.dev`)
- `www.aihzcc.top` -> Worker route `www.aihzcc.top/*` using Worker `aihzcc-www-redirect`, which returns a 301 redirect to `https://aihzcc.top/` while preserving the path and query string.
- Email Routing remains enabled through Cloudflare MX, SPF, DKIM, and DMARC records.

## Pages files

- `landing-page/index.html`: personal homepage and project hub.
- `landing-page/_redirects`: backup canonical redirect rule for Pages-level routing.
- `landing-page/_headers`: static security headers for the landing page.

## Cloudflare free protections currently used

- Proxied CNAME records for the apex and `www` hostnames.
- Cloudflare Pages HTTPS certificate validation for both hostnames.
- Cloudflare managed Free WAF and L7 DDoS managed rulesets visible on the zone.
- Static security headers through Pages `_headers`.
- Email Routing authentication records: MX, SPF, DKIM, and DMARC.

## Rollback

Revert the commit that changed the files above. If the domain should no longer serve this Pages project, remove the Pages custom domains and point the `aihzcc.top` / `www.aihzcc.top` CNAME records away from `ai-workbench-cvs.pages.dev`. If the `www` redirect should be removed, delete the Worker route `www.aihzcc.top/*` and the Worker `aihzcc-www-redirect`.
