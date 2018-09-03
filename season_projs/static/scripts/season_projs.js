$.noConflict();
        jQuery(document).ready(function( $ ) {
            // All Table Columns
            table_columns = [
                    { "title": "Team", data: 'team'},
                    { "title": "Points" , data: 'points_avg'},
                    { "title": "Points Std" , data: 'points_std'},
                    { "title": "Round 1%",  data: 'round_1_prob'},
                    { "title": "Division Finals%", data: 'round_2_prob'},
                    { "title": "Conference Finals%", data: 'round_3_prob'},
                    { "title": "Finals%", data: 'round_4_prob'},
                    { "title": "Champion%", data: 'champion_prob'},
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
                "ajax": {
                    "url": "/seasonprojections/Query/",
                    "type": "GET",
                 }
            });
        });
