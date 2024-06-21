FROM python:3.12-slim

WORKDIR /code

EXPOSE 80

ENV PYTHONPATH=/code/app
ENV PATH="/root/.cargo/bin:${PATH}"

COPY ./requirements.txt /code/requirements.txt

RUN curl https://sh.rustup.rs -sSf | sh -s -- -y
RUN ln -s $HOME/.cargo/env /etc/profile.d/cargo_env.sh
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

COPY ./app /code/app

CMD ["uvicorn", "app.pwgateway:app", "--host", "0.0.0.0", "--port", "80"]

# docker build -t jbuchner/pwplugin .
# docker buildx build --platform linux/arm/v7,linux/arm64/v8,linux/amd64 -t jbuchner/pwplugin --push .
# docker push jbuchner/pwplugin
