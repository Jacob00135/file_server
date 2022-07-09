import re
import os.path
import filetype
import mimetypes


class FileItem(object):

    def __init__(self, path: str):
        self.path: str = ''
        self.file_type: str = ''
        self.name: str = ''
        self.size: str = ''
        self.init_file(path)

    def init_file(self, path: str):
        path: str = path.lower().replace('/', '\\')
        if not re.findall('^[a-zA-Z]', path) or '\\' not in path or not os.path.exists(path):
            raise OSError
        self.path = os.path.abspath(path)
        self.name = os.path.basename(self.path)
        if os.path.isdir(self.path):
            self.file_type = 'dir'
        self.file_type = self.get_file_type(self.path)
        self.size = self.get_file_size(self.path)

    @staticmethod
    def get_file_type(file_path: str) -> str:
        # 根据文件扩展名识别压缩包
        extension: str = os.path.basename(file_path).split('.')[-1]
        if extension in ['7z', 'gz', 'zip', 'rar', 'tar']:
            return 'package'

        # 获取mimetype
        kind = filetype.guess(file_path)
        if kind is None:
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
