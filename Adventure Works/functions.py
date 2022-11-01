import re
from sys import displayhook
import pandas as pd
import matplotlib.pyplot as plt  # type: ignore
import seaborn as sns  # type: ignore
from pathlib import Path
from typing import Optional
from pandas.core.frame import DataFrame
from config.core import config


plt.style.use('dark_background')


def get_table(tabname: str, datapath: Path, sep: str = '\t') -> DataFrame:
    with open(datapath/'instawdb.sql', 'r', encoding='UTF-16') as file:
        sql_header = file.read()
    s = re.search(fr'CREATE TABLE \[[^\[]*\][.]\[{tabname}\].*?GO',
                  sql_header,
                  flags=re.DOTALL)
    assert s is not None, 'Tabela não encontrada'
    colnames = re.findall('^\s{4}\[(.*?)\]', s.group(0), flags=re.MULTILINE)
    df = pd.read_csv(datapath / f'{tabname}.csv',
                     sep=sep,
                     encoding='ISO-8859-1',
                     header=None,
                     names=colnames)
    
    df = df.astype(
    {key: value for key, value in config.datatypes.items()
        if key in df.columns})
    return df


def summarize_dtypes(df: DataFrame) -> None:
    print('\033[1m' +
          re.sub('\n',
                 '\033[0m\n',
                 df.dtypes
                   .astype(str)
                   .value_counts()
                   .rename('Quantidade')
                   .to_frame()
                   .reset_index()
                   .rename(columns={'index': 'Tipo dos Dados'})
                   .to_string(index=False),
                 1),
          end='\n\n')
    return None


def plot_null(df: DataFrame, *,
              figsize: tuple[int, int] = (10, 4),
              filter: bool = False,
              hue: Optional[str] = 'dtypes') -> None:

    plt.figure(figsize=figsize)
    df_info = pd.concat([df.dtypes.rename('dtypes'),
                         df.isnull().mean().rename('values')],
                        axis=1).reset_index()
    if filter:
        df_info = df_info.loc[df_info['values'] > 0, :]

    sns.barplot(x='index', y='values', data=df_info,
                hue=hue,
                color=(plt.rcParams['axes.prop_cycle'].by_key()['color'][0]
                       if hue is None else None),
                dodge=False).set(
        title='Valores nulos por coluna',
        xlabel='Colunas do Dataframe',
        ylabel='Percentual de valores nulos'
    )
    plt.xticks(rotation=90)
    if hue is not None:
        plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left',
                   borderaxespad=0, title='Tipo dos Dados')
    vals = plt.gca().get_yticks()
    plt.gca().yaxis.set_ticks(vals)
    plt.gca().set_yticklabels(['{:,.0%}'.format(x) for x in vals])
    plt.gca().set_ylim(top=1)
    plt.tick_params(axis='x', which='major', labelsize=7)
    plt.tick_params(axis='y', which='major', labelsize=8)
    plt.show()


def show_pandas(df: DataFrame, *,
                cmap: str = 'Greens', col_format: str = '${0:,.2f}') -> None:
    displayhook(df.style
                .format_index("{:%Y}")
                .format(col_format, thousands='.', decimal=',')
                .background_gradient(cmap=cmap)
                .set_table_styles([
                    {'selector': 'th.col_heading',
                     'props': 'font-size: 1.25em;'},
                    {'selector': 'td',
                     'props': 'text-align:center; font-weight:bold;'},
                    {'selector': '.index_name',
                     'props': 'font-style:italic; color:lightgrey; font-weight:normal;font-size:1.2em;'},
                    {'selector': 'th',
                     'props': 'background-color:#1e1f29; color:lightgrey;'},
                    {'selector': 'th:not(.col_heading):not(.index_name)',
                     'props': 'color:white;font-size:1.1em;'},
                ], overwrite=False))
    return None
