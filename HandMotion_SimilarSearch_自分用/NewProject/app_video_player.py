import numpy as np
import PySimpleGUI as sg
import cv2
from pathlib import Path

def file_read():
    '''
    ファイルを選択して読み込む
    '''
    fp = ""
    # GUIのレイアウト
    layout = [
        [
            sg.Text("ファイル"),
            sg.InputText(),
            sg.FileBrowse(key="file")
        ],
        [sg.Submit(key="submit"), sg.Cancel("Exit")]
    ]
    # WINDOWの生成
    window = sg.Window("ファイル選択", layout)

    # イベントループ
    while True:
        event, values = window.read(timeout=100)
        if event == 'Exit' or event == sg.WIN_CLOSED:
            break
        elif event == 'submit':
            if values[0] == "":
                sg.popup("ファイルが入力されていません。")
                event = ""
            else:
                fp = values[0]
                break
    window.close()
    return Path(fp)

class Main:
    def __init__(self):
        self.fp = file_read()
        self.cap = cv2.VideoCapture(str(self.fp))

        # 1フレーム目の取得
        # 取得可能かの確認
        self.ret, self.f_frame = self.cap.read()

        if self.ret:

            self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
            # 動画情報の取得
            self.fps = self.cap.get(cv2.CAP_PROP_FPS)
            self.width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            self.height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            self.total_count = self.cap.get(cv2.CAP_PROP_FRAME_COUNT)

            # フレーム関係
            self.frame_count = 0
            self.s_frame = 0
            self.e_frame = self.total_count

            # 再生の一時停止フラグ
            self.stop_flg = False

            cv2.namedWindow("Movie")

        else:
            sg.Popup("ファイルの読込に失敗しました。")
            return


    def run(self):
        # GUI #######################################################
        # GUIのレイアウト
        layout = [
            [
                sg.Text("Start", size=(8, 1)),
                sg.Slider(
                    (0, self.total_count - 1),
                    0,
                    1,
                    orientation='h',
                    size=(45, 15),
                    key='-START FRAME SLIDER-',
                    enable_events=True
                )
            ],
            [
                sg.Text("End ", size=(8, 1)),
                sg.Slider(
                    (0, self.total_count - 1), self.total_count - 1,
                    1,
                    orientation='h',
                    size=(45, 15),
                    key='-END FRAME SLIDER-',
                    enable_events=True
                )
            ],
            [
                sg.Text("Progress ", size=(8, 1)),
                sg.Slider(
                (0, self.total_count - 1),
                0,
                1,
                orientation='h',
                size=(45, 15),
                key='-PROGRESS SLIDER-',
                enable_events=True
            )],
            [
                sg.Button('<<<', size=(5, 1)),
                sg.Button('<<', size=(5, 1)),
                sg.Button('<', size=(5, 1)),
                sg.Button('Play / Stop', size=(9, 1)),
                sg.Button('Reset', size=(7, 1)),
                sg.Button('>', size=(5, 1)),
                sg.Button('>>', size=(5, 1)),
                sg.Button('>>>', size=(5, 1))
            ],
            [
                sg.Text("Speed", size=(6, 1)),
                sg.Slider(
                    (0, 240),
                    10,
                    10,
                    orientation='h',
                    size=(19.4, 15),
                    key='-SPEED SLIDER-',
                    enable_events=True
                ),
                sg.Text("Skip", size=(6, 1)),
                sg.Slider(
                    (0, 300),
                    0,
                    1,
                    orientation='h',
                    size=(19.4, 15),
                    key='-SKIP SLIDER-',
                    enable_events=True
                )
            ],
            [sg.HorizontalSeparator()],
            [sg.Output(size=(65, 5), key='-OUTPUT-')],
            [sg.Button('Clear')]
        ]


        # Windowを生成
        window = sg.Window('OpenCV Integration', layout, location=(0, 0))
        # 動画情報の表示
        self.event, values = window.read(timeout=0)
        print("ファイルが読み込まれました。")
        print("File Path: " + str(self.fp))
        print("fps: " + str(int(self.fps)))
        print("width: " + str(self.width))
        print("height: " + str(self.height))
        print("frame count: " + str(int(self.total_count)))

    # メインループ #########################################################
        try:
            while True:
                self.event, values = window.read(
                    timeout=values["-SPEED SLIDER-"]
                )

                if self.event == "Clear":
                    pass

                if self.event != "__TIMEOUT__":
                    print(self.event)
                # Exitボタンが押されたら、またはウィンドウの閉じるボタンが押されたら終了
                if self.event in ('Exit', sg.WIN_CLOSED, None):
                    break

                # 動画の再読み込み
                # スタートフレームを設定していると動く
                if self.event == 'Reset':
                    self.cap.set(cv2.CAP_PROP_POS_FRAMES, self.s_frame)
                    self.frame_count = self.s_frame
                    window['-PROGRESS SLIDER-'].update(self.frame_count)

                    # Progress sliderへの変更を反映させるためにcontinue
                    continue

                # フレーム操作 ################################################
                # スライダを直接変更した場合は優先する
                if self.event == '-PROGRESS SLIDER-':
                    # フレームカウントをプログレスバーに合わせる
                    self.frame_count = int(values['-PROGRESS SLIDER-'])
                    self.cap.set(cv2.CAP_PROP_POS_FRAMES, self.frame_count)
                    if values['-PROGRESS SLIDER-'] > values['-END FRAME SLIDER-']:
                        window['-END FRAME SLIDER-'].update(
                            values['-PROGRESS SLIDER-'])

                # スタートフレームを変更した場合
                if self.event == '-START FRAME SLIDER-':
                    self.s_frame = int(values['-START FRAME SLIDER-'])
                    self.cap.set(cv2.CAP_PROP_POS_FRAMES, self.s_frame)
                    self.frame_count = self.s_frame
                    window['-PROGRESS SLIDER-'].update(self.frame_count)
                    if values['-START FRAME SLIDER-'] > values['-END FRAME SLIDER-']:
                        window['-END FRAME SLIDER-'].update(
                            values['-START FRAME SLIDER-'])
                        self.e_frame = self.s_frame

                # エンドフレームを変更した場合
                if self.event == '-END FRAME SLIDER-':
                    if values['-END FRAME SLIDER-'] < values['-START FRAME SLIDER-']:
                        window['-START FRAME SLIDER-'].update(
                            values['-END FRAME SLIDER-'])
                        self.s_frame = self.e_frame

                    # エンドフレームの設定
                    self.e_frame = int(values['-END FRAME SLIDER-'])

                if self.event == '<<<':
                    self.frame_count = np.maximum(0, self.frame_count - 150)
                    window['-PROGRESS SLIDER-'].update(self.frame_count)
                    self.cap.set(cv2.CAP_PROP_POS_FRAMES, self.frame_count)

                if self.event == '<<':
                    self.frame_count = np.maximum(0, self.frame_count - 30)
                    window['-PROGRESS SLIDER-'].update(self.frame_count)
                    self.cap.set(cv2.CAP_PROP_POS_FRAMES, self.frame_count)

                if self.event == '<':
                    self.frame_count = np.maximum(0, self.frame_count - 1)
                    window['-PROGRESS SLIDER-'].update(self.frame_count)
                    self.cap.set(cv2.CAP_PROP_POS_FRAMES, self.frame_count)

                if self.event == '>':
                    self.frame_count = self.frame_count + 1
                    window['-PROGRESS SLIDER-'].update(self.frame_count)
                    self.cap.set(cv2.CAP_PROP_POS_FRAMES, self.frame_count)

                if self.event == '>>':
                    self.frame_count = self.frame_count + 30
                    window['-PROGRESS SLIDER-'].update(self.frame_count)
                    self.cap.set(cv2.CAP_PROP_POS_FRAMES, self.frame_count)

                if self.event == '>>>':
                    self.frame_count = self.frame_count + 150
                    window['-PROGRESS SLIDER-'].update(self.frame_count)
                    self.cap.set(cv2.CAP_PROP_POS_FRAMES, self.frame_count)

                # カウンタがエンドフレーム以上になった場合、スタートフレームから再開
                if self.frame_count >= self.e_frame:
                    self.cap.set(cv2.CAP_PROP_POS_FRAMES, self.s_frame)
                    self.frame_count = self.s_frame
                    window['-PROGRESS SLIDER-'].update(self.frame_count)
                    continue

                # ストップボタンで動画の読込を一時停止
                if self.event == 'Play / Stop':
                    self.stop_flg = not self.stop_flg

                # ストップフラグが立っており、eventが発生した場合以外はcountinueで
                # 操作を停止しておく

                # ストップボタンが押された場合は動画の処理を止めるが、何らかの
                # eventが発生した場合は画像の更新のみ行う
                # mouse操作を行っている場合も同様
                if(
                    (
                        self.stop_flg
                        and self.event == "__TIMEOUT__"
                    )
                ):
                    window['-PROGRESS SLIDER-'].update(self.frame_count)
                    continue

                # スキップフレーム分とばす
                if not self.stop_flg and values['-SKIP SLIDER-'] != 0:
                    self.frame_count += values["-SKIP SLIDER-"]
                    self.cap.set(cv2.CAP_PROP_POS_FRAMES, self.frame_count)

                # フレームの読込 ##############################################
                self.ret, self.frame = self.cap.read()                
                self.valid_frame = int(self.frame_count - self.s_frame)
                # 最後のフレームが終わった場合self.s_frameから再開
                if not self.ret:
                    self.cap.set(cv2.CAP_PROP_POS_FRAMES, self.s_frame)
                    self.frame_count = self.s_frame
                    continue

                # 以降にフレームに対する処理を記述 ##################################
                # frame全体に対する処理をはじめに実施 ##############################
                reduction_ratio = 1.5
                self.frame = cv2.resize(self.frame, dsize=(int(self.width/reduction_ratio), int(self.height/reduction_ratio)))


                
                # フレーム数と経過秒数の表示
                cv2.putText(
                    self.frame, str("frame: {0:.0f}".format(self.frame_count)), (
                        5, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (250, 250, 0), 1, cv2.LINE_AA
                )
                cv2.putText(
                    self.frame, str("time: {0:.1f} s".format(
                        self.frame_count / self.fps)), (5, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (250, 250, 0), 1, cv2.LINE_AA
                )

                # 画像を表示
                cv2.imshow("Movie", self.frame)

                if self.stop_flg:
                    self.cap.set(cv2.CAP_PROP_POS_FRAMES, self.frame_count)

                else:
                    self.frame_count += 1
                    window['-PROGRESS SLIDER-'].update(self.frame_count + 1)

        finally:
            cv2.destroyWindow("Movie")
            self.cap.release()
            window.close()


if __name__ == '__main__':
    Main().run()