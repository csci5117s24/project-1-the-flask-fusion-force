# Module 1 Group Assignment

CSCI 5117, Spring 2024, [assignment description](https://canvas.umn.edu/courses/413159/pages/project-1)

## App Info:

* Team Name: The Flask Fusion Force
* App Name: Mixtape.fm
* App Link: <https://TODO.com/>

### Students

* Conner DeJong, dejon113
* Owen Ratgen, ratge006
* Thomas Knickerbocker, knick073
* Allen Liao, liao0144
* Kris Moe, moe00013


## Key Features

**Describe the most challenging features you implemented
(one sentence per bullet, maximum 4 bullets):**

* The spotify callback to be able to extract a user's information from their library then import these playlists onto the website
* Another hard part was saving the user's information, playlist information, the songs in the playlist and its' information, and other information that's valuable to the website in the database along with retrieving it correctly

## Testing Notes

**Is there anything special we need to know in order to effectively test your app? (optional):**

* If you're not signed in you won't be able to leave a comment or rating, import your playlist, or see all the available menu options
* You can leave comments and ratings if you click on the playlist while signed in
* Comments and ratings left on a playlist will be viewable when a user refreshes the page


## Screenshots of Site

**[Add a screenshot of each key page (around 4)](https://stackoverflow.com/questions/10189356/how-to-add-screenshot-to-readmes-in-github-repository)
along with a very brief caption:**

Playlist Page
<img width="503" alt="Playlist Page" src="https://github.com/csci5117s24/project-1-the-flask-fusion-force/blob/main/FinalScreenshots/Screenshot%202024-02-28%20162241.png">

Edit playlist page
<img width="503" alt="Edit_playlist_Page" src="https://github.com/csci5117s24/project-1-the-flask-fusion-force/blob/main/FinalScreenshots/Screenshot%202024-02-28%20161854.png">

Library page
<img width="503" alt="Library page" src="https://github.com/csci5117s24/project-1-the-flask-fusion-force/blob/main/FinalScreenshots/Screenshot%202024-02-28%20161742.png">

Home page
<img width="503" alt="Home page" src="https://github.com/csci5117s24/project-1-the-flask-fusion-force/blob/main/FinalScreenshots/Screenshot%202024-02-28%20161707.png">
![](https://media.giphy.com/media/o0vwzuFwCGAFO/giphy.gif)


## Mock-up 
We are using Canva to create our mock ups link is here:
https://www.canva.com/design/DAF7eiceWJs/7_WpszTzMRMUg8rbZjcjuQ/edit?utm_content=DAF7eiceWJs&utm_campaign=designshare&utm_medium=link2&utm_source=sharebutton

![Homepage](/MOCKUP/mixtape.fm_homepage.png?raw=true)
![Login](/MOCKUP/mixtape.fm_login_page.png?raw=true)
![Search_Results](/MOCKUP/mixtape.fm_search_results_page.png?raw=true)
![Library](/MOCKUP/mixtape.fm_user_library_page.png?raw=true)
![Playlist](/MOCKUP/mixtape.fm_individual_playlist_page.png?raw=true)
![Settings](/MOCKUP/mixtape.fm_settings_page.png?raw=true)
<img width="503" alt="Edit_Comments_Page" src="https://github.com/csci5117s24/project-1-the-flask-fusion-force/assets/136757799/1c64e066-3fcb-498b-b7e9-6ca0c9245fbf">
<img width="508" alt="Individual_Playlist_Page" src="https://github.com/csci5117s24/project-1-the-flask-fusion-force/assets/136757799/9c46035a-f800-4bb8-8328-05f15048890b">
<img width="509" alt="Write_a_Comment_Page" src="https://github.com/csci5117s24/project-1-the-flask-fusion-force/assets/136757799/f2486515-e9a8-4e04-b12d-5eb340d890ad">
<img width="512" alt="Create_Edit_Playlist_Page" src="https://github.com/csci5117s24/project-1-the-flask-fusion-force/assets/136757799/e4553c57-23ee-4ed5-9d4e-eb0422ecd636">

## External Dependencies

**Document integrations with 3rd Party code or services here.
Please do not document required libraries. or libraries that are mentioned in the product requirements**

* For our 3rd Party Service, we used the Spotify API so we could directly interact with the user's Spotify account. This will let the user import all of their playlists onto our website and have people rate the playlist and leave comments on what they think about it.

**If there's anything else you would like to disclose about how your project
relied on external code, expertise, or anything else, please disclose that
here:**

* We relied on the Spotify API Authorization Tutorial for us to gain the user's access token. https://developer.spotify.com/documentation/web-api/tutorials/code-flow
