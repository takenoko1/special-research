import mediapipe as mp#ポーズと手の追跡用
import cv2#OpenCVを使用したビデオ処理用
import glob#ファイル操作用
import os
import math

import my_functions as my#データの保存や印刷を含むカスタム関数用
import p_gui #gui関連制御

ALL_JOINT_NUM = 11#手ごとに追跡する関節の総数

# MediaPipe周辺設定（https://github.com/google/mediapipe/blob/master/docs/solutions/holistic.md）
mp_drawing = mp.solutions.drawing_utils
drawing_spec = mp_drawing.DrawingSpec(color=[0, 180, 0], thickness=2, circle_radius=4)
mp_holistic = mp.solutions.holistic
holistic =  mp_holistic.Holistic(
        static_image_mode=False,        # 静止画:True 動画:False
        #UPPER_BODY_ONLY=True,           # 上半身のみ:True 全身:False
        smooth_landmarks=True,          # ジッターを減らすかどうか
        min_detection_confidence=0.7,
        min_tracking_confidence=0.7)

# 関節データラベル
labels = ['', '0x_L', '0y_L', '1x_L', '1y_L', '2x_L', '2y_L', '3x_L', '3y_L', '4x_L', '4y_L',
            '5x_L', '5y_L','6x_L', '6y_L', '7x_L', '7y_L', '8x_L', '8y_L', '9x_L', '9y_L',
            '10x_L', '10y_L', '11x_L', '11y_L', '12x_L', '12y_L', '13x_L', '13y_L', '14x_L', '14y_L',
            '15x_L', '15y_L', '16x_L', '16y_L', '17x_L', '17y_L', '18x_L', '18y_L', '19x_L', '19y_L', '20x_L',
            '20y_L',
            '0x_R', '0y_R', '1x_R', '1y_R', '2x_R', '2y_R', '3x_R', '3y_R', '4x_R', '4y_R',
            '5x_R', '5y_R', '6x_R', '6y_R', '7x_R', '7y_R', '8x_R', '8y_R', '9x_R', '9y_R',
            '10x_R', '10y_R', '11x_R', '11y_R', '12x_R', '12y_R', '13x_R', '13y_R', '14x_R', '14y_R',
            '15x_R', '15y_R', '16x_R', '16y_R', '17x_R', '17y_R', '18x_R', '18y_R', '19x_R', '19y_R', '20x_R',
            '20y_R',
            'x_Body', 'y_Body']


def main():#メインプログラム
    load_video_dir, output_dir = p_gui.get_dir_input_output()#GUIの関連

    videoPath_list = glob.glob(load_video_dir +"*") # ディレクトリ内のすべてのファイル取得

    p_gui_progressBar = p_gui.ProgressBar()#
    p_gui_progressBar.set_window(bar_max=len(videoPath_list))#プログレスバーの初期化

    for videoPath in videoPath_list:#各ビデオファイルを繰り返し処理し，関節位置を抽出してCSVに保存
        p_gui_progressBar.update_window()

        videoFile = os.path.basename(videoPath) # パスからファイル名取得
        videoName, videoExt = os.path.splitext(videoFile) # 

        jointPositionData = get_jointPosition_fromVideo(videoPath)
        my.save_2dData_csv(fileName=videoName, 
                            dirName=output_dir, 
                            data=jointPositionData)
        my.printline("saved as " + output_dir + videoName + '.csv')
    
    p_gui_progressBar.close_window()#プログレスバーを閉じる

"""
def find_distance():
    for i in labels_1:
        labels_1[i + 1] = sqrt(labels[])"""

# 動画から関節位置データを作成
def get_jointPosition_fromVideo(videoPath):
    cap = cv2.VideoCapture(videoPath)
    frame_width = float(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    frame_height = float(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    jointPositionData = [labels]

    frameNum = 1

    while True:
        ret, frame = cap.read()
        if ret:
            frame_RGB = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB) # 色型変換

            # MediaPipe実行，ランドマーク情報を取得（MediaPipeデータはランドマークとかいう変な構造体で返ってくる）
            holistic_results = holistic.process(frame_RGB)
            
            hand_L = None
            hand_R = None
            pose = None
            if holistic_results.left_hand_landmarks is not None: # 左手ランドマーク
                hand_L = holistic_results.left_hand_landmarks.landmark
            if holistic_results.right_hand_landmarks is not None: # 右手ランドマーク
                hand_R = holistic_results.right_hand_landmarks.landmark
            if holistic_results.pose_landmarks is not None: # 体ランドマーク
                pose = holistic_results.pose_landmarks.landmark
            
            jointPosition_L, jointPosition_R , bodyPosition_center = list_from_randmark(hand_L, hand_R, pose, frame_width, frame_height) #MediaPipe出力データ（ランドマーク）をリストに変換
            
            frameData = []
            frameData.append(str(frameNum))
            frameData.extend(jointPosition_L)
            frameData.extend(jointPosition_R)
            frameData.extend(bodyPosition_center)

            jointPositionData.append(frameData)

            frameNum += 1
        else:
            break
    
    cap.release()

    return jointPositionData


# MediaPipe出力データ（ランドマーク）をリストに変換
def list_from_randmark(hand_L, hand_R, pose, frame_width, frame_height):
    jointPosition_L = [] # 左手関節情報のリスト
    jointPosition_R = [] # 右手関節情報のリスト
    bodyPosition_center = [] # 体関節情報のリスト

    if hand_L is not None:
        for joint in hand_L:
            joint_x = joint.x * frame_width
            joint_y = joint.y * frame_height
            jointPosition_L.append(str(joint_x))
            jointPosition_L.append(str(joint_y))
    else:
        for _ in range(ALL_JOINT_NUM*2):
            jointPosition_L.append('None')
    
    if hand_R is not None:
        for joint in hand_R:
            joint_x = joint.x * frame_width
            joint_y = joint.y * frame_height
            jointPosition_R.append(str(joint_x))
            jointPosition_R.append(str(joint_y))
    else:
        for _ in range(ALL_JOINT_NUM*2):
            jointPosition_R.append('None')

    # 肩関節から体中心を計算
    if pose is not None:
        shoulder_L = pose[mp_holistic.PoseLandmark.LEFT_SHOULDER]
        shoulder_R = pose[mp_holistic.PoseLandmark.RIGHT_SHOULDER]
        center_x = (shoulder_L.x*frame_width + shoulder_R.x*frame_width) / 2
        center_y = (shoulder_L.y*frame_height + shoulder_R.y*frame_height) / 2
        bodyPosition_center.append(str(center_x))
        bodyPosition_center.append(str(center_y))
    else:
        bodyPosition_center.append('None')
        bodyPosition_center.append('None')
    
    return jointPosition_L, jointPosition_R, bodyPosition_center


if __name__ == "__main__":
    main()