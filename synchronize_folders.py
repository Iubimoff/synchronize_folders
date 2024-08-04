import os
import shutil
import time
import hashlib


def log_changes(message, file):
    with open(file, 'a') as f:
        f.write(message + '\n')
    print(message)


def make(path, log_file):
    os.makedirs(path)
    log_changes(f"Create directory {path}", log_file)


def copy(source_file, replica_file, log_file):
#    os.system(f'cp {source_file} {replica_file}')
    shutil.copy2(source_file, replica_file)
    log_changes(f"Copied {source_file} to {replica_file}", log_file)


def delete(path, log_file):
    try:
        os.rmdir(path)
        log_changes(f"Delete {path}", log_file)
    except OSError:
        try:
            os.remove(path)
            log_changes(f"Delete {path}", log_file)
        except OSError:
            log_changes(f"Error with delete {path}", log_file)

def calculate_md5(file_path):
    hash_md5 = hashlib.md5()
    with open(file_path, 'rb') as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()


def synchronize_folders(source, replica, log_file):
    # Synchronize folders
    for root, dirs, files in os.walk(source):
        source_tile = os.path.relpath(root, source)
        replica_path = os.path.join(replica, source_tile)

        if not os.path.exists(replica_path):
            make(replica_path, log_file)
            log_changes(f"Created directory: {replica_path}", log_file)

        for file in files:
            source_file_path = os.path.join(root, file)
            replica_file_path = os.path.join(replica_path, file)

            if not os.path.exists(replica_file_path) or calculate_md5(source_file_path) != calculate_md5(replica_file_path):
                copy(source_file_path, replica_file_path, log_file)


def check_replica_folder(source, replica, log_file):
    for root, dirs, files in os.walk(replica):
        replica_tile = os.path.relpath(root, replica)
        source_path = os.path.join(source, replica_tile)

        if not os.path.exists(source_path):
            delete(root, log_file)

        for file in files:
            replica_file = os.path.join(root, file)
            source_file = os.path.join(source_path, file)

            if not os.path.exists(source_file):
                delete(replica_file, log_file)

def main():
    args = input(
        "Enter origin path, replica path, log path, and interval (sec) separated by spaces "
        "(e.g., home/user/origin home/user/replica home/user/log_path.txt 10): ").split()

    while len(args) != 4:
        args = input("Invalid input. Enter 4 arguments (source, replica, log, interval):").split()

    source, replica, log_path, interval = args

    while not int(interval):
        interval = input("Invalid input. Interval must be integer. Enter interval (sec): ")

    for path in [source, replica, log_path]:
        if not os.path.exists(path):
            print(f'Error: {path} is not exist')
            return

    while True:
        synchronize_folders(source, replica, log_path)
        check_replica_folder(source, replica, log_path)
        time.sleep(int(interval))


if __name__ == '__main__':
    main()

