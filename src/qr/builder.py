
import os
import numpy as np
import qr.constants as constants

# Class that manages loading data streams into qr
class QRCodeBuilder:
    def __init__(self, matrix: np.array = np.zeros((25,25), dtype=int)):
        self.qr_matrix = matrix
        self.fill_finder_patterns()

    def fill_finder_patterns(self) -> None:
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        f = open(os.path.join(project_root, 'src', 'qr', 'res', 'function_patterns.txt'))
        i = 0
        for line in f.readlines():
            j = 0
            for val in line.split():
                self.qr_matrix[i,j] = int(val)
                j += 1
            i += 1

    def print_matrix(self) -> None:
        for i in range(self.qr_matrix.shape[0]):
            for j in range(self.qr_matrix.shape[1]):
                print(self.qr_matrix[i, j], end=" ")
            print()

    def load_stream_in_qr(self, data: str) -> None:
        matrix = self.qr_matrix
        n = 25

        data = list(data)
        for i in range(len(data)):
            if data[i] == '1':
                data[i] = 0
            else:
                data[i] = 1

        group_idx, col_idx, ch_idx = 0, 24, 0
        data_length = len(data)

        while ch_idx < data_length and group_idx <= 12:
            if group_idx == 9:
                # at this group we encounter the vertical timing pattern. Here we skip 1 column:
                col_idx -= 1

            #print(f'Filling group: {group_idx}, and col_idx at {col_idx}')

            if group_idx % 2 == 0:
                #fill from bottom to top
                for line in range(n-1, -1, -1):
                    el_r = matrix[line, col_idx]
                    el_l = matrix[line, col_idx-1] if col_idx-1 >= 0 else -1

                    if el_r == 4:
                        #it is not reserved
                        matrix[line, col_idx] = data[ch_idx]
                        ch_idx += 1

                    if ch_idx >= data_length:
                        break

                    if el_l == 4:
                        #it is not reserved
                        matrix[line, col_idx-1] = data[ch_idx]
                        ch_idx += 1

                col_idx -= 2
            else:
                #fill from top to bottom
                for line in range(0, n):
                    el_r = matrix[line][col_idx]
                    el_l = matrix[line, col_idx-1] if col_idx-1 >= 0 else -1
                    if el_r == 4:
                        #it is not reserved
                        matrix[line, col_idx] = data[ch_idx]
                        ch_idx += 1

                    if ch_idx >= data_length:
                        break

                    if el_l == 4:
                        #it is not reserved
                        matrix[line, col_idx-1] = data[ch_idx]
                        ch_idx += 1
                col_idx -= 2

            if ch_idx >= data_length:
                break
            group_idx += 1

    def apply_mask(self, mask_idx:int) -> None:
        if mask_idx == 0:
            self.mask0()
        elif mask_idx == 1:
            self.mask1()
        elif mask_idx == 2:
            self.mask2()
        elif mask_idx == 3:
            self.mask3()
        elif mask_idx == 4:
            self.mask4()
        elif mask_idx == 5:
            self.mask5()
        elif mask_idx == 6:
            self.mask6()
        elif mask_idx == 7:
            self.mask7()

        self.apply_format_info(constants.FORMAT_STRING[mask_idx])


    def mask0(self)-> None:
            a = np.zeros((25,25), dtype=int)
            f = open('./res/function_patterns.txt')
            i = 0
            for line in f.readlines():
                j = 0
                for val in line.split():
                    a[i,j] = int(val)
                    j += 1
                i += 1
            # Iterate through matrix
            for i in range(self.qr_matrix.shape[0]):
                for j in range(self.qr_matrix.shape[1]):
                    if self.qr_matrix[i,j] in [0,1] and (i + j) % 2 == 0 and a[i,j] == 4:
                        self.qr_matrix[i,j] = 1 - self.qr_matrix[i,j]

    def mask1(self)-> None:
        a = np.zeros((25,25), dtype=int)
        f = open('./res/function_patterns.txt')
        i = 0
        for line in f.readlines():
            j = 0
            for val in line.split():
                a[i,j] = int(val)
                j += 1
            i += 1
            # Iterate through matrix
        for i in range(self.qr_matrix.shape[0]):
            for j in range(self.qr_matrix.shape[1]):
                if self.qr_matrix[i,j] in [0,1] and i % 2 == 0 and a[i,j] == 4:
                    self.qr_matrix[i,j] = 1 - self.qr_matrix[i,j]


    def mask2(self)-> None:
        a = np.zeros((25,25), dtype=int)
        f = open('./res/function_patterns.txt')
        i = 0
        for line in f.readlines():
            j = 0
            for val in line.split():
                a[i,j] = int(val)
                j += 1
            i += 1
            # Iterate through matrix
        for i in range(self.qr_matrix.shape[0]):
            for j in range(self.qr_matrix.shape[1]):
                if self.qr_matrix[i,j] in [0,1] and j % 3 == 0 and a[i,j] == 4:
                    self.qr_matrix[i,j] = 1 - self.qr_matrix[i,j]


    def mask3(self)-> None:
        a = np.zeros((25,25), dtype=int)
        f = open('./res/function_patterns.txt')
        i = 0
        for line in f.readlines():
            j = 0
            for val in line.split():
                a[i,j] = int(val)
                j += 1
            i += 1
            # Iterate through matrix
        for i in range(self.qr_matrix.shape[0]):
            for j in range(self.qr_matrix.shape[1]):
                if self.qr_matrix[i,j] in [0,1] and (i+j) % 3 == 0 and a[i,j] == 4:
                    self.qr_matrix[i,j] = 1 - self.qr_matrix[i,j]


    def mask4(self)-> None:
        a = np.zeros((25,25), dtype=int)
        f = open('./res/function_patterns.txt')
        i = 0
        for line in f.readlines():
            j = 0
            for val in line.split():
                a[i,j] = int(val)
                j += 1
            i += 1
            # Iterate through matrix
        for i in range(self.qr_matrix.shape[0]):
            for j in range(self.qr_matrix.shape[1]):
                if self.qr_matrix[i,j] in [0,1] and ((int(i/2) + int(j/3)) % 2) == 0 and a[i,j] == 4:
                    self.qr_matrix[i,j] = 1 - self.qr_matrix[i,j]


    def mask5(self)-> None:
        a = np.zeros((25,25), dtype=int)
        f = open('./res/function_patterns.txt')
        i = 0
        for line in f.readlines():
            j = 0
            for val in line.split():
                a[i,j] = int(val)
                j += 1
            i += 1
            # Iterate through matrix
        for i in range(self.qr_matrix.shape[0]):
            for j in range(self.qr_matrix.shape[1]):
                if self.qr_matrix[i,j] in [0,1] and (((i*j) % 2) + ((i*j) % 3)) == 0 and a[i,j] == 4:
                    self.qr_matrix[i,j] = 1 - self.qr_matrix[i,j]


    def mask6(self)-> None:
        a = np.zeros((25,25), dtype=int)
        f = open('./res/function_patterns.txt')
        i = 0
        for line in f.readlines():
            j = 0
            for val in line.split():
                a[i,j] = int(val)
                j += 1
            i += 1
            # Iterate through matrix
        for i in range(self.qr_matrix.shape[0]):
            for j in range(self.qr_matrix.shape[1]):
                if self.qr_matrix[i,j] in [0,1] and ((((i*j) % 2) + ((i*j) % 3))%2) == 0 and a[i,j] == 4:
                    self.qr_matrix[i,j] = 1 - self.qr_matrix[i,j]


    def mask7(self)-> None:
        a = np.zeros((25,25), dtype=int)
        f = open('./res/function_patterns.txt')
        i = 0
        for line in f.readlines():
            j = 0
            for val in line.split():
                a[i,j] = int(val)
                j += 1
            i += 1
            # Iterate through matrix
        for i in range(self.qr_matrix.shape[0]):
            for j in range(self.qr_matrix.shape[1]):
                if self.qr_matrix[i,j] in [0,1] and ((((i+j) % 2) + ((i*j) % 3)) % 2) == 0 and a[i,j] == 4:
                    self.qr_matrix[i,j] = 1 - self.qr_matrix[i,j]


    def apply_format_info(self, format_string: str) -> None:
        if len(format_string) != 15:
            print('Invalid format string!')
            return

        # Invert bits and convert to integers
        bits = [0 if int(b) == 1 else 1 for b in format_string]

        # Define coordinate mappings for the two format info sections
        coords_top_left = [
            (8, 0), (8, 1), (8, 2), (8, 3), (8, 4), (8, 5),
            (8, 7), (8, 8), (7, 8), (5, 8), (4, 8), (3, 8),
            (2, 8), (1, 8), (0, 8)
        ]
        coords_bottom_left = [
            (24, 8), (23, 8), (22, 8), (21, 8), (20, 8), (19, 8),
            (18, 8), (8, 17), (8, 18), (8, 19), (8, 20), (8, 21),
            (8, 22), (8, 23), (8, 24)
        ]

        # Apply the format bits to the matrix using the coordinate mappings
        for idx, (i, j) in enumerate(coords_top_left):
            self.qr_matrix[i, j] = bits[idx]
        for idx, (i, j) in enumerate(coords_bottom_left):
            self.qr_matrix[i, j] = bits[idx]

    def get_matrix(self) -> np.array:
        return self.qr_matrix

    def best_mask(self) -> int:
        # condition 1: row by row
        penalty = 0
        for i in range (0,25):
            cnt = 1
            for j in range (1,25):
                if self.qr_matrix[i,j] == self.qr_matrix[i, j-1]:
                    cnt += 1
                else:
                    if cnt >= 5:
                        penalty += (cnt-5) + 3
                    cnt = 1
            if cnt >= 5:
                penalty += (cnt-5) + 3
        # column by column
        for i in range (0,25):
            cnt = 1
            for j in range (1,25):
                if self.qr_matrix[j - 1,i] == self.qr_matrix[j, i]:
                    cnt += 1
                else:
                    if cnt >= 5:
                        penalty += (cnt-5) + 3
                    cnt = 1
            if cnt >= 5:
                penalty += (cnt - 5) + 3
        cnt = 0
        # condition 2: solid color blocks
        for i in range(24):  # Rows 0 to 23 (inclusive)
            for j in range(24):  # Columns 0 to 23 (inclusive)
            # Check if all 4 cells in the 2x2 block are the same
                if (
                    self.qr_matrix[i][j] == self.qr_matrix[i][j+1]
                    and self.qr_matrix[i][j] == self.qr_matrix[i+1][j]
                    and self.qr_matrix[i][j] == self.qr_matrix[i+1][j+1]
                ):
                    penalty += 3

        # condition 3: patterns of modules
        pattern1 = [0,1,0,0,0,1,0,1,1,1,1]
        pattern2 = [1,1,1,1,0,1,0,0,0,1,0]
        for i in range(25):
            for j in range (25):
                cnt1 = 0
                cnt2 = 0
                for c in range (11):
                    if j + c < 25:
                        if self.qr_matrix[i,j + c] == pattern1[c]:
                            cnt1 += 1
                        if self.qr_matrix[i,j + c] == pattern2[c]:
                            cnt2 += 1
                        if cnt1 == 11 or cnt2 == 11:
                            penalty += 40
        for i in range(25):
            for j in range (25):
                cnt1 = 0
                cnt2 = 0
                for c in range (11):
                    if j + c < 25:
                        if self.qr_matrix[j + c,i] == pattern1[c]:
                            cnt1 += 1
                        if self.qr_matrix[j + c,i] == pattern2[c]:
                            cnt2 += 1
                        if cnt1 == 11 or cnt2 == 11:
                            penalty += 40

        # condition 4: no of blocks
        total_modules = 625
        white = 0
        for i in range (25):
            for j in range (25):
                if self.qr_matrix[i,j] == 1:
                    white += 1
        black = total_modules - white
        percent = int((black/total_modules) * 100)
        if percent % 10 <= 5:
            a = percent - percent % 10
            b = a + 5
            a = abs(a - 50)
            b = abs(b - 50)
            a = a // 5
            b = b // 5
            penalty += min(a,b) * 10
        else:
            a = percent - percent % 10 + 5
            b = a + 5
            a = abs(a - 50)
            b = abs(b - 50)
            a = a // 5
            b = b // 5
            penalty += min(a,b) * 10

        return penalty

    def apply_best_mask(self) -> int:
        l =[]
        mat = self.qr_matrix.copy()
        for i in range(8):
            self.qr_matrix = mat.copy()
            self.apply_mask(i)
            l.append(self.best_mask())

        self.qr_matrix = mat.copy()
        lowest = min(l)
        best_mask_idx = l.index(lowest)
        self.apply_mask(best_mask_idx)
        return (best_mask_idx, lowest)
