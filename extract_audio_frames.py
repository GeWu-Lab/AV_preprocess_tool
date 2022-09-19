from audio_2_frames import extract_frames_from_wav

if __name__ == "__main__":
    list_path = "data_list.pkl"
    src_dir = "/home/data/Kinetics400_all/Kinetics400"
    des_dir = "/home/data/Kinetics400_audio"
    n_thread = 32
    sr = 44100
    n_fft = 512
    print("deal with audio frame")
    extract_frames_from_wav(src_dir,des_dir,list_path,sr,n_fft,n_thread)