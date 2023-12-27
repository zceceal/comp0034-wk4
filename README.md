# Testing REST API routes

_COMP0034 2023-24 Week 4 coding activities_

## 1. Preparation and introduction

This assumes you have already forked the coursework repository and cloned the resulting repository to your IDE.

1. Create and activate a virtual environment
2. Install the requirements `pip install -r requirements.txt`
3. Run the app `flask --app paralympics run --debug`
4. Open a browser and go to http://127.0.0.1:5000/regions
5. Stop the app using `CTRL+C`
6. Check that you have an instance folder containing `paralympics.sqlite`
7. Add data to the database by running `data\add_data.py`

## Overview

This tutorial focuses on functional testing covering:

1. The Flask routes
2. Simulated user behaviour when using the app in a web browser

Refer to the COMP0035 week 9 tutorial for:

- test naming convention
- using GIVEN-WHEN-THEN style syntax to specify a test
- Unit tests with pytest
- running pytest tests
- Pytest fixtures, including adding these to `conftest.py`
- using GitHub Actions to automatically run tests when code is pushed to GitHub
- coverage reporting
- using GitHub CoPilot or ChatGPT to write tests

## Setup the test environment

To do this you need to:

1. Install pytest and Selenium
2. Create a tests directory and test files
3. Install your app code

### 1. Install pytest and selenium

Make sure you have installed pytest and selenium in your Python environment e.g.: `pip install pytest selenium`

You may also need to configure your IDE to support running pytest tests, follow the relevant documentation:

- [Pycharm help: Testing frameworks](https://www.jetbrains.com/help/pycharm/testing-frameworks.html)
- [Python testing in VS Code](https://code.visualstudio.com/docs/python/testing)

### 2. Create a test folder and files

- Create a folder called `tests`. Refer to
  the [pytest documentation](https://docs.pytest.org/en/7.1.x/explanation/goodpractices.html#choosing-a-test-layout-import-rules)
  for alternate test directory structures.
- Create a Python test file in the `tests` folder called `test_routes.py` and another called `test_browser.py`. You will
  add the tests to this.
- Create an empty Python file in the `tests` folder called `conftest.py`. You will add the fixtures to this.

### 3. Install your app code

You should have an a `pyproject.toml`.

In the Terminal of your IDE, install your code using `pip unstall -e .`

Note: The `.` is part of the command and not a typo!

If you don't have a `pyproject.toml` then you need to create one. The minimum you need is:

```toml
[project]
name = "paralympics"

[build-system]
requires = [
    "setuptools>=65.0",
    "setuptools-scm[toml]>=6.2.3",
]
build-backend = "setuptools.build_meta"
```

## Test the REST API routes using the Flask test client and pytest

To test the routes you will use a combination of:

- [Flask test client](https://flask.palletsprojects.com/en/3.0.x/testing/#fixtures) to create a running Flask app in a
  Pytest fixture
- [Pytest](https://docs.pytest.org/en/7.1.x/explanation/goodpractices.html#choosing-a-test-layout-import-rules) for test
  assertions

### Create a Flask test client as a pytest fixture

This is explained with code in the [Flask documentation](https://flask.palletsprojects.com/en/3.0.x/testing/#fixtures).

Add the following to `conftest.py`:

```python
import pytest
from paralympics import create_app


@pytest.fixture()
def app():
    app = create_app()
    app.config.update({
        "TESTING": True,
    })

    # TODO: Add data to the database
    with app.app_context():

    yield app

    # clean up / reset resources


@pytest.fixture()
def client(app):
    return app.test_client()
```

### Using the Flask Test Client for API routes

This is explained in the Flask documentation
in [Sending Requests with the Test Client](https://flask.palletsprojects.com/en/3.0.x/testing/#sending-requests-with-the-test-client)
which you should read now.

You use the Flask test client to make an HTTP request to one of your API routes.

You can then access the response from the HTTP request and use Pytest assertions to test for conditions such as:

- the JSON payload (`response.json`)
- the HTTP status code (`request.status_code`)
- page content (`response.data`). This is not relevant for the API routes so is not covered in this tutorial.

The HTTP status codes you might expect are:

- 404 Resource not found
– 200 OK for GET requests
– 201 for POST or PUT requests creating a new resource 
– 200, 202, or 204 for a DELETE operation

The test cases that you might write could include:

- Positive tests (happy paths)
- Positive tests with optional parameters
- Negative tests with valid input
- Negative tests with invalid input
- Security, authorization, and permission tests (not covered in this tutorial)

### Test the 
Add the following test code to `test_routes.py` and run the test:





## Test the REST API routes from a browser using Selenium Webdriver and pytest

To test from the browser you will use a combination of:

- [Flask test client](https://flask.palletsprojects.com/en/3.0.x/testing/#fixtures) to create a running Flask app in a
  Pytest fixture
- [Selenium webdriver](https://www.selenium.dev/documentation/webdriver/) to launch and navigate the browser interface (
  i.e. to simulate user clicks and interactions)
- [Chrome driver](https://chromedriver.chromium.org/downloads) to allow Selenium to work with Chrome browser. The
  Selenium webdriver passes commands to the browser
  through the Chrome driver, and receives information back via the same route.
- [Pytest](https://docs.pytest.org/en/7.1.x/explanation/goodpractices.html#choosing-a-test-layout-import-rules) for test
  assertions

### Check Chrome driver works

You will use the Chrome browser for this tutorial, though Selenium supports a number of browsers (Firefox, Safari,
Edge).

In mid-2023, Chromium.org changed how the Chrome Driver works. Also from Selenium version 4.6 it is no longer required
to
explicitly download Chrome Driver.

As a result of the above two changes, any tutorials before mid to late 2023 that explain how to set-up the Chrome driver
will be misleading.

In `test_browser.py` add the following code:

```python
from selenium import webdriver

# Create a Chrome driver
driver = webdriver.Chrome()
# Use the driver to navigate to the Google home page
driver.get("https://www.google.com/")
# Wait for 3 seconds
driver.implicitly_wait(3)
```

Run the code. It should launch Chrome, go to the Google home page and wait for 3 seconds.


## Reading
https://www.sisense.com/blog/rest-api-testing-strategy-what-exactly-should-you-test/