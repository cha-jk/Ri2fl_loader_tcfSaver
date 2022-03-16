from attr import attrs
import h5py
from pathlib import Path
from shutil import copy2
from multiprocessing import Pool
from copy import deepcopy

'''
def copy(path):
    dst = f"/data8/cils/result_tcf/{path.parts[3]}"
    copy2(path, dst)
'''
    
def get_attrs(h):
    for k, v in h.items():
        attrs = v.attrs
        print(k)
        for a, i in attrs.items():
            print(a, i)
            
            
def save(path):
    FL_DICT = {
        "CH0": "fl_mem",
        "CH1": "fl_act",
        "CH2": "fl_mito",
        "CH3": "fl_lipid",
        "CH4": "fl_nuc",
        "CH5": "fl_oli",
    }
    FL_ATTRS = dict(
        Channels=6,
        DataCount=1,
        SizeX=512,
        SizeY=512,
        SizeZ=64,
    )
   
    sort = path.parts[4]
    stem = path.stem
    print(path) #/tcf_root/ + *.TCF
    print(sort) #*.TCF
    print(stem) #*
    
    h5_path = f"/Users/jinkookcha/RI2FL/infer_2022TCF/{stem}.h5"      #output of infer  :  h5의 경로
    h5 = h5py.File(h5_path, "r")
    with h5py.File(path, "a") as h:
        if "3DFL" in list(h["Data"]):
            del h["Data/3DFL"]
        attrs_3d = h["Data/3D"].attrs
        res_xy = attrs_3d["SizeX"] / 512 * attrs_3d["ResolutionX"]
        res_z = attrs_3d["ResolutionZ"]
        offset_z = attrs_3d["SizeZ"] / 2 * res_z
        time_interval = attrs_3d["TimeInterval"]
        FL_ATTRS["ResolutionX"] = res_xy
        FL_ATTRS["ResolutionY"] = res_xy
        FL_ATTRS["ResolutionZ"] = res_z
        FL_ATTRS["OffsetZ"] = offset_z
        FL_ATTRS["TimeInterval"] = time_interval
        group_3dfl = h["Data"].create_group("3DFL")
        group_3dfl.attrs.update(FL_ATTRS)
        data_attrs = {
            k: v for k, v in h["Data/3D/000000"].attrs.items() if "RI" not in k
        }
        for tcf_ch, h5_ch in FL_DICT.items():
            group_ch = group_3dfl.create_group(tcf_ch)
            print("a")
            dataset = group_ch.create_dataset(
                "000000", data=((h5[h5_ch][()] * 255).astype("uint8"))
            )
            print((h5[h5_ch][()]*255).astype("uint8"))
            print("b")
            dataset.attrs.update(data_attrs)
        
            
if __name__ == "__main__":
    tcf_root = "/Users/jinkookcha/RI2FL/20220221ESCcropTCF"        #input of infer : TCF의 경로
    tcf_paths = list(Path(tcf_root).glob("*.TCF"))
    with Pool(50) as pool:
        pool.map(save, tcf_paths)
        
        
#tcf_root로부터 tcf_paths를 저장하고, map으로 save(tcf_paths)실행.
#save 메소드에서 파일이름(stem)을 이용해 h5_path/stem.h5 h5파일로부터 TCF를 업데이트한다.