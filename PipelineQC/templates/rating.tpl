    <div class=fixedpos>
    <h2>{{ name }}</h2>
    {% if radio %}
    <h3>{{ radio.name_ }}</h3>
    <form name="{{ radio.name_no_spaces }}" class=radioform>
    {% for option in radio.options %}
       <input type="radio" value="{{ option.value }}">{{ option.name_ }} 
    {% endfor %}
    </form>
    {% endif %}
    {% if checkbox %}
    <h3>{{ checkbox.name_ }}</h3>
    <form name="{{ checkbox.name_no_spaces }}" class=checkboxform>
    {% for field in checkbox.fields %}
       <input type="checkbox" value="{{ field }}">{{ field }}
    {% endfor %}
    </form>
    {% endif %}
    {% if text %}
    <h3>{{ text.name_ }}</h3>
    <form name="{{ text.name_no_spaces }}" class=textform>
    <input type="text">
    </form>
    {% endif %}
    </div>