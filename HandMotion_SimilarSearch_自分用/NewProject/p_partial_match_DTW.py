import numpy as np
import my_functions as my
import os

class Partial_match_DTW():
    def __init__(self):
        self.key_data_usedFrames = None # key data

        self.paths = []
        self.costs = [] 
        self.dataDist = None
        
        self.dataCost = None

        self.costMatrix = None
        self.pathMatrix = None
        self.headMatrix = None

        self.keyData = None
        self.tgtData = None
        self.cost_TH = None
        self.frame_TH = None

    def set_values(self, keyData, tgtData, cost_TH, frame_TH):
        self.keyData = keyData
        self.tgtData = tgtData
        self.cost_TH = cost_TH
        self.frame_TH = frame_TH

    # 距離計算
    def get_dist(self, x, y):
        return np.sqrt((x-y)**2) # ユークリッド距離

    # 最小値返却
    def get_min_cell(self, m0, m1, m2, i, j):
        if m0 < m1:
            if m0 < m2:
                return i - 1, j, m0
            else:
                return i - 1, j - 1, m2
        else:
            if m1 < m2:
                return i, j - 1, m1
            else:
                return i - 1, j - 1, m2

    def create_matrix(self):
        x = self.tgtData # 検索される対象(ターゲット)
        y = self.keyData # 検索キー
        #dataDist = np.array(x).reshape(1, -1)**2 + np.array(y).reshape(-1, 1)**2
        #dataDist = np.sqrt((np.array(x).reshape(1, -1) - np.array(y).reshape(-1, 1))**2)

        len_x = len(x)
        len_y = len(y)
        #my.printline(len_x)
        #my.printline(len_y)

        costM = np.zeros((len_x, len_y), float)            # 合計距離行列 各点におけるパス開始点までの最短合計コストを保存
        pathM = np.zeros((len_x, len_y, 2), int)    # パス連結行列 各点において，その点を通るパスのひとつ前の点(連結関係)を保存
        headM = np.zeros((len_x, len_y), int)       # パス開始点行列 各点において，その点を通るパスの開始点を保存



        # 0列目
        costM[0, 0] = self.get_dist(x[0], y[0])
        for j in range(1, len_y):
            costM[0, j] = costM[0, j - 1] + self.get_dist(x[0], y[j])
            pathM[0, j] = [0, j - 1] # 1列目のパスは固定(縦直線)
            headM[0, j] = 0

        # i列目
        for i in range(1, len_x):
            # 0行目
            costM[i, 0] = self.get_dist(x[i], y[0])
            pathM[i, 0] = [i, 0]
            headM[i, 0] = i


            # i行目
            for j in range(1, len_y):
                # 左，下，左下のセルのうちコストが最小のセルを選択
                m_i, m_j, m_cost = self.get_min_cell(costM[i - 1, j],
                                    costM[i, j - 1],
                                    costM[i - 1, j - 1],
                                    i, j)
                costM[i, j] = m_cost + self.get_dist(x[i], y[j])
                pathM[i, j] = [m_i, m_j]
                headM[i, j] = headM[m_i, m_j]

                # 本来はココでパスの選定を行うが，選定条件をいじって実験したいため，
                # 一旦，データの前処理のみここで行う

        
        self.costMatrix = costM
        self.pathMatrix = pathM
        self.headMatrix = headM
    
    # パスのコストが小さい順に三つを取得
    def select_path_topThree(self):
        costM = self.costMatrix.copy()
        pathM = self.pathMatrix.copy()
        headM = self.headMatrix.copy()

        matrix_Xlen = len(headM[:, 0])
        matrix_Ylen = len(headM[0, :])

        for i, head_i in enumerate(headM[:, -1]):
            
            # X方向フレーム幅について，しきい値より小さいパスを候補から外す
            if not self.frame_TH == None:
                X_range = i - head_i
                if X_range < self.frame_TH:
                    costM[i, -1] = 99999 # 例外値
                    
            """
            # 不要
            # パスのコストについて，しきい値より大きいパスを候補から外す
            if not self.COST_TH == None:
                if costM[i, -1] > self.COST_TH:
                    costM[i, -1] = 99999 # 例外値
            """

        path_end_list = []
        i = 0
        while(i < matrix_Xlen): # 最終フレームまで探査
            # 開始地点が同じパスの中から，コストが最小のパスを選択
            sameHead_i_list =  np.where((headM[:, -1] == headM[i, -1]))[0] # 開始地点が同じパスのインデックス取得
            sameHead_i_min = sameHead_i_list[np.argmin(costM[sameHead_i_list[0]:(sameHead_i_list[-1]+1), -1])] # 最小選択，返却地はx方向フレーム番号
            i = i + len(sameHead_i_list) # 次の開始地点が同じパスの組を参照するため，インデックスを加算
            path_end_list.append(sameHead_i_min)

        ################################################################
        #path_end_list = [i for i in range(matrix_Xlen)] # 全のパス表示
        ################################################################

        path_list = []
        path_sect_cost_list = []
        # 選択されたパスを出力パスリストに追加
        for i in path_end_list:
            # パスのコストについて，しきい値より大きいパスを候補から外す
            if not self.cost_TH == None:
                if costM[i, -1] > self.cost_TH:
                    continue
            
            # 生き残ったパスを参照してリストに追加
            reservation_i = i
            reservation_j = matrix_Ylen - 1 
            path_conn = [[reservation_i, reservation_j]]
            path_sect_cost_list.append([headM[reservation_i, -1], reservation_i, costM[reservation_i, -1]]) # [開始フレーム, 終了フレーム]
            while(pathM[reservation_i, reservation_j][1] != 0):
                conn = pathM[reservation_i, reservation_j]
                path_conn.append([conn[0], conn[1]]) # 通過したマスとコストを保存
                reservation_i = conn[0]
                reservation_j = conn[1]
            path_list.append(path_conn)
            

        return path_list, path_sect_cost_list
    
    # パスのコストが小さい順に三つを取得
    def select_path(self):
        costM = self.costMatrix.copy()
        pathM = self.pathMatrix.copy()
        headM = self.headMatrix.copy()

        matrix_Xlen = len(headM[:, 0])
        matrix_Ylen = len(headM[0, :])

        

        path_end_i_list = []
        sameHead_i_list = [0] # 開始地点が同じパスの，終了地点(i)を格納
        for i in range(1, matrix_Xlen): # 条件2の処理に合わせるため，どうせ使わない0フレーム目はスキップ
            
            # パス選択条件１ ###############################################
            # パスの区間サイズが小さすぎるものを除外
            if not self.frame_TH == None:
                sectionSize = i - headM[i, -1]
                if sectionSize < self.frame_TH:
                    costM[i, -1] = 999999 # 例外値
            
            """
            # 不要
            # パスのコストについて，しきい値より大きいパスを候補から外す
            if not self.COST_TH == None:
                if costM[i, -1] > self.COST_TH:
                    costM[i, -1] = 99999 # 例外値
            """

            # パス選択条件2 ###############################################
            if headM[i-1, -1] == headM[i, -1] and i < matrix_Xlen - 1: # 前回参照のパスと現在参照のパスの開始地点が同じ場合（もしくは最終フレーム）
                sameHead_i_list.append(i)

            
            else:
                section_i_first = sameHead_i_list[0]
                section_i_end = sameHead_i_list[-1]
                section_i_costMin = np.argmin(costM[section_i_first:(section_i_end + 1), -1])
                i_costMin = sameHead_i_list[section_i_costMin]
                path_end_i_list.append(i_costMin)
                sameHead_i_list = [i]

        ################################################################
        #path_end_list = [i for i in range(matrix_Xlen)] # 全のパス表示
        ################################################################

        path_list = []
        path_sect_cost_list = [] # [開始フレーム, 終了フレーム, コスト]

        # 選択されたパスを出力パスリストに追加
        for i in path_end_i_list:
            # パスのコストについて，しきい値より大きいパスを候補から外す
            if not self.cost_TH == None:
                if costM[i, -1] > self.cost_TH:
                    continue
            
            # 生き残ったパスを参照してリストに追加
            reservation_i = i
            reservation_j = matrix_Ylen - 1 
            path_conn = [[reservation_i, reservation_j]]
            path_sect_cost_list.append([headM[reservation_i, -1], reservation_i, costM[reservation_i, -1]]) # [開始フレーム, 終了フレーム]
            while(pathM[reservation_i, reservation_j][1] != 0):
                conn = pathM[reservation_i, reservation_j]
                path_conn.append([conn[0], conn[1]]) # 通過したマスとコストを保存
                reservation_i = conn[0]
                reservation_j = conn[1]
            conn = pathM[reservation_i, 0]
            path_conn.append([conn[0], conn[1]]) # 終点
            
            path_list.append(path_conn)
            
        
        return path_list, path_sect_cost_list

if __name__ == '__main__':
    pass