# Real-time live leaderboard for Super Smash Bros Ultimate

## Tools
- Nintendo Switch
- EVGA Capture Card
- Google Gemini 2.5 Pro
- Cloudflare R2 Storage (optional)

## How it works
Matches are automatically detected & recorded by a computer program connected to the capture card that is continuously monitoring the nintendo switch.
Once a match is finished, a clip showing the results screen is sent to Gemini 2.5 Pro to extract stats from, after which the leaderboard is updated based on the match's stats.

Match videos are stored locally and can optionally be uploaded to Cloudflare R2 bucket for cloud storage.

## Setup

### Required Environment Variables
Create a `.env` file in the root directory with the following variables:

```bash
# Google Gemini API Configuration
GEMINI_API_KEY=your_gemini_api_key_here

# Supabase Configuration
SUPABASE_URL=your_supabase_project_url
SUPABASE_SERVICE_ROLE_KEY=your_supabase_service_role_key
```

### Optional: Cloudflare R2 Storage
To enable cloud storage of match videos, add these variables to your `.env` file:

```bash
# Cloudflare R2 Storage Configuration (Optional)
R2_ACCOUNT_ID=your_cloudflare_account_id
R2_ACCESS_KEY_ID=your_r2_access_key_id
R2_SECRET_ACCESS_KEY=your_r2_secret_access_key
R2_BUCKET_NAME=your_r2_bucket_name
```

If R2 is not configured, videos will only be stored locally. The application will log a warning but continue to function normally.

### Database Migration
If you're upgrading from a previous version, run the SQL migration to add R2 URL columns to the matches table:

```sql
-- See migrations/add_r2_urls_to_matches.sql
ALTER TABLE matches
ADD COLUMN IF NOT EXISTS video_url TEXT,
ADD COLUMN IF NOT EXISTS result_screen_video_url TEXT,
ADD COLUMN IF NOT EXISTS frame_42_image_url TEXT;
```
