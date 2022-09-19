import os
import pickle
from video_2_audio import extract_wav

if __name__ == "__main__":
    print("get the wav")
    
    list_path = "/dataset/5a175768/GeWu/ActivityNet/train/v1-3/train_val.pkl"
    src_dir = "/dataset/5a175768/GeWu/ActivityNet/train/v1-3"
    des_dir = "/dataset/5a175768/GeWu/ActivityNet/train/v1-3_frames"
    n_thread = 1
    
    extract_wav(src_dir,des_dir,list_path,n_thread)