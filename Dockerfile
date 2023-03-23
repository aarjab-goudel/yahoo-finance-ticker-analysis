# Use the official OpenJDK 11 JRE slim image as base
FROM openjdk:11-jre-slim

# Install Python 3.10 and pipenv
RUN apt-get update && \
    apt-get install -y python3.10 python3.10-dev python3-pip && \
    pip3 install pipenv

# Set the working directory
WORKDIR /app

# Copy the three jar files to the working directory
COPY AnnualAndFuture.jar Quarterly.jar ./

# Copy the Pipfile and Pipfile.lock to the working directory
COPY Pipfile Pipfile.lock ./

# Create a logs directory
RUN mkdir logs


# Install Python dependencies using pipenv
RUN pipenv install --system --deploy --ignore-pipfile

# Set the entrypoint to run the Java code
ENTRYPOINT ["java", "-jar", "AllInOne.jar"]

RUN mkdir app/logs








 
