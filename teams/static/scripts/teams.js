$.noConflict();
        jQuery(document).ready(function( $ ) {

            // Set Dates
            $( "#date_filter_1" ).datepicker({dateFormat: "yy-mm-dd"});
            $( "#date_filter_2" ).datepicker({dateFormat: "yy-mm-dd"});

            /**
                This function is called when the loadButton is clicked.
                It first checks if the inputs are valid (if not it outputs an error message).
                If it's good it sends an ajax request to get the requested query. The previous table is destroyed and
                replaced by the new table with the data.
            */
            $("#loadButton").click(function(){

                // Check that specified something for every query parameter
                if(!verify_inputs()){
                    var firstLine = "Invalid Input: You are missing at least one required input.";
                    var secondLine = "The following buttons are required:";
                    var thirdLine = "1. Strength \n2. Split By \n3. Venue \n4. Season Type \n5. Adjustments";
                    alert(firstLine + "\n\n" + secondLine + "\n" + thirdLine)

                    return;
                }

                // Ajax request to get data
                $.ajax({
                    url: '/teams/Query/',
                    type : "GET",
                    data: {
                        'strength': getStrength(),
                        'split_by': get_split_by(),
                        'team': getTeam(),
                        'venue': get_venue(),
                        'season_type': get_season_type(),
                        'date_filter_from': get_dateFilter1(),
                        'date_filter_to': get_dateFilter2(),
                        'adjustment': getAdjustments(),
                        'toi': getToi(),
                    },
                    dataType: 'json',

                    /*
                        If it's good we destroy the previous table and create a new one with the new data
                    */
                    success: function (response) {
                          table.destroy();
                          $("#mydata").html('<thead class="bg-primary"></thead><tbody></tbody>');

                          table = $('#mydata').DataTable({
                                dom: 'Bfrtip',
                                data: response.data,
                                columns: return_table_columns(get_split_by()),
                                info: false,
                                "deferRender": true,
                                "searching":   false,
                                "pageLength": 50,
                                buttons: [
                                   { extend: 'csvHtml5', text: 'Export Data' }
                                ],
                                scrollX: true,
                                fixedColumns: true
                          });

                    }

                });
            });


            //All possible table columns
            table_columns= [
                        { "title": "Team", data: 'team' },
                        { "title": "Season" , data: 'season'},
                        { "title": "GP" , data: 'games'},
                        { "title": "Game.ID" , data: 'game_id'},
                        { "title": "Date" , data: 'date'},
                        { "title": "Opponent" , data: 'opponent'},
                        { "title": "Venue" , data: 'home'},
                        { "title": "Strength" , data: 'strength'},
                        { "title": "TOI" , data: 'toi'},
                        { "title": "GF" , data: 'goals_f'},
                        { "title": "xGF" , data: 'xg_f'},
                        { "title": "SF" , data: 'shots_f'},
                        { "title": "FF" , data: 'fenwick_f'},
                        { "title": "CF" , data: 'corsi_f'},
                        { "title": "GA" , data: 'goals_a'},
                        { "title": "xGA" , data: 'xg_a'},
                        { "title": "SA" , data: 'shots_a'},
                        { "title": "FA" , data: 'fenwick_a'},
                        { "title": "CA" , data: 'corsi_a'},
                        { "title": "GF%" , data: 'GF%'},
                        { "title": "xGF%" , data: 'xGF%'},
                        { "title": "CF%" , data: 'CF%'},
                        { "title": "FF%" , data: 'FF%'},
                        { "title": "wSHF%" , data: 'wshF%'},
                        { "title": "GF60" , data: 'goals_f_60'},
                        { "title": "xGF60" , data: 'xg_f_60'},
                        { "title": "SF60" , data: 'shots_f_60'},
                        { "title": "FF60" , data: 'fenwick_f_60'},
                        { "title": "CF60" , data: 'corsi_f_60'},
                        { "title": "wSHF60" , data: 'wsh_f_60'},
                        { "title": "GA60" , data: 'goals_a_60'},
                        { "title": "xGA60" , data: 'xg_a_60'},
                        { "title": "SA60" , data: 'shots_a_60'},
                        { "title": "FA60" , data: 'fenwick_a_60'},
                        { "title": "CA60" , data: 'corsi_a_60'},
                        { "title": "wSHA60" , data: 'wsh_a_60'},
                        { "title": "Sh%" , data: 'Sh%'},
                        { "title": "FSh%" , data: 'fSh%'},
                        { "title": "xFSh%" , data: 'xfSh%'},
                        { "title": "Sv%" , data: 'Sv%'},
                        { "title": "FSv%" , data: 'FSv%'},
                        { "title": "xFSv%" , data: 'xFSv%'},
                        { "title": "Miss%" , data: 'Miss%'},
                        { "title": "PENT" , data: 'pent'},
                        { "title": "PEND" , data: 'pend'},
                        { "title": "HF" , data: 'hits_f'},
                        { "title": "HA" , data: 'hits_a'},
                        { "title": "Takes" , data: 'takes'},
                        { "title": "Gives" , data: 'gives'},
                        { "title": "Faceoff Wins" , data: 'face_w'},
                        { "title": "Faceoff Losses" , data: 'face_l'},
                        { "title": "Neu. Faceoffs" , data: 'face_neu'},
                        { "title": "Off. Faceoffs" , data: 'face_off'},
                        { "title": "Def. Faceoffs" , data: 'face_def'},
            ]

            /*
                Create a Generic table with no data when request page...need to query to get data.
                This is just to start off...
            */
            table = $('#mydata').DataTable({
                dom: 'Bfrtip',
                data:[],
                columns: table_columns,
                info: false,
                "deferRender": true,
                "searching":   false,
                "pageLength": 50,
                buttons: [
                   { extend: 'csvHtml5', text: 'Export Data' }
                ],
                "scrollX": true,
                fixedColumns: true
            } );


/**********************************************************************************************************************
**********************************************************************************************************************
**********************************************************************************************************************/

            /*
               Get the specific columns for each type of split_by
            */
            function return_table_columns(table_type){
                var tmp_table = []

                if(table_type == "Season"){
                    for(var i = 0; i < table_columns.length; i++) {
                        var column = table_columns[i];

                        if(column.title != "Game.ID" && column.title != "Date"  && column.title != "Opponent"
                           && column.title!="Venue"){
                            tmp_table.push(column);
                        }
                    }
                }else if(table_type == "Cumulative"){
                    for(var i = 0; i < table_columns.length; i++) {
                        var column = table_columns[i];

                        if(column.title!="Game.ID" && column.title!="Date" && column.title!="Opponent"
                               && column.title!="Season" && column.title!="Venue"){
                                tmp_table.push(column);
                        }
                    }
                }else{
                    for(var i = 0; i < table_columns.length; i++) {
                        var column = table_columns[i];

                        if(column.title!="GP"){
                            tmp_table.push(column);
                        }
                    }
                }
                return tmp_table
            }

            // Check that a choice was submitted for each param
            function verify_inputs(){
                if(document.getElementById("Split_By").value == ''){
                   return false;
                }
                if(document.getElementById("Strength").value == ''){
                    return false;
                }
                if(document.getElementById("Venue").value == ''){
                    return false;
                }
                if(document.getElementById("season_type").value == ''){
                    return false;
                }
                if(document.getElementById("adjustmentButton").value == ''){
                    return false;
                }

                return true
            }


            function getStrength() {
                return document.getElementById("Strength").value;
            }

            function get_split_by() {
                return document.getElementById("Split_By").value;
            }

            function getTeam() {
                return document.getElementById("TeamButton").value;
            }

            function get_venue(){
                return document.getElementById("Venue").value;
            }

            function getAdjustments(){
                return document.getElementById("adjustmentButton").value;
            }

            function getToi(){
                s = document.getElementById("toi_filter").value;
                if(s == ''){
                    return 0
                }
                else{
                    return s
                }

            }

            function get_dateFilter1(){
                return document.getElementById("date_filter_1").value;
            }

            function get_dateFilter2(){
                return document.getElementById("date_filter_2").value;
            }

            function get_season_type(){
                return document.getElementById("season_type").value;
            }


            //So Load Button doesn't stay depressed
            $(".btn").mouseup(function(){
                $(this).blur();
            })

        });