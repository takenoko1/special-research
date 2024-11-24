import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import matplotlib.cm as cm
import seaborn as sns#データの視覚化用
import pandas as pd#データ操作用
import numpy as np#データ操作用
import os
from tqdm import tqdm#進行状況バー表示用
import PySimpleGUI as sg#GUI作成用
import shutil#ファイル操作
import time#時間管理
import random


#my code
#import partial_match_DTW
import p_load_handData
import p_partial_match_DTW
import p_gui
import my_functions as my



class Search_shuwa():#手話の類似区間検索とその結果の視覚化を行うためのクラス
    def __init__(self):
        
        
        # set_values関数内で代入　>>>
        self.cost_TH_dict = {} # DTWの経路選択に使用
        self.weight_dict = {} # 合計スコア計算に使用
        self.feature_label_list = None # 特徴ラベル
        self.similar_sections_list = [] # 目視で求めた類似区間
        self.frame_TH = None # DTWの経路選択に使用
        self.output_dir = None # 出力用ディレクトリ
        self.keyDataBase = None # 単語データ保存
        self.tgtDataBase = None # 文章データ保存
        # <<<

        self.all_path_sect_cost_list = []
        self.keyName = None
        self.tgtName = None
        self.key_len = None
        self.tgt_len = None
        self.saveFile = None

        # select True or False
        self.isPlt_sections = True # DTW行列に類似区間を描画

        self.isSave_path = False # DTW行列を保存
        self.isSave_score = True # スコアデータを保存

        self.isShow_path = False # DTW行列を表示
        self.isShow_score = True # スコアデータを表示



    def set_values(self, cost_TH_file, weight_file, feature_label_file, similar_sections_file, keyDataDir, tgtDataDir):#指定されたファイルから各種設定値を読みこみ，クラス変数に設定する
        # コスト閾値
        values_dict = {}
        with open(cost_TH_file, "r") as f:
            for line in f:
                key, value = line.split(":")# 行をコロンで分割してキーと値に分ける
                values_dict[key] = float(value.strip()) # 改行コードを削除するためにstrip()を使う
        self.cost_TH_dict = values_dict
        
        # 重みデータ
        values_dict = {}
        with open(weight_file, "r") as f:
            for line in f:
                key, value = line.split(":")# 行をコロンで分割してキーと値に分ける
                values_dict[key] = float(value.strip()) # 改行コードを削除するためにstrip()を使う
        self.weight_dict = values_dict
        
        # 特徴ラベルリスト
        with open(feature_label_file, "r", encoding="utf-8") as f:
            self.feature_label_list = f.read().split('\n')


        # 類似区間リスト（目視で求めたやつをグラフに描画するのに用用いる）
        with open(similar_sections_file, "r") as f:
            for line in f.readlines():
                start, end = line.split(",")# 行をコロンで分割してキーと値に分ける
                self.similar_sections_list.append([int(start), int(end)]) # 改行コードを削除するためにstrip()を使う
        
        self.frame_TH = 10
        self.output_dir = "result/"

        my.printline("loading handData..")
        self.keyDataBase = p_load_handData.get_handDataBase(keyDataDir)
        self.tgtDataBase = p_load_handData.get_handDataBase(tgtDataDir)
        my.printline("completed")


    def save_dict(self):#コストしきい値とファイル名を保存
        # cost_TH_dict保存
        with open("result/values/cost_TH_dict.txt", "w") as f:
            for key, value in self.cost_TH_dict.items():
                f.write(f"{key}:{value}\n")
        
        with open("result/values/names.txt", "w") as f:
            f.write('key file : ' + str(self.keyName) + '\n')
            f.write('tgt file : ' + str(self.tgtName) + '\n')
    
    def calc_feature(self):
        # gui
        keyName, tgtName = p_gui.select_key_tgt(self.keyDataBase.handDataName_list, self.tgtDataBase.handDataName_list)
        featureLabel = p_gui.select_feature()

        partial_match_DTW = p_partial_match_DTW.Partial_match_DTW()

        # 指定手話のデータフレームをfloat型で取得
        keyData_df = self.keyDataBase.handData_df_dict[keyName].astype(float)
        tgtData_df = self.tgtDataBase.handData_df_dict[tgtName].astype(float)

        # 指定特徴のデータをリストとして取得
        keyData_feature = keyData_df[featureLabel].tolist()
        tgtData_feature = tgtData_df[featureLabel].tolist()

        self.key_len = len(keyData_feature)
        self.tgt_len = len(tgtData_feature)

        self.keyName = keyName
        self.tgtName = tgtName

        partial_match_DTW.set_values(keyData_feature, 
                                    tgtData_feature, 
                                    self.cost_TH_dict[featureLabel], 
                                    self.frame_TH)

        partial_match_DTW.create_matrix()
        
        path_list, path_sect_cost_list = partial_match_DTW.select_path()

        if path_sect_cost_list == []:
            my.printline("path is not founded")
        else:
            #self.print_path(path_sect_cost_list)
            self.plt_path(partial_match_DTW.costMatrix, 
                        path_list, path_sect_cost_list, 
                        featureLabel, 
                        keyData_feature, 
                        tgtData_feature)
        
        self.print_sect_score(path_sect_cost_list, featureLabel)

    def calc_shuwa(self):
    #GUIを使ってkeyDataとtgtDataを選択/各特徴ラベルについてDTWを計算し，経路とスコアを求める/結果をリストに保存し，進行状況バーを更新する
        # gui
        keyName, tgtName = p_gui.select_key_tgt(self.keyDataBase.handDataName_list, self.tgtDataBase.handDataName_list)
        # 指定手話のデータフレームをfloat型で取得
        keyData_df = self.keyDataBase.handData_df_dict[keyName].astype(float)
        tgtData_df = self.tgtDataBase.handData_df_dict[tgtName].astype(float)

        self.saveFile = "search_" + str(keyName) + "_from_" + str(tgtName)
        
        p_gui_progressBar = p_gui.ProgressBar()
        p_gui_progressBar.set_window(len(self.feature_label_list))

        for featureLabel in self.feature_label_list:
            partial_match_DTW = p_partial_match_DTW.Partial_match_DTW()


            # 指定特徴のデータをリストとして取得
            keyData_feature = keyData_df[featureLabel].tolist()
            tgtData_feature = tgtData_df[featureLabel].tolist()

            self.key_len = len(keyData_feature)
            self.tgt_len = len(tgtData_feature)

            self.keyName = keyName
            self.tgtName = tgtName

            partial_match_DTW.set_values(keyData_feature, 
                                        tgtData_feature, 
                                        self.cost_TH_dict[featureLabel], 
                                        self.frame_TH)

            partial_match_DTW.create_matrix()

            #########################
            ########################
            
            path_list, path_sect_cost_list = partial_match_DTW.select_path()[:20]

            self.all_path_sect_cost_list.append(path_sect_cost_list)


            self.plt_path(partial_match_DTW.costMatrix, 
                        path_list, path_sect_cost_list, 
                        featureLabel, 
                        keyData_feature, 
                        tgtData_feature)
            

            
            self.plt_path(partial_match_DTW.costMatrix, path_list, path_sect_cost_list, featureLabel, keyData_feature, tgtData_feature)

            # gui更新
            p_gui_progressBar.update_window()
    
    def print_sect_score(self, path_sect_cost_list, featureLabel):
        print(featureLabel + " >>>")
        for head, end, cost in path_sect_cost_list:
            score = self.cost_TH_dict[featureLabel] - cost
            print("range : {} ~ {}, score : {}".format(head, end, score))
        print("<<<")


    # パスをグラフに描画して表示
    def plt_path(self, list_2d, path_list, path_sect_cost_list, featureLabel, keyData, tgtData):

        # ウィンドウ横幅
        #aspectRatio = self.tgt_len/self.key_len # フレーム数に変動させる
        aspectRatio = 4

        graphWindowSizeBase = 5
        plt.figure(figsize=(graphWindowSizeBase*aspectRatio, graphWindowSizeBase)) # ウィンドウサイズ

        gs = gridspec.GridSpec(2, 2, width_ratios=[1, 5*aspectRatio], height_ratios=[5, 1]) # グラフの個数，サイズ定義
        ax1 = plt.subplot(gs[0])
        ax2 = plt.subplot(gs[1])
        ax4 = plt.subplot(gs[3])

        # ヒートマップ作成操作
        list_2d = np.transpose(list_2d) # 転置
        sns.heatmap(list_2d, square=False, cmap='Greys', xticklabels=50, yticklabels=50, cbar=False, ax=ax2)
        ax2.invert_yaxis()  # 上下反転

        
        # ヒートマップにパスを描画
        if not path_list == []:
            for i, path in enumerate(path_list):
                score = self.cost_TH_dict[featureLabel] - path_sect_cost_list[i][2]
                color = cm.Reds((score/self.cost_TH_dict[featureLabel])**3) # コストの値に応じて色変更
                path_np = np.array(path)
                ax2.plot(path_np[:,0], path_np[:,1], c=color)

        ax4.plot(tgtData)
        ax4.set_xlabel("$X$")

        ax1.plot(keyData, range(len(keyData)), c="C1")
        ax1.set_ylabel("$Y$")
        
        if self.isPlt_sections:
            self.plt_similar_section(ax2)

        if self.isSave_path:
            plt.savefig("result/path/" + featureLabel +'.png')

        if self.isShow_path:
            plt.show()
        
        plt.clf()
        plt.close()

    # 設定した類似区間に矢印を描画
    def plt_similar_section(self, ax):
        
        for start, end in self.similar_sections_list:
            '''
            section_list.append([int(head),int(end)])
            similar_sect_path = []
            for j in range(int(head), int(end)+1):
                similar_sect_path.append([0,j])
            similar_sect_path_np = np.array(similar_sect_path)
            ax.plot(similar_sect_path_np[:,1], similar_sect_path_np[:,0], c="b")
            '''
            arrow_props = dict(arrowstyle="->", mutation_scale=10, color="blue", linewidth=1)
            ax.annotate("", xy=[start, 0], xytext=[end-5, 0], arrowprops=arrow_props)
            ax.annotate("", xy=[end, 0], xytext=[start+5, 0], arrowprops=arrow_props)

    def plt_scoreData(self):
        #totalNum_frame_tgt = self.tgtDataBase.originallyTotalFrame_list[self.tgtDataNum]
        #print(self.tgtDataBase.handData_df_dict[self.tgtName].index.tolist())
        #tgtLen = len(self.tgtDataBase.handData_df_dict[self.tgtName].index.tolist())
    
        # all_path_sect_cost_listを展開，関節要素についてパスとスコアの情報を取得，時系列スコアデータを行列計算
        fig, ax = plt.subplots()

        self.plt_similar_section(ax)

        scoreM = np.zeros((self.tgt_len, len(self.all_path_sect_cost_list)), float)

        plt.xlabel("フレーム", fontname="MS Gothic", fontsize=14)
        plt.ylabel("スコア", fontname="MS Gothic", fontsize=14)
        #plt.tick_params(labelsize=12) #目盛文字サイズ

        for j, path_sect_cost_list in enumerate(self.all_path_sect_cost_list):
            #label = self.feature_labels[1+j]
            label = self.feature_label_list[j]
            weight = self.weight_dict[label]
            Reference_value = self.cost_TH_dict[label]
            for path_Xrange in path_sect_cost_list:
                
                path_head = path_Xrange[0]
                path_end = path_Xrange[1]
                path_cost = path_Xrange[2]

                #maxPathScore = (len_Y + ((path_end - path_head))) * MAX_DIST
                #maxPathScore =  (len_Y + (len_Y * 1.5)) * MAX_DIST

                path_score = (Reference_value - path_cost)*weight # スコアに変換（スコア : 値が大きいほど類似度高い）
                for i in range(path_head, (path_end)): # path_head ~ path_end の値をiに代入
                    if scoreM[i][j] == 0: # スコアが入ってなければスコアを代入
                        scoreM[i][j] = path_score
                    elif scoreM[i][j] < path_score: # すでにスコアが入っているなら比較して代入
                        scoreM[i][j] = path_score
        
        frame_nums = list(range(0, self.tgt_len))
        frame_score = np.sum(scoreM, axis=1)
        plt.plot(frame_nums, frame_score, c="r") # 点列(x,y)を黒線で繋いだプロット

        

        # 保存，出力の選択
        if self.isSave_score:
            plt.savefig(self.output_dir + self.saveFile + "_score.png")
        
        if self.isShow_score:
            plt.show()
        
        plt.clf()
        plt.close()


def main():
    # 平滑化前(平滑化を導入する前)
    #keyDataDir = "handData/key/d4_feature_d2/"
    #tgtDataDir = "handData/tgt/d4_feature_d2/"
    # 平滑化後
    keyDataDir = "handData/key/d4_feature_d3/"
    tgtDataDir = "handData/tgt/d4_feature_d3/"

    #keyDataDir = "handData_new/key/d3_feature"
    #tgtDataDir = "handData_new/tgt/d3_feature"

    cost_TH_file = "values/cost_TH_dict_high.txt"
    weight_file = "values/weight_LR_xW_yW.txt"
    feature_label_file="values/feature_label.txt"
    similar_sections_file = "similar_sections/tgt4_key95.txt"

    search_shuwa = Search_shuwa()
    search_shuwa.set_values(cost_TH_file,
                            weight_file,
                            feature_label_file,
                            similar_sections_file,
                            keyDataDir,
                            tgtDataDir)
    search_shuwa.calc_shuwa()
    #search_shuwa.calc_feature() # 特徴毎のパスなどを出力
    
    search_shuwa.plt_scoreData()


if __name__ == '__main__':
    #p_gui.select_feature()
    main()