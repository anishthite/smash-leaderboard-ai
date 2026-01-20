-- Add R2 storage URL fields to matches table
-- These fields store the Cloudflare R2 URLs for match videos and related media

ALTER TABLE matches
ADD COLUMN IF NOT EXISTS video_url TEXT,
ADD COLUMN IF NOT EXISTS result_screen_video_url TEXT,
ADD COLUMN IF NOT EXISTS frame_42_image_url TEXT;

-- Add comments to document the columns
COMMENT ON COLUMN matches.video_url IS 'Cloudflare R2 URL for the full match video';
COMMENT ON COLUMN matches.result_screen_video_url IS 'Cloudflare R2 URL for the result screen video clip';
COMMENT ON COLUMN matches.frame_42_image_url IS 'Cloudflare R2 URL for the frame 42 screenshot (used for player identification)';
