 '''<!--This will be adjusted later-->

import os
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SECRET_KEY'] = '11d5c86229d773022cb61679343f8232'
class DevelopmentConfig(Config): 
	DEBUG = True

	'''