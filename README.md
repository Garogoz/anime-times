# anime-times
#### Video Demo:  <https://youtu.be/9uFuEAUt5R0?si=IAvGLUmZatvsYY1q>
#### Description:

    **Anime Times** is a Web Application which allows you to create a personalized schedule to follow your favorites anime shows that are currently airing, It also allows you to search and get information about any anime show that has ever been aired.

#### Why I decided to create this App?

    At first I wanted to make a project about things I like, so I could enjoy and be creative in the development of it. So I started looking for a problem that I was currently having which was to be able to follow a dynamic weekly schedule of the current anime shows that I was watching. For that reason I decided to solve this problem that I was having, and also I wanted to be able to design it as I wanted with the possibility of adding even more features in the future.

#### Technologies:

    For this WebApp, I decided to stick with what I had learned in Cs50, I used HTML, CSS, JS and the Python framework called Flask.

    I also had to learn and use an API called Anilist and learn GraphQL language to be able to fetch up-to-date information about all the animes.

#### Key features:

    There are 4 Main features that **Anime Times** has:

    1. Weekly Schedule: Easily track the airing times of your favorite anime series throughout the week.
    2. Anime Searcher: Find anime shows by name and multiple filters such as genres, format, and order them by Popularity, trending or score.
    3. Detailed Anime Info: Access comprehensive details about each anime, including genre, release date, synopsis, and more.
    4. Season searcher: Find all the anime that was airing in a given season such as Winter, Summer, Spring or Fall in a given year.

### Technical explanation of project files:

#### app.py

    This is a python file which contains the main code for the Flask server to function, in this file I created and handled all the possible routes of the web app, all the POST and GET requests are handled here also.

    This file is the one that makes all the connections and where most of the logic for the webapp to work.

    There is also an implementation of Cache from a Python library which I used so I could store some small amount of data in order to not make too many requests of the same information to the API and be able to stay beneath the Api request limit. 
    (I just implemented this solution for one of the key features, the season searcher feature)

#### graph.py

    This Python File is basically where I created all of the function that I could abstract from the main App.py, in order to keep it cleaner and more elegant.

    This is where all the Api querys are done, all the data is retrieved from the Api, is cleaned, and then is returned to the main application app.py

    The workflow for the Api Query is

    1. The query parameters are retrieved from the main APP.PY
    2. The data is used to construct a Query request to the api
    3. The api response is then structured in a dictionary
    4. The data(cleaned and structured) is returned to the main App.py to then render all the information.

#### /static/js/script.js
#### /static/js/schedule.js

    This two are JavaScript files I used to add all the main client-side interactivity and its where the Schedule feature is brought to life.

    The schedule works by creating an array inside of the LocalStorage of the browser, saving all of the IDs of the animes that are being followed by the user. This data is saved in order to display the correct content and add the correct styles to the web depending on what shows are being followed.

#### styles/styles.css

    This is the css file which contains all of the styles applied to the HTML.

#### templates/

    This folder contains all of the different views of the web app, there is a main layout.html that sets the general view of the web from which the other .html inherit.

    All the data on these .hmtl files is dynamically obtained from the server and displayed using Jinja2.

#### templates/about.html
    This is a .html that has some information for the users to understand what this webapp is about, and also some information about myself.

#### /static/img
#### /static/logos

    These two static folders contain images used in the web.

#### Conclusion

    This was a brief explanation of what all of the files and folders inside of my project do. In the future I would like to add more useful features that can make my WebApp more appealing and enjoyable to users.




