import glob
import os
import my_functions as my
import pandas as pd
import PySimpleGUI as sg
from tqdm import tqdm  # 進行状況バーの表示用ライブラリ
import mediapipe as mp  # MediaPipe のランドマーク定義に必要

# pandas ターミナル出力設定
pd.set_option('display.max_rows', None)

import p_gui
import my_functions as my

# MediaPipe のランドマークに基づいた新しい順序
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

def main():
    # 入出力ファイルのディレクトリ指定
    load_joint_dir, output_dir, _ = p_gui.get_dir_input_output()

    filePath_list = glob.glob(load_joint_dir + "*")
    fileName_list = []

    # GUIレイアウト
    p_gui_progressBar = p_gui.ProgressBar()
    p_gui_progressBar.set_window(len(filePath_list))

    for filePath in filePath_list:
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
    jointPosition_perFrame = pd.read_csv(path, header=0, index_col=0, dtype=str)

    handData_df = pd.DataFrame()  # 新しいデータフレーム handData を作成し，インデックスを設定
    handData_df.index = jointPosition_perFrame.index

    # それぞれを計算する各関数を呼び出し，それらのデータを結合
    wristVel_df = calc_wristVel(jointPosition_perFrame)  # 手首の移動速度
    posFromWrist_df = calc_posFromWrist_df(jointPosition_perFrame)  # 手首からの相対位置
    posFromBody = calc_posFromBody_df(jointPosition_perFrame)  # 体中心からの相対位置

    handData_df = handData_df.join(wristVel_df)
    handData_df = handData_df.join(posFromWrist_df)
    handData_df = handData_df.join(posFromBody)

    handData_df = handData_df.iloc[1:, :].round(6)  # 先頭フレームは NaN データが含まれるためカット

    handData_df.to_csv(saveFileName)

def calc_wristVel(jointPosition_perFrame):  # 手首の移動速度計算関数
    # フレーム毎手首位置移動量計算
    wrist_labels = ['0x_L', '0y_L', '0x_R', '0y_R']
    wristPos_df = (jointPosition_perFrame.loc[:, wrist_labels]).astype(float)  # 指定した列名（手首情報）の列を取得

    vel_labels = ['vel_0x_L', 'vel_0y_L', 'vel_0x_R', 'vel_0y_R']
    wristVel_df = pd.DataFrame()
    wristVel_df[vel_labels] = wristPos_df.diff()  # 一つ前のフレームからの移動量を計算 (行間の差)

    return wristVel_df

def calc_posFromWrist_df(jointPosition_perFrame):  # 手首からの相対位置計算関数
    wrist_labels = ['0x_L', '0y_L', '0x_R', '0y_R']
    wristPos_df = (jointPosition_perFrame.loc[:, wrist_labels]).astype(float)  # 指定した列名（手首情報）の列を取得

    # 新しいラベルの作成（手首以外の指の関節データ用）
    joint_labels_x_L = [f'{point}x_L' for point in range(0, 10)]
    joint_labels_y_L = [f'{point}y_L' for point in range(0, 10)]
    joint_labels_x_R = [f'{point}x_R' for point in range(0, 10)]
    joint_labels_y_R = [f'{point}y_R' for point in range(0, 10)]

    posFromWrist_df = pd.DataFrame()

    # 左手 X 軸と Y 軸の処理
    for axis, joint_labels, wrist_label in zip(['x', 'y'], [joint_labels_x_L, joint_labels_y_L], ['0x_L', '0y_L']):
        posInImg = jointPosition_perFrame.loc[:, joint_labels].astype(float)
        posFromWrist = posInImg.subtract(wristPos_df[wrist_label], axis=0)
        posFromWrist.columns = [f'posFromWrist_{label}' for label in joint_labels]
        posFromWrist_df = pd.concat([posFromWrist_df, posFromWrist], axis=1)

    # 右手 X 軸と Y 軸の処理
    for axis, joint_labels, wrist_label in zip(['x', 'y'], [joint_labels_x_R, joint_labels_y_R], ['0x_R', '0y_R']):
        posInImg = jointPosition_perFrame.loc[:, joint_labels].astype(float)
        posFromWrist = posInImg.subtract(wristPos_df[wrist_label], axis=0)
        posFromWrist.columns = [f'posFromWrist_{label}' for label in joint_labels]
        posFromWrist_df = pd.concat([posFromWrist_df, posFromWrist], axis=1)

    return posFromWrist_df

def calc_posFromBody_df(jointPosition_perFrame):  # 体中心からの相対位置計算関数
    wrist_labels = ['0x_L', '0y_L', '0x_R', '0y_R']
    wristPos_df = (jointPosition_perFrame.loc[:, wrist_labels]).astype(float)  # 指定した列名（手首情報）の列を取得

    # 体中心から左右の手までのベクトル
    joint_body = ['x_Body', 'y_Body']
    posInImg_body_df = jointPosition_perFrame.loc[:, joint_body].astype(float)
    posFromBody_labels = ['posFromBody_0x_L', 'posFromBody_0y_L', 'posFromBody_0x_R', 'posFromBody_0y_R']

    posFromBody_df = pd.DataFrame()
    posFromBody_df['posFromBody_0x_L'] = wristPos_df['0x_L'] - posInImg_body_df['x_Body']
    posFromBody_df['posFromBody_0y_L'] = wristPos_df['0y_L'] - posInImg_body_df['y_Body']
    posFromBody_df['posFromBody_0x_R'] = wristPos_df['0x_R'] - posInImg_body_df['x_Body']
    posFromBody_df['posFromBody_0y_R'] = wristPos_df['0y_R'] - posInImg_body_df['y_Body']

    return posFromBody_df

if __name__ == '__main__':
    main()
