# Deployment and cache configuration

`docs/` is the published site, served at **aiprogrammer.ai** by **Cloudflare Pages**
(project `aiprogrammer`, connected to this repo). Unmatched paths fall back to
`docs/index.html`, so a request for something that does not exist returns the landing
page with a 200 rather than a 404. Nothing outside `docs/` is served.

## Load-bearing setting: Browser Cache TTL — do not "tidy" it

There is deliberately **no `_headers` file in this repo.** Cache behaviour comes from a
zone setting instead:

> Cloudflare dashboard → **aiprogrammer.ai** → Caching → Configuration →
> **Browser Cache TTL = 4 hours**

That setting replaces the origin's `Cache-Control` on static assets, producing
`public, max-age=14400, must-revalidate`. The `must-revalidate` is the part that
matters — a deploy always reaches visitors after at most one revalidation, and the
edge revalidates too (`cf-cache-status: REVALIDATED`, verified 2026-08-21). HTML is
unaffected and stays `max-age=0, must-revalidate`.

**Changing Browser Cache TTL to "Respect Existing Headers" would break this.** With no
`_headers` file to fall back on, static assets would inherit Cloudflare Pages' own
default for non-HTML content — `public, s-maxage=604800`, a seven-day pin with **no
revalidation**. A CSS, JS or image update would then fail to reach anyone who had
visited in the previous week, and neither a targeted URL purge nor Purge Everything
reliably evicts it, because that layer sits above the zone cache. This is not
hypothetical: it happened on autocache.ai on 2026-08-20 and took a repo restructure to
resolve.

## If you ever do want per-path control

Do it in this order, or you will open the seven-day window described above:

1. Add `docs/_headers` with a safe default on `/*`
   (`Cache-Control: public, max-age=0, must-revalidate`) and longer TTLs opted in per
   path. Every override must start with `! Cache-Control` — Cloudflare Pages joins
   duplicate headers with a comma instead of letting the specific rule win, so without
   the detach a path emits two conflicting `max-age` values.
2. Deploy and confirm the headers are actually present at the origin.
3. Only then set Browser Cache TTL to **Respect Existing Headers**.

`autocache-site` and `Voice-Command` both use that `_headers` pattern and are worth
copying from.

## Related

GitHub Pages is also enabled on this repo (`main` / `docs`), but Cloudflare serves the
domain. Note that **GitHub Pages ignores `_headers` entirely** — it is a Cloudflare
Pages / Netlify convention — so a `_headers` file would have no effect on any
GitHub-Pages-served host.
