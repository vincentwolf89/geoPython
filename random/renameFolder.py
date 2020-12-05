import os

path = r"C:\Users\Vincent\Desktop\geomtoets_v1\geomtoetsV1_plots"     


directory_list = os.listdir(path)




for filename in directory_list:
    src = filename
    dst = filename.split("_")[0]

    # print(dst)

    os.rename(os.path.join(path, src), os.path.join(path, dst))

