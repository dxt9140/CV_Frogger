import os
import platform

PROJECT_DIR = os.path.dirname(os.path.dirname(__file__))
SRC_DIR = os.path.dirname(os.path.dirname(__file__))

OS = platform.system()

if OS in ['Linux', 'Darwin']:
    TEMPLATE_DIR = PROJECT_DIR + "/Templates/"
elif OS in ['Windows']:
    TEMPLATE_DIR = PROJECT_DIR + "\\Templates\\"

