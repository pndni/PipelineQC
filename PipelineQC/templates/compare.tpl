    {% extends "reportlet.tpl" %}
    {% block header %}{{ name1 }} and {{ name2 }}{% endblock %}
    {% block description %}
    Comparing files
    <ul>
        <li><a href="{{ filename1 }}">{{ filename1 }}</a></li>
    	<li><a href="{{ filename2 }}">{{ filename2 }}</a></li>
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