'''
Driver file
    applies settings from SETTINGS dict loaded from .env
    then creates AppEngine and runs the app
'''
import os
from AppEngine import AppEngine

#from dotenv import load_dotenv
#dotenv_path = os.path.join(os.getcwd(),'app.env')
#load_dotenv(dotenv_path)

SETTINGS =  {
    'BASEDIR'       :   os.getcwd(),
    'LAYOUT'        :   os.getenv('LAYOUT',"wide"),
    'PAGE_NAME'     :   os.getenv('PAGE_NAME',"Тестовое приложение"),
    'PAGE_ICON'     :   os.getenv('PAGE_ICON',":warning:"),
    'ENCODING'      :   os.getenv('ENCODING', "utf-8"),
    'CONFIG_PATH'   :   os.getenv('CONFIG_PATH', "configs/conf_main.json")
}


if __name__ == '__main__':
    app = AppEngine(SETTINGS)