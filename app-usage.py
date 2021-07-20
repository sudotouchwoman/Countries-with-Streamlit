import os
import requests
import json
import streamlit as st
import numpy as np
import pandas as pd
import networkx as nx
import schema


class PageExposer:
    BASEDIR:str = None
    def __init__(self, **settings) -> None:
        self.BASEDIR = os.getcwd()
        self.ENCODING = settings.get('ENCODING', 'utf-8')
        self.FORMAT = settings.get('FORMAT', 'json')
        for ATTRNAME, ATTRVALUE in settings.items():
            self.__setattr__(ATTRNAME, ATTRVALUE)


    def markup_page(self, UI_SRC:dict) -> dict:
        OPTIONS = {
            'REMOTE':   UI_SRC['REMOTE'],
            'LOCAL':    UI_SRC['LOCAL'],
            'FORMAT':   UI_SRC['FORMAT']
        }
        ds = DataSource(OPTIONS)
        self.UI_INFO = ds.unpack_target()
        return self.UI_INFO is not None  


    def fetch_data(self, context:dict):
        OPTIONS = {
            'REMOTE':   self.REMOTE,
            'LOCAL':    self.LOCAL,
            'FORMAT':   self.FORMAT,
            'CONTEXT':  context
        }

    def set_options(self) -> bool:
        if self.markup_page(self.UI):
            self.expose()  


    def expose(self) -> bool:
        st.info('This is a blank page of base class. Inherit from this class to make things brighter!')
        return True


    def show_selected(self) -> bool:
        st.info('Nothing to select, this is base class method!')
        return True


class EstimationPlot(PageExposer):

    def __init__(self, **settings) -> None:
        super().__init__(**settings)
        self.set_options()


    def expose(self) -> bool:
        pass


    def show_selected(self) -> bool:
        pass


class AppEngine:
    BASEDIR:str = None
    ENCODING:str = None
    def __init__(self, **settings) -> None:
        self.BASEDIR = settings.get('BASEDIR', os.getcwd())
        self.ENCODING = settings.get('ENCODING', 'utf-8')
        self.load_configs(settings.get('CONFIG_PATH', None))


    def run_app(self)->bool:
        pass


    def load_configs(self, path)->bool:
        OPTIONS = {
            'LOCAL': {
                'PATH': path
            },
            'FORMAT':'json'
        }
        ds = DataSource(OPTIONS)
        CONFIG = ds.unpack_target()
        for ATTRNAME, ATTRVALUE in CONFIG:
            self.__setattr__(ATTRNAME, ATTRVALUE)


class DataSource:
    BASEDIR:str = None
    REMOTESRC:dict = None
    LOCALSRC:dict = None
    ENCODING:str = None
    FORMAT:str = None
    def __init__(self, **options) -> None:
        self.BASEDIR = os.getcwd()
        self.REMOTESRC = options.get('REMOTE', None)
        self.LOCALSRC = options.get('LOCAL', None)
        self.ENCODING = options.get('ENCODING','utf-8')
        self.FORMAT = options.get('FORMAT', 'json')


    def load_target_string(self) -> str:
        RESULT = None
        if self.REMOTESRC:
            RESULT = self.get_from_remote()
        if RESULT is None:
            RESULT = self.get_from_local()
        return RESULT


    def unpack_target(self):
        if self.FORMAT == 'json':
            try:
                return json.loads(self.load_target_string())
            except json.JSONDecodeError:
                return None


    def get_from_local(self) -> str:
        try:
            PATH = os.path.join(self.BASEDIR, self.LOCALSRC['PATH'])
        except KeyError:
            return None
        if os.path.isfile(PATH):
            with open(PATH, 'r', encoding= self.ENCODING) as FILE:
                return FILE.read()
        else:
            return None


    def get_from_remote(self) -> str:
        try:
            SESSION = requests.Session()
            URL =self.REMOTESRC['HEAD']+self.REMOTESRC['HOST']+self.REMOTESRC['PORT']+self.REMOTESRC['ROUTE']+self.REMOTESRC['DATA']
            PARAMS = self.REMOTESRC['CONTEXT']
            TIMEOUT = tuple(self.REMOTESRC['TIMEOUT'])
        except KeyError:
            return None
        try:
            RESPONSE = SESSION.get(url=URL,  params=PARAMS, timeout= TIMEOUT)
        except requests.RequestException:
            RESPONSE = None
        if not RESPONSE or RESPONSE.status_code != 200:
            return None
        RESPONSE.encoding = self.ENCODING
        return RESPONSE.text        


if __name__ == '__main__':
    pass