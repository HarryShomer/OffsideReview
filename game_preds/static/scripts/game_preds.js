$.noConflict();
        jQuery(document).ready(function( $ ) {

            // Set Dates
            $( "#date_filter_1" ).datepicker({dateFormat: "yy-mm-dd"});
            $( "#date_filter_1" ).datepicker("setDate", new Date());
            $( "#date_filter_2" ).datepicker({dateFormat: "yy-mm-dd"});
            $( "#date_filter_2" ).datepicker("setDate", new Date());


            // All Table Columns
            table_columns = [
                    { "title": "Game.ID", data: 'game_id' },
                    { "title": "Date" , data: 'date'},
                    { "title": "Season" , data: 'season'},
                    { "title": "Home Team", data: 'home_team'},
                    { "title": "Away Team", data: 'away_team'},
                    { "title": "Home Win Probability%", data: 'home_probs'},
                    { "title": "Away Win Probability%", data: 'away_probs'}
            ]

            /*
                Initialize Table with data for that day
            */
            table = $('#mydata').DataTable({
                dom: 'Bfrtip',
                columns: table_columns,
                info: false,
                "deferRender": true,
                "searching":   false,
                "pageLength": 50,
                "scrollX": true,
                /*
                "ajax": {
                    "url": "/gamepredictions/Query/",
                    "type": "GET",
                    "data": {
                        'team': getTeam(),
                        'date_filter_from': get_dateFilter1(),
                        'date_filter_to': get_dateFilter2()
                    }
                 }
                 */
            });


            /**
                This function is called when the loadButton is clicked.
                It sends an ajax request to get the requested query. The previous table is destroyed and
                replaced by the new table with the data.
            */
            $("#loadButton").click(function(){
                // Ajax request to get data
                $.ajax({
                    url: '/gamepredictions/Query/',
                    type : "GET",
                    data: {
                        'team': getTeam(),
                        'date_filter_from': get_dateFilter1(),
                        'date_filter_to': get_dateFilter2()
                    },
                    dataType: 'json',

                    // If it's good we destroy the previous table and create a new one with the new data
                    success: function (response) {
                          table.destroy();
                          $("#mydata").html('<thead class="bg-primary"></thead><tbody></tbody>');

                          table = $('#mydata').DataTable({
                                dom: 'Bfrtip',
                                data: response.data,
                                columns: table_columns,
                                info: false,
                                "deferRender": true,
                                "searching":   false,
                                "pageLength": 50,
                                "scrollX": true,
                          });
                    }
                });
            });


/**********************************************************************************************************************/
            function get_dateFilter1(){
                return document.getElementById("date_filter_1").value;
            }

            function get_dateFilter2(){
                return document.getElementById("date_filter_2").value;
            }

            function getTeam() {
                return document.getElementById("TeamButton").value;
            }


        });


