# aibaba-shorts-pipeline

Cloud pipeline for AI BABA Shorts/Reels. Raw video (Google Drive) -> silence cut + zoom + audio cleanup ->
Hindi word-level transcript -> animated word-by-word captions + hook + CTA -> final MP4 back to Drive.

## Flow
1. Upload raw video to Drive: `AIBABA/inbox`
2. GitHub -> Actions -> **Process Short** -> Run workflow (works from the GitHub mobile app)
3. Get `AIBABA/outputs/<name>/<name>_final.mp4` + `transcript.txt`

## One-time setup
- Drive folders: `AIBABA/inbox`, `AIBABA/outputs`, `AIBABA/processed`
- Create an rclone remote named `gdrive` (OAuth) and paste the full `rclone.conf` content into
  repo Settings -> Secrets and variables -> Actions -> `RCLONE_CONF`. Never commit it.

## Security
- Manual trigger only; jobs run only for the repo owner.
- No secrets in code. Brand templates/prompts belong in a private repo or Drive.

## License
All rights reserved. No license is granted to copy or reuse this code.
