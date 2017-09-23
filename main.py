# -*- coding: utf-8 -*-
import os
import re
import time
import shutil

# Check dictionary
dir_sample = os.path.join(os.path.abspath('.'), "sample")
dir_failed = os.path.join(os.path.abspath('.'), "failed")
dir_log = os.path.join(os.path.abspath('.'), "log")
if not os.path.exists(dir_sample):
    print "There is no folder named sample!"
    exit(0)
if not os.path.exists(dir_failed):
    os.mkdir(dir_failed)
if not os.path.exists(dir_log):
    os.mkdir(dir_log)

# Process within each week folder
weeks = os.listdir(dir_sample)
for str_week in weeks:
    reg = r'^(31\d{8})-(' + str_week + ')-(F|N|S)([1-6]).wav$'
    re_filename = re.compile(reg)
    dictionary = {}
    passed = []
    failed = {}
    missing = []
    dir_week = os.path.join(dir_sample, str_week)

    # Read sid list
    with open("sid.txt", "r") as f:
        sids = f.readlines()
        for sid in sids:
            dictionary[sid.strip()] = 18

    # File filter
    folders = os.listdir(dir_week)
    for sidfolder in folders:
        dir_sid = os.path.join(dir_week, sidfolder)
        files = os.listdir(dir_sid)
        if sidfolder in files:
            dir_sid = os.path.join(dir_sid, sidfolder)
        files = os.listdir(dir_sid)
        for filename in files:
            result = re_filename.match(filename)
            if (result is None) or (dictionary.get(result.group(1)) is None):
                shutil.move(dir_sid + "\\" + filename, dir_failed + "\\" + str_week + "_" + sidfolder + "_" + filename)
            else:
                dictionary[result.group(1)] -= 1

    # Sid filter
    for sid in dictionary.keys():
        if dictionary[sid] == 0:
            passed.append(sid)
        else:
            failed[sid] = [dictionary[sid], []]

    # Check missing files and sids
    for sid in failed.keys():
        dir_sid = os.path.join(dir_week, sid + "-" + str_week)
        if os.path.exists(dir_sid):
            list_filename = os.listdir(dir_sid)
            # Make checklist
            checklist = []
            for speed in ["F", "S", "N"]:
                for num in range(6):
                    checklist.append(sid + "-" + str_week + "-" + speed + str(num + 1) + ".wav")
            for name in checklist:
                if name not in list_filename:
                    failed[sid][1].append(name)
        else:
            failed.pop(sid)
            missing.append(sid)

    # Output results and logs
    currenttime = time.strftime("-%Y_%m_%d_%H_%M_%S", time.localtime())
    try:
        with open(dir_log + "\\" + str_week + "-result" + currenttime + ".txt", "w") as f:
            f.write("Sid\tStatus\tMissing\n" + "\tPassed\n".join(passed))
            if passed:
                f.write("\tPassed\n")
            f.write("\tMissed\n".join(missing))
            if missing:
                f.write("\tMissed\n")
            for sid in failed.keys():
                f.write(sid + "\tFailed\t" + str(failed[sid][0]) + "\t" + "\t".join(failed[sid][1]) + "\n")
        with open(dir_log + "\\" + str_week + "-passedsids" + currenttime + ".log", "w") as f:
            f.write("\n".join(passed))
        with open(dir_log + "\\" + str_week + "-missingsids" + currenttime + ".log", "w") as f:
            f.write("\n".join(missing))
        with open(dir_log + "\\" + str_week + "-failedfiles" + currenttime + ".log", "w") as f:
            f.write("\n".join(os.listdir(dir_failed)))
        with open(dir_log + "\\" + str_week + "-missingfiles" + currenttime + ".log", "w") as f:
            for sid in failed.keys():
                f.write(sid + "\n" + "\n".join(failed[sid][1]) + "\n\n")
    finally:
        if f:
            f.close()
