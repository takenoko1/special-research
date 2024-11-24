import glob
import os
import my_functions as my
import pandas as pd
import PySimpleGUI as sg
from tqdm import tqdm#進行状況バーの表示用ライブラリ

# pandas ターミナル出力設定
#pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)
#pd.set_option("display.width", 300)

import p_gui
import my_functions as my

def main():
    # 入出力ファイルのディレクトリ指定
    load_joint_dir, output_dir = p_gui.get_dir_input_output()

    filePath_list = glob.glob(load_joint_dir +"*")
    fileName_list = []

    # guiレイアウト
    p_gui_progressBar = p_gui.ProgressBar()
    p_gui_progressBar.set_window(len(filePath_list))

    for filePath in filePath_list:
        #　gui処理
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

    handData_df = pd.DataFrame()#新しいデータフレームhandDataを作成し，インデックスを設定
    handData_df.index = jointPosition_perFrame.index

    #それぞれを計算する各関数を呼び出し，それらのデータを結合
    wristVel_df = calc_wristVel(jointPosition_perFrame)#手首の移動速度
    posFromWrist_df = calc_posFromWrist_df(jointPosition_perFrame)#手首からの相対位置
    posFromBody = calc_posFromBody_df(jointPosition_perFrame)#体中心からの相対位置

    handData_df = handData_df.join(wristVel_df)
    handData_df = handData_df.join(posFromWrist_df)
    handData_df = handData_df.join(posFromBody)

    handData_df = handData_df.iloc[1:,:].round(6) # 先頭フレームはNanデータが含まれるためカット

    handData_df.to_csv(saveFileName)
    #print(handData_df)


def calc_wristVel(jointPosition_perFrame):#手首の移動速度計算関数
    # フレーム毎手首位置移動量計算
    wrist_labels = ['0x_L', '0y_L', '0x_R', '0y_R']
    wristPos_df = (jointPosition_perFrame.loc[:, wrist_labels]).astype(float) # 指定した列名（手首情報）の列を取得

    vel_labels = ['vel_0x_L', 'vel_0y_L', 'vel_0x_R', 'vel_0y_R']
    wristVel_df = pd.DataFrame()
    wristVel_df[vel_labels] = wristPos_df.diff() # 一つ前のフレームからの移動量を計算　(行間の差)

    return wristVel_df

def calc_posFromWrist_df(jointPosition_perFrame):#手首からの相対位置計算関数
    wrist_labels = ['0x_L', '0y_L', '0x_R', '0y_R']
    wristPos_df = (jointPosition_perFrame.loc[:, wrist_labels]).astype(float) # 指定した列名（手首情報）の列を取得

    # 手首からのベクトル計算
    joint_x_L_labels = ['1x_L', '2x_L', '3x_L', '4x_L', '5x_L', '6x_L', '7x_L', '8x_L', '9x_L', '10x_L', '11x_L', '12x_L', '13x_L', '14x_L', '15x_L', '16x_L', '17x_L', '18x_L', '19x_L', '20x_L'] # 手首を除いた手指関節ラベル
    posInImg_x_L_df = jointPosition_perFrame.loc[:, joint_x_L_labels].astype(float)
    posFrmWrist_x_L_df = posInImg_x_L_df.copy()
    for jointLabel in joint_x_L_labels:
        posFrmWrist_x_L_df[jointLabel] = (posInImg_x_L_df[jointLabel] - wristPos_df['0x_L'])
    posFromWrist_x_L_labels = ['posFromWrist_1x_L', 'posFromWrist_2x_L', 'posFromWrist_3x_L', 'posFromWrist_4x_L', 'posFromWrist_5x_L', 'posFromWrist_6x_L', 'posFromWrist_7x_L', 'posFromWrist_8x_L', 'posFromWrist_9x_L', 'posFromWrist_10x_L', 'posFromWrist_11x_L', 'posFromWrist_12x_L', 'posFromWrist_13x_L', 'posFromWrist_14x_L', 'posFromWrist_15x_L', 'posFromWrist_16x_L', 'posFromWrist_17x_L', 'posFromWrist_18x_L', 'posFromWrist_19x_L', 'posFromWrist_20x_L']
    posFrmWrist_x_L_df.set_axis(posFromWrist_x_L_labels, axis='columns') #列名変更

    joint_y_L_labels = ['1y_L', '2y_L', '3y_L', '4y_L', '5y_L', '6y_L', '7y_L', '8y_L', '9y_L', '10y_L', '11y_L', '12y_L', '13y_L', '14y_L', '15y_L', '16y_L', '17y_L', '18y_L', '19y_L', '20y_L'] # 手首を除いた手指関節ラベル
    posInImg_y_L_df = jointPosition_perFrame.loc[:, joint_y_L_labels].astype(float)
    posFrmWrist_y_L_df = posInImg_y_L_df.copy()
    for jointLabel in joint_y_L_labels:
        posFrmWrist_y_L_df[jointLabel] = (posInImg_y_L_df[jointLabel] - wristPos_df['0y_L'])
    posFromWrist_y_L_labels = ['posFromWrist_1y_L', 'posFromWrist_2y_L', 'posFromWrist_3y_L', 'posFromWrist_4y_L', 'posFromWrist_5y_L', 'posFromWrist_6y_L', 'posFromWrist_7y_L', 'posFromWrist_8y_L', 'posFromWrist_9y_L', 'posFromWrist_10y_L', 'posFromWrist_11y_L', 'posFromWrist_12y_L', 'posFromWrist_13y_L', 'posFromWrist_14y_L', 'posFromWrist_15y_L', 'posFromWrist_16y_L', 'posFromWrist_17y_L', 'posFromWrist_18y_L', 'posFromWrist_19y_L', 'posFromWrist_20y_L']
    posFrmWrist_y_L_df.set_axis(posFromWrist_y_L_labels, axis='columns') #列名変更
    
    joint_x_R_labels = ['1x_R', '2x_R', '3x_R', '4x_R', '5x_R', '6x_R', '7x_R', '8x_R', '9x_R', '10x_R', '11x_R', '12x_R', '13x_R', '14x_R', '15x_R', '16x_R', '17x_R', '18x_R', '19x_R', '20x_R'] # 手首を除いた手指関節ラベル
    posInImg_x_R_df = jointPosition_perFrame.loc[:, joint_x_R_labels].astype(float)
    posFrmWrist_x_R_df = posInImg_x_R_df.copy()
    for jointLabel in joint_x_R_labels:
        posFrmWrist_x_R_df[jointLabel] = (posInImg_x_R_df[jointLabel] - wristPos_df['0x_R'])
    posFromWrist_x_R_labels = ['posFromWrist_1x_R', 'posFromWrist_2x_R', 'posFromWrist_3x_R', 'posFromWrist_4x_R', 'posFromWrist_5x_R', 'posFromWrist_6x_R', 'posFromWrist_7x_R', 'posFromWrist_8x_R', 'posFromWrist_9x_R', 'posFromWrist_10x_R', 'posFromWrist_11x_R', 'posFromWrist_12x_R', 'posFromWrist_13x_R', 'posFromWrist_14x_R', 'posFromWrist_15x_R', 'posFromWrist_16x_R', 'posFromWrist_17x_R', 'posFromWrist_18x_R', 'posFromWrist_19x_R', 'posFromWrist_20x_R']
    posFrmWrist_x_R_df.set_axis(posFromWrist_x_R_labels, axis='columns') #列名変更
    
    joint_y_R_labels = ['1y_R', '2y_R', '3y_R', '4y_R', '5y_R', '6y_R', '7y_R', '8y_R', '9y_R', '10y_R', '11y_R', '12y_R', '13y_R', '14y_R', '15y_R', '16y_R', '17y_R', '18y_R', '19y_R', '20y_R'] # 手首を除いた手指関節ラベル
    posInImg_y_R_df = jointPosition_perFrame.loc[:, joint_y_R_labels].astype(float)
    posFrmWrist_y_R_df = posInImg_y_R_df.copy()
    for jointLabel in joint_y_R_labels:
        posFrmWrist_y_R_df[jointLabel] = (posInImg_y_R_df[jointLabel] - wristPos_df['0y_R'])
    posFromWrist_y_R_labels = ['posFromWrist_1y_R', 'posFromWrist_2y_R', 'posFromWrist_3y_R', 'posFromWrist_4y_R', 'posFromWrist_5y_R', 'posFromWrist_6y_R', 'posFromWrist_7y_R', 'posFromWrist_8y_R', 'posFromWrist_9y_R', 'posFromWrist_10y_R', 'posFromWrist_11y_R', 'posFromWrist_12y_R', 'posFromWrist_13y_R', 'posFromWrist_14y_R', 'posFromWrist_15y_R', 'posFromWrist_16y_R', 'posFromWrist_17y_R', 'posFromWrist_18y_R', 'posFromWrist_19y_R', 'posFromWrist_20y_R']
    posFrmWrist_y_R_df.set_axis(posFromWrist_y_R_labels, axis='columns') #列名変更

    posFromWrist_df = pd.DataFrame()
    posFromWrist_df[posFromWrist_x_L_labels] = posFrmWrist_x_L_df
    posFromWrist_df[posFromWrist_y_L_labels] = posFrmWrist_y_L_df
    posFromWrist_df[posFromWrist_x_R_labels] = posFrmWrist_x_R_df
    posFromWrist_df[posFromWrist_y_R_labels] = posFrmWrist_y_R_df

    return posFromWrist_df

def calc_posFromBody_df(jointPosition_perFrame):#体中心からの相対位置計算関数
    wrist_labels = ['0x_L', '0y_L', '0x_R', '0y_R']
    wristPos_df = (jointPosition_perFrame.loc[:, wrist_labels]).astype(float) # 指定した列名（手首情報）の列を取得

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
    #execute("handData/d2_smoothed_joint/key/0.csv", "a")
    main()