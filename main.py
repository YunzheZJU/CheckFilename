# -*- coding: utf-8 -*-
import os
import time
import wave
import shutil


def make_dirs(paths):
    for path in paths:
        if not os.path.exists(path):
            os.mkdir(path)


# Check dictionary
str_time = time.strftime("%Y_%m_%d_%H_%M_%S", time.localtime())
dir_sample = os.path.join(os.path.abspath('.'), "sample")
dir_result = os.path.join(os.path.abspath('.'), "result")
dir_report = os.path.join(os.path.abspath('.'), "report")
dir_time = os.path.join(dir_report, str_time)
make_dirs([dir_sample, dir_result, dir_report, dir_time])

# Process within each week folder
weeks = os.listdir(dir_sample)
for str_week in weeks:
    print str_week + ": Processing..."
    status = {}
    dir_week = os.path.join(dir_sample, str_week)
    dir_week_result = os.path.join(dir_result, str_week)
    make_dirs([dir_week_result])

    # Read sid list
    with open("sid.txt", "r") as f:
        sids = f.readlines()
        for sid in sids:
            sid = sid.strip()
            status[sid] = {"status": "全部通过", "problems": []}
            str_sid_week = sid + "-" + str_week
            dir_sid = os.path.join(dir_week, str_sid_week)
            dir_sid_result = os.path.join(dir_week_result, str_sid_week)
            if os.path.exists(dir_sid):
                make_dirs([dir_sid_result])
                list_filename = os.listdir(dir_sid)
                # In case the folder is nested
                if len(list_filename) == 1 and sid + "-" + str_week in list_filename:
                    dir_sid = os.path.join(dir_sid, str_sid_week)
                    list_filename = os.listdir(dir_sid)
                for speed in ["F", "S", "N"]:
                    for num in range(6):
                        check_name = str_sid_week + "-" + speed + str(num + 1) + ".wav"
                        if check_name in list_filename:
                            file_path = os.path.join(dir_sid, check_name)
                            try:
                                wav_file = wave.open(file_path)
                                nChannels, depth, frequency = wav_file.getparams()[:3]
                                wav_file.close()
                                if nChannels == 1:
                                    if depth == 2:
                                        if frequency == 8000:
                                            # All OK! Move the file to result folder
                                            # print "Success: " + check_name
                                            shutil.copy(file_path, os.path.join(dir_sid_result, check_name))
                                            continue
                                        else:
                                            # Wrong Frequency
                                            # print "Failure: " + check_name + " with Frequency of " + str(frequency)
                                            status[sid]["problems"].append([speed + str(num + 1), "采样率非8000Hz"])
                                    else:
                                        # Wrong Depth
                                        # print "Failure: " + check_name + " with Depth of " + str(depth * 8)
                                        status[sid]["problems"].append([speed + str(num + 1), "位深度非16位"])
                                else:
                                    # Wrong nChannels
                                    if str_week in ['W1', 'W2', 'W3', 'W4'] and nChannels == 2:
                                        # Regard it as passed
                                        shutil.copy(file_path, os.path.join(dir_sid_result, check_name))
                                        continue
                                    else:
                                        # print "Failure: " + check_name + " with Channels of " + str(nChannels)
                                        status[sid]["problems"].append([speed + str(num + 1), "非单通道"])
                            except:
                                # print "Fail to open file: " + file_path
                                status[sid]["problems"].append([speed + str(num + 1), "无法读取"])
                        else:
                            # Miss file
                            # print "Failure: " + check_name + " Not Found"
                            status[sid]["problems"].append([speed + str(num + 1), "格式或命名错误"])
                        status[sid]["status"] = "存在错误"
            else:
                # Does not Exist
                status[sid]["status"] = "未提交"

    # Output results
    try:
        with open(os.path.join(dir_time, str_week + "-Result-" + str_time + ".txt"), "w") as f:
            f.write("学号\t提交状态\t通过数\t存在的问题\n")
            for sid in status.keys():
                m_status = status[sid]["status"]
                f.write(sid + "\t" + m_status + "\t")
                if m_status == "存在错误":
                    # Problem exists
                    f.write(str(18 - len(status[sid]["problems"])))
                    for problem in status[sid]["problems"]:
                        f.write("\t" + ": ".join(problem))
                f.write("\n")
    finally:
        if f:
            f.close()

    print str_week + ": Finished."
