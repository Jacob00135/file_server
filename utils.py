import os.path
import filetype
import mimetypes
from models import Directory


class FileItem(object):

    def __init__(self, visible_dir_path: str, path: str, file_name: str):
        self.visible_dir_path: str = visible_dir_path
        self.path: str = path
        self.name: str = file_name

        # 检查相对子目录路径
        self.path: str = self.path.replace('/', '\\')
        if self.path.startswith('\\'):
            self.path: str = self.path[1:]

        # 检查完整的文件路径
        self.page_dir_path = os.path.abspath(os.path.join(self.visible_dir_path, self.path))
        self.full_path: str = os.path.abspath(os.path.join(self.page_dir_path, self.name))
        if not os.path.exists(self.full_path):
            raise OSError

        # 获取文件类型和文件大小
        if os.path.isdir(self.full_path):
            self.path: str = os.path.join(self.path, self.name).replace('/', '\\')
            if self.path.endswith('\\'):
                self.path = self.path[:-1]
            self.file_type: str = 'dir'
            self.size: str = ''
        else:
            self.file_type: str = self.get_file_type(self.full_path)
            self.size: str = self.get_file_size(self.full_path)

    @staticmethod
    def get_file_type(file_path: str) -> str:
        # 根据文件扩展名识别压缩包
        extension: str = os.path.basename(file_path).split('.')[-1]
        if extension in ['7z', 'gz', 'zip', 'rar', 'tar']:
            return 'package'

        # 获取mimetype
        kind = filetype.guess(file_path)
        if kind is not None:
            mime_type = kind.mime.split('/')[0]
        else:
            kind = mimetypes.guess_type(file_path)[0]
            if kind is None:
                return 'other'
            mime_type = kind.split('/')[0]

        # 返回类型
        if mime_type in ['text', 'image', 'audio', 'video']:
            return mime_type
        return 'other'

    @staticmethod
    def get_file_size(file_path: str) -> str:
        size: float = os.path.getsize(file_path)
        unit_list = ['B', 'KB', 'MB', 'GB', 'TB']
        index = 0
        while size >= 1024:
            size = size / 1024
            index = index + 1
        return '{}{}'.format(round(size, 2), unit_list[index])

    @property
    def is_visible_dir(self) -> bool:
        return Directory.query.filter_by(dir_path=self.full_path).first() is not None

    @property
    def is_dir(self) -> bool:
        return self.file_type == 'dir'

    def __repr__(self):
        return '<FileItem "{}">'.format(self.path)


def sort_file_item(file_item_list: list) -> None:
    """对FileItem对象按类型排序（冒泡排序）"""
    weight_map = {
        'dir': 6,
        'package': 5,
        'video': 4,
        'audio': 3,
        'image': 2,
        'text': 1,
        'other': 0
    }
    length = len(file_item_list)
    for i in range(length):
        for j in range(length - i - 1):
            file_item_1 = file_item_list[j]
            file_item_2 = file_item_list[j + 1]
            if weight_map[file_item_1.file_type] < weight_map[file_item_2.file_type]:
                file_item_list[j], file_item_list[j + 1] = file_item_list[j + 1], file_item_list[j]
