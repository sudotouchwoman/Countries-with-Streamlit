'''
Module implements API for getting data from server or (if unable or told to) local files
'''
import os
import requests
import streamlit as st
import json
import schema


class DataSource:
    BASEDIR:str = None
    REMOTESRC:dict = None
    LOCALSRC:dict = None
    ENCODING:str = None
    FORMAT:str = None
    CONTEXT:dict = None
    def __init__(self, options) -> None:
        self.BASEDIR = os.getcwd()
        self.FROM_LOCAL = False
        if isinstance(options,dict):
            self.REMOTESRC = options.get('REMOTE', None)
            self.LOCALSRC = options.get('LOCAL', None)
            self.ENCODING = options.get('ENCODING','utf-8')
            self.FORMAT = options.get('FORMAT', 'json')
        if isinstance(options, str):
            self.LOCALSRC = dict()
            self.ENCODING = 'utf-8'
            self.FORMAT = 'json'
            self.LOCALSRC['PATH']=options


    @st.cache(persist = True, show_spinner=False, suppress_st_warning=True)
    def load_target_string(self, CONTEXT:dict) -> str:
        RESULT = None
        if self.REMOTESRC:
            RESULT = self.get_from_remote(CONTEXT)
        if RESULT is None:
            RESULT = self.get_from_local()
        return RESULT


    @st.cache(persist = True, show_spinner=False, suppress_st_warning=True, allow_output_mutation=True)
    def unpack_target(self, CONTEXT:dict = None):
        if self.FORMAT == 'json':
            try:
                #st.code(self.load_target_string(CONTEXT))
                FETCHED = json.loads(self.load_target_string(CONTEXT))
                if self.FROM_LOCAL == True:
                    return apply_context_filter(FETCHED,CONTEXT)
                return FETCHED
            except json.JSONDecodeError:
                return None


    def get_from_local(self) -> str:
        try:
            PATH = os.path.join(self.BASEDIR, self.LOCALSRC['PATH'])
        except KeyError:
            return None
        if os.path.isfile(PATH):
            with open(PATH, 'r', encoding= self.ENCODING) as FILE:
                INFILE = (FILE.read())
                self.FROM_LOCAL = True
                #st.info(INFILE)
                return INFILE
        else:
            return None

    @st.cache(persist = True, show_spinner=False, suppress_st_warning=True)
    def get_from_remote(self, CONTEXT:dict) -> str:
        try:
            SESSION = requests.Session()
            URL =self.REMOTESRC['HEAD']+self.REMOTESRC['HOST']+self.REMOTESRC['PORT']+self.REMOTESRC['ROUTE']
            PARAMS = CONTEXT
            TIMEOUT = tuple(self.REMOTESRC['TIMEOUT'])
        except KeyError:
            return None
        try:
            RESPONSE = SESSION.get(url=URL, params=PARAMS, timeout= TIMEOUT)
        except requests.RequestException:
            RESPONSE = None
        if not RESPONSE or RESPONSE.status_code != 200:
            return None
        RESPONSE.encoding = self.ENCODING
        return RESPONSE.text


@st.cache(persist = True, show_spinner=False, suppress_st_warning=True)
def pack_DataSource_settings(remote:dict, local:dict, encoding:str = 'utf-8', format:str = 'json') -> dict:
    return {
        'REMOTE'    :   remote,
        'LOCAL'     :   local,
        'ENCODING'  :   encoding,
        'FORMAT'    :   format 
    }


@st.cache(persist = True, show_spinner=False, suppress_st_warning=True)
def apply_context_filter(to_resolve:dict, context:dict) -> dict:
        if to_resolve is None:
            return None
        if context is None:
            return to_resolve
        for element in to_resolve:
            assume_OK = True
            for key, value in context.items():
                if element[key] != value:
                    assume_OK = False
                    break
            if assume_OK == True:
                return element