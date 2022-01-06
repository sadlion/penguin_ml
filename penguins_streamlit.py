import streamlit as st
from streamlit_lottie import st_lottie
import requests
import pandas as pd

from sklearn.metrics import accuracy_score
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split

import pickle

import matplotlib.pyplot as plt
import seaborn as sns

from pandas_profiling import ProfileReport
from streamlit_pandas_profiling import st_profile_report

'''
[History]
2021.12.30 Add Password on streamlit app
'''
def load_lottieurl(url: str):
    r = requests.get(url)
    if r.status_code != 200:
        return None
    return r.json()

lottie_penguin = load_lottieurl('https://assets9.lottiefiles.com/private_files/lf30_lntyk83o.json')
st_lottie(lottie_penguin, speed=1.5, width=800, height=400)

st.title('Penguin Classifier: A Machine Learning App V0.1.5:Sadlion')
st.write("This app uses 6 inputs to predict the species of penguin using "
         "a model built on the Palmer's Penguin's dataset. Use the form below"
         " to get started!")

password_guess = st.text_input('What is the Password?')
#deploy to stream share
#if password_guess != st.secrets["password"]:
if password_guess != "sadlion":
    st.stop()

penguin_file = st.file_uploader('Upload your own penguin data')
penguin_df = None
if penguin_file is None:
    st.write("No selection")
    #cym... for histogram but it needs to load from latested training file
    penguin_df = pd.read_csv('penguins.csv')
    rf_pickle = open('random_forest_penguin.pickle', 'rb')
    map_pickle = open('output_penguin.pickle', 'rb')
    rfc = pickle.load(rf_pickle)
    unique_penguin_mapping = pickle.load(map_pickle)
    rf_pickle.close()
    map_pickle.close()

else:
    st.write("selection:{}".format(penguin_file))
    penguin_df = pd.read_csv(penguin_file)
    penguin_df = penguin_df.dropna()
    output = penguin_df['species']
    features = penguin_df[['island', 'bill_length_mm', 'bill_depth_mm',
                           'flipper_length_mm', 'body_mass_g',
                           'sex']]
    features = pd.get_dummies(features)
    output, unique_penguin_mapping = pd.factorize(output)
    x_train, x_test, y_train, y_test = train_test_split(features, output, test_size=.8)
    rfc = RandomForestClassifier(random_state=15)
    rfc.fit(x_train, y_train)
    y_pred = rfc.predict(x_test)
    score = round(accuracy_score(y_pred, y_test), 2)
    st.write('We trained a Random Forest model on these data,'
             ' it has a score of {}! Use the '
             'inputs below to try out the model.'.format(score))


with st.form('user_inputs'):
    island = st.selectbox('Penguin Island', options=['Biscoe', 'Dream', 'Torgerson'])
    sex = st.selectbox('Sex', options=['Female', 'Male'])
    bill_length = st.number_input('Bill Length (mm)', min_value=0)
    bill_depth = st.number_input('Bill Depth (mm)', min_value=0)
    flipper_length = st.number_input('Flipper Length (mm)', min_value=0)
    body_mass = st.number_input('Body Mass (g)', min_value=0)
    st.form_submit_button()

island_biscoe, island_dream, island_torgerson = 0, 0, 0
if island == 'Biscoe':
    island_biscoe = 1
elif island == 'Dream':
    island_dream = 1
elif island == 'Torgerson':
    island_torgerson = 1
sex_female, sex_male = 0, 0
if sex == 'Female':
    sex_female = 1
elif sex == 'Male':
    sex_male = 1

new_prediction = rfc.predict([[bill_length, bill_depth,flipper_length,body_mass, island_biscoe,island_dream,island_torgerson, sex_female,sex_male]])
prediction_species = unique_penguin_mapping[new_prediction][0]
st.write('We predict your penguin is of the {} species'.format(prediction_species))

st.write('We used a machine learning (Random Forest) model to '
         'predict the species, the features used in this prediction '
         ' are ranked by relative importance below.')
st.image('feature_importance.png')

st.write('Below are the histograms for each continuous variable'
         'separated by penguin species. The vertical line '
         'represents your the inputted value.')

fig, ax = plt.subplots()
ax = sns.displot(x=penguin_df['bill_length_mm'],hue=penguin_df['species'])
plt.axvline(bill_length)
plt.title('Bill Length by Species')
st.pyplot(ax)
fig, ax = plt.subplots()
ax = sns.displot(x=penguin_df['bill_depth_mm'],hue=penguin_df['species'])
plt.axvline(bill_depth)
plt.title('Bill Depth by Species')
st.pyplot(ax)
fig, ax = plt.subplots()
ax = sns.displot(x=penguin_df['flipper_length_mm'],hue=penguin_df['species'])
plt.axvline(flipper_length)
plt.title('Flipper Length by Species')
st.pyplot(ax)


st.title('Pandas Profiling of Penguin Dataset')
penguin_profile = ProfileReport(penguin_df, explorative=True)
st_profile_report(penguin_profile)
