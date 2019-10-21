import os
import shutil
import glob
import logging
#import sys
import time
import datetime
import config_indo as config


from inApp_review_analysis_1To1_ml_prod_indo import in_app_reviews_writeToES

logger = logging.getLogger(config.logger_description)
logger.setLevel(logging.INFO)
today = datetime.datetime.today().strftime('%Y%m%d')
handler = logging.FileHandler(config.prefix_log_file_name+today+'.log')
logger.info("Started running "+time.asctime( time.localtime(time.time())))
handler.setLevel(logging.INFO)

formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)

logger.addHandler(handler)

arch_dir=config.arch_dir
src_dir=config.source_dir

files = glob.glob(src_dir + '/*.csv')

print(files)
if len(files) == 0: #If no new files to process
    logger.warning('No new files to process!')
#    exit()

try:
    if not os.path.isdir(arch_dir):
        raise Exception('Archive directory does not exist!')
    for f in files:
        in_app_reviews_writeToES(f, logger)
        base, extension = os.path.splitext(f)
        head, base = os.path.split(base)
        dest = os.path.join(arch_dir, base + extension)
        shutil.move(f, dest) 
        logger.info("Completed running "+time.asctime( time.localtime(time.time())))
except Exception as ex:
    logger.error(ex)
#    exit()
    

logger.info('Files moved from source to archive.')
