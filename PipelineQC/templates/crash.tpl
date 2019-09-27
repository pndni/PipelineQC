    <h2>{{ name|e }}</h2>
    {% for crash in crashes %}
       <div class="description">
       From crashfile <a href="{{ crash.crashfile }}">{{ crash.crashfile|e }}</a>
       </div>
       <div class="crash">
       {% if crash.text %}
       <pre>
       {{ crash.text|e }}
       </pre>
       {% else %}
       <dl>
           <dt>Node Name</dt><dd>{{ crash.nodename|e }}</dd>
           <dt>Node Full Name</dt><dd>{{ crash.nodefullname|e }}</dd>
           <dt>Interface</dt><dd>{{ crash.interface|e }}</dd>
           <dt>Traceback</dt><dd><samp>{{ crash.traceback|e }}</samp></dd>
       </dl>
       {% endif %}
       </div>
   {% else %}
       <div class="success">
       No crash files found!
       </div>
   {% endfor %}
	   