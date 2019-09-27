    <h2>{% block header %}{% endblock %}</h2>
    {% if errormessage %}
    <div class="errormessage">
    {{ errormessage|e }}
    </div>
    {% else %}
    <div class="description">
    {% block description %}{% endblock %}
    </div>
    {% block images %}{% endblock %}
    {% endif %}
    {% if form %}
    {% include formfile %}
    {% endif %}