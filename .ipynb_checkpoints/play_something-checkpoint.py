# initial imports
import streamlit as st
import pandas as pd
import numpy as np
import pickle
from sklearn.preprocessing import MinMaxScaler
import matplotlib.pyplot as plt
from math import pi
from sklearn.metrics.pairwise import cosine_similarity
import os
import bz2

st.set_option('deprecation.showPyplotGlobalUse', False)

st.set_page_config(
            page_title="Play Something by Spotify",
            page_icon=':twisted_rightwards_arrows:',
            initial_sidebar_state="expanded")

st.title(':twisted_rightwards_arrows: Play Something by Spotify')

st.write('')

# path for image
path = os.path.dirname(__file__)
spotify_image = path+'/images/spotify_play_something.png'
st.image(spotify_image)

st.markdown("---")

st.write("""
### Tell us your mood, choose a track and your personal DJ will do the rest.
""")

st.markdown("---")

#############################
#                           #
#  RECOMMENDER - STEP 1     #
#                           #
#############################

#-------------------------------------------------------------------------------

# User selects user persona --> Model returns mapped genre
## The mapped genre will not be visible to the user

# load genre personas
path = os.path.dirname(__file__)
genre_personas_path = path+'/pickle_files_for_app/genre_personas.csv'
genre_personas = pd.read_csv(genre_personas_path)

#-------------------------------------------------------------------------------

# first recommendation
def recommender_personas(user_persona):
    
    idx_persona = genre_personas.index[genre_personas['user_persona'] == user_persona]
    recommendation_genre = genre_personas.iloc[idx_persona]['genre_study'].values[0]
    
    return recommendation_genre

# title step
st.write("""
    ### Step 1: How are you feeling?
    """)

# display user persona selection on streamlit    
input_persona = st.selectbox('',
                             [list(set(genre_personas['user_persona'].tolist()))[0], 
                              list(set(genre_personas['user_persona'].tolist()))[1], 
                              list(set(genre_personas['user_persona'].tolist()))[2],
                              list(set(genre_personas['user_persona'].tolist()))[3],
                              list(set(genre_personas['user_persona'].tolist()))[4],
                              list(set(genre_personas['user_persona'].tolist()))[5],
                              list(set(genre_personas['user_persona'].tolist()))[6],
                              list(set(genre_personas['user_persona'].tolist()))[7]])

st.markdown("---")

#-------------------------------------------------------------------------------

# run first recommendation
if input_persona:
     recommended_genre = recommender_personas(input_persona)


#############################
#                           #
#  RECOMMENDER - STEP 2     #
#                           #
#############################

#-------------------------------------------------------------------------------

# Genre from inputed persona --> Model returns top three songs in terms of cosine similarity
## These three songs will be visible to the user, who will have to select their favorite one

# load files
genres_study_indexed_df_path = path+'/pickle_files_for_app/genres_study_indexed_df.csv'
genres_study_indexed_df = pd.read_csv(genres_study_indexed_df_path).set_index('genre_study')

track_features_indexed_df_path = path+'/pickle_files_for_app/track_features_indexed_df.csv'
track_features_indexed_df = pd.read_csv(track_features_indexed_df_path).set_index('id')

track_features_path = path+'/pickle_files_for_app/track_features.csv'
track_features = pd.read_csv(track_features_path)

#-------------------------------------------------------------------------------

# second recommendation
def get_cosim_genre_tracks(genre, df_music_genres = genres_study_indexed_df, df_songs = track_features_indexed_df, num_tracks = 3):
    
    # temporary df based on the genre resulting from the first genre recommendation
    genre_temp = df_music_genres.loc[[str(genre)]]
    
    # create arrays of music features
    genre_array = np.array(genre_temp.T).reshape(1,-1)
    tracks_array = df_songs.values
    
    # compute cosine similarity
    cosim_scores = cosine_similarity(genre_array, tracks_array).flatten()
    tracks_similar_array = df_songs.index.values
    
    # initialize df results including most similar tracks 
    df_result = pd.DataFrame(data = {'tracks': tracks_similar_array,
                                     'cosim_' + genre: cosim_scores})
    
    # sort tracks and take only first 3
    df_result = df_result.sort_values(by='cosim_' + genre, ascending=False).head(num_tracks)
    
    # add new columns to to the df result dataframe
    list_top_3 = df_result['tracks'].tolist()
    
    # initialize empty dictionaries
    title_dict = {}
    album_dict = {}
    artist_dict = {}
    genre_dict = {}
    popularity_dict = {}
    
    # for the top 3 tracks --> look for additional features
    for track_id in list_top_3:
        title_dict[track_id] = track_features.iloc[track_features[track_features['id']==track_id].index.values]['track_name'].values[0]
        album_dict[track_id] = track_features.iloc[track_features[track_features['id']==track_id].index.values]['album_name'].values[0]
        artist_dict[track_id] = track_features.iloc[track_features[track_features['id']==track_id].index.values]['artist_name'].values[0]
        genre_dict[track_id] = track_features.iloc[track_features[track_features['id']==track_id].index.values]['genre_study'].values[0]
        popularity_dict[track_id] = track_features.iloc[track_features[track_features['id']==track_id].index.values]['track_popularity'].values[0]
    
    # add new cols
    df_result['url'] = 'https://open.spotify.com/track/' + df_result['tracks'].astype(str)
    df_result['title'] = df_result['tracks'].map(title_dict)
    df_result['album'] = df_result['tracks'].map(album_dict)
    df_result['artist'] = df_result['tracks'].map(artist_dict)
    df_result['genre'] = df_result['tracks'].map(genre_dict)
    df_result['popularity'] = df_result['tracks'].map(popularity_dict)
    
    
    # reorganize df
    df_result = df_result[['tracks','url','title','album',
                            'artist','genre', 'popularity',
                            'cosim_' + genre]]
    
    return df_result.reset_index(drop=True)

#-------------------------------------------------------------------------------

# run second recommendation
if recommended_genre:
    
    # retrieve df
    recommended_tracks = get_cosim_genre_tracks(str(recommended_genre))
    
    # retrieve top 3 tracks
    seed_track_1 = recommended_tracks.iloc[0]['title']
    seed_track_2 = recommended_tracks.iloc[1]['title']
    seed_track_3 = recommended_tracks.iloc[2]['title']
    
    # retrieve artists
    seed_artist_1 = recommended_tracks.iloc[0]['artist']
    seed_artist_2 = recommended_tracks.iloc[1]['artist']
    seed_artist_3 = recommended_tracks.iloc[2]['artist']
    
    # retrieve uris
    seed_url_1 = recommended_tracks.iloc[0]['url']
    seed_url_2 = recommended_tracks.iloc[1]['url']
    seed_url_3 = recommended_tracks.iloc[2]['url']
    
    # retrieve ids
    seed_id_1 = recommended_tracks.iloc[0]['tracks']
    seed_id_2 = recommended_tracks.iloc[1]['tracks']
    seed_id_3 = recommended_tracks.iloc[2]['tracks']
        

# title step
st.write("""
    ### Step 2: What are you most in the mood for?
    """)

# retrieve df
recommended_tracks = get_cosim_genre_tracks(str(recommended_genre))

# display resulting 3 songs on streamlit
seed_track = st.radio('',
                    [seed_track_1,
                     seed_track_2,
                     seed_track_3],
                     format_func=lambda x: str(x) + ' by ' + recommended_tracks[recommended_tracks['title']==str(x)]['artist'].values[0])

# find seed artist and seed track url
seed_artist = recommended_tracks[recommended_tracks['title']==str(seed_track)]['artist'].values[0]
seed_url = recommended_tracks[recommended_tracks['title']==str(seed_track)]['url'].values[0]

st.write("")

# display second selection by the user
st.write('Music Profile of {track} by {artist}'.format(track = '['+str(seed_track)+']('+str(seed_url)+')', artist = seed_artist))

#-------------------------------------------------------------------------------

# fx to get uri and artist from chosen track
def get_artist_uri(chosen_track):
    if seed_track == seed_track_1:
        seed_artist = seed_artist_1 
        seed_url = seed_url_1
        seed_id = seed_id_1
    elif seed_track == seed_track_2:
        seed_artist = seed_artist_2 
        seed_url = seed_url_2
        seed_id = seed_id_2
    else:
        seed_artist = seed_artist_3 
        seed_url = seed_url_3
        seed_id = seed_id_3
    
    return seed_artist, seed_url, seed_id

# get uri and artist from seed track
seed_artist, seed_url, seed_id = get_artist_uri(seed_track)

st.write("")

#-------------------------------------------------------------------------------

# create a function to plot the seed track chosen by the user
def plot_radar_seed_track(seed_track_id):
    
    # find seed track title
    seed_track_title = track_features.iloc[track_features[track_features['id']==seed_track_id].index.values]['track_name'].values[0]
    
    # identify labels to be plotted
    labels = ['danceability','energy', 'loudness','speechiness', 'acousticness',
                  'duration_mins','instrumentalness','liveness', 'valence', 'tempo']
    
    num_vars = len(labels)

    # calculate angle for each music feature
    angles=[n/float(num_vars)*2*pi for n in range(num_vars)]
    angles+=angles[:1]
    
    # set figure parameters
    fig, ax = plt.subplots(figsize=(6, 6), subplot_kw=dict(polar=True))
    fig.patch.set_facecolor('#0E1117')
    
    # helper function to plot seed track on the radar chart
    def add_to_radar(seed_track_id, color):
        
        # filter tracks df for the seed track only
        seed_track_df = track_features[track_features['id'] == str(seed_track_id)]
        
        # compute median of every music feature for the seed track
        values = list(seed_track_df[labels].median())
        values+=values[:1]

        ax.plot(angles, values, color=color, linewidth=1)
        ax.fill(angles, values, color=color, alpha=0.25)

    # add seed track to the radar graph
    add_to_radar(seed_track_id, '#1ed760') # green from spotify color pallette

    # find polar coordinates 
    ax.set_theta_offset(np.pi / 2)
    ax.set_theta_direction(-1)

    # draw axis lines for each angle and label
    labels+=labels[:1] # ensure that labels and angles have the same dimensions
    ax.set_thetagrids(np.degrees(angles), labels)

    # go through labels and adjust alignment based on where it is in the circle
    for label, angle in zip(ax.get_xticklabels(), angles):
        if angle in (0, np.pi):
            label.set_horizontalalignment('center')
        elif 0 < angle < np.pi:
            label.set_horizontalalignment('left')
        else:
            label.set_horizontalalignment('right')

    # set position of y-labels (0-100) to be in the middle of the first two axes
    ax.set_ylim(0, 1)
    ax.set_rlabel_position(180 / num_vars)

    # add some custom styling
    ax.tick_params(color = '#ecebe8')         # color of tick labels
    ax.tick_params(axis='y', labelsize=8)    # y-axis labels
    ax.spines['polar'].set_color('#ecebe8')  # color of outermost gridline (spine)
    ax.set_facecolor('#222222')              # background color inside the circle itself
    ax.tick_params(axis='y', colors='#ecebe8')
    ax.tick_params(axis='x', colors='#ecebe8');
    
    
# run function
fig = plot_radar_seed_track(seed_id)
st.pyplot(fig)

st.markdown("---")


#############################
#                           #
#  RECOMMENDER - STEP 3     #
#                           #
#############################

#-------------------------------------------------------------------------------

# Seed song --> Final playlist of top 10 songs in terms of cosine similarity
## These 10 songs will be visible to the user and will constitute our final recommendation
# third recommendation
def get_cosim_seed_tracks(track_seed_id, df_songs = track_features_indexed_df, num_tracks = 10):
    
    # temporary df based on the seed song resulting from step 2
    seed_temp = df_songs.loc[[track_seed_id]]
    
    # create arrays of music features
    seed_array = np.array(seed_temp.T).reshape(1,-1)
    tracks_array = df_songs.values
    
    # compute cosine similarity
    cosim_scores = cosine_similarity(seed_array, tracks_array).flatten()
    tracks_similar_array = df_songs.index.values
    
    # initialize df results including most similar tracks 
    df_result = pd.DataFrame(data = {'tracks': tracks_similar_array,
                                     'cosim': cosim_scores})
    
    # sort tracks and take only first 10
    ## purposedly serving the seed song selected by the user because since it's the most appealing 
    ### to the user and should be included in the final recommendation
    df_result = df_result.sort_values(by='cosim', ascending=False).head(num_tracks)
    
    # add new columns to to the df result dataframe
    list_top_10 = df_result['tracks'].tolist()
    
    # initialize empty dictionaries
    title_dict = {}
    album_dict = {}
    artist_dict = {}
    genre_dict = {}
    popularity_dict = {}
    
    # for the top 3 tracks --> look for additional features
    for track_id in list_top_10:
        title_dict[track_id] = track_features.iloc[track_features[track_features['id']==track_id].index.values]['track_name'].values[0]
        album_dict[track_id] = track_features.iloc[track_features[track_features['id']==track_id].index.values]['album_name'].values[0]
        artist_dict[track_id] = track_features.iloc[track_features[track_features['id']==track_id].index.values]['artist_name'].values[0]
        genre_dict[track_id] = track_features.iloc[track_features[track_features['id']==track_id].index.values]['genre_study'].values[0]
        popularity_dict[track_id] = track_features.iloc[track_features[track_features['id']==track_id].index.values]['track_popularity'].values[0]
    
    # add new cols
    df_result['url'] = 'https://open.spotify.com/track/' + df_result['tracks'].astype(str)
    df_result['title'] = df_result['tracks'].map(title_dict)
    df_result['album'] = df_result['tracks'].map(album_dict)
    df_result['artist'] = df_result['tracks'].map(artist_dict)
    df_result['genre'] = df_result['tracks'].map(genre_dict)
    df_result['popularity'] = df_result['tracks'].map(popularity_dict)
    
    
    # reorganize df
    df_result = df_result[['tracks','url','title','album',
                           'artist','genre', 'popularity',
                           'cosim']]
    
    return df_result.reset_index(drop=True)

#-------------------------------------------------------------------------------

# run final recommendation
if seed_id:
    
    # retrieve df
    recommended_tracks_final = get_cosim_seed_tracks(str(seed_id))
    
    # retrieve top 10 tracks
    final_track_1 = recommended_tracks_final.iloc[0]['title']
    final_track_2 = recommended_tracks_final.iloc[1]['title']
    final_track_3 = recommended_tracks_final.iloc[2]['title']
    final_track_4 = recommended_tracks_final.iloc[3]['title']
    final_track_5 = recommended_tracks_final.iloc[4]['title']
    final_track_6 = recommended_tracks_final.iloc[5]['title']
    final_track_7 = recommended_tracks_final.iloc[6]['title']
    final_track_8 = recommended_tracks_final.iloc[7]['title']
    final_track_9 = recommended_tracks_final.iloc[8]['title']
    final_track_10 = recommended_tracks_final.iloc[9]['title']
    
    
    # retrieve artists
    final_artist_1 = recommended_tracks_final.iloc[0]['artist']
    final_artist_2 = recommended_tracks_final.iloc[1]['artist']
    final_artist_3 = recommended_tracks_final.iloc[2]['artist']
    final_artist_4 = recommended_tracks_final.iloc[3]['artist']
    final_artist_5 = recommended_tracks_final.iloc[4]['artist']
    final_artist_6 = recommended_tracks_final.iloc[5]['artist']
    final_artist_7 = recommended_tracks_final.iloc[6]['artist']
    final_artist_8 = recommended_tracks_final.iloc[7]['artist']
    final_artist_9 = recommended_tracks_final.iloc[8]['artist']
    final_artist_10 = recommended_tracks_final.iloc[9]['artist']
    
    # retrieve uris
    final_url_1 = recommended_tracks_final.iloc[0]['url']
    final_url_2 = recommended_tracks_final.iloc[1]['url']
    final_url_3 = recommended_tracks_final.iloc[2]['url']
    final_url_4 = recommended_tracks_final.iloc[3]['url']
    final_url_5 = recommended_tracks_final.iloc[4]['url']
    final_url_6 = recommended_tracks_final.iloc[5]['url']
    final_url_7 = recommended_tracks_final.iloc[6]['url']
    final_url_8 = recommended_tracks_final.iloc[7]['url']
    final_url_9 = recommended_tracks_final.iloc[8]['url']
    final_url_10 = recommended_tracks_final.iloc[9]['url']
        
# display final 10 recommendations
st.write("""
    ## :headphones: Your personal DJ recommends
    """)
st.write('{track_1} by {artist_1}'.format(track_1 = '['+str(final_track_1)+']('+str(final_url_1)+')', artist_1 = final_artist_1))
st.write('{track_2} by {artist_2}'.format(track_2 = '['+str(final_track_2)+']('+str(final_url_2)+')', artist_2 = final_artist_2))
st.write('{track_3} by {artist_3}'.format(track_3 = '['+str(final_track_3)+']('+str(final_url_3)+')', artist_3 = final_artist_3))
st.write('{track_4} by {artist_4}'.format(track_4 = '['+str(final_track_4)+']('+str(final_url_4)+')', artist_4 = final_artist_4))
st.write('{track_5} by {artist_5}'.format(track_5 = '['+str(final_track_5)+']('+str(final_url_5)+')', artist_5 = final_artist_5))
st.write('{track_6} by {artist_6}'.format(track_6 = '['+str(final_track_6)+']('+str(final_url_6)+')', artist_6 = final_artist_6))
st.write('{track_7} by {artist_7}'.format(track_7 = '['+str(final_track_7)+']('+str(final_url_7)+')', artist_7 = final_artist_7))
st.write('{track_8} by {artist_8}'.format(track_8 = '['+str(final_track_8)+']('+str(final_url_8)+')', artist_8 = final_artist_8))
st.write('{track_9} by {artist_9}'.format(track_9 = '['+str(final_track_9)+']('+str(final_url_9)+')', artist_9 = final_artist_9))
st.write('{track_10} by {artist_10}'.format(track_10 = '['+str(final_track_10)+']('+str(final_url_10)+')', artist_10 = final_artist_10))

st.markdown("---")

#-------------------------------------------------------------------------------