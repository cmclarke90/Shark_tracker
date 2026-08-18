# Shark Tracker Relay

A scheduled GitHub Action that fetches [OCEARCH](https://www.ocearch.org/)'s live shark-tracking feed, filters it down to the nearest few sharks to a fixed location, and commits the small result as `sharks_nearest.json`.

It exists because the source feed (served via Mapotic, behind Cloudflare) uses an ECDSA TLS certificate that some embedded/microcontroller devices can't negotiate a handshake with. This relay does the fetching and filtering on a normal machine, so any device that can do plain HTTPS can read the tiny output file from `raw.githubusercontent.com` instead of talking to the source feed directly. Built for [my PyPortal tide & shark display](https://github.com/cmclarke90/Tidal-Monitor-w-Nearby-Shark-Tracker), but the output is just JSON — usable from anything.

## Using this for your own location

1. **Fork this repo** (or copy `update_sharks.py` and `.github/workflows/update-sharks.yml` into your own).
2. Edit the `HOME_LAT` / `HOME_LON` constants near the top of `update_sharks.py` to your own coordinates.
3. On your fork, go to the **Actions** tab and enable workflows (GitHub disables them on forks by default).
4. Trigger it once manually — **Actions → Update nearest shark data → Run workflow** — rather than waiting for the daily schedule.
5. Once it succeeds, your filtered data is at:
   ```
   https://raw.githubusercontent.com/<your-username>/<your-repo>/main/sharks_nearest.json
   ```

## Output format

```json
[
  {
    "name": "Jason",
    "species": "White Shark",
    "distance": 95.9,
    "last_move": "2026-05-04T16:00:56Z",
    "age_days": 104
  }
]
```

Up to 5 entries, nearest first, limited to sharks with a ping in the last `MAX_PING_AGE_DAYS` (default 365 — most tagged sharks in the feed haven't reported in years, so without this cutoff "nearest" just means "nearest stale coordinate").

## Schedule

Runs daily via `cron` in `.github/workflows/update-sharks.yml`. GitHub auto-disables scheduled workflows after 60 days with no commits to the repo — since this workflow commits its own output daily, that shouldn't trigger under normal use.
