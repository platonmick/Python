from pathlib import Path, PureWindowsPath
import hashlib
import json
import logging

def lowpriority():
    """ Set the priority of the process to below-normal."""

    import sys
    try:
        sys.getwindowsversion()
    except AttributeError:
        isWindows = False
    else:
        isWindows = True

    if isWindows:
        # Based on:
        #   "Recipe 496767: Set Process Priority In Windows" on ActiveState
        #   http://code.activestate.com/recipes/496767/
        import win32api,win32process,win32con

        pid = win32api.GetCurrentProcessId()
        handle = win32api.OpenProcess(win32con.PROCESS_ALL_ACCESS, True, pid)
        win32process.SetPriorityClass(handle, win32process.BELOW_NORMAL_PRIORITY_CLASS)
    else:
        import os
        os.nice(1)
        
from enum import IntEnum
class FileStatus(IntEnum):
    OK = 1
    MISSING = 2
    CORRUPT = 3
    UNKNOWN = 4

def init_logging():
    log = logging.getLogger('check_md5')
    log.setLevel(logging.INFO)

    fh = logging.FileHandler('checkmd5.log')
    fh.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    fh.setFormatter(formatter)

    ch = logging.StreamHandler()
    ch.setLevel(logging.WARNING)
    formatter = logging.Formatter('%(message)s')
    ch.setFormatter(formatter)

    log.addHandler(fh)
    log.addHandler(ch)
    return log

def check_md5(hash, filepath):
    md5 = hashlib.md5()
    if not isinstance(filepath, Path):
        filepath = Path(filepath)
    try:
        with filepath.open('rb') as file:
            chunksize = 2**16
            while True:
                chunk = file.read(chunksize)
                if not chunk:
                    break
                md5.update(chunk)
        log.info(str(filepath) + " md5: " + md5.hexdigest())
        return hash == md5.hexdigest()
    except:
        log.error("exception in check_md5()")
        return False    

    
def process_md5_file(md5file, dict):
    assert isinstance(md5file, Path), "md5file has to be an instance of pathlib.Path"
    dir = md5file.resolve().parent
    log.info("checking {}".format(str(md5file)))
    with md5file.open() as f:
        lines = f.read().splitlines()

    for line in lines:
        [hash, rel_path] = line.split(' *')
        rel_path = PureWindowsPath(rel_path)
        abs_path = dir / rel_path
        
        if hash not in dict:
            dict[hash] = []
        if str(abs_path) in [item[0] for item in dict[hash]]:
            #already checked
            continue
        elif not abs_path.is_file():
            status = FileStatus.MISSING
        elif check_md5(hash, abs_path):
            status = FileStatus.OK
        else:
            log.warning("corrupted file " + str(abs_path))
            status = FileStatus.CORRUPT
        dict[hash].append((str(abs_path), status))    


def report(dict):
    num_ok, num_corrupt, num_missing, num_duplicates = 0, 0, 0, 0

    for hash, list in dict.items():
        status = list[0][1]

        if status == FileStatus.OK:
            num_ok += 1
        elif status == FileStatus.CORRUPT:
            num_corrupt += 1
        elif status == FileStatus.MISSING:
            num_missing += 1
        
        if len(list) > 1:
            num_duplicates += 1
    
    log.info("")
    log.info("Report")
    log.info("======")
    log.info("")
    log.info("Hashes:         {}".format(len(dict)))
    log.info("Files OK:       {}".format(num_ok))
    log.info("Missing files:  {}".format(num_missing))
    log.info("Corrupted files:{}".format(num_corrupt))
    log.info("Duplicates:     {}".format(num_duplicates))

    if num_missing > 0:
        log.info("")
        log.info("Missing Files")
        log.info("=============\n")
        for e in sorted(missing_files(dict), key=lambda s: s.lower()):
            log.info("missing: " + e)

    if num_corrupt > 0:
        log.info("")
        log.info("Corrupted Files")
        log.info("===============\n")
        for e in sorted(corrupted_files(dict), key=lambda s: s.lower()):
            log.info("corrupted: " + e)

        log.info("")
        log.info("Rehashed Files")
        log.info("==============\n")
        for e in sorted(rehashed_files(dict), key= lambda s: s[0].lower()):
            log.info("rehashed: " + e[0])
            log.info("  Old:", e[1])
            log.info("  New:", e[2])
    
    log.info("")
    log.info("End of report")
    
    
def load_dictionary(json_file_name):
    p = Path(json_file_name)
    if not p.exists():
        return {}
    with p.open() as f:
        d = json.load(f)
    return d

def readFileLocations(file_list):
    with file_list.open() as f:
        l = f.read().splitlines()
    return [item for item in l if '@eaDir' not in item]


def unhashed_file_locations(d, list):
    hashed_locations = set([v[0][0] for v in d.values()])
    return [item for item in list if item not in hashed_locations]
    
def missing_files(d):
    return [v[0][0] for v in d.values() if v[0][1] == FileStatus.MISSING]
    

def duplicates(d):
    l = []
    for hash, list in d.items():
        if len(list) > 1:
            l.append(hash)
    return l
    
    
def update_dictionary_from_md5_files(dict, dirname):
    rootdir = Path(dirname)
    assert rootdir.exists(), "rootdir {} does not exist".format(dirname) 
    for md5file in rootdir.glob('**/*.md5'):
        process_md5_file(md5file, dict)


def chain(*iterables):
    for iterable in iterables: yield from iterable
    

def save_directory(dict, filename):
    with open(filename, 'w') as f:
        json.dump(dict, f, indent = 2)  


def corrupted_files(d):
    return [v[0][0] for v in d.values() if v[0][1] == FileStatus.CORRUPT]


def rehashed_files(d):
    rhf_list = []
    ok_dict = {d[k][0][0]: k 
                    for k in d.keys() 
                    if d[k][0][1] == FileStatus.OK}
    corrupt_dict = {d[k][0][0]: k 
                    for k in d.keys() 
                    if d[k][0][1] == FileStatus.CORRUPT}
    for file, hash in corrupt_dict.items():
        if file in ok_dict:
            rhf_list.append((file,hash, ok_dict[file]))
    return rhf_list

    
def converted_to_dng(l, dng_list):
    return [e for e in l if e.replace('.NEF', '.dng') in dng_list
                         or e.replace('.ORF', '.dng') in dng_list]
                         
def deleted_files(d, file_list):
    list(set(missing_files(d)) - set(converted_to_dng(missing_files(d), file_list)))

def cleanup(d):
    for k, v in list(d.items()):
        if v[0][1] != FileStatus.OK:
            del d[k]


def verify(d):
    for k, v in list(d.items()):
        if v[0][1] == FileStatus.OK:
            if not check_md5(k, v[0][0]):
                v[0][1] = FileStatus.CORRUPT


def write_md5_file(d, md5file_path, rootpath):
    list = []
    for hash, file_list in d.items():
        for file in file_list:
            if file[1] == FileStatus.OK:
               if rootpath.lower() in file[0].lower():
                    p = PureWindowsPath(file[0]).relative_to(Path(rootpath))
                    list.append((str(p), hash))
                    
    with Path(md5file_path).open('w') as f:
        for file in sorted(list, key=lambda s: s[0].lower()):
            f.write("{} *{}\n".format(file[1], file[0]))


def parse_commandline_args():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("rootdir", help="root directory")
    parser.add_argument("-v", "--verify", help="verify dictionary",
                        action="store_true")
    parser.add_argument("-u", "--update", help="update dictionary from md5 files",
                        action="store_true")
    return parser.parse_args()


log = init_logging()

if __name__ == "__main__":
    import sys
    args = parse_commandline_args()
    dict = load_dictionary('checkmd5.json')
    cleanup(dict)
#   lowpriority()

    if args.verify:
        verify(dict)

    if args.update:
        update_dictionary_from_md5_files(dict, args.rootdir)

    report(dict)
    write_md5_file(dict, 'out_checkmd5.md5', args.rootdir)
    save_directory(dict, 'out_checkmd5.json')
