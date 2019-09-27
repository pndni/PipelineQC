    {% extends "reportlet.tpl" %}
    {% block header %}{{ name|e }}{% endblock %}
    {% block description %}
    Showing file
    <ul>
        <li><a href="{{ filename }}">{{ filename|e }}</a></li>
    </ul>
    {% if labelfilename %}
    with contours from
    <ul>
        <li><a href="{{ labelfilename }}">{{ labelfilename|e }}</a></li>
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