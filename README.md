# gpt-tutorial
Tutorial for creating apps with GPTs using the Open AI framework in Python.

A helpful rule of thumb is that one token generally corresponds to ~4 characters of text for common English text. This translates to roughly ¾ of a word (so 100 tokens ~= 75 words).

flask --app gpt_chat_app run --debug

flask --app gpt_chat_app init-db

docker build -t gpt-chat-app:v1.0 .

docker run -d -p 5000:5000 gpt-chat-app:v1.0
