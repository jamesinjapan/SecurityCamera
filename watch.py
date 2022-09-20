import os
import sys
import shutil
import glob
from pathlib import Path

from dotenv import load_dotenv

import ffmpeg
from datetime import datetime

import boto3

import logging

# Lock so only one job will run at any one time
lock_file = Path("lock.txt")
if lock_file.is_file():
    logging.warning("Exiting because earlier script is still running!")
    exit()
else: 
    lock_file.touch()
 
logfile_name = datetime.now().strftime("%Y%m%d")
logging.basicConfig(level=logging.INFO, filename=f"/home/james/Projects/SecurityCamera/logs/log_{logfile_name}.log")
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
        s3.upload_file(local_file, bucket, path_from_current_time(local_file), ExtraArgs={'ACL':'public-read'})
        logging.info(f"Upload Successful: {local_file}")
        return True
    except:
        logging.error(f"Error occurred in {local_file}: {sys.exc_info()}")
        return False


def convert_to_mp4(file = str) -> str: 
    filepath = Path(file)
    base_filename = filepath.stem + '.mp4'
    ffmpeg.input(file).filter('fps', fps=25, round='up').output(str(base_filename)).run()
    return str(filepath.rename(filepath.with_suffix('.mp4')))

try: 
    ftp_dir_path = '/home/james/FTP/camera/'
    failed_dir_path = '/home/james/FTP/failed/'
    files_to_upload = []
    files_to_delete = []

    logging.info(f'Checking files.')
    for file in glob.glob(ftp_dir_path + '**/*.*', recursive=True):
        logging.info(f'Checking file: {file}')
        if  Path(file).stat().st_size < (1024*100):
            logging.warn(f'File is too small, skipping: {file}')
            continue
        elif Path(file).suffix == '.265':
            logging.info(f'Converting {file}')
            old_file = file
            file = convert_to_mp4(old_file)
            files_to_delete.append(old_file)
        
        files_to_upload.append(file)
        files_to_delete.append(file)

    logging.info(f'Uploading files.')
    for file in files_to_upload:
        logging.info(f'Uploading file: {file}')
        uploaded = upload_to_aws(file)
        if not uploaded:
            logging.info(f"Failed to upload: {uploaded}")
            failed_filepath = failed_dir_path + path_from_current_time(file)
            shutil.move(file, failed_filepath)

    logging.info(f'Deleting uploaded files.')
    for file in files_to_delete:
        logging.info(f'Deleting file: {file}')
        path = Path(file)
        if path.is_file():
            path.unlink()
            logging.info(f"Deleted: {file}")

    logging.info(f'Deleting empty folders.')
    folders = list(os.walk(ftp_dir_path))[1:]
    for folder in folders:
        logging.info(f'Checking folder: {folder}')
        if not folder[1] and not folder[2]:
            os.rmdir(folder[0])
            
    logging.info(f'Deleting video tmp files.')
    current_dir = os.getcwd()
    files = os.listdir(current_dir)
    for file in files:
        if file.endswith('.mp4'):
            logging.info(f'Checking file: {file}')      
            os.remove(file)
except Exception as e:
    logging.error(f"Error encountered: {e}")
finally:
    lock_file.unlink()
    logging.info(f"Finished job: {datetime.now().isoformat()}")