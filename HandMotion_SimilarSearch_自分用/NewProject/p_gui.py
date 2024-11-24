import PySimpleGUI as sg
import os

import my_functions as my

p_gui_values_file = "values/p_gui_values.txt"

def load_dict():
    values_dict = {}
    with open(p_gui_values_file, "r") as f:
        for line in f:
            key, value = line.split(":")# 行をコロンで分割してキーと値に分ける
            values_dict[key] = value.strip() # 改行コードを削除するためにstrip()を使う
    
    return values_dict


def save_dict(values_dict):
    # ファイルを書き込みモードで開く
    with open(p_gui_values_file, "w") as f:
        # 辞書のキーと値を1行ずつファイルに書き込む
        for key, value in values_dict.items():
            f.write(f"{key}:{value}\n")

# プログレスバー表示用クラス．
class ProgressBar():
    def __init__(self):
        self.bar_current = 1
        self.window = None
    
    # 初期設定，ループ処理前に一度呼び出す
    def set_window(self, bar_max):
        layout = [[sg.Text('実行中...')],
            [sg.ProgressBar(bar_max, orientation='h', size=(20,20), key='-PROG-')],
            [sg.Cancel()]]
        self.window = sg.Window('プログレスバー', layout)
    
    # 更新処理，ループ内で呼び出すごとにプログレスバーを更新
    def update_window(self):
        event, values = self.window.read(timeout=10)
        if event == 'Cancel' or event == sg.WIN_CLOSED:
            my.printline("プログラムを終了します")
            os.sys.exit()
        self.window['-PROG-'].update(self.bar_current)
        self.bar_current += 1

    def close_window(self):
        self.window.close()

# 入力ファイル格納ディレクトリと出力ファイル保存ディレクトリを選択
def get_dir_input_output():
    # GUIのレイアウト
    layout = [
        [
            sg.Text("入力フォルダ"),
            sg.InputText(),
            sg.FolderBrowse(key="folder_from", initial_folder="handData/key")
        ],
        [
            sg.Text("出力フォルダ"),
            sg.InputText(),
            sg.FolderBrowse(key="folder_to", initial_folder="handData/tgt")
        ],
        [
            sg.Text("出力フォルダ(平滑化あり)"),
            sg.InputText(),
            sg.FolderBrowse(key="folder_to_with_smooth", initial_folder="handData/tgt")
        ],
        [sg.Submit(key="選択"), sg.Cancel("終了")]
    ]
    # WINDOWの生成
    window = sg.Window("ファイル選択", layout)

    # イベントループ
    while True:
        event, values = window.read(timeout=100)
        if event == '終了' or event == sg.WIN_CLOSED:
            my.printline("プログラムを終了します")
            os.sys.exit()
        elif event == '選択':
            if values[0] == "":
                sg.popup("ファイルが入力されていません。")
                event = ""
            else:
                input_dir = values['folder_from'] + '/'
                output_dir = values['folder_to'] + '/'
                smoothed_output_dir = values['folder_to_with_smooth'] + '/'

                break
    window.close()
    
    return input_dir, output_dir, smoothed_output_dir

def select_key_tgt(keyName_list, tgtName_list):
    values_dict = load_dict()
    # 名前を昇順にする
    keyName_list = sorted(keyName_list, key=lambda x: (len(x), x))
    tgtName_list = sorted(tgtName_list, key=lambda x: (len(x), x))

    # ウィンドウのレイアウトを定義
    layout = [
        [sg.Text("単語と文章を選んでください")],
        [sg.Text("単語"), sg.Combo(keyName_list, size=(20, 1), key="-KEYNAME-", default_value=values_dict["key"])],
        [sg.Text("文章"), sg.Combo(tgtName_list, size=(20, 1), key="-TGTNAME-", default_value=values_dict["tgt"])],
        [sg.Button("選択"), sg.Button("終了")]
    ]

    # ウィンドウの生成
    window = sg.Window("ャ-", layout)

    # イベントループ
    while True:
        event, values = window.read()

        if event == sg.WINDOW_CLOSED or event == "終了":
            my.printline("プログラムを終了します")
            os.sys.exit()
        elif event == "選択":
            keyName = values["-KEYNAME-"]
            tgtName = values["-TGTNAME-"]
            values_dict["key"] = keyName
            values_dict["tgt"] = tgtName
            break
    
    # ウィンドウを閉じる
    save_dict(values_dict)
    window.close()
    
    return keyName, tgtName


def select_feature():
    values_dict = load_dict()

    # 特徴ラベルリスト
    with open("values/feature_label.txt", "r", encoding="utf-8") as f:
        feature_label_list = f.read().split('\n')

    # ウィンドウのレイアウトを定義
    layout = [
        [sg.Text("特徴ラベルを選んでください")],
        [sg.Combo(feature_label_list, size=(20, 1), key="-FEATURENAME-", default_value=values_dict["feature"])],
        [sg.Button("選択"), sg.Button("終了")]
    ]

    # ウィンドウの生成
    window = sg.Window("ャ-", layout)

    # イベントループ
    while True:
        event, values = window.read()

        if event == sg.WINDOW_CLOSED or event == "終了":
            my.printline("プログラムを終了します")
            os.sys.exit()
        elif event == "選択":
            featureName = values["-FEATURENAME-"]
            values_dict["feature"] = featureName
            break
    
    # ウィンドウを閉じる
    save_dict(values_dict)
    window.close()
    
    return featureName


def select_cost(cost_TH):
    # GUIのレイアウト
    layout = [
        [sg.Slider(range=(1,5000),
                    default_value =cost_TH,
                    resolution=10,
                    orientation='h',
                    size=(34.3, 15),
                    enable_events=True,
                    key='slider1')],
        [sg.Submit("選択"), sg.Cancel("終了")]
    ]
    # WINDOWの生成
    window = sg.Window("ファイル選択", layout)

    # イベントループ
    while True:
        event, values = window.read(timeout=100)
        if event == '終了' or event == sg.WIN_CLOSED:
            cost_TH = None
            break
        elif event == '選択':
            cost_TH = values["slider1"]
            break

    window.close()
    
    return cost_TH


