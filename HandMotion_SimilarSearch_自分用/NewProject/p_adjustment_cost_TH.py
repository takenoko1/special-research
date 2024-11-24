import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.cm as cm
import seaborn as sns
import pandas as pd
import numpy as np
import os
from tqdm import tqdm
import PySimpleGUI as sg
import shutil
import time
import copy
import random


# my code
#import partial_match_DTW
import p_load_handData
import p_partial_match_DTW
import p_gui
import my_functions as my


class Search_shuwa():
    def __init__(self):
        self.keyDataBase = None
        self.tgtDataBase = None
        self.output_dir = None
        self.cost_TH_dict = {}
        self.weight_dict = {}
        self.frame_TH = 10
        self.feature_label_list = None
        self.all_path_sect_cost_list = []

        self.keyName = None
        self.tgtName = None
        self.key_len = None
        self.tgt_len = None

        self.similar_sections_list = []
        self.saveFile = None

        # select True or False
        self.isPlt_sections = True # DTW行列に類似区間を描画

        self.isSave_path = False # DTW行列を保存
        self.isSave_score = False # スコアデータを保存

        self.isShow_path = True # DTW行列を表示
        self.isShow_score = False # スコアデータを表示

    def set_values(self, cost_TH_file, weight_file, keyDataDir, tgtDataDir):
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
        with open("values/feature_label.txt", "r", encoding="utf-8") as f:
            self.feature_label_list = f.read().split('\n')


        self.similar_sections_file = "similar_sections/tgt4_key33.txt"
        # 類似区間リスト（目視で求めたやつをグラフに描画するのに用用いる）
        with open(self.similar_sections_file, "r") as f:
            for line in f.readlines():
                start, end = line.split(",")# 行をコロンで分割してキーと値に分ける
                self.similar_sections_list.append([int(start), int(end)]) # 改行コードを削除するためにstrip()を使う
        
        self.frame_TH = 10
        self.output_dir = "result/"

        my.printline("loading handData..")
        self.keyDataBase = p_load_handData.get_handDataBase(keyDataDir)
        self.tgtDataBase = p_load_handData.get_handDataBase(tgtDataDir)
        my.printline("conpleted")

    def save_dict(self):
        # cost_TH_dict保存
        dict_file = "values/cost_TH_dict.txt"
        with open(dict_file, "w") as f:
            for key, value in self.cost_TH_dict.items():
                f.write(f"{key}:{int(value)}\n")
        my.printline("updated costTH values " + "[" + dict_file + "]")
    
    def calc_feature_variableCostTH(self):
        while True:
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
            
            while True:
                cost_TH = p_gui.select_cost(self.cost_TH_dict[featureLabel])
                if cost_TH == None:
                    break
                self.cost_TH_dict[featureLabel] = cost_TH
                partial_match_DTW.cost_TH = cost_TH

                path_list, path_sect_cost_list = partial_match_DTW.select_path()

                self.print_sect_score(path_sect_cost_list, featureLabel)

                self.plt_path(partial_match_DTW.costMatrix, 
                            path_list, 
                            path_sect_cost_list, 
                            featureLabel, 
                            keyData_feature, 
                            tgtData_feature)
                
                
            
            self.save_dict()
    
    def test(self):
        while True:
            # キーとターゲットの名前選択
            keyName, tgtName = p_gui.select_key_tgt(self.keyDataBase.handDataName_list, self.tgtDataBase.handDataName_list)
            featureLabel = p_gui.select_feature()

            # 部分一致DTWクラス
            partial_match_DTW = p_partial_match_DTW.Partial_match_DTW()

            # 指定手話のデータフレームをfloat型で取得
            keyData_df = self.keyDataBase.handData_df_dict[keyName].astype(float)
            tgtData_df = self.tgtDataBase.handData_df_dict[tgtName].astype(float)

            # データフレームから，指定特徴のデータをリストとして取得
            keyData_feature = keyData_df[featureLabel].tolist()
            tgtData_feature = tgtData_df[featureLabel].tolist()

            self.key_len = len(keyData_feature)
            self.tgt_len = len(tgtData_feature)
            self.keyName = keyName
            self.tgtName = tgtName

            # 初期パラメータ設定
            partial_match_DTW.set_values(keyData_feature, 
                                        tgtData_feature, 
                                        self.cost_TH_dict[featureLabel], 
                                        self.frame_TH)
            
            # DTW行列作成
            partial_match_DTW.create_matrix()
            # ヒートマップ用行列
            list_2d = np.transpose(partial_match_DTW.costMatrix) # 転置

            # グラフ設定 >>>
            aspectRatio = 4 # 縦に対する横の比率
            graphWindowSizeBase = 4 # guiのサイズ
            fig = plt.figure(figsize=(graphWindowSizeBase*aspectRatio, graphWindowSizeBase)) # ウィンドウサイズ
            

            gs = gridspec.GridSpec(2, 2, width_ratios=[1, 5*aspectRatio], height_ratios=[5, 1]) # グラフの個数，サイズ定義
            ax_X = plt.subplot(gs[0]) # 文章データ描画に使用
            ax_D = plt.subplot(gs[1]) # DTW行列描画に使用
            ax_Y = plt.subplot(gs[3]) # 単語データ描画に使用

            ax_Y.plot(tgtData_feature)
            ax_Y.set_xlim(0, self.tgt_len-1) # グラフのx軸を描画範囲全体を使うように調整
            ax_Y.set_xlabel("$Y$")

            ax_X.plot(keyData_feature, range(len(keyData_feature)), c="C1")
            ax_X.set_ylim(0, self.key_len-1) # グラフのy軸を描画範囲全体を使うように調整
            ax_X.invert_yaxis()  # 上下反転

            ax_X.set_ylabel("$X$")

            plt.subplots_adjust(wspace=0.035, hspace=0.15) # グラフ同士の隙間をイイ感じに調整
            

            # GUIのレイアウト
            layout = [
                [sg.Canvas(key='-CANVAS-')],
                [sg.Slider(range=(0,5000),
                            default_value =self.cost_TH_dict[featureLabel],
                            resolution=10,
                            orientation='h',
                            size=(34.3, 15),
                            enable_events=True,
                            key='-SLIDER-')],
                [sg.Output(size=(100, 30), key="-OUTPUT-")],
                [sg.Cancel("終了")]
            ]
            # WINDOWの生成
            window = sg.Window("コストしきい値選択", layout, finalize=True, location=(0,0))

            # figとCanvasを関連付ける
            fig_agg = FigureCanvasTkAgg(fig, window['-CANVAS-'].TKCanvas)
            fig_agg.get_tk_widget().pack(side='top', fill='both', expand=1)
            #canvas.get_tk_widget().pack(side='top', fill='both', expand=1)


            
            # イベントループ
            while True:
                event, values = window.read(timeout=100)
                if event == '終了' or event == sg.WIN_CLOSED:
                    #print(self.cost_TH_dict)
                    self.save_dict()
                    break
                else:
                    if values["-SLIDER-"] is None:
                        cost_TH = 0.0
                    else:
                        cost_TH = values["-SLIDER-"]

                    self.cost_TH_dict[featureLabel] = cost_TH
                    partial_match_DTW.cost_TH = cost_TH

                    path_list, path_sect_cost_list = partial_match_DTW.select_path()

                    #self.print_sect_score(path_sect_cost_list, featureLabel)
                    
                    window['-OUTPUT-'].update("")
                    print(featureLabel + " / cost_TH is " + str(self.cost_TH_dict[featureLabel]) + " >>>")
                    if not path_sect_cost_list == None:
                        for head, end, cost in path_sect_cost_list:
                            score = self.cost_TH_dict[featureLabel] - cost
                            print("range : {} ~ {}, score : {}".format(head, end, score))
                    print("<<<")

                    # ループ内で描画
                    ax_D.clear() # 初期化（前の描画内容削除．これがないと重くなる）
                    ax_D.pcolor(list_2d, cmap=plt.cm.Greys) # ヒートマップ
                    ax_D.get_xaxis().set_ticks([]) # 目盛を削除
                    ax_D.get_yaxis().set_ticks([])
                    ax_D.set_ylim(0, self.key_len-1) # 行列の端をカット（描画のつじつま合わせ）
                    ax_D.set_xlim(0, self.tgt_len-1)
                    ax_D.invert_yaxis()  # 上下反転

                    
                    self.plt_similar_section(ax_D)

                    
                    
                    # ヒートマップにパスを描画
                    if not path_list == []:
                        for i, path in enumerate(path_list):
                            score = self.cost_TH_dict[featureLabel] - path_sect_cost_list[i][2]
                            color = cm.Reds((score/self.cost_TH_dict[featureLabel])**3) # コストの値に応じて色変更
                            path_np = np.array(path)
                            ax_D.plot(path_np[:,0], path_np[:,1], c=color)
                    ###
                    fig_agg.draw() # よくわからんがpltとguiを紐づけたばあいの描画更新関数
            
            
            window.close()




    def print_sect_score(self, path_sect_cost_list, featureLabel):
        print(featureLabel + " / cost_TH is " + str(self.cost_TH_dict[featureLabel]) + " >>>")
        if not path_sect_cost_list == None:
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
            plt.pause(.01)
            
        plt.clf()
        
        
        
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
            y = int(self.key_len*(9/10))
            ax.annotate("", xy=[start, y], xytext=[end-5, y], arrowprops=arrow_props)
            ax.annotate("", xy=[end, y], xytext=[start+5, y], arrowprops=arrow_props)
def main():
    #keyDataDir = "handData/key/d4_feature_d2/"
    #tgtDataDir = "handData/tgt/d4_feature_d2/"
    keyDataDir = "handData/key/d4_feature_d3/"
    tgtDataDir = "handData/tgt/d4_feature_d3/"

    cost_TH_file = "values/cost_TH_dict_4_part95.txt"
    weight_file = "values/weight_LR_xVWB_yVWB.txt"

    search_shuwa = Search_shuwa()
    search_shuwa.set_values(cost_TH_file, weight_file, keyDataDir, tgtDataDir)
    search_shuwa.test()


if __name__ == '__main__':
    #p_gui.select_feature()

    main()