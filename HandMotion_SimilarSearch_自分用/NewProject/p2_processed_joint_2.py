import glob
import os
import pandas as pd  # データフレーム操作用ライブラリ
import PySimpleGUI as sg  # GUI作成用ライブラリ

import my_functions as my
import p_gui  # GUI関連のカスタムモジュール
import mediapipe as mp  # MediaPipe のランドマーク定義に必要

# pandas ターミナル出力設定
pd.set_option('display.max_rows', None)

# MediaPipeを参考にしたデータラベル設定
HAND_BASE_TIP_POINTS = [
    mp.solutions.hands.HandLandmark.THUMB_CMC,      # 親指付け根
    mp.solutions.hands.HandLandmark.THUMB_TIP,     # 親指先端
    mp.solutions.hands.HandLandmark.INDEX_FINGER_MCP,  # 人差し指付け根
    mp.solutions.hands.HandLandmark.INDEX_FINGER_TIP,  # 人差し指先端
    mp.solutions.hands.HandLandmark.MIDDLE_FINGER_MCP, # 中指付け根
    mp.solutions.hands.HandLandmark.MIDDLE_FINGER_TIP, # 中指先端
    mp.solutions.hands.HandLandmark.RING_FINGER_MCP,   # 薬指付け根
    mp.solutions.hands.HandLandmark.RING_FINGER_TIP,   # 薬指先端
    mp.solutions.hands.HandLandmark.PINKY_MCP,         # 小指付け根
    mp.solutions.hands.HandLandmark.PINKY_TIP          # 小指先端
]

# ラベルを新しい順序に基づいて構築
labels = ['frame']
for prefix in ['L', 'R']:  # 左手(L)と右手(R)
    for point in range(len(HAND_BASE_TIP_POINTS)):
        labels.append(f'{point}x_{prefix}')
        labels.append(f'{point}y_{prefix}')
labels.extend(['x_Body', 'y_Body'])  # 体中心

def main():
    # 読み込む動画ファイルがあるディレクトリと，関節データを出力するディレクトリ指定
    load_joint_dir, output_dir = p_gui.get_dir_input_output()

    filePath_list = glob.glob(load_joint_dir + "*")  # 指定ディレクトリ内の全てのファイルパスを取得
    fileName_list = []

    # GUIレイアウト
    p_gui_progressBar = p_gui.ProgressBar()
    p_gui_progressBar.set_window(len(filePath_list))

    for filePath in filePath_list:  # 各ファイルに対してexecute関数を呼び出し，処理結果を保存
        # GUI処理
        p_gui_progressBar.update_window()

        # 変換処理
        fileFile = os.path.basename(filePath)
        fileName, fileExt = os.path.splitext(fileFile)
        fileName_list.append(fileName)

        saveFileName = output_dir + fileName + '.csv'
        execute(filePath, saveFileName)
        my.printline("saved as " + saveFileName)

    p_gui_progressBar.close_window()

def execute(path, saveFileName):
    # CSVファイルを読み込み，データフレームに変換
    jointPosition_perFrame_df = pd.read_csv(path, header=0, index_col=0, dtype=str)

    # 線形補完
    jointPosition_perFrame_df = linerInterpolation(jointPosition_perFrame_df)

    # 後方移動平均
    smoothed_jointPosition_perFrame_df = backwardMovingAverage(jointPosition_perFrame_df)

    # 処理結果を新しいCSVファイルとして保存
    smoothed_jointPosition_perFrame_df.to_csv(saveFileName)

# 線形補完
def linerInterpolation(df):
    # 先頭・最後尾の行にNoneが含まれる場合削除
    while True:
        if df.iloc[0].isin(["None"]).any():
            df = df.drop(df.index[0])
            continue
        if df.iloc[-1].isin(["None"]).any():
            df = df.drop(df.index[-1])
            continue
        break

    # Noneが含まれる列を対象に補完
    for col in df.columns:
        df[col] = pd.to_numeric(df[col], errors='coerce')  # NoneをNaNに変換
        df[col] = df[col].interpolate(method='linear')  # 線形補完
        df[col] = df[col].fillna(method='bfill')  # 前方補完
        df[col] = df[col].fillna(method='ffill')  # 後方補完
    return df

# 後方移動平均(データの平滑化)
WINDOW_SIZE = 5
def backwardMovingAverage(df):
    smoothed_df = df.copy()
    for col in df.columns:
        smoothed_df[col] = df[col].astype(float).rolling(window=WINDOW_SIZE, min_periods=1).mean()
    return smoothed_df.astype(str)

if __name__ == '__main__':
    main()
