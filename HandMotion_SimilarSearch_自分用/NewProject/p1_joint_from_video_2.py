import mediapipe as mp
import cv2
import glob
import os

import my_functions as my
import p_gui

# 追跡する関節数（新しい順序で定義）
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

# MediaPipe周辺設定
mp_drawing = mp.solutions.drawing_utils
mp_holistic = mp.solutions.holistic
holistic = mp_holistic.Holistic(
    static_image_mode=False,
    smooth_landmarks=True,
    min_detection_confidence=0.7,
    min_tracking_confidence=0.7
)

# 関節データラベル
labels = ['frame']
for prefix in ['L', 'R']:  # 左手(L)と右手(R)の2つの指
    for point in range(len(HAND_BASE_TIP_POINTS)):
        labels.append(f'{point}x_{prefix}')
        labels.append(f'{point}y_{prefix}')
labels.extend(['x_Body', 'y_Body'])  # 体中心

def main():
    load_video_dir, output_dir = p_gui.get_dir_input_output()

    videoPath_list = glob.glob(load_video_dir + "*")
    p_gui_progressBar = p_gui.ProgressBar()
    p_gui_progressBar.set_window(bar_max=len(videoPath_list))

    for videoPath in videoPath_list:
        p_gui_progressBar.update_window()

        videoFile = os.path.basename(videoPath)
        videoName, videoExt = os.path.splitext(videoFile)

        jointPositionData = get_jointPosition_fromVideo(videoPath)
        my.save_2dData_csv(fileName=videoName, dirName=output_dir, data=jointPositionData)
        my.printline("saved as " + output_dir + videoName + '.csv')

    p_gui_progressBar.close_window()

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
            frame_RGB = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            holistic_results = holistic.process(frame_RGB)

            hand_L = None
            hand_R = None
            pose = None
            if holistic_results.left_hand_landmarks is not None:
                hand_L = holistic_results.left_hand_landmarks.landmark
            if holistic_results.right_hand_landmarks is not None:
                hand_R = holistic_results.right_hand_landmarks.landmark
            if holistic_results.pose_landmarks is not None:
                pose = holistic_results.pose_landmarks.landmark

            jointPosition_L, jointPosition_R, bodyPosition_center = list_from_randmark(hand_L, hand_R, pose, frame_width, frame_height)

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
    jointPosition_L = []  # 左手のデータ
    jointPosition_R = []  # 右手のデータ
    bodyPosition_center = []  # 体の中心位置

    # 左手の座標取得
    if hand_L is not None:
        for point in HAND_BASE_TIP_POINTS:
            joint_x = hand_L[point].x * frame_width
            joint_y = hand_L[point].y * frame_height
            jointPosition_L.append(str(joint_x))
            jointPosition_L.append(str(joint_y))
    else:
        for _ in HAND_BASE_TIP_POINTS:
            jointPosition_L.append('None')
            jointPosition_L.append('None')

    # 右手の座標取得
    if hand_R is not None:
        for point in HAND_BASE_TIP_POINTS:
            joint_x = hand_R[point].x * frame_width
            joint_y = hand_R[point].y * frame_height
            jointPosition_R.append(str(joint_x))
            jointPosition_R.append(str(joint_y))
    else:
        for _ in HAND_BASE_TIP_POINTS:
            jointPosition_R.append('None')
            jointPosition_R.append('None')

    # 体の中心位置（肩から計算）
    if pose is not None:
        shoulder_L = pose[mp_holistic.PoseLandmark.LEFT_SHOULDER]
        shoulder_R = pose[mp_holistic.PoseLandmark.RIGHT_SHOULDER]
        center_x = (shoulder_L.x * frame_width + shoulder_R.x * frame_width) / 2
        center_y = (shoulder_L.y * frame_height + shoulder_R.y * frame_height) / 2
        bodyPosition_center.append(str(center_x))
        bodyPosition_center.append(str(center_y))
    else:
        bodyPosition_center.append('None')
        bodyPosition_center.append('None')

    return jointPosition_L, jointPosition_R, bodyPosition_center


if __name__ == "__main__":
    main()
