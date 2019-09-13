    <h2>{{ name1 }} and {{ name2 }}</h2>
    {% if errormessage %}
    <div class="errormessage">
    {{ errormessage }}
    </div>
    {% else %}
    <div class="description">
    Comparing files
    <ul>
        <li><a href="{{ filename1 }}">{{ filename1 }}</a></li>
	<li><a href="{{ filename2 }}">{{ filename2 }}</a></li>
    </ul>
    </div>
    <div class="imagebase">
        {{ svg1 }}
        {{ svg2 }}
    </div>
    {% endif %}
    {% if form %}
    <form name={{ name_no_spaces }} class=radioform>
    	  <input type="radio" value="0">0 <input type="radio" value="0.25">0.25 <input type="radio" value="0.5">0.5 <input type="radio" value="0.75">0.75  <input type="radio" value="1">1 
    </form>
    <form name={{ name_no_spaces }}_notes class=textform>
    	  Notes
    	  <input type="text">
    </form>
    {% endif %}