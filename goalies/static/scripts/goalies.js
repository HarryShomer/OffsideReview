$.noConflict();
        jQuery(document).ready(function( $ ) {


            //Used to get player search list when page loads
            $.ajax({
                url: "/goalies/GetPlayerList/",
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
                    var thirdLine = "1. Strength \n2. Split By \n3. Venue \n4. Season Type \n5. Adjustments";
                    alert(firstLine + "\n\n" + secondLine + "\n" + thirdLine)

                    return;
                }

                $.ajax({
                    url: '/goalies/Query/',
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
                        'toi': getToi(),
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

                          });
                    }

                });
            });


            //All possible table columns
            table_columns= [
                        { "title": "Player", data: 'player' },
                        { "title": "Season" , data: 'season'},
                        { "title": "GP" , data: 'games'},
                        { "title": "Game.ID" , data: 'game_id'},
                        { "title": "Date" , data: 'date'},
                        { "title": "Team" , data: 'team'},
                        { "title": "Opponent" , data: 'opponent'},
                        { "title": "Strength" , data: 'strength'},
                        { "title": "TOI" , data: 'toi_on'},
                        { "title": "GA" , data: 'goals_a'},
                        { "title": "SA" , data: 'shots_a'},
                        { "title": "FA" , data: 'fenwick_a'},
                        { "title": "CA" , data: 'corsi_a'},
                        { "title": "GA60" , data: 'goals_a_60'},
                        { "title": "SA60" , data: 'shots_a_60'},
                        { "title": "FA60" , data: 'fenwick_a_60'},
                        { "title": "CA60" , data: 'corsi_a_60'},
                        { "title": "Sv%" , data: 'Sv%'},
                        { "title": "FSv%" , data: 'FSv%'},
                        { "title": "Miss%" , data: 'Miss%'}
            ]

            //Generic table with no data when request page...need to query to get data
            table = $('#mydata').DataTable({
                dom: 'Bfrtip',
                data:[],
                columns: table_columns,
                info: false,
                "searching":   false,
                "pageLength": 50,
                buttons: [
                    { extend: 'csvHtml5', text: 'Export Data' }
                ],

                "scrollX": true
            } );


            function return_table_columns(table_type){
                var tmp_table = []

                if(table_type == "Season"){
                    for(var i = 0; i < table_columns.length; i++) {
                        var column = table_columns[i];

                        if(column.title != "Game.ID" && column.title != "Date"  && column.title != "Opponent"){
                            tmp_table.push(column);
                        }
                    }
                }else if(table_type == "Cumulative"){
                    for(var i = 0; i < table_columns.length; i++) {
                        var column = table_columns[i];

                        if(column.title!="Game.ID" && column.title!="Date" && column.title!="Opponent" && column.title!="Season"){
                            tmp_table.push(column);
                        }
                    }
                }else if(table_type == "Game"){
                    for(var i = 0; i < table_columns.length; i++) {
                        var column = table_columns[i];

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


            //So Load Button doesn't stay depressed
            $(".btn").mouseup(function(){
                $(this).blur();
            })


        });





