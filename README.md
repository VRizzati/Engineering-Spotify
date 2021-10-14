# PLAY SOMETHING BY SPOTIFY

---

The app was deployed on Streamlit and is available [here](https://share.streamlit.io/vrizzati/engineering-spotify/main/play_something.py).

---

How to navigate this repo:
- proposal_spotify.pdf: my initial proposal for an image classification project 
- mvp_spotify.pdf: mvp presented two days before the final project submission
- final folder: all files used for the final submission
  1. 01_spotify_track_collection.ipynb : gathered data from Spotify API and conducted initial EDA
  2. 01a_spotify_track_collection_colab.ipynb: supplemented notebook 01 in gathering data from Spotify API
  3. 02_spotify_modeling.ipynb : conducted data preprocessing, EDA, and built the recommendation engine 
  4. spotify_play_something.pdf : final presentation
- images folder: folder containing the images included in the presentation
- pickle_files_for_app folder: folder containing the pickle files that have been referenced to in the .py file for the streamlit app
- requirements.txt: requirements for the app
- spotify_recommender_streamlit_app.py: created the code to build the Play Something app

---

## ABSTRACT
As a Data Scientist at Spotify, I have been asked to come up with an idea to increase retention and Daily Active Users (DAUs). Building upon the past success of personalization-based strategies, I have decided to build a recommendation engine that provides a curated Top 10 playlist based on the user’s daily mood. Thanks to this new product, *Play Something*, users will enjoy the experience of having a personal DJ at their fingertips.

In particular, my prototype is built upon the user’s mood at the time of logging into the app. The idea of building a recommendation engine based on mood feeds into a larger vision of creating a matrix between user personas (i.e. mirroring a user’s musical taste) and occasion/mood. Clearly, the applicability of such a vision is of course tied to access to a large pool of user data. 

After collecting data on [Individual Differences in Musical Taste](https://www.jstor.org/stable/10.5406/amerjpsyc.123.2.0199) from a study by Adrian C. North and gathering Spotify tracks data from the [Spotify API](https://developer.spotify.com/documentation/web-api/), I have preprocessed and explored the data. Then, I build the three-step recommender based on mood and deployed the Play Something app on streamlit. 

## DATA
I have collected data on the mapping mood to music genre from the Adrian C. North study on [Individual Differences in Musical Taste](https://www.jstor.org/stable/10.5406/amerjpsyc.123.2.0199), and data on Spotify tracks from the [Spotify API](https://developer.spotify.com/documentation/web-api/) by using spotipy.  

Since Spotify assigns music genres at the artist level. So, to gather the data for all the genres that were mentioned in the study, I had to first pull a table of artists by genre, then a table of albums by artist and finally a table of tracks by albums. I saved these tables locally in a SQL database for easier access.

After preprocessing and cleaning the data, I have obtained a total of ~ 256,000 tracks across 15 music genres. Then, I realigned the genre nomenclature between the study and Spotify to enable the mapping between music genre and moods, derived from the study. 

As an additional step, to make the personality traits more relatable and actionable, I merged the insights from the study with my domain knowledge to assign a **user persona** to every music genre. This user persona will constitute the first choice that a user will make on the final app.

## DESIGN
As reflected in the notebooks included in the final folder of this repo, this project is designed around five main components:
1. **Data Gathering** : obtain data by pulling from the API in parallel on Jupyter Lab and Google Colab 
2. **Preprocessing** : clean and prepare the data for modeling
3. **Conducting EDA** : visualize music features by genre or track via radar graphs
4. **Building Recommender** : create a recommender based on mood, leveraging the concept of cosine similarity
5. **Deploying app on streamlit** : build an interactive app on streamlit

As a last step, in light of the results from my analysis, I have generated a few business insights and model development ideas that I have summarized in the final presentation. 

## ALGORITHM
As a first step, I **pulled data** from the Spotify API through spotipy. I structured my data across the *artists*, *albums* and *tracks* tables and I saved these in a SQL database. In order to reduce the time cost of this operation, I pulled from the API simultaneouslu on Jupyter Lab and Google Colab (hence the presence of two notebooks on dat gathering in this repo).

Then, I preprocessed the data and segmented the tracks by music genre. I also studied and conducted EDA on the music features (more info [here](https://developer.spotify.com/documentation/web-api/reference/#category-tracks)) and compared different music genres and tracks on a radar graph. In this step, I mapped the Spotify music genres to the music genres as presented in the source study, so as to allow for the mood-to-genre mapping and modeling. 

As a third step, I built the recommendation engine according to the following process:
- Map mood (selected by the user) to a music genre (not revealed to the user)
- **Recommendation #1**: returns the top 3 songs that are the closest to the seed genre, in terms of cosine similarity
- **Recommendation #2 (final)**: returns the top 10 songs that are the closest to the seed track selected by the user in the previous step

Of course this is a relatively simplified implementation of a recommendation system, because I am lacking user data.

As a final step, I deployed my app on Streamlit. 

## TOOLS
- Os to interact with the operating system from jupyter lab
- Pandas and numpy for data manipulation
- Sklearn for data modeling
- Matplotlib for data visualization
- Google Colab and related GPU to accelerate data gathering
- SQLalchemy and SQLlite to store data locally
- Streamlit for app deployment

## COMMUNICATION
A slide deck is included in this repo. 

In addition, see a few examples of radar graphs used to investigate the track data in terms of music features.

**1. Jazz | Blues | Soul**

![jazz_blues_soul](https://user-images.githubusercontent.com/68084582/126735213-0885c172-cded-40ef-82d3-5a9f6fd7f098.jpg)


**2. Rap | Metal | Electronic**

![rap_metal_electronic](https://user-images.githubusercontent.com/68084582/126735300-beef2ea0-4f42-44d2-8cd6-e8f73a104f85.jpg)

