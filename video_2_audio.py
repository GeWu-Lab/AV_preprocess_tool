import os
from multiprocessing import Pool
from functools import partial
import subprocess
import utils
import pickle

def extract_wav_from_video(file_name,src_video_path,des_audio_path):
    audio_file_name = utils.change_suffix(file_name,"wav") 
    audio_path = os.path.join(des_audio_path,audio_file_name)
    # 已经处理过就跳过
    if os.path.exists(audio_path):
        return
    
    video_path = os.path.join(src_video_path,file_name)
    video_suffix = ["mp4","mkv"]
    if not os.path.exists(video_path):
        print("the video {} does not exist".format(video_path))
    
    # 判断源文件是不是视频文件
    if video_path.split(".")[-1] not in video_suffix:
        print("the file {} is not video".format(video_path))
        return 
    
    audio_dir = utils.get_dir(audio_path)
    if not os.path.exists(audio_dir):
        os.makedirs(audio_dir)
    
    print("extract the wav file {} from the video file {}".format(audio_path,video_path))
    
    strcmd = "ffmpeg -i " + video_path + " -f wav " + audio_path
    subprocess.call(strcmd,shell=True)
    
def extract_wav(src_dir,des_dir,data_list_path,n_thread = 1):
    
    data_list = pickle.load(open(data_list_path,"rb"))
    worker = partial(extract_wav_from_video,\
        src_video_path=src_dir,des_audio_path=des_dir)
    p = Pool(n_thread)
    p.imap_unordered(worker,data_list)
    p.close()
    p.join()