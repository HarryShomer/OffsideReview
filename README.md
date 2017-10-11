# OffsideReview

[OffsideReview](offsidereview.com) is a website for modern National Hockey League (NHL) 
statistics from the 2016-2017 season onwards for all Regular Season and Playoff games.  

 
##Features

There are currently three views for querying data: Skaters, Teams, and Goalies.

In each view you query data by a variety of different parameters, including:

*  Team
*  Time on ice
*  Venue - Home, Away, or Both
*  Strength  (e.g. 5v5)
*  Between a given Date Range
*  Season Type - Regular Season, Playoffs, or Both
*  Split By - Game, Season, or Cumulative
*  Adjustments - Specify if the data should be adjusted for score
*  Position (for skaters)
* Player (for skaters and goalies)


##Built With

###Server-Side
* Python 3 - Language of choice.
* Django - Web Framework Used.
* Postgresql - Database used to store and retrieve data.

###Client-Side and Design
* Bootstrap - Used for frontend styling.
* JQuery - Event handling, Ajax calls, and standard Javascript code.
* JQuery Plugins - [Datatables](https://github.com/DataTables/DataTables) was used to construct
the tables to hold the data and [select2](https://github.com/select2/select2) was used for
select boxes. 


##Contact

Please contact me for any issues, suggestions, or anything site related. For any bugs or
anything related to the code please open an issue. Otherwise you can contact me at either:

* Email   - offsidereviewhockey@gmail.com
* Twitter - @offsides_review