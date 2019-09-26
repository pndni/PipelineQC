    {% extends "reportlet.tpl" %}
    {% block header %}{{ name }}{% endblock %}
    {% block description %}
    Showing file
    <ul>
        <li><a href="{{ filename }}">{{ filename }}</a></li>
    </ul>
    {% if labelfilename %}
    with contours from
    <ul>
        <li><a href="{{ labelfilename }}">{{ labelfilename }}</a></li>
    </ul>
    {% endif %}
    {% endblock %}
    {% block images %}
    <div class="imagearray">
    	 {% for svgrow in svg %}
	     <div class="imagerow">
	      {% for svgsingle in svgrow %}
	         <div class="imagebase">
		 {{ svgsingle }}
	         </div>
	      {% endfor %}
	      </div>
	 {% endfor %}
    </div>
    {% endblock %}