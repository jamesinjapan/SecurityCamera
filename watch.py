import os
import shutil
import glob
from pathlib import Path

from dotenv import load_dotenv

import ffmpeg
from datetime import datetime

import boto3

import logging

logfile_name = datetime.now().strftime("%Y%m%d")
logging.basicConfig(level=logging.DEBUG, filename=f"/home/james/Projects/SecurityCamera/logs/log_{logfile_name}.log")
logging.info(f"Starting job: {datetime.now().isoformat()}")


load_dotenv()

def path_from_current_time(file = str) -> str:
    basename = os.path.basename(file)
    prefix = datetime.now().strftime("%Y/%m/%d/%H")
    return prefix + '/' + basename


def upload_to_aws(local_file = str) -> bool:
    s3 = boto3.client(
        's3', 
        aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
        aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
    )
    bucket = os.getenv('S3_BUCKET_NAME')
    
    try:
        s3.upload_file(local_file, bucket, path_from_current_time(local_file))
        logging.info(f"Upload Successful: {local_file}")
        return True
    except:
        logging.error(f"Error occurred! {local_file}")
        return False


def convert_to_mp4(file = str) -> str: 
    filepath = Path(file)
    base_filename = filepath.stem + '.mp4'
    ffmpeg.input(file).filter('fps', fps=25, round='up').output(base_filename).run()
    return filepath.rename(filepath.with_suffix('.mp4'))


ftp_dir_path = '/home/james/FTP/camera/'
failed_dir_path = '/home/james/FTP/failed/'
files_to_upload = []
files_to_delete = []

for file in glob.glob(ftp_dir_path + '**/*.*', recursive=True):
    if Path(file).suffix == '.265':
        logging.info(f'Converting {file}')
        old_file = file
        file = convert_to_mp4(old_file)
        files_to_delete.append(old_file)
    
    files_to_upload.append(file)
    files_to_delete.append(file)

for file in files_to_upload:
    uploaded = upload_to_aws(file)
    if not uploaded:
        failed_filepath = failed_dir_path + path_from_current_time(file)
        shutil.move(file, failed_filepath)

for file in files_to_delete:
    os.remove(file)
    logging.info(f"Deleted: {file}")

# Clean up empty folders
folders = list(os.walk(ftp_dir_path))[1:]
for folder in folders:
    print(folder)
    if not folder[1] or folder[2]:
        os.rmdir(folder[0])
        

# Clean up ffmpeg's mess
current_dir = os.getcwd()
files = os.listdir(current_dir)
for file in files:
    if file.endswith('.mp4'):
        os.remove(file)

        