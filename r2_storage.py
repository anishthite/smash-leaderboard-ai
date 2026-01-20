"""
Cloudflare R2 Storage Client for video uploads.

This module provides functionality to upload videos to Cloudflare R2 bucket.
R2 is S3-compatible, so we use boto3 for interaction.
"""

import os
import logging
from typing import Optional
import boto3
from botocore.exceptions import ClientError

logger = logging.getLogger(__name__)


class R2StorageClient:
    """Client for uploading videos to Cloudflare R2 bucket."""

    def __init__(self):
        """
        Initialize R2 storage client with credentials from environment variables.

        Required environment variables:
        - R2_ACCOUNT_ID: Cloudflare account ID
        - R2_ACCESS_KEY_ID: R2 access key ID
        - R2_SECRET_ACCESS_KEY: R2 secret access key
        - R2_BUCKET_NAME: R2 bucket name
        """
        self.account_id = os.getenv('R2_ACCOUNT_ID')
        self.access_key_id = os.getenv('R2_ACCESS_KEY_ID')
        self.secret_access_key = os.getenv('R2_SECRET_ACCESS_KEY')
        self.bucket_name = os.getenv('R2_BUCKET_NAME')

        # Check if R2 is configured
        if not all([self.account_id, self.access_key_id, self.secret_access_key, self.bucket_name]):
            logger.warning(
                "R2 storage not fully configured. Missing one or more environment variables: "
                "R2_ACCOUNT_ID, R2_ACCESS_KEY_ID, R2_SECRET_ACCESS_KEY, R2_BUCKET_NAME. "
                "Video uploads to R2 will be skipped."
            )
            self.enabled = False
            self.s3_client = None
        else:
            self.enabled = True
            # R2 endpoint format: https://<account_id>.r2.cloudflarestorage.com
            endpoint_url = f"https://{self.account_id}.r2.cloudflarestorage.com"

            self.s3_client = boto3.client(
                's3',
                endpoint_url=endpoint_url,
                aws_access_key_id=self.access_key_id,
                aws_secret_access_key=self.secret_access_key,
                region_name='auto'  # R2 uses 'auto' for region
            )
            logger.info(f"R2 storage client initialized for bucket: {self.bucket_name}")

    def upload_file(
        self,
        file_path: str,
        object_key: str,
        content_type: str = 'video/mp4',
        metadata: Optional[dict] = None
    ) -> Optional[str]:
        """
        Upload a file to R2 bucket.

        Args:
            file_path: Local path to the file to upload
            object_key: The key (path) to store the file under in R2
            content_type: MIME type of the file (default: video/mp4)
            metadata: Optional metadata dictionary to attach to the object

        Returns:
            Public URL of the uploaded file if successful, None otherwise
        """
        if not self.enabled:
            logger.debug(f"R2 storage disabled, skipping upload of {file_path}")
            return None

        if not os.path.exists(file_path):
            logger.error(f"File not found: {file_path}")
            return None

        try:
            extra_args = {
                'ContentType': content_type
            }

            if metadata:
                extra_args['Metadata'] = metadata

            logger.info(f"Uploading {file_path} to R2 as {object_key}")
            self.s3_client.upload_file(
                file_path,
                self.bucket_name,
                object_key,
                ExtraArgs=extra_args
            )

            # Generate public URL
            # Format: https://<bucket>.<account_id>.r2.cloudflarestorage.com/<key>
            public_url = f"https://{self.bucket_name}.{self.account_id}.r2.cloudflarestorage.com/{object_key}"

            logger.info(f"Successfully uploaded to R2: {public_url}")
            return public_url

        except ClientError as e:
            logger.error(f"Failed to upload {file_path} to R2: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error uploading {file_path} to R2: {e}")
            return None

    def upload_match_video(
        self,
        file_path: str,
        match_id: int,
        timestamp: str,
        participants: Optional[list] = None
    ) -> Optional[str]:
        """
        Upload a match video to R2 with appropriate naming and metadata.

        Args:
            file_path: Local path to the match video
            match_id: Database ID of the match
            timestamp: Timestamp string for the match
            participants: Optional list of participant names

        Returns:
            Public URL of the uploaded video if successful, None otherwise
        """
        # Create object key: matches/YYYY/MM/match_id-timestamp.mp4
        filename = f"{match_id}-{timestamp}.mp4"

        # Extract year and month from timestamp (format: YYYYMMDD_HHMMSS)
        year = timestamp[:4]
        month = timestamp[4:6]

        object_key = f"matches/{year}/{month}/{filename}"

        # Add metadata
        metadata = {
            'match-id': str(match_id),
            'timestamp': timestamp
        }

        if participants:
            metadata['participants'] = ','.join(participants)

        return self.upload_file(file_path, object_key, metadata=metadata)

    def upload_result_screen_video(
        self,
        file_path: str,
        match_id: int,
        timestamp: str
    ) -> Optional[str]:
        """
        Upload a result screen video to R2.

        Args:
            file_path: Local path to the result screen video
            match_id: Database ID of the match
            timestamp: Timestamp string for the match

        Returns:
            Public URL of the uploaded video if successful, None otherwise
        """
        # Create object key: result_screens/YYYY/MM/match_id-timestamp-result.mp4
        filename = f"{match_id}-{timestamp}-result.mp4"

        # Extract year and month from timestamp
        year = timestamp[:4]
        month = timestamp[4:6]

        object_key = f"result_screens/{year}/{month}/{filename}"

        metadata = {
            'match-id': str(match_id),
            'timestamp': timestamp,
            'type': 'result-screen'
        }

        return self.upload_file(file_path, object_key, metadata=metadata)

    def upload_frame_image(
        self,
        file_path: str,
        match_id: int,
        timestamp: str,
        frame_number: int = 42
    ) -> Optional[str]:
        """
        Upload a frame image (e.g., frame 42 for player identification) to R2.

        Args:
            file_path: Local path to the frame image
            match_id: Database ID of the match
            timestamp: Timestamp string for the match
            frame_number: Frame number (default: 42)

        Returns:
            Public URL of the uploaded image if successful, None otherwise
        """
        # Create object key: frames/YYYY/MM/match_id-timestamp-frame_XX.png
        filename = f"{match_id}-{timestamp}-frame_{frame_number}.png"

        # Extract year and month from timestamp
        year = timestamp[:4]
        month = timestamp[4:6]

        object_key = f"frames/{year}/{month}/{filename}"

        metadata = {
            'match-id': str(match_id),
            'timestamp': timestamp,
            'frame-number': str(frame_number)
        }

        return self.upload_file(file_path, object_key, content_type='image/png', metadata=metadata)
