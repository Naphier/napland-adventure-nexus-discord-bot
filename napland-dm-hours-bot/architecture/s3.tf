resource "aws_s3_bucket" "s3_naplanddnd" {
    bucket = var.bucket_name
    tags = {
        Name = "Napland DND",
        description = "Resources for Napland DND applications"
    }
}

resource "aws_s3_bucket_ownership_controls" "s3_naplanddnd_ownership" {
    bucket = aws_s3_bucket.s3_naplanddnd.bucket.id
    rule {
        object_ownership = "BucketOwnerPreferred"
    }
}

resource "aws_s3_bucket_acl" "s3_naplanddnd_acl" {
    depends_on = [ aws_s3_bucket_ownership_controls.s3_naplanddnd_ownership ]
    bucket = aws_s3_bucket.s3_naplanddnd.bucket.id
    acl = "private"
}

resource "aws_s3_lifecycle_configuration" "s3_naplanddnd_lifecycle" {
    bucket = aws_s3_bucket.s3_naplanddnd.bucket.id
    lifecycle_rule {
        status = "Enabled"
        id      = "napland-dnd-lifecycle-rule"
        transition {
            days          = 30
            storage_class = "INTELLIGENT_TIERING"
        }
        abort_incomplete_multipart_upload {
            days_after_initiation = 3
        }
    }
}

resource "aws_s3_object" "s3_naplanddnd_hours" {
    bucket = aws_s3_bucket.s3_naplanddnd.bucket
    key    = "dm-hours/data.csv"
    source = "resources/dm-hours-template.csv"
}