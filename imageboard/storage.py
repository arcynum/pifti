from django.core.files.storage import FileSystemStorage

class MediaFileStorage(FileSystemStorage):
	def get_available_name(self, name, max_length=None):
		return name

	def _save(self, name, content):
		if self.exists(name):
			return name
		return super(MediaFileStorage, self)._save(name, content)