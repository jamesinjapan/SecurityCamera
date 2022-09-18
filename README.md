# Security Camera Upload

## Description

I have a Raspberry Pi running an FTP server on my local network to receive images and videos from my security camera. This repo contains a python script to convert the `.265` video files into mp4 and then upload all the files from the camera to an S3 bucket.

Infrastructure for this project is maintained by Terraform.