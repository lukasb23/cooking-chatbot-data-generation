# cooking-chatbot-data-generation

Building a Cooking Chatbot to search through >35.000 recipes from Epicurious, brief YouTube demo below: 

[![EpiBot Demo](https://img.youtube.com/vi/UUA2kssApyA/0.jpg)](https://www.youtube.com/watch?v=UUA2kssApyA)

#### Key points:
- \>35k recipes extracted from epicurious.com
- Flask application communicating with: 
  - Facebook Messenger over the [*fbmessenger*](https://github.com/rehabstudio/fbmessenger) library
  - Google Dialogflow API (chatbot platform) via Python's [*dialogflow*](https://dialogflow-python-client-v2.readthedocs.io/en/latest/) library 
  - Elasticsearch as recipe store and search engine via [*elasticsearch-py*](https://elasticsearch-py.readthedocs.io/en/master/)
  - Redis for temporarily storing dialogue elements via [*redis-py*](https://redis-py.readthedocs.io/en/latest/)
- Hosted on Google Cloud Platform
  - Google App Engine Flex for running the flask app 
  - Bitnami Elasticsearch-Cluster on Google Compute Engine 
  - Google Cloud Memorystore for Redis

The project was running on Facebook Messenger under [EpiBot - Find your Recipe](https://www.facebook.com/find.your.recipe.1/?modal=admin_todo_tour) (now offline). 

#### Repo: 
This repo focuses on the steps to crawl the data and prepare them for Elasticsearch. The actual app is found under [*cooking-chatbot-app*](https://github.com/lukasb23/cooking-chatbot-app).

#### Disclaimer:
This project is for research purposes only.
