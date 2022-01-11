from django.core.files.storage import Storage

from meiduo.settings import FDFS_BASE_URL


class FastDFSStorage(Storage):

    def _open(self):
        pass

    def _save(self):
        pass

    def url(self, name):

        # 返回图片的完整路径
        return FDFS_BASE_URL + name
