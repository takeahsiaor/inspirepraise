// THIS IS FOR POPULATING VERSES
$(document).ready(function () {
    //create book list
    $('<tr><th><label for="id_verses">Verses:</label></th><td class="versebox"><select id="id_books" name="books"></select></td>').appendTo('table');
    // Populate Book list
    $('<option value selected="selected">--------- Book ---------</option>').appendTo('#id_books')
        $.get('/worship/book_list/', function(response){
        $(response).appendTo('#id_books');
    });

    var $parent = $('#id_books').parent()
    
    //make chapter list box and verse list box
    $('<select id="id_chapters" name="chapters"></select>').appendTo($parent);
    $('<option value selected="selected">--- Chapter ---</option>').appendTo('#id_chapters')
    $('<select multiple="multiple" id="id_verses" name="verses" ></select>').appendTo($parent);


    //if book selection changes
    $('#id_books').change(function(){
        //clear the chapter and verse lists
        $('#id_chapters').html(""); 
        $('#id_verses_from').html("");
        // <!-- repopulate chapter list with blanks -->
        $('<option value selected="selected">--- Chapter ---</option>').appendTo('#id_chapters')
        
        var $book_id = $('#id_books').val();
        // <!-- looks at url for response. url goes to view goes to template -->
        $.get('/worship/chapters_in_book/' + $book_id,
            function(response){
                // <!-- adds contents of response (option list) to #id chapter dropdown menu -->
                $(response).appendTo('#id_chapters');
                

            }
        );
        
    });
    
    
    //if chapter selection changes
    $('#id_chapters').change(function(){
        //clear verse list
        $('#id_verses_from').html("");
        // $('<select multiple="multiple" id="id_verses" name="verses" ></select>').appendTo($parent);

        // <!-- get the chapter id number -->
        var $chapter_id = $('#id_chapters').val();

        // <!-- look at url that goes to view to template for option list response -->
        $.get('/worship/verses_in_chapter/' + $chapter_id,
            function(response2){
                $(response2).appendTo('#id_verses_from');  
                SelectBox.clear_cache('id_verses_from');
             $('#id_verses_from option').each(function(index){
                
                SelectBox.add_to_cache('id_verses_from', {value: $(this).val(), text: $(this).text(), displayed: 1});
                
             });
            SelectFilter.refresh_icons('id_verses');
            });
            

    });
    
    jQuery.each($("select[multiple]"), function () {    
    SelectFilter.init(this.id, this.name, 0, "/static/songs/admin/");  

    });  
    
    
    
});



