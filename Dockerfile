# ---------------------------------------------------------------------------------------------------------------------
# ** info: stage 1: testing stage
# ---------------------------------------------------------------------------------------------------------------------

# ** info: declaration of the testing image base version
FROM python:3.10.6 as testing

# ** info: declaration of the testing image file system
ARG WORKDIR=/home/testing

# ** info: creating the testing image file system
RUN mkdir -p $WORKDIR

# ** info: establishing the default working directory
WORKDIR $WORKDIR

# ** info: copying the requirements files from the building context
COPY ["requirements.app.txt" ,"$WORKDIR/"]
COPY ["requirements.dev.txt" ,"$WORKDIR/"]

# ** info: installing the dependencies and upgrading pip, wheel and setuptools
RUN pip install --no-cache --upgrade pip
RUN pip install --no-cache --upgrade wheel
RUN pip install --no-cache --upgrade setuptools
RUN pip install --no-cache -r $WORKDIR/requirements.app.txt
RUN pip install --no-cache -r $WORKDIR/requirements.dev.txt

# ** info: validating dependencies integrity
RUN pip check

# ** info: copying the source code of the application from the building context
COPY ["src", "$WORKDIR/src"]

# ** info: cleaning the python __pycache__ files
RUN find . | grep -E "(/__pycache__$|\.pyc$|\.pyo$)" | xargs rm -rf

# ** info: running the application tests
# ! warning: test unabled
# todo: Restore testing in this stage.
# RUN python -m unittest -v $WORKDIR/src/testing/*.py

# ---------------------------------------------------------------------------------------------------------------------
# ** stage 2: production image
# ---------------------------------------------------------------------------------------------------------------------

# ** info: declaration of the production image base version
FROM python:3.10.6-slim-buster

# ** info: declaration of the production file system and username inside the production image
ARG USERNAME=production
ARG WORKDIR=/home/$USERNAME

# ** info: creating the user on bash and their home directory
RUN useradd --create-home --shell /bin/bash $USERNAME

# ** info: copying the app requirements file from the testing image
COPY --from=testing ["/home/testing/requirements.app.txt","$WORKDIR/"]

# ** info: changing the premises of the file system
RUN chown -R $USERNAME $WORKDIR

RUN find "$WORKDIR/" -type d -exec chmod 755 {} \;
RUN find "$WORKDIR/" -type f -exec chmod 755 {} \;

RUN chmod 755 $WORKDIR

# ** info: establishing the default working directory inside the production image
WORKDIR $WORKDIR

# ** info: installing the dependencies and upgrading pip, wheel and setuptools
RUN pip install --no-cache --upgrade pip
RUN pip install --no-cache --upgrade wheel
RUN pip install --no-cache --upgrade setuptools
RUN pip install --no-cache -r $WORKDIR/requirements.app.txt

# ** info: copying source code of the application from the testing image
COPY --from=testing ["/home/testing/src", "$WORKDIR/src"]

# ** info: cleaning the python __pycache__ files
RUN find . | grep -E "(/__pycache__$|\.pyc$|\.pyo$)" | xargs rm -rf

# ** info: removing the app requirements file
RUN rm -r requirements.app.txt

# ** info: establishing the default user inside the production image
USER $USERNAME

# ** info: executing the app
ENTRYPOINT ["python", "src/main.py"]