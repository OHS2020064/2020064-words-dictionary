import os


def file_name(file_dir):  # 获取文件夹信息
    for root, dirs, files in os.walk(file_dir):
        return files  # 返回文件列表


def process_line(line):
    words = line.split(',')[2:]
    rtn_line = '%s,%s,%s' % (words[0], words[1], words[2])
    return rtn_line
    pass


def export():
    export_path = os.path.join(os.path.abspath('../'), 'exports')
    folders = ['20210128']
    results = []
    file_names = []
    for folder in folders:
        folder_path = os.path.join(export_path, folder)
        files = file_name(folder_path)
        for file in files:
            file_ = file.replace('mba_word_', '')
            file_ = file_.replace('.csv', '')
            file_ = file_.split('_')
            for file__ in file_:
                file_names.append('%s\n' % file__)
            with open(os.path.join(folder_path, file), 'r', errors='ignore', encoding='utf-8') as f:
                text = f.read().strip()
                lines = ['%s\n' % process_line(line) for line in text.splitlines()[1:]]
            results += lines
    to_file_path = os.path.join(os.path.abspath('./'), 'finance_dict_.txt')
    with open(to_file_path, 'w', encoding='utf-8') as file:
        file.writelines(results)
    # to_file_path = os.path.join(os.path.abspath('./'), 'cats.txt')
    # with open(to_file_path, 'w', encoding='utf-8') as file:
    #     file.writelines(file_names)
    pass


if __name__ == '__main__':
    export()
