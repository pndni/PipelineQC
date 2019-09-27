    {% extends "reportlet.tpl" %}
    {% block header %}<h2>{{ name|e }}{% endblock %}
    {% block description %}
    Showing file
    <ul>
        <li><a href="{{ filename }}">{{ filename|e }}</a></li>
    </ul>
    with labels from
    <ul>
        <li><a href="{{ labelfilename }}">{{ labelfilename|e }}</a></li>
    </ul>
    {% endblock %}
    {% block images %}
    <div class="plotbase">
    	 {{ svg }}
    </div>
    {% endblock %}