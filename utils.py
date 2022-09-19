import os

def get_suffix(file_name):
    return file_name.split(".")[-1]

def get_dir(file_path):
    return "/".join(file_path.split("/")[:-1])

def change_suffix(src_file,des_suffix):
    return src_file.replace(src_file.split(".")[-1],des_suffix)

def get_name(file_path):
    return file_path.split("/")[-1].split(".")[0]