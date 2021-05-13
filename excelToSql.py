#  Copyright (c) 2021. 楊鵬. All Rights Reserved.

import pandas as pd

if __name__ == '__main__':
    filepath = './r3ippan3.xlsx'
    result = []
    with pd.ExcelFile(filepath) as xlsx:
        for sheetname in xlsx.sheet_names:
            df = pd.read_excel(xlsx, sheetname, index_col=None, header=None)
            row = (
                '        DB::insert("INSERT INTO insurance_rates(started_at, ended_at, prefecture_id',
                'health_insurance_rate1, health_insurance_rate2, employee_pension_rate) VALUES(\'2021/04/01\'',
                '\'2022/03/31\'',
                str(xlsx.sheet_names.index(sheetname) + 1),
                str(round(df.iloc[8, 5], 4)),
                str(round(df.iloc[8, 7], 4)),
                str(round(df.iloc[8, 9], 4)) + ');"); // ' + df.iloc[5, 0][1: -1] + '\n',
            )
            result.append(', '.join(row))
    output_file = 'sql.txt'
    with open(output_file, 'w', encoding='utf-8') as f:
        f.writelines(result)
