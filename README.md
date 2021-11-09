# Leave Management App
Leave management app is a django application that helps employees and managers manage their leaves. This project was the capstone for CS50 Web Programming with Python and Javascript. 

## Features

- **A login and register page.**

- **Employee account**:
  - Number of days of leave left.
  - Apply leave form: includes start date, end date, and who is the superior in charge. Supports both half and full day type leaves.
  - Once leave is approved by a manager, update total leave count on profile.
  - If leave is rejected, total leave count would not change.
  - A tool to help calculate how many days of leave is taken by the employee.

- **Manager account**:
  - List of employees under them ordered by name.
  - Table view of when employees are on leave, arranged chronologically for better planning.
  - List of pending leaves with approve or reject leave button.
  - Section to add new members this manager is in charge of.

## Demonstration 

[Click here to view the demonstration on Youtube](https://youtu.be/TVhaovQ0HVQ)

## How to run this application

### In your terminal

Run this to make migrations for leave app.

```shell
python manage.py makemigrations leave
```

Run this to apply migrations.

```shell
python manage.py migrate
```

Open the server and visit the website using your browser.

```shell
python manage.py runserver
```
