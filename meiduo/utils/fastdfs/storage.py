from django.core.files.storage import Storage

from meiduo.settings import FDFS_BASE_URL


class FastDFSStorage(Storage):

    def _open(self, name, mode='rb'):
        pass

    def _save(self, name, content, max_length=None):
        pass

    def exists(self, name):
        """
        校验是否存在
        存在也可以上传
        """
        return False

    def url(self, name):
        # 返回图片的完整路径
        return FDFS_BASE_URL + name
