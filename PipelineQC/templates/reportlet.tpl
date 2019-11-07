    <h2>{% block header %}{% endblock %}</h2>
    {% if errormessage %}
    <div class="errormessage">
    {{ errormessage|e }}
    {% if errormessageverbatim %}
    <pre>{{ errormessageverbatim|e }}<pre>
    {% endif %}
    </div>
    {% else %}
    <div class="description">
    {% if description %}
	<p>{{ description|e }}</p>
    {% endif %}
    {% block description %}{% endblock %}
    </div>
    {% block images %}{% endblock %}
    {% endif %}
    {% if form %}
    {% include formfile %}
    {% endif %}