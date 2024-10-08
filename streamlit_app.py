# Import python packages
import streamlit as st
import pandas as pd_df
import requests
#from snowflake.snowpark.context import get_active_session
from snowflake.snowpark.functions import col

# Write directly to the app
st.title(" My parents new healthy dinner :balloon:")
st.write(
    """Choose the fruits you want in your custom Smoothie!
    [docs.streamlit.io](https://docs.streamlit.io).
    """
)

cnx=st.connection("snowflake")
session= cnx.session()

#option = st.selectbox(
#    "What is your favorite fruit?",
#    ("Banana", "Strawberries", "Peaches"))
#st.write("My favorite fruit is :", option)

name_on_order= st.text_input('Name on smoothie:')
st.write('The name on your Smoothie will be:',name_on_order)

#session = get_active_session()
#my_dataframe = session.table("smoothies.public.fruit_options").select (col('FRUIT_NAME'))
#st.dataframe(data=my_dataframe, use_container_width=True)

my_dataframe = session.table("smoothies.public.fruit_options").select(col('FRUIT_NAME'),col('SERCH_ON'))
#st.dataframe(data=my_dataframe, use_container_width=True)
#st.stop()

#Convert the snowpart Dataframe to a Pandas Dataframe so we can use the LOC function
pd_df = my_dataframe.to_pandas()
#st.dataframe(pd_df)
#st.stop()

ingredients_list = st.multiselect (
    'Choose up to 5 ingredients'
    , my_dataframe
    , max_selections=5
)

if ingredients_list:
    ingredients_string = ''
    
    for fruit_chosen in ingredients_list:
        ingredients_string += fruit_chosen + ' '

        search_on=pd_df.loc[pd_df['FRUIT_NAME'] == fruit_chosen, 'SERCH_ON'].iloc[0]
        st.write('The search value for ', fruit_chosen,' is ', search_on, '.')

        st.subheader(fruit_chosen + 'Nutrition Information')
        fruityvice_response = requests.get("https://fruityvice.com/api/fruit/watermelon")
        fv_df=st.dataframe (data=fruityvice_response.json(), use_container_width=True)
    
    my_insert_stmt = """ insert into smoothies.public.orders(ingredients,NAME_ON_ORDER)
            values ('""" + ingredients_string + """','"""+name_on_order+"""')"""
    
    #st.write(my_insert_stmt)
    #st.stop()
    
    time_to_insert = st.button('Submit Order')
    
    if time_to_insert:
       session.sql(my_insert_stmt).collect()
       st.success('Your Smoothie is ordered! ' + name_on_order , icon="✅")
