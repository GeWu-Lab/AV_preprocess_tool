from video_2_frame import video_processing


if __name__=="__main__":
    print("deal with video")

    list_path = "vgg_test_data_list_name.pkl"
    src_dir = "/home/data/VGGsound/test-videos/test-set"
    des_dir = "/home/data/VGGsound_1fps/test"

    video_processing(src_dir,des_dir,list_path,process_count=8,fps_count=1)