import os
import pickle
import multiprocessing
import logging
import time
import sys
from functools import partial
from moviepy.editor import VideoFileClip,concatenate_videoclips
import utils
import h5py
import cv2
import shutil
import numpy as np
import glob
# save log
def log_config(logger=None, file_name="log"):
    if logger is None:
        logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    if not os.path.exists("log"):
        os.makedirs("log")
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(name)s - %(message)s')
    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(logging.INFO)
    ch.setFormatter(formatter)
    logger.addHandler(ch)
    if file_name is not None:
        fh = logging.FileHandler("log/%s-%s.log" % (file_name, time.strftime("%Y-%m-%d")), mode='a')
        fh.setLevel(logging.DEBUG)
        fh.setFormatter(formatter)
        logger.addHandler(fh)
    return logger

logger = log_config()


def read_frame(reader, pos):
    if not reader.proc:
        reader.initialize()
        reader.pos = pos
        reader.lastread = reader.read_frame()

    if pos == reader.pos:
        return reader.lastread
    elif (pos < reader.pos) or (pos > reader.pos + 100):
        reader.initialize()
        reader.pos = pos
    else:
        reader.skip_frames(pos - reader.pos - 1)
    result = reader.read_frame()
    reader.pos = pos
    return result


def extract_frames(src_file_path,save_path,fps_count):
    """
        将视频保存成对应总长度的pickle文件，如果需要其中部分，可以再写函数截取
    """

    with VideoFileClip(src_file_path) as clip:
        # 保存的路径和地址
        filename = utils.get_name(save_path)
        save_path = utils.change_suffix(save_path,"hdf5")
        
        save_dir = os.path.join(utils.get_dir(save_path), filename)
        # 已经处理过就跳过

        if os.path.exists(save_path):
            return
        if not os.path.exists(save_dir):
            os.makedirs(save_dir)


        reader = clip.reader
        fps = clip.reader.fps
        total_frames = reader.nframes
        last_frames = int(total_frames % fps) if int(total_frames % fps)!= 0 else int(fps)
        last_start = total_frames - last_frames

        video_len = round(total_frames/fps)

        # 获得对应时间片段上的帧
        save_frames_index_arr = []
        for i in range(video_len):
            absolute_frame_pos = round((1 / (2*fps_count) + i / fps_count) * fps)
            if absolute_frame_pos > total_frames:
                relative_frame_pos = last_start + 1 + ((absolute_frame_pos - last_start - 1) % last_frames)
            else:
                relative_frame_pos = absolute_frame_pos
            print("--------relative_frame_pos: ",relative_frame_pos,'---------------')

            save_frames_index_arr.append(relative_frame_pos)



        loop_arr = list(set(save_frames_index_arr))
        loop_arr.sort()
        for time_idx,i in enumerate(loop_arr):
            image = read_frame(reader,i)
            image = image[:,:,::-1]
            pic_path = os.path.join(save_dir,str(time_idx).rjust(5,"0") + ".jpg")
            cv2.imwrite(pic_path,image)
            
        # 保存文件路径

        pics = glob.glob(os.path.join(save_dir,"*.jpg"))

        with h5py.File(save_path, 'w') as f:
            dtype = h5py.special_dtype(vlen='uint8')
            video = f.create_dataset('video',
                                    (len(list(pics)),),
                                    dtype=dtype)

        for i, file_path in enumerate(sorted(pics)):
            with open(file_path,'rb') as f:
                data = f.read()

            with h5py.File(save_path, 'r+') as f:
                video = f['video']
                video[i] = np.frombuffer(data, dtype='uint8')
    print(save_dir)
    shutil.rmtree(save_dir)


def deal_video(data_path,src_path,des_path,fps_count):
    file_path = os.path.join(src_path,data_path)
    if not os.path.exists(file_path):
        logger.warning("the file path : {} does not exist".format(file_path))
    else:
        print("-"* 10 + "deal with the video " + data_path + "-" * 10)
        # 保存的文件路径
        save_path = os.path.join(des_path,data_path)
        extract_frames(file_path,save_path,fps_count)

        pass


def deal_videos(src_path,des_path,data_list,fps_count,pool):
    """
        分发任务给各个线程，处理单独的视频文件
    """
    worker_deal_single_video = partial(deal_video,src_path=src_path,\
        des_path = des_path,fps_count = fps_count)
    print(worker_deal_single_video)
    print("the length of data_list is ",len(data_list))
    pool.imap_unordered(worker_deal_single_video,data_list)
    pool.close()
    pool.join()


def video_processing(src_path,des_path,data_list_path,process_count=1,fps_count=1):
    """
        入口函数，定义一些基本配置信息，为方便适应不同格式，需要用户事先生成list存放文件路径
    """
    cpu_count = multiprocessing.cpu_count()
    if process_count == 0:
        process_count = cpu_count * 2 + 1

    pool = multiprocessing.Pool(process_count)
    logger.info("cpu count is {}, create {}, process pool".format(cpu_count, process_count))

    data_list = pickle.load(open(data_list_path,"rb"))
    deal_videos(src_path,des_path,data_list,fps_count,pool)