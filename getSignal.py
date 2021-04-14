import requests
import pandas as pd
from bs4 import BeautifulSoup
import sys

class HTMLTableParser:

    def parse_url(self, url):
        response = requests.get(url)
        #print("response: {}".format(response.text))
        soup = BeautifulSoup(response.text, 'lxml')
        #table = soup.find('table', attrs={'class':'lineItemsTable'})
        #table_body = table.find('tbody')
#        rows = soup.find_all('tr')
#        print ("all rows: {}".format(rows))
        tables = soup.find_all('table')
        print("Tables found: {}".format(len(tables)))
        # Table 3 is the downstream one
        #print("all soup table ids: {}".format(soup.find_all('table')))
        #rows = table[3].find_all('tr') # Old modem
        return tables[2]

    def parse_html_table(self, table):
        n_columns = 0
        n_rows=0
        column_names = []

        #print ("Parsing html table")
        # Find number of rows and columns
        # we also find the column titles if we can
        for idx, row in enumerate(table.find_all('tr')):
            #print ("idx is: {}".format(idx))
            # Skip the first line
#            if idx == 0:
#                continue
            n_columns = 0; # reset for this line
            #print ("row is: {}".format(row))

            # Determine the number of rows in the table
            td_tags = row.find_all('td')
            #print ("td_tags are: {} and len: {}".format(td_tags, len(td_tags)))
            if len(td_tags) > 0:
                n_rows+=1
                if n_columns == 0:
                    # Set the number of columns for our table
                    n_columns = len(td_tags)

            #print ("n_rows: {}, n_columns: {}".format(n_rows, n_columns))
            # Handle column names if we find them
            th_tags = row.find_all('th') 
            #print ("th_tags: {}".format(th_tags))
            if len(th_tags) > 0 and len(column_names) == 0:
                for th in th_tags:
                    column_names.append(th.get_text())

        # Safeguard on Column Titles
        print ("Column Names: {}".format(column_names))
        print ("N_Columns: {}".format(n_columns))
        if len(column_names) > 0 and len(column_names) != n_columns:
            raise Exception("Column titles do not match the number of columns")

        columns = column_names if len(column_names) > 0 else range(0,n_columns)
        df = pd.DataFrame(columns = columns,
                index= range(0,n_rows))
        row_marker = 0
        for row in table.find_all('tr'):
            column_marker = 0
            columns = row.find_all('td')
            for column in columns:
                df.iat[row_marker,column_marker] = column.get_text()
                column_marker += 1
            if len(columns) > 0:
                row_marker += 1
        # Convert to float if possible
        for col in df:
            try:
                df[col] = df[col].astype(float)
            except ValueError:
                pass

        return df


if __name__ == '__main__':
    print("Parsing cable modem")
    #url = 'http://192.168.100.1/RgConnect.asp' # old cable modem
    url = 'http://192.168.100.1/cmconnectionstatus.html' # old cable modem
    hp = HTMLTableParser()
    table = hp.parse_url(url) # Grabbing the table from the tuple
    #print ("table is: {}".format(table))
    #print('Tables are: {}'.format(tables))
    df = hp.parse_html_table(table)
    df.columns = ['Channel Lock', 'Status','Modulation','Channel ID','Frequency','Power','SNR','Correctables','Uncorrectables']
    df = df[2:]
    print ("{}".format(df))

#    table.head()


