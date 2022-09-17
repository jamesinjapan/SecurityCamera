import glob
from pathlib import Path
import ffmpeg

def convert_to_mp4(file):
    filepath = Path(file)
    filepath_after_move = filepath.rename(filepath.with_suffix('.mp4'))
    base_filename = filepath.stem + '.mp4'
    
    print(f'New file: {base_filename}')
    ffmpeg.input(file).filter('fps', fps=25, round='up').output(base_filename).run()
    
    print(f'Moving file: {filepath_after_move}')

ftp_dir_path = r'/home/james/FTP/camera/**/*.*'

for file in glob.glob(ftp_dir_path, recursive=True):
    if Path(file).suffix == '.265':
        print(f'Converting {file}')
        convert_to_mp4(file)
    
    print(f'Send {file}')
    
    # Send file to S3 bucket
    # Delete file if successfully uploaded, else skip and retry later.
