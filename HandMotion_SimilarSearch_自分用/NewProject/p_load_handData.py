import glob
import csv
import os
import my_functions as my
import pandas as pd
import re
from tqdm import tqdm

# データ保存用クラス
class HandDataBase():
    def __init__(self):
        self.handData_df_dict = {}
        self.handDataName_list = []

    def load_data(self, dataPath):
        dataFile = os.path.basename(dataPath)
        handData_df = pd.read_csv(dataPath, header=0, index_col=0, dtype=str)
        dataFile_noneExt = os.path.splitext(dataFile)[0] # 拡張子なしのファイル名

        self.handData_df_dict[dataFile_noneExt]= handData_df
        self.handDataName_list.append(dataFile_noneExt)

    def load_data_all(self, dataDir):
        dataFile_list = os.listdir(dataDir)
        for dataFile in dataFile_list:
            dataPath = dataDir + dataFile
            handData_df = pd.read_csv(dataPath, header=0, index_col=0, dtype=str)
            dataFile_noneExt = os.path.splitext(dataFile)[0] # 拡張子なしのファイル名

            self.handData_df_dict[dataFile_noneExt]= handData_df
            self.handDataName_list.append(dataFile_noneExt)

def get_handDataBase(dataDir):
    dataBase = HandDataBase()

    dataBase.load_data_all(dataDir)
    #keyDataBase.load_data(testKeyFile)

    return dataBase

if __name__ == '__main__':
    testKeyDir = "handData/d3_feature/key/"
    testTgtDir = "handData/d3_feature/tgt/"

    testKeyFile = "handData/d3_feature/key/33.csv"
    testTgtFile = "handData/d3_feature/tgt/4.csv"

    keyDataBase = get_handDataBase(testKeyDir)
    tgtDataBase = get_handDataBase(testTgtDir)

    print(keyDataBase.handDataName_list)
    print(tgtDataBase.handDataName_list)