import pandas as pd
from datetime import datetime, timedelta



def get_stats():
    #read the file
    df = pd.read_csv('RocketType/key_log.txt', sep=" ", encoding='latin-1')


    # In[73]:

    #convert https://exceptionshub.com/python-convert-unix-epoch-time-to-datetime-in-pandas.html
    start = datetime(1970, 1, 1)  # Unix epoch start time
    df.time = df.time.apply(lambda x: start + timedelta(seconds=x))


    # In[74]:


    #df.time


    # In[75]:


    df['CPM'] = 60/(df['delta']/1000)
    df['WPM'] = df['CPM']/5
    #df


    # In[61]:


    #remove 0 for delta and anything with a pause longer than 2 secs
    df = df.query('delta != 0 & delta < 2000')

    # In[77]:

    # TODO: Clean this up somehow, maybe remove first and last lines
    return df.groupby([df.time.dt.date]).median().WPM.astype(int)

if __name__ == "__main__":
    print(get_stats()) # Print stats if called in its own namespace (file not imported)
