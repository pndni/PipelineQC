    {% extends "reportlet.tpl" %}
    {% block header %}{{ name1|e }} and {{ name2|e }}{% endblock %}
    {% block description %}
    Comparing files
    <ul>
        <li><a href="{{ filename1 }}">{{ filename1|e }}</a></li>
       <li><a href="{{ filename2 }}">{{ filename2|e }}</a></li>
    </ul>
    {% endblock %}
    {% block images %}
    <div class="imagearray">
    {% for svgrow in svg %}
        <div class="imagerow">
        {% for svg1, svg2 in svgrow %}
            <div class="imagebase">
            {{ svg1 }}
            {{ svg2 }}
            </div>
        {% endfor %}
        </div>
    {% endfor %}
    </div>
    {% endblock %}