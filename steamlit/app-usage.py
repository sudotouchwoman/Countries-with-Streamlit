import os
from typing import Text
import requests
import json
import streamlit as st
import numpy as np
import pandas as pd
import networkx as nx
import schema
import datetime
import matplotlib.pyplot as plt
import matplotlib.dates as mdates



#   The concept is quite simple: we have out app engine class which wraps the whole thing up
#   in the spaghetti insides of it PageExposer sublasses are created for each certain page
#   (by now i only finished 1-st page, the Plot and Table). The data is grabbed from either remote server or local file
#   (well, frankly speaking, my trivial flask app just does the same thing - like opening and parsing the file from local dir,
#   but the importance is all about how requests are made. hell it took me like 5 hours till i finally fixed all the bugs and stuff.
#   the local load works fine, but slightly slow - due to a complicated try-catch rolleycoaster)


class PageExposer:
    BASEDIR:str = None
    REMOTE:dict = None
    LOCAL:dict = None
    CONTENT:dict = None
    def __init__(self, settings:dict) -> None:
        self.BASEDIR = os.getcwd()
        self.ENCODING = settings.get('ENCODING', 'utf-8')
        self.FORMAT = settings.get('FORMAT', 'json')
        for ATTRNAME, ATTRVALUE in settings.items():
            self.__setattr__(ATTRNAME, ATTRVALUE)


    def markup_page(self, UI_SRC:dict) -> dict:
        OPTIONS = pack_DataSource_settings(
            remote= UI_SRC['REMOTE'],
            local= UI_SRC['LOCAL']
        )
        ds = DataSource(OPTIONS)
        self.UI_INFO = ds.unpack_target(None)
        return self.UI_INFO is not None  


    @st.cache(persist = True, show_spinner=False, suppress_st_warning=True)
    def fetch_data(self, context:dict) -> dict:
        OPTIONS = pack_DataSource_settings(
            remote=self.CONTENT['REMOTE'],
            local=self.CONTENT['LOCAL']
        )
        ds = DataSource(OPTIONS)
        return ds.unpack_target(context)


    def set_options(self) -> bool:
        UI = pack_DataSource_settings(
            self.UI['REMOTE'],
            self.UI['LOCAL'],
            'utf-8',
            self.UI.get('FORMAT', None))
        self.expose() if self.markup_page(UI) else st.error('Failed to markup the page!')


    def expose(self) -> bool:
        st.info('This is a blank page of base class. Inherit from this class to make things brighter!')
        return True


    def show_selected(self) -> bool:
        st.info('Nothing to select, this is base class method!')
        return True


class EstimationPage(PageExposer):
    def __init__(self, settings:dict) -> None:
        super().__init__(settings)
        self.set_options()


    def expose(self) -> bool:
        TEXT = self.TEXT
        st.success('Estimation method called!')
        sbox = st.selectbox(TEXT['select_country'], self.UI_INFO['COUNTRIES'])
        CONTEXT = {
            'country':sbox
        }
        FETCHED = self.fetch_data(CONTEXT)
        if FETCHED is None:
            st.warning('Failed to load contents!')
            return
        self.show_selected(FETCHED)


    def show_selected(self, FETCHED:dict) -> bool:
        timeline = self.form_dates_from_strings(FETCHED['timestamps'])
        columns = st.beta_columns(2)
        with columns[0]:
            st.pyplot(self.show_plot(timeline, [FETCHED['facts'], FETCHED['forecast']]))
        with columns[1]:
            st.table(self.create_table(FETCHED))


    def show_plot(self, xaxis:np.ndarray, yaxis:np.ndarray):
        fig = plt.figure()
        ax = fig.add_subplot(111)
        for idx, yvalues in enumerate(yaxis):
            ax.plot(xaxis,
                    yvalues,
                    color=self.PLOT['linestyling']['colors'][idx],
                    linestyle=self.PLOT['linestyling']['linestyles'][idx])

        ax.xaxis.set_major_formatter(mdates.DateFormatter(self.PLOT['timeformat']))
        plt.ylabel(self.PLOT['yaxisname'])
        plt.xlabel(self.PLOT['xaxisname'])
        plt.legend(self.PLOT['legend'], loc = self.PLOT['loc'])
        fig.autofmt_xdate()
        return fig


    def create_table(self, FETCHED:dict)->pd.DataFrame:
        contents = {
            self.PLOT['xaxisname']  : FETCHED['timestamps'],
            self.PLOT['legend'][0]  : FETCHED['forecast'],
            self.PLOT['legend'][1]  : FETCHED['facts']
        }
        dtable = pd.DataFrame(contents)
        dtable.index += 1
        return dtable


    @st.cache(persist = True, show_spinner=False)
    def form_dates_from_strings(self, timeline)->np.ndarray:
        dates_from_string = [ datetime.datetime.strptime(date, self.PLOT['timeformat']).date() for date in timeline]
        return np.array(dates_from_string)


class VariantsPage(PageExposer):
    def __init__(self, settings: dict) -> None:
        super().__init__(settings)
        self.set_options()


    def expose(self) -> bool:
        TEXT = self.TEXT
        st.success('Variants method called!')
        with st.form('variants'):
            columns = st.beta_columns(3)
            with columns[0]:
                country = st.selectbox(TEXT['columns'][0], self.UI_INFO['COUNTRIES'], help=TEXT['help'][0])
            with columns[1]:
                date = st.date_input(
                    TEXT['columns'][1],
                    value=datetime.date.today(),
                    #min_value=self.UI_INFO['DATE']['min'],
                    #max_value=self.UI_INFO['DATE']['max'],
                    help=TEXT['help'][1]
                    )
            with columns[2]:
                option = st.selectbox(TEXT['columns'][2], self.UI_INFO['OPTIONS'])
            SUBMIT_BUTTON = st.form_submit_button(label=TEXT['submit_button'])
            CONTEXT = {
                'country':country,
                #'date':date,
                'option':option
            }
        if SUBMIT_BUTTON:
            FETCHED = self.fetch_data(CONTEXT)
            if FETCHED is None:
                st.warning('Failed to load contents!')
                return
            self.show_selected(FETCHED)


    def show_selected(self, FETCHED:dict) -> bool:
        TEXT = self.TEXT
        numeric_output = (
            FETCHED['real_value'],
            FETCHED['delta'],
            FETCHED['required_force'],
            FETCHED['required_publications'])
        self.form_table_header(numeric_output)
        st.table(self.build_table(FETCHED['contents']))
        pass


    def form_table_header(self, numeric_output:tuple):
        TEXT = self.TEXT
        columns = st.beta_columns(3)
        with columns[0]:
            line =' ('+ ["","+"][numeric_output[1]>0] + str(numeric_output[1]) + ')'
            st.markdown(TEXT['fetched'][0] + str(numeric_output[0]) + line)
        with columns[1]:
            st.markdown(TEXT['fetched'][1] + str(numeric_output[2]))
        with columns[2]:
            st.markdown(TEXT['fetched'][2] + str(numeric_output[3]))
        pass


    
    @st.cache(persist = True, show_spinner=False)
    def build_table(self, CONTENTS:dict) -> pd.DataFrame:
        TABLE_STYLE = self.TABLE['styling']
        dtable = pd.DataFrame(CONTENTS)
        for col in (TABLE_STYLE['percents']):
            dtable[col] = dtable[col].apply(lambda x: "{0:.2f}%".format(x*100))
        for col in (TABLE_STYLE['commas']):
            dtable[col] = dtable[col].apply(lambda x: ', '.join(x))
        dtable.sort_values(by='theme', inplace=False)
        dtable.reset_index(drop=True, inplace=True)
        dtable.index += 1
        dtable = dtable[self.UI_INFO['ORDER']]
        dtable.rename(columns=self.UI_INFO['LAYOUT'], inplace=True)
        return dtable






class AppEngine:
    BASEDIR:str = None
    ENCODING:str = None
    def __init__(self, settings:dict) -> None:
        st.set_page_config(layout="wide", page_title= 'App 2.0')
        self.BASEDIR = settings.get('BASEDIR', os.getcwd())
        self.ENCODING = settings.get('ENCODING', 'utf-8')
        if not self.load_configs(settings.get('CONFIG_PATH', None)):
            st.error('Failed to load main config! App stopped')


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
            PAGETYPE = EstimationPage
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
        self.SBARINDEX = {
            val:idx for idx, val in enumerate(SIDEBAR['pagenames'])
        }


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


    @st.cache(persist = True, show_spinner=False, suppress_st_warning=True)
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
                

if __name__ == '__main__':
    SETTINGS = {
        'CONFIG_PATH': '../configs/conf_main.json',
#        'CONFIG_PATH': 'configs/conf_main.json',
#   used this to debug the application (my rel-paths broke somehow,
#   maybe VSCode considers debugging from the ~ project directory only) 
#   whatever, the 1-st page works fine now, requests are done properly
#   and this is what i was heading towards to 
        'ENCODING':'utf-8'
    }
#   i also have modified the JSON-s, now they look more kinda mature,
#   not like the first one i have written (lord forgive me)
    app = AppEngine(SETTINGS)
    app.run_app()