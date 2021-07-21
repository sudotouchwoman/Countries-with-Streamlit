'''
The concept is quite simple: we have out app engine class which wraps the whole thing up
in the spaghetti insides of it PageExposer sublasses are created for each certain page
(by now i only finished 1-st page, the Plot and Table). The data is grabbed from either remote server or local file
(well, frankly speaking, my trivial flask app just does the same thing - like opening and parsing the file from local dir,
but the importance is all about how requests are made. hell it took me like 5 hours till i finally fixed all the bugs and stuff.
the local load works fine, but slightly slow - due to a complicated try-catch rolleycoaster)
'''
import os
import streamlit as st
from streamlit.caching import clear_cache
from DataSource import *
from PageExposer import *


class AppEngine:
    BASEDIR:str = None
    ENCODING:str = None
    def __init__(self, settings:dict) -> None:
        self.BASEDIR = settings['BASEDIR']
        self.ENCODING = settings['ENCODING']
        st.set_page_config(
            layout=settings['LAYOUT'],
            page_title=settings['PAGE_NAME'],
            page_icon=settings['PAGE_ICON'])
        if not self.load_configs(settings['CONFIG_PATH']):
            st.error('Failed to load main config! App stopped')
            return
        self.run_app()


    def run_app(self)->bool:
        self.prefill_body()
        if self.SBARINDEX[self.sidebar] == 0:
            PAGETYPE = EstimationPage
            ds = DataSource(self.CONFIGS['estimation'])
            PAGE_CONF = ds.unpack_target()
            if PAGE_CONF is None:
                st.error('Page configuration aborted')
                return False
        if self.SBARINDEX[self.sidebar] == 1:
            PAGETYPE = VariantsPage
            ds = DataSource(self.CONFIGS['variants'])
            PAGE_CONF = ds.unpack_target()
            if PAGE_CONF is None:
                st.error('Page configuration aborted')
                return False
        if self.SBARINDEX[self.sidebar] == 2:
            PAGETYPE = ModelPage
            ds = DataSource(self.CONFIGS['model'])
            PAGE_CONF = ds.unpack_target()
            if PAGE_CONF is None:
                st.error('Page configuration aborted')
                return False
        PAGETYPE(PAGE_CONF)
        return True


    def prefill_body(self):
        SIDEBAR = self.TEXT['sidebar']
        st.sidebar.title(SIDEBAR['title'])
        self.sidebar = st.sidebar.radio(SIDEBAR['description'],SIDEBAR['pagenames'])
        CLEAR_CACHE = st.sidebar.button(SIDEBAR['cache']['button'])
        self.SBARINDEX = {
            val:idx for idx, val in enumerate(SIDEBAR['pagenames'])
        }
        if CLEAR_CACHE:
            st.success(SIDEBAR['cache']['success']) if clear_cache() else st.info(SIDEBAR['cache']['failure'])


    def load_configs(self, path)->bool:
        if path is None:
            return False
        OPTIONS = {
            'LOCAL': {
                'PATH': path
            },
            'FORMAT':'json'
        }
        ds = DataSource(OPTIONS)
        CONFIG = ds.unpack_target()
        if CONFIG is None:
            return False
        for ATTRNAME, ATTRVALUE in CONFIG.items():
            self.__setattr__(ATTRNAME, ATTRVALUE)
        return True