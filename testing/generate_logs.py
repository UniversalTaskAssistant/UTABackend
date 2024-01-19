import json
import os
import glob
from os.path import join as pjoin
from jinja2 import Template

from uta.config import *


# HTML/CSS/JS Template
html_template = """
<!DOCTYPE html>
<html>
<head>
<style>
  table {
    width: 100%;
    border-collapse: collapse;
    overflow: scroll;
  }
  th, td {
    border: 1px solid black;
    text-align: left;
    padding: 8px;
    max-width:200px;
    word-wrap: break-word;
  }
  tr:nth-child(even) {background-color: #f2f2f2;}
  .pink { background-color: pink; }
</style>
<script>
  function togglePink(element) {
    element.classList.toggle('pink');
  }
</script>
</head>
<body>

<h2>Screenshots and Data Table</h2>

<table>
  <!-- Table header -->
  <tr>
    <th>Task</th>
    <th>Task Type</th>
    <th>Sub-Tasks</th>
    <th>Fail</th>
    <th>Records</th>
  </tr>

  <!-- Loop over tasks -->
  {% for task_dir_name, data in directories.items() %}
    <!-- First sub-row -->
    <tr>
      <td rowspan="5">{{task_dir_name}}</td>
      <td rowspan="5">{{data['task_type']}}</td>
      <td rowspan="5">{{data['subtasks']}}</td>
      <td rowspan="5"><input type="radio" onclick="togglePink(this.parentNode)"></td>
      <!-- Loop for conversation assistant -->
      {% for (conv_id, conversation) in data['conversation_clarification']|dictsort %}
        <td>{{conversation['assistant']}}</td>
      {% endfor %}
    </tr>

    <!-- Second sub-row for conversation user -->
    <tr>
      {% for (conv_id, conversation) in data['conversation_clarification']|dictsort %}
        <td>{{conversation['user']}}</td>
      {% endfor %}
    </tr>

    <!-- Third and Fourth sub-rows for screenshots -->
    {% for _ in range(2) %} <!-- Repeat twice for two sub-rows -->
      <tr>
        {% for (key, screenshot) in data['screenshot']|dictsort %}
          <td>
            {% if loop.index == 1 %} <!-- Only add image in the third sub-row -->
              <img src="{{screenshot['img']}}" alt="Screenshot_{{key}}" style="width:200px">
            {% else %} <!-- Add relation and action in the fourth sub-row -->
              <input type="radio" onclick="togglePink(this.parentNode)">
              <p>Relation: {{screenshot['info']['rel']}}</p>
              <p>Action: {{screenshot['info']['act']}}</p>
            {% endif %}
          </td>
        {% endfor %}
      </tr>
    {% endfor %}

    <!-- Fifth sub-row for error -->
    <tr>
      <td><p>Error: {{data['error']}}</p></td>
    </tr>
  {% endfor %}
</table>

</body>
</html>
"""


user_id = 'user1'
directories = {}
for task_dir in glob.glob(pjoin(DATA_PATH, user_id) + '/task*'):
    task_dir_name = os.path.basename(task_dir)
    data = {}
    with open(task_dir + '/task.json', 'r', encoding='utf-8') as file:
        task_json = json.load(file)
        data['task_type'] = task_json['task_type']
        data['subtasks'] = str(task_json['subtasks'])
        data['conversation_clarification'] = {}

        for i in range(0, len(task_json['conversation_clarification']) - 1, 2):
            data['conversation_clarification'][str(i)] = {'assistant': str(task_json['conversation_clarification'][i]),
                                                          'user': str(task_json['conversation_clarification'][i + 1])}
        data['conversation_clarification'][str(i)] = {'assistant': str(task_json['conversation_clarification'][i]),
                                                      'user': str(task_json['conversation_clarification'][i])}

        data['screenshot'] = {}
        for img_idx, one_img in enumerate(glob.glob(task_dir + '/*_annotated.png')):
            data['screenshot'][str(img_idx)] = {'img': one_img, 'info': {'rel': str(task_json['relations'][img_idx]),
                                                                         'act': str(task_json['actions'][img_idx])}}

        if os.path.exists(task_dir + '/error.json'):
            with open(task_dir + '/error.json', 'r', encoding='utf-8') as error:
                error_json = json.load(error)
                data['error'] = error_json['error']
        else:
            data['error'] = "No error."

    if len(data) > 0:
        directories[task_dir_name] = data

# Generate the final HTML
template = Template(html_template)
html = template.render(directories=directories)

# Write the HTML file
with open(pjoin(DATA_PATH, user_id) + '/output.html', 'w', encoding='utf-8') as file:
    file.write(html)

# Notify user
print("HTML file 'output.html' generated successfully.")
