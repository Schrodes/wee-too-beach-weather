# Wee Too Beach — public weather dashboard

Public GitHub Pages version of the Version 10 dashboard. No indoor or sunroom readings are published.

## Setup
1. Upload the files and the `.github/workflows/update-weather.yml` workflow to your repository, preserving folder paths.
2. In repository **Settings → Secrets and variables → Actions**, create a repository secret named `THINGSPEAK_READ_API_KEY` containing the private ThingSpeak Read API key.
3. In **Settings → Actions → General → Workflow permissions**, select **Read and write permissions** (if available), then Save.
4. In **Actions → Update public weather data**, choose **Run workflow** to create the first public JSON files.
5. In **Settings → Pages**, choose **Deploy from a branch**, branch **main**, folder **/(root)**.
6. Visit `https://YOUR-USERNAME.github.io/wee-too-beach-weather/` after Pages publishes.

**Privacy:** Do not upload `server.py`, `.env` files, API keys, or the private Version 10 HTML. The weather JSON files are public. Do not make the ThingSpeak channel itself public.

**Notes:** Scheduled GitHub Actions can run late or be skipped. ThingSpeak history responses are capped at 8,000 entries, so 30-day history may be incomplete. The browser refreshes the published JSON, not ThingSpeak directly.
