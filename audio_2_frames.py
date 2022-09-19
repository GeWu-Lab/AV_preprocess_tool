from functools import partial
from multiprocessing import Pool
import os
import pickle
import utils
import librosa
import numpy as np

def wav_fixed(wav,des_time,sr):
    """
        最后不足1秒则重复最后的小于1秒的片段补齐
    """
    dst_s = int(des_time * sr)
    wav_len = len(wav)

    print("---- dst_s: %s, wav_len %s ----" % (dst_s, wav_len))
    last_s = wav_len % sr
    end = wav_len
    start = end - last_s
    if end == start:
        start = end - sr
    while len(wav) <= dst_s:
        wav = np.concatenate((wav, wav[start:end]), axis=0)
    wav = wav[0:dst_s]
    return wav

def audio_extract(data_path,src_dir,des_dir,sr,n_fft):
    audio_suffix = ["wav","flac"]
    if utils.get_suffix(data_path) not in audio_suffix:
        return
    file_dir = data_path.split(".")[0]

    audio_path = os.path.join(src_dir,file_dir)
    audio_path = os.path.join(audio_path,data_path)
    print(audio_path)
    if not os.path.exists(audio_path):
        print("the audio file {} does not exist".format(audio_path))
        return
    save_name = utils.change_suffix(data_path,"pkl")
    save_path = os.path.join(des_dir,save_name)
    save_dir = utils.get_dir(save_path)
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)


    wav, cur_sr = librosa.load(audio_path,sr)

    print("sr:",sr)
    wav_secs = len(wav) / sr
    print("-"* 10 + "wav_secs : " + str(wav_secs) + "-" * 10)

    wav = wav_fixed(wav,10,sr)

    #wav = wav_fixed(wav,round(wav_secs),sr)
    fixed_len = len(wav) / sr

    print("-"* 10 + "the fixed wav_secs : " + str(fixed_len) + "-" * 10)

    i = 0
    spec = np.abs(librosa.core.stft(wav,512,hop_length=440,window='hann',center=True,pad_mode='reflect'))
    print("-------------spec.shape:",spec.shape,"-------------\n")
    #mel = librosa.feature.melspectrogram(S = np.abs(spec),sr = sr,n_mels = 64,fmax = sr / 2)
    #log_mel = librosa.power_to_db(mel)
    #log_mel_T = log_mel.T.astype('float32')
    #print('--------------log_mel_T.shape :',log_mel_T.shape,'-----------\n')
    print(save_path)
    pickle.dump(spec,open(save_path,"wb"))

def extract_frames_from_wav(src_dir,des_dir,data_list_path,sr,n_fft,n_thread):
    data_list = pickle.load(open(data_list_path,"rb"))
    p = Pool(n_thread)
    print(len(data_list))
    worker = partial(audio_extract,src_dir = src_dir,des_dir = des_dir,sr = sr,n_fft = n_fft)
    p.imap_unordered(worker,data_list)
    p.close()
    p.join()