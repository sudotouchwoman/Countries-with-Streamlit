'''
Module implements classes for various pages
base class PageExposer has some basic methods and primarily
loads UI data (see markup_page) and passes control to expose() method
expose() loads content with user-selected context and displays the fetched results
now i am willing to add some data validation with schema
'''
import os
import json
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import datetime
import streamlit as st
import streamlit.components.v1 as components
import base64

from DataSource import *
from DisplayGraph import *

class PageExposer:
    BASEDIR:str = None
    REMOTE:dict = None
    LOCAL:dict = None
    CONTENT:dict = None
    TEXT:dict = None
    def __init__(self, settings:dict) -> None:
        self.BASEDIR = os.getcwd()
        self.ENCODING = settings.get('ENCODING', 'utf-8')
        self.FORMAT = settings.get('FORMAT', 'json')
        self.PAGE_CONFIG = settings
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


    def show_links(self):
        with st.beta_expander(self.LINKS['expander']):
                attrs = ['PAGE_CONFIG', 'UI_INFO','PAGE_DATA']
                for attr in attrs:
                    if hasattr(self,attr):
                        if getattr(self, attr) != None:
                            link = download_link(
                                getattr(self, attr),
                                self.LINKS[attr]['filename'],
                                self.LINKS[attr]['text'],
                                self.ENCODING)
                            st.markdown(link, unsafe_allow_html=True)        
        pass


class EstimationPage(PageExposer):
    def __init__(self, settings:dict) -> None:
        super().__init__(settings)
        self.set_options()
        self.show_links()


    def expose(self) -> bool:
        TEXT = self.TEXT
        #st.success('Estimation method called!')
        sbox = st.selectbox(TEXT['select_country'], self.UI_INFO['COUNTRIES'])
        CONTEXT = {
            'country':sbox
        }
        FETCHED = self.fetch_data(CONTEXT)
        if FETCHED is None:
            st.warning('Failed to load contents!')
            return False
        self.PAGE_DATA = FETCHED
        self.show_selected(FETCHED)
        return True


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
    TABLE:dict = None
    def __init__(self, settings: dict) -> None:
        super().__init__(settings)
        self.set_options()
        self.show_links()


    def expose(self) -> bool:
        TEXT = self.TEXT
        #st.success('Variants method called!')
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
                return False
            self.PAGE_DATA = FETCHED
            self.show_selected(FETCHED)
            return True


    def show_selected(self, FETCHED:dict) -> bool:
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
        dtable.sort_values(by='theme', inplace=True)
        dtable.reset_index(drop=True, inplace=True)
        dtable.index += 1
        dtable = dtable[self.UI_INFO['ORDER']]
        dtable.rename(columns=self.UI_INFO['LAYOUT'], inplace=True)
        return dtable


class ModelPage(PageExposer):
    MODEL:dict = None
    PYVIS:dict = None
    def __init__(self, settings: dict) -> None:
        super().__init__(settings)
        self.set_options()
        self.show_links()


    def expose(self) -> bool:
        TEXT = self.TEXT
        #st.success('Model method called!')
        with st.form('model'):
            columns = st.beta_columns(2)
            with columns[0]:
                country = st.selectbox(TEXT['selectbox_titles'][0], self.UI_INFO['COUNTRIES'])
            with columns[1]:
                pov = st.selectbox(TEXT['selectbox_titles'][1], self.UI_INFO['POV'])
            CONTEXT = {
                'country':country,
                'pov':pov
            }
            SUBMIT_BUTTON = st.form_submit_button(label=TEXT['submit_button'])
        if SUBMIT_BUTTON:
            FETCHED = self.fetch_data(CONTEXT)
            if FETCHED is None:
                st.warning('Failed to load contents!')
                return False
            self.PAGE_DATA = FETCHED
            HTML_LOC = os.path.join(self.BASEDIR, self.HTMLDIR,'_'.join(list(CONTEXT.values()))+'.html')
            self.show_selected(FETCHED, HTML_LOC)
            return True


    def show_selected(self, FETCHED:dict, HTMLfilename:list) -> bool:
        TEXT = self.TEXT
        GRAPH = DisplayGraph()
        GRAPH.fill(FETCHED, self.MODEL)
        OPTIONS = (self.PYVIS)
        OPTIONS.update({'HTML':HTMLfilename})
        GRAPH.get_pyvis(OPTIONS)

        st.markdown(TEXT['body']['model'])
        with open(HTMLfilename,'r',encoding=self.ENCODING) as html_file:
            DISPLAYABLE = html_file.read()
            components.html(DISPLAYABLE, height=600)
        st.markdown(TEXT['body']['tables'])
        TABLES = GRAPH.get_dataframes(TEXT['columns'])
        columns = st.beta_columns(2)
        for i in range(len(TABLES)):
            with columns[i%2]:
                st.dataframe(TABLES[i])


@st.cache(persist = True, show_spinner= False, suppress_st_warning=True)
def download_link(obj_to_download, download_filename, link_text, ENCODING):
    if isinstance(obj_to_download, pd.DataFrame):
        obj_to_download = obj_to_download.to_csv(index=False, encoding=ENCODING)
    if isinstance(obj_to_download, dict):
        obj_to_download = json.dumps(obj_to_download, ensure_ascii=False)
    link = base64.b64encode(obj_to_download.encode(ENCODING)).decode(ENCODING)
    return f'<a href="data:file/txt;base64,{link}" download="{download_filename}">{link_text}</a>'