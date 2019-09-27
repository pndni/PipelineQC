    <div class=leftcolumn>
    <h2>{{ name|e }}</h2>
    {% if radio %}
    <h3>{{ radio.name_|e }}</h3>
    <form name="{{ radio.name_no_spaces }}" class=radioform>
    {% for option in radio.options %}
       <input type="radio" value="{{ option.value }}">{{ option.name_|e }}<br>
    {% endfor %}
    </form>
    {% endif %}
    {% if checkbox %}
    <h3>{{ checkbox.name_|e }}</h3>
    <form name="{{ checkbox.name_no_spaces }}" class=checkboxform>
    {% for field in checkbox.fields %}
       <input type="checkbox" value="{{ field }}">{{ field|e }}<br>
    {% endfor %}
    </form>
    {% endif %}
    {% if text %}
    <h3>{{ text.name_|e }}</h3>
    <form name="{{ text.name_no_spaces }}" class=textform>
    <input type="text">
    </form>
    {% endif %}
      <form onsubmit="submitform()">
	<input type="submit" value="Download QC">
      </form>
    </div>