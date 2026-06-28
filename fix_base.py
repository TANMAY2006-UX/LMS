import os

path = r'c:\Users\mayur\OneDrive\Desktop\Coding\libra\app\templates\base.html'
with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

# Replace all occurrences
content = content.replace('request.endpoint', 'endpoint')

# Find the body tag to inject the variable
body_tag = '<body class="font-sans text-stone-900 bg-stone-50 flex h-full overflow-hidden">'
replacement = body_tag + '\n    {% set endpoint = request.endpoint or \'\' %}'

content = content.replace(body_tag, replacement)

# Because we replaced request.endpoint globally above, our injection just became 
# {% set endpoint = endpoint or '' %}. We must fix that back:
content = content.replace('{% set endpoint = endpoint or \'\' %}', '{% set endpoint = request.endpoint or \'\' %}')

with open(path, 'w', encoding='utf-8') as f:
    f.write(content)
print("Success")
