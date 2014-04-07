// FOR POPULATING SONGS
$(document).ready(function () {
    //create alphabet list
    $('<tr><th><label for="id_songs">Songs:</label></th><td class="versebox"><select id="id_alpha" name="alpha"></select></td>').appendTo('table');
    // Populate alphabet list
    $('<option value selected="selected">---- Begins With ----</option>').appendTo('#id_alpha')
        $.get('/worship/alpha/', function(response){
        $(response).appendTo('#id_alpha');
    });
    // all songs no longer makes sense
    // $('<option value="all">All Songs</option>').appendTo('#id_alpha');
    $('<option value="num">0-9</option>').appendTo('#id_alpha');
    var $parent = $('#id_alpha').parent();
    //<img src='/static/songs/admin/img/icon_addlink.gif' width='10' height='10' alt='Add Another'/>
    $("<br>Can't find your song? <a href='../lookup/' onclick='return showAddAnotherPopup(this);'>Import from CCLI</a> or <a href='../songs/' onclick='return showAddAnotherPopup(this);'>Add Manually</a>, then <a href='#' id='refresh'>Refresh</a>.").appendTo($parent);
    //make song box
    $('<select multiple="multiple" id="id_songs" name="songs" ></select>').appendTo($parent);


    
    $('#refresh').click(function(){
            //clear the song list
        $('#id_songs_from').html("");
        //clear the filter query
        $('#id_songs_input').val("");

        
        var $alpha_id = $('#id_alpha').val();
        // <!-- looks at url for response. url goes to view goes to template -->
        $.get('/worship/songs_in_alpha/' + $alpha_id,
            function(response){
                // <!-- adds contents of response (option list) to #id songs dropdown menu -->
                $(response).appendTo('#id_songs_from');
                SelectBox.clear_cache('id_songs_from');
                $('#id_songs_from option').each(function(index){
                    //this is to preserve the contents of 'onmouseover' attribute to preserve tooltip behavior 
                    //after filter. should only affect option values that have attribute 'onmouseover'
                    var $onmouse = $(this).attr('onmouseover');
                    SelectBox.add_to_cache('id_songs_from', {value: $(this).val(), text: $(this).text(), onmouse:$onmouse, displayed: 1});
                });
            SelectFilter.refresh_icons('id_songs');    
            }
        );
    });
    
    //if alpha selection changes
    $('#id_alpha').change(function(){
        //clear the song list
        $('#id_songs_from').html("");
        //clear the filter query
        $('#id_songs_input').val("");

        
        var $alpha_id = $('#id_alpha').val();
        // <!-- looks at url for response. url goes to view goes to template -->
        $.get('/worship/songs_in_alpha/' + $alpha_id,
            function(response){
                // <!-- adds contents of response (option list) to #id songs dropdown menu -->
                $(response).appendTo('#id_songs_from');
                SelectBox.clear_cache('id_songs_from');
                $('#id_songs_from option').each(function(index){
                    //this is to preserve the contents of 'onmouseover' attribute to preserve tooltip behavior 
                    //after filter. should only affect option values that have attribute 'onmouseover'
                    var $onmouse = $(this).attr('onmouseover');
                    SelectBox.add_to_cache('id_songs_from', {value: $(this).val(), text: $(this).text(), onmouse:$onmouse, displayed: 1});
                });
            SelectFilter.refresh_icons('id_songs');    
            }
        );
        
    });
    
    
    // THIS DOES NOT INITIALIZE THE FILTER BOXES. RELIES ON DYNAMIC_POPULATE.JS TO DO THAT.
    // jQuery.each($("select[multiple]"), function () {    
    // SelectFilter.init(this.id, this.name, 0, "/static/songs/admin/");  

    // });  
    
    
    
});



