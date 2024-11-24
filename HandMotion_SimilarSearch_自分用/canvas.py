"C:\Users\root\Desktop\hisa_reserch\HandMotion_SimilarSearch_引継ぎ用\NewProject"

C:\Users\root\Desktop\hisa_reserch\HandMotion_SimilarSearch_引継ぎ用\NewProject>tree /a /f
フォルダー パスの一覧:  ボリューム Windows
ボリューム シリアル番号は 3EC5-9DA9 です
C:.
|   app_mediapipe_video_player.py # 選択した動画にメディアパイプを適用して再生
|   app_video_player.py # 動画再生
|   feature_from_joint.py # 旧版
|   joint_from_video.py # 旧版
|   load_handData.py # 旧版
|   mediapipe_video_player.py # 旧版
|   my_functions.py # 汎用関数
|   p1_joint_from_video.py # 動画から関節情報取得
|   p2_smooth_joint.py # 線形補完と平滑化
|   p3_feature_from_joint.py # 関節データから特徴データ作成
|   p4_search_shuwa.py # DTWによる類似検索
|   p_adjustment_cost_TH.py # しきい値調整によるパスの出力結果をリアルタイムにグラフ表示
|   p_gui.py # gui関連制御
|   p_load_handData.py # クラスによる疑似構造体としてデータを展開
|   p_partial_match_DTW.py # 旧版
|   shuwa_similarity_search.py # 旧版（search_shuwa）
|   test.py # 適当な動作確認
|   video_player.py # 旧版
|
+---handData
|   +---key
|   |   +---d1_joint # 関節データ
|   |   |       0.csv
|   |   |       ︙
|   |   |       153.csv
|   |   |
|   |   +---d2_complemented_joint # 線形補完後の関節データ
|   |   |       0.csv
|   |   |       ︙
|   |   |       153.csv
|   |   |
|   |   +---d3_smoothed_joint # 平滑化後の関節データ
|   |   |       0.csv
|   |   |       ︙
|   |   |       153.csv
|   |   |
|   |   +---d4_feature_d2 # 旧版（平滑化導入前の特徴データ）
|   |   |       0.csv
|   |   |       ︙
|   |   |       153.csv
|   |   |
|   |   +---d4_feature_d3 # 特徴データ
|   |   |       0.csv
|   |   |       ︙
|   |   |       153.csv
|   |   |
|   |   \---video # 動画データ
|   |           0.mp4
|   |           ︙
|   |           153.mp4
|   |
|   \---tgt
|       +---d1_joint
|       |       0.csv
|       |       ︙
|       |       20.csv
|       |
|       +---d2_complemented_joint
|       |       0.csv
|       |       ︙
|       |       20.csv
|       |
|       +---d3_smoothed_joint
|       |       0.csv
|       |       ︙
|       |       20.csv
|       |
|       +---d4_feature_d2
|       |       0.csv
|       |       ︙
|       |       20.csv
|       |
|       +---d4_feature_d3
|       |       0.csv
|       |       ︙
|       |       20.csv
|       |
|       \---video
|               0.mp4
|               ︙
|               20.mp4
|
+---result # p4_search_shuwa.pyの出力
|   |   search_33_part_from_4_score.png # スコアデータ（名前を変えないと上書きされる）
|   |   search_95_part_from_4_score.png
|   |   search_part95_from_4_score.png
|   |
|   +---path # p4_search_shuwa.pyのcalc_feature()関数で生成．特徴毎のパスを表示
|   |       posFromBody_0x_L.png
|   |       ︙
|   |       posFromBody_0y_R.png
|   |       posFromWrist_10x_L.png
|   |       ︙
|   |       posFromWrist_9y_R.png
|   |       vel_0x_L.png
|   |       ︙
|   |       vel_0y_R.png
|   |
|   \---values
|           cost_TH_dict.txt # 使用したしきい値
|           names.txt # 使用した単語と文章
|
+---similar_sections # 目視で求めた類似区間（フレーム）（スコアデータに描画）
|       tgt4_key13.txt
|       tgt4_key33.txt
|       tgt4_key95.txt
|
+---values
|       cost_TH_dict・・・.txt # パスの閾値
|       feature_label.txt # 特徴データラベル
|       joint_label.txt # 関節データラベル
|       p_gui_values.txt # guiへの入力履歴などが保存される
|       weight_・・・txt # スコア計算の際の重み
|
\---__pycache__# 無視
        my_functions.cpython-310.pyc
        my_functions.cpython-37.pyc
        p_gui.cpython-310.pyc
        p_gui.cpython-37.pyc
        p_load_handData.cpython-310.pyc
        p_load_handData.cpython-37.pyc
        p_partial_match_DTW.cpython-310.pyc
        p_partial_match_DTW.cpython-37.pyc