# -*- coding: utf-8 -*-
import os
import re
import time
import wave
import shutil

# Check dictionary
str_time = time.strftime("%Y_%m_%d_%H_%M_%S", time.localtime())
dir_sample = os.path.join(os.path.abspath('.'), "sample")
dir_failed = os.path.join(os.path.abspath('.'), "failed")
dir_report = os.path.join(os.path.abspath('.'), "report")
dir_time = os.path.join(dir_report, str_time)
if not os.path.exists(dir_sample):
    print "There is no folder named sample!"
    exit(0)
if not os.path.exists(dir_failed):
    os.mkdir(dir_failed)
if not os.path.exists(dir_report):
    os.mkdir(dir_report)
os.mkdir(dir_time)

# Process within each week folder
weeks = os.listdir(dir_sample)
for str_week in weeks:
    passed = []
    failed = {}
    failedFiles = []
    missing = []
    dictionary = {}
    dir_week = os.path.join(dir_sample, str_week)
    reg = r'^(31\d{8})-(' + str_week + ')-(F|N|S)([1-6]).wav$'
    re_filename = re.compile(reg)

    # Read sid list
    with open("sid.txt", "r") as f:
        sids = f.readlines()
        for sid in sids:
            dictionary[sid.strip()] = 18

    # File filter
    folders = os.listdir(dir_week)
    for folder in folders:
        dir_sid = os.path.join(dir_week, folder)
        files = os.listdir(dir_sid)
        if folder in files:
            dir_sid = os.path.join(dir_sid, folder)
            files = os.listdir(dir_sid)
        for filename in files:
            result = re_filename.match(filename)
            if (result is None) or (dictionary.get(result.group(1)) is None):
                failedName = str_week + "\\" + folder + "\\" + filename
                failedFiles.append(failedName)
                shutil.move(dir_sid + "\\" + filename, dir_failed + "\\" + failedName.replace("\\", "_"))
            else:
                dictionary[result.group(1)] -= 1

    # Sid filter
    for sid in dictionary.keys():
        if dictionary[sid] == 0:
            passed.append(sid)
        else:
            failed[sid] = [dictionary[sid], []]
            dir_sid = os.path.join(dir_week, sid + "-" + str_week)
            if os.path.exists(dir_sid):
                list_filename = os.listdir(dir_sid)
                # Check missing files
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

    # Output reports
    try:
        with open(dir_time + "\\" + str_week + "-Result-" + str_time + ".txt", "w") as f:
            f.write("Sid\tStatus\tMissing\n" + "\tPassed\n".join(passed))
            if passed:
                f.write("\tPassed\n")
            f.write("\tMissed\n".join(missing))
            if missing:
                f.write("\tMissed\n")
            for sid in failed.keys():
                f.write(sid + "\tFailed\t" + str(failed[sid][0]) + "\t" + "\t".join(failed[sid][1]) + "\n")
        with open(dir_time + "\\" + str_week + "-Report-" + str_time + ".log", "w") as f:
            f.write("These Sids are passed.\n=======================\n\n" + "\n".join(passed)
                    + "\n\n=======================\n")
            f.write("These Sids are missed.\n=======================\n\n" + "\n".join(missing)
                    + "\n\n=======================\n")
            f.write("These files are failed.\n=======================\n\n" + "\n".join(failedFiles)
                    + "\n\n=======================\n")
            f.write("These files are missed.\n=======================\n\n")
            for sid in failed.keys():
                f.write(sid + "\n" + "\n".join(failed[sid][1]) + "\n\n")
            f.write("\n\n=======================\n")
    finally:
        if f:
            f.close()
