$.noConflict();
        jQuery(document).ready(function( $ ) {

            //Used to get player search list when page loads
            $.ajax({
                url: "/skaters/GetPlayerList/",
                type : "GET",
                context: document.body,
                dataType: 'json',

                success: function(response){
                   search_array = response['search_list'];
                   searchBar.data('select2').dataAdapter.updateOptions(search_array);
                }
            });


            // Making it so that the search bar options can be updated dynamically
            // This is only done once with an ajax call when the page first loads
            $.fn.select2.amd.define('select2/data/customAdapter',
                ['select2/data/array', 'select2/utils'],
                function (ArrayAdapter, Utils) {
                    function CustomDataAdapter ($element, options) {
                        CustomDataAdapter.__super__.constructor.call(this, $element, options);
                    }
                    Utils.Extend(CustomDataAdapter, ArrayAdapter);
                    CustomDataAdapter.prototype.updateOptions = function (data) {
                        this.$element.find('option').remove(); // remove all options
                        this.addOptions(this.convertToOptions(data));
                    }
                    return CustomDataAdapter;
                }
            );
            var customAdapter = $.fn.select2.amd.require('select2/data/customAdapter');

            var search_array = []
            var searchBar = $("#search").select2({
                placeholder: "Search a Player",
                allowClear: true,
                dataAdapter: customAdapter,
                data: search_array,
                maximumSelectionLength: 10
            });


            //Get query when click load button
            $("#loadButton").click(function(){

                if(!verify_inputs()){
                    var firstLine = "Invalid Input: You are missing at least one required input.";
                    var secondLine = "The following buttons are required:";
                    var thirdLine = "1. Strength \n2. Split By \n3. Venue \n4. Season Type \n5. Adjustments \n6. Stats";
                    alert(firstLine + "\n\n" + secondLine + "\n" + thirdLine)

                    return;
                }

                $.ajax({
                    url: '/skaters/Query/',
                    type : "GET",
                    data: {
                        'strength': getStrength(),
                        'split_by': get_split_by(),
                        'team': getTeam(),
                        'search': getSearch(),
                        'venue': get_venue(),
                        'season_type': get_season_type(),
                        'date_filter_from': get_dateFilter1(),
                        'date_filter_to': get_dateFilter2(),
                        'adjustment': getAdjustments(),
                        'position': get_position(),
                        'toi': getToi(),
                        'stats_view': get_stats_view(),
                    },
                    dataType: 'json',

                    success: function (response) {
                          //Destroy and recreate table
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
                                "scrollX": true,
                                fixedColumns: true
                          });

                    }

                });
            });

            table_columns_on_ice = [
                { "title": "Player", data: 'player' },
                { "title": "Position", data: 'position' },
                { "title": "Handedness", data: 'handedness' },
                { "title": "Season" , data: 'season'},
                { "title": "Team", data: 'team' },
                { "title": "GP" , data: 'games'},
                { "title": "Game.ID" , data: 'game_id'},
                { "title": "Date" , data: 'date'},
                { "title": "Opponent" , data: 'opponent'},
                { "title": "Venue" , data: 'home'},
                { "title": "Strength" , data: 'strength'},
                { "title": "TOI" , data: 'toi_on'},
                { "title": "GF" , data: 'goals_f'},
                { "title": "GA" , data: 'goals_a'},
                { "title": "SF" , data: 'shots_f'},
                { "title": "SA" , data: 'shots_a'},
                { "title": "FF" , data: 'fenwick_f'},
                { "title": "FA" , data: 'fenwick_a'},
                { "title": "CF" , data: 'corsi_f'},
                { "title": "CA" , data: 'corsi_a'},
                { "title": "GF%" , data: 'GF%'},
                { "title": "CF%" , data: 'CF%'},
                { "title": "FF%" , data: 'FF%'},
                { "title": "GF60" , data: 'goals_f_60'},
                { "title": "GA60" , data: 'goals_a_60'},
                { "title": "SF60" , data: 'shots_f_60'},
                { "title": "SA60" , data: 'shots_a_60'},
                { "title": "FF60" , data: 'fenwick_f_60'},
                { "title": "FA60" , data: 'fenwick_a_60'},
                { "title": "CF60" , data: 'corsi_f_60'},
                { "title": "CA60" , data: 'corsi_a_60'},
                { "title": "Sh%" , data: 'Sh%'},
                { "title": "FSh%" , data: 'fSh%'},
                { "title": "Sv%" , data: 'Sv%'},
                { "title": "FSv%" , data: 'FSv%'},
                { "title": "Miss%" , data: 'Miss%'},
            ]


            table_columns_ind = [
                { "title": "Player", data: 'player' },
                { "title": "Position", data: 'position' },
                { "title": "Handedness", data: 'handedness'},
                { "title": "Season" , data: 'season'},
                { "title": "Team", data: 'team' },
                { "title": "GP" , data: 'games'},
                { "title": "Game.ID" , data: 'game_id'},
                { "title": "Date" , data: 'date'},
                { "title": "Opponent" , data: 'opponent'},
                { "title": "Venue" , data: 'home'},
                { "title": "Strength" , data: 'strength'},
                { "title": "TOI" , data: 'toi_on'},
                { "title": "Goals" , data: 'goals'},
                { "title": "Assists" , data: 'assists'},
                { "title": "A1" , data: 'a1'},
                { "title": "A2" , data: 'a2'},
                { "title": "P" , data: 'p'},
                { "title": "P1" , data: 'p1'},
                { "title": "iSh%" , data: 'ish%'},
                { "title": "ifSh%" , data: 'ifsh%'},
                { "title": "iSF" , data: 'isf'},
                { "title": "iFen" , data: 'ifen'},
                { "title": "iCorsi" , data: 'icors'},
                { "title": "G60" , data: 'g60'},
                { "title": "A60" , data: 'a60'},
                { "title": "A160" , data: 'a160'},
                { "title": "A260" , data: 'a260'},
                { "title": "P60" , data: 'p60'},
                { "title": "P160" , data: 'p160'},
                { "title": "iSF60" , data: 'isf60'},
                { "title": "iFen60" , data: 'ifen60'},
                { "title": "iCorsi60" , data: 'icors60'},
                { "title": "HF" , data: 'hits_f'},
                { "title": "HA" , data: 'hits_a'},
                { "title": "Takeaways" , data: 'takes'},
                { "title": "Giveaways" , data: 'gives'},
                { "title": "PEND" , data: 'pend'},
                { "title": "PENT" , data: 'pent'},
                { "title": "Blocks" , data: 'iblocks'},
                { "title": "Faceoff Wins" , data: 'ifac_win'},
                { "title": "Faceoff Losses" , data: 'ifac_loss'},
                { "title": "Faceoff%" , data: 'face%'},
            ]


            table_columns_rel = [
                { "title": "Player", data: 'player' },
                { "title": "Position", data: 'position' },
                { "title": "Handedness", data: 'handedness' },
                { "title": "Season" , data: 'season'},
                { "title": "Team", data: 'team' },
                { "title": "GP" , data: 'games'},
                { "title": "Game.ID" , data: 'game_id'},
                { "title": "Date" , data: 'date'},
                { "title": "Opponent" , data: 'opponent'},
                { "title": "Venue" , data: 'home'},
                { "title": "Strength" , data: 'strength'},
                { "title": "TOI" , data: 'toi_on'},
                { "title": "REL GF%" , data: 'GF%_rel'},
                { "title": "REL CF%" , data: 'CF%_rel'},
                { "title": "REL FF%" , data: 'FF%_rel'},
                { "title": "REL GF60" , data: 'goals_f_60_rel'},
                { "title": "REL GA60" , data: 'goals_a_60_rel'},
                { "title": "REL SF60" , data: 'shots_f_60_rel'},
                { "title": "REL SA60" , data: 'shots_a_60_rel'},
                { "title": "REL FF60" , data: 'fenwick_f_60_rel'},
                { "title": "REL FA60" , data: 'fenwick_a_60_rel'},
                { "title": "REL CF60" , data: 'corsi_f_60_rel'},
                { "title": "REL CA60" , data: 'corsi_a_60_rel'},
                { "title": "REL Sh%" , data: 'Sh%_rel'},
                { "title": "REL Fsh%" , data: 'fSh%_rel'},
                { "title": "REL Sv%" , data: 'Sv%_rel'},
                { "title": "REL FSv%" , data: 'FSv%_rel'},
                { "title": "REL Miss%" , data: 'Miss%_rel'},
            ]

            table_columns_zone = [
                { "title": "Player", data: 'player' },
                { "title": "Position", data: 'position' },
                { "title": "Handedness", data: 'handedness' },
                { "title": "Season" , data: 'season'},
                { "title": "Team", data: 'team' },
                { "title": "GP" , data: 'games'},
                { "title": "Game.ID" , data: 'game_id'},
                { "title": "Date" , data: 'date'},
                { "title": "Opponent" , data: 'opponent'},
                { "title": "Venue" , data: 'home'},
                { "title": "Strength" , data: 'strength'},
                { "title": "TOI" , data: 'toi_on'},
                { "title": "Neu. Faceoffs" , data: 'face_neu'},
                { "title": "Off. Faceoffs" , data: 'face_off'},
                { "title": "Def. Faceoffs" , data: 'face_def'},
                { "title": "Off.Zone%" , data: 'off_zone%'},
                { "title": "Def.Zone%" , data: 'def_zone%'},
                { "title": "Neu.Zone%" , data: 'neu_zone%'},
                { "title": "REL Off.Zone%" , data: 'off_zone%_rel'},
                { "title": "REL Def.Zone%" , data: 'def_zone%_rel'},
                { "title": "REL Neu.Zone%" , data: 'neu_zone%_rel'},
            ]


            //Generic table with no data when request page...need to query to get data
            table = $('#mydata').DataTable({
                dom: 'Bfrtip',
                data:[],
                columns: table_columns_on_ice,
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


            function return_table_columns(season_type){
                //Get view type
                view_type = get_stats_view()

                if(view_type == "Individual"){
                    full_table = table_columns_ind;
                }else if(view_type == "On Ice"){
                    full_table = table_columns_on_ice;
                }else if(view_type == "Relative"){
                    full_table = table_columns_rel;
                }else {
                    full_table = table_columns_zone;
                }

                var tmp_table = []

                if(season_type == "Season"){
                    for(var i = 0; i < full_table.length; i++) {
                        var column = full_table[i];

                        if(column.title != "Game.ID" && column.title != "Date"  && column.title != "Opponent"
                           && column.title!="Venue"){
                            tmp_table.push(column);
                        }
                    }
                }else if(season_type  == "Cumulative"){
                    for(var i = 0; i < full_table.length; i++) {
                        var column = full_table[i];

                        if(column.title!="Game.ID" && column.title!="Date" && column.title!="Opponent"
                               && column.title!="Season" && column.title!="Venue"){
                                tmp_table.push(column);
                        }
                    }
                }else{
                    for(var i = 0; i < full_table.length; i++) {
                        var column = full_table[i];

                        if(column.title!="GP"){
                            tmp_table.push(column);
                        }
                    }
                }
                return tmp_table
            }


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
                if(document.getElementById("stats_view").value == ''){
                    return false;
                }

                return true
            }


            function getSearch(){
                return document.getElementById("search").value;
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

            function get_position(){
                return document.getElementById("position").value;
            }

            function get_stats_view(){
                return document.getElementById("stats_view").value;
            }


            //So Load Button doesn't stay depressed
            $(".btn").mouseup(function(){
                $(this).blur();
            })

        });





