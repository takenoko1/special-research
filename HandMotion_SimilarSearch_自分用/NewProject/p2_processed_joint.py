import glob
import os
import my_functions as my
import pandas as pd#データフレーム操作用ライブラリ
import PySimpleGUI as sg#GUI作成用ライブラリ

# pandas ターミナル出力設定
#pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)
#pd.set_option("display.width", 300)

import p_gui#GUI関連のカスタムモジュール
import my_functions as my


def main():
    # 読み込む動画ファイルがあるディレクトリと，関節データを出力するディレクトリ指定
    load_joint_dir, output_dir, smoothed_output_dir = p_gui.get_dir_input_output()

    filePath_list = glob.glob(load_joint_dir +"*")#指定ディレクトリ内の全てのファイルパスを取得
    fileName_list = []

    # guiレイアウト
    p_gui_progressBar = p_gui.ProgressBar()
    p_gui_progressBar.set_window(len(filePath_list))

    for filePath in filePath_list:#各ファイルに対してexecute関数を呼び出し，処理結果を保存
        #　gui処理
        p_gui_progressBar.update_window()

        # 変換処理
        fileFile = os.path.basename(filePath)
        fileName, fileExt = os.path.splitext(fileFile)
        fileName_list.append(fileName)

        saveFileName = output_dir + fileName + '.csv'
        smoothedSaveFileName = smoothed_output_dir + fileName + '.csv'

        execute(filePath, saveFileName, smoothedSaveFileName)
        my.printline("saved as " + saveFileName)
        my.printline("saved as " + smoothedSaveFileName)
    
    p_gui_progressBar.close_window()

def execute(path, saveFileName, smoothedSaveFileName):
    jointPosition_perFrame_df = pd.read_csv(path, header=0, index_col=0, dtype=str)#CSVファイルを読み込み，データフレームに変換
    jointPosition_perFrame_df = linerInterpolation(jointPosition_perFrame_df)
    smoothed_jointPosition_perFrame_df = backwardMovingAverage(jointPosition_perFrame_df)#関数で後方移動平均を適用

    jointPosition_perFrame_df.to_csv(saveFileName)#処理結果を新しいCSVファイルとして保存
    smoothed_jointPosition_perFrame_df.to_csv(smoothedSaveFileName)

#線形補完
"""
検出結果がNoneのフレームを線形補完する (pandasによる行列計算で実行)
x0 : Noneフレームの，一つ前のフレームのデータ
xn : Noneフレームの，一つ後のフレームのデータ
n : 連続するNoneフレームの数
m : 補完するフレームの順番（1<=m<=n）
xm : 補完するフレームのデータ
xm = (xn-x0)*(m/n) + x0

例 フレーム番号（30,31,32）がNoneフレームだった場合，
x0 = データ[29]
xn = データ[33]
n = 3 
xm = (データ[33]-データ[29])*(m/3) + データ[29]
フレーム番号30を補完するデータの値は
x1 = (データ[33]-データ[29])*(1/3) + データ[29]
フレーム番号31を補完するデータの値は
x2 = (データ[33]-データ[29])*(1/3) + データ[29]
"""

def linerInterpolation(df):
    n=0
    # 先頭，最後尾の行にNoneが含まれる場合削除
    while True:
        if df.iloc[0]["0x_L"] == "None" or df.iloc[0]["0x_R"] == "None" or df.iloc[0]["x_Body"] == "None":
            df = df.drop(df.index[[0]])
            continue

        if df.iloc[-1]["0x_L"] == "None" or df.iloc[-1]["0x_R"] == "None" or df.iloc[-1]["x_Body"] == "None":
            df = df.drop(df.index[[-1]])
            continue
        break
    
    # None が含まれるフレームを抽出
    containgNone_L_df = df[df["0x_L"] == "None"]
    containgNone_R_df = df[df["0x_R"] == "None"]
    containgNone_B_df = df[df["x_Body"] == "None"]
    # 列名に特定の文字列を含む列を選択
    containgNone_L_df = containgNone_L_df.loc[:,containgNone_L_df.columns.str.contains("_L")]
    containgNone_R_df = containgNone_R_df.loc[:,containgNone_R_df.columns.str.contains("_R")]
    containgNone_B_df = containgNone_B_df.loc[:,containgNone_B_df.columns.str.contains("_B")]

    df = calc_linerInterpolation(df, containgNone_L_df, "0x_L", "_L")
    df = calc_linerInterpolation(df, containgNone_R_df, "0x_R", "_R")
    df = calc_linerInterpolation(df, containgNone_B_df, "x_Body", "_B")

    return df

def calc_linerInterpolation(df, containgNone_df, noneJdgLabel, featureLabel):#線形補完計算関数
    if not containgNone_df.empty:
        i = 0
        
        # Noneを含むフレームを走査（Noneフレームが連続している場合の処理に注意）
        while i < containgNone_df.shape[0]:
            # x0のデータ番号
            x0_frame = containgNone_df.index[i] - 1
            
            # Noneフレームが連続する場合の変数制御
            n_skippedFrame = 1
            while True: 
                if df.loc[containgNone_df.index[i] + 1, noneJdgLabel] == "None":
                    n_skippedFrame += 1
                    i += 1
                    continue
                break
            
            # xnのデータ番号
            xn_frame = containgNone_df.index[i] + 1
            
            xn = df.loc[xn_frame,df.columns.str.contains(featureLabel)].astype(float)
            x0 = df.loc[x0_frame,df.columns.str.contains(featureLabel)].astype(float)

            diff_frame_df = xn - x0
            
            # 一次関数の傾き
            slope_frame_df = diff_frame_df/(n_skippedFrame + 1)
            
            # データの上書き
            for m in range(1, n_skippedFrame+1):
                xm = (slope_frame_df*m + x0).round(6) # 補完データ（少数6桁）
                df.loc[x0_frame + m, df.columns.str.contains(featureLabel)] = xm.astype(str) # ちゃんとstr型に戻す

            i += 1
            
    return df

# 後方移動平均(データの平滑化を行っている)
WINDOW_SIZE = 5
def backwardMovingAverage(df):
    smoothed_df = df.iloc[(WINDOW_SIZE-1):, :].astype(float)
    for i in range(smoothed_df.shape[0]):
        window = df.iloc[i:i+WINDOW_SIZE].astype(float) # ウィンドウサイズのフレームを抽出
        ave_df = window.mean().round(6) # ウィンドウサイズのフレームの平均をとって少数6桁きりすて
        smoothed_df.iloc[i] = ave_df

    return smoothed_df.astype(str)

if __name__ == '__main__':
    #ofo = "C:/Users/root/Desktop/hisa_reserch/HandMotion_SimilarSearch/workspace/NewProject/smoothed_joint/oosa.csv"
    #execute("C:/Users/root/Desktop/hisa_reserch/HandMotion_SimilarSearch/workspace/NewProject/joint/key/0.csv",ofo)
    main()