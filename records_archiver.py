import os
import zipfile
import shutil
from datetime import datetime

# storage and archive paths
RECORDS_STORAGE_PATH = "D:\\Programming\\test tasks\\task\\storage\\"
RECORDS_ARCHIVE_PATH = "D:\\Programming\\test tasks\\task\\archive\\"
LOG_PATH = "D:\\Programming\\test tasks\\task\\"
# file extensions to be archived
RECORDS_FILES_EXTENSIONS = (".wav", ".mp3")
DISK_SPACE_LOW_LIMIT = 10


records = []
len_RECORDS_STORAGE_PATH = len(RECORDS_STORAGE_PATH)
current_date = datetime.today()

class Record():
    def __init__(self, name: str, path: str):
        self.name = name
        self.path = path
        self.creation_date = datetime.strptime(path[len_RECORDS_STORAGE_PATH:], "%Y\%m\%d")

def days_between(date_1: datetime, date_2: datetime) -> int:
    """
    returns the difference in days between two dates
    """
    return abs((date_2 - date_1).days)
            
def archive_record(record: Record) -> None:
    """
    archives the record and deletes the original file
    """
    os.chdir(record.path)
    new_dir_name = record.creation_date.strftime("%Y\\%m\\%d\\")
    if not os.path.exists(f"{RECORDS_ARCHIVE_PATH}{new_dir_name}"):
        os.makedirs(f"{RECORDS_ARCHIVE_PATH}{new_dir_name}")
    new_archive = zipfile.ZipFile(f"{RECORDS_ARCHIVE_PATH}{new_dir_name}{record.name}.zip", mode="w")
    new_archive.write(record.name)
    new_archive.close()
    os.remove(record.name)
    log(f"[ INFO ] records_archiver: record '{record.path}\{record.name}' has been archived")

def get_storage_free_space(storage_path: str) -> float:
    """
    return free space in percents of storage disk
    """
    os.chdir(storage_path)
    return round(shutil.disk_usage("/").free / shutil.disk_usage("/").total * 100, 2)

def log(message: str) -> None:
    """
    print message to terminal and write message to log.txt
    """
    print(message)
    with open(f"{LOG_PATH}log.txt", "a") as log_file:
        log_message = datetime.now().strftime("%Y.%m.%d, %H:%M:%S") + " " + message + "\n"
        log_file.write(log_message)

# getting records list
for root, _, files in os.walk(RECORDS_STORAGE_PATH):
    for file in files:
        if file.endswith(RECORDS_FILES_EXTENSIONS):
            try:
                records.append(Record(file, root))
            except:
                pass

# sorting records by date
records.sort(key=lambda r: r.creation_date, reverse=False)

# archive records
record_index = 0
if len(records) == 0:
    log(f"[ INFO ] records_archiver: no records")    
else:
    for record in records:
        if days_between(current_date, record.creation_date) > 90:
            archive_record(record)
            record_index += 1
        else:
            break

    if record_index == 0:
        log(f"[ INFO ] records_archiver: no records older 90 days")

# check disk space
storage_free_space = get_storage_free_space(RECORDS_STORAGE_PATH)
if storage_free_space < DISK_SPACE_LOW_LIMIT:
    log(f"[ WARNING ] records_archiver: storage free space is lower then {DISK_SPACE_LOW_LIMIT} % = {storage_free_space} %")
    if len(records) > 0:
        while storage_free_space < DISK_SPACE_LOW_LIMIT:
            archive_record(records[record_index])
            storage_free_space = get_storage_free_space(RECORDS_STORAGE_PATH)
            record_index += 1
            if record_index >= len(records):
                break
            if storage_free_space < DISK_SPACE_LOW_LIMIT:
                log(f"[ ALERT ] records_archiver: no more records to archive! \
                Storage free space is lower then {DISK_SPACE_LOW_LIMIT} % = {storage_free_space} %. Free up disk space!")  
    else:
        log(f"[ ALERT ] records_archiver: no more records to archive! \
                Storage free space is lower then {DISK_SPACE_LOW_LIMIT} % = {storage_free_space} %. Free up disk space!")      
else:
    log(f"[ INFO ] records_archiver: storage free space = {storage_free_space} %")
