    <div class=rightcolumn>
    <h2>{{ name|e }}</h2>
    {% for widget in widgets %}
        <h3>{{ widget.name_|e }}</3>
        {% if widget.type == "radio" %}
        	<form name="{{ widget.name_no_spaces }}" class=radioform>
        	{% for option in widget.options %}
        	   <input type="radio" name="{{ widget.name_no_spaces }}" value="{{ option.value }}">{{ option.name_|e }}<br>
        	{% endfor %}
        	</form>
        {% endif %}
        {% if widget.type == "checkbox" %}
        	<form name="{{ widget.name_no_spaces }}" class=checkboxform>
        	{% for field in widget.fields %}
        	   <input type="checkbox" value="{{ field }}">{{ field|e }}<br>
        	{% endfor %}
        	</form>
        {% endif %}
        {% if widget.type ==  "text" %}
        	<form name="{{ widget.name_no_spaces }}" class=textform>
        	<input type="text">
        	</form>
        {% endif %}
    {% endfor %}
    <form onsubmit="submitform()">
      <input type="submit" value="Download QC">
    </form>
    </div>