    {% extends "reportlet.tpl" %}
    {% block header %}<h2>{{ name }}{% endblock %}
    {% block description %}
    Showing file
    <ul>
        <li><a href="{{ filename }}">{{ filename }}</a></li>
    </ul>
    with labels from
    <ul>
        <li><a href="{{ labelfilename }}">{{ labelfilename }}</a></li>
    </ul>
    {% endblock %}
    {% block images %}
    <div class="plotbase">
    	 {{ svg }}
    </div>
    {% endblock %}