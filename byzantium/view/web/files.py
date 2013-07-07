'''
	Serve files!
'''
import os
import .page

class Files(page.Page):
	cType = {
            "png":"images/png",
            "jpg":"images/jpeg",
            "gif":"images/gif",
            "ico":"images/x-icon"
			}
	file_dir = 'files'

	def serve_file(self, name):
        ext = os.path.splitext(name)[-1] # Gather extension
        if name in os.listdir(self.file_dir):  # Security
            web.header("Content-Type", self.cType[ext]) # Set the Header
            return open(os.path.join(self.file_dir, name),"rb").read() # Notice 'rb' for reading images
        return None

	def on_GET(self):
		''' example /placeholder '''
        self.set_defaults
        if self.render:
        	self.serve_file('/'.join(self.path))
        else:
            raise web.not_found()
		return
